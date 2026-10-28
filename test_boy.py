"""Run with: python -m unittest -v (no game window required)."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_a

from boy import AutoRun, Boy, Idle, Run


class BoyTests(unittest.TestCase):
    def setUp(self):
        width = patch('boy.get_canvas_width', return_value=800)
        image = patch('boy.load_image')
        width.start()
        image.start()
        self.addCleanup(width.stop)
        self.addCleanup(image.stop)
        self.boy = Boy()

    def key(self, key, event_type=SDL_KEYDOWN):
        self.boy.handle_event(SimpleNamespace(type=event_type, key=key))

    def test_idle_a_starts_faster_larger_run_without_held_keys(self):
        self.assertIs(self.boy.state, Idle)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (100, 100))
        self.key(SDLK_a)
        self.boy.update(0.25)
        self.assertIs(self.boy.state, AutoRun)
        self.assertEqual(self.boy.run_keys, [])
        self.assertAlmostEqual(self.boy.x, 500)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (200, 200))

    def test_returns_idle_at_five_seconds_and_stays_stopped(self):
        self.key(SDLK_a)
        self.boy.update(4.99)
        self.assertIs(self.boy.state, AutoRun)
        self.boy.update(0.01)
        self.assertIs(self.boy.state, Idle)
        stopped_x = self.boy.x
        self.boy.update(1.0)
        self.assertEqual(self.boy.x, stopped_x)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (100, 100))

    def test_reflects_at_both_edges_including_exact_boundary(self):
        for start, direction, dt, expected, expected_direction in (
                (690, 1, 0.05, 690, -1),
                (110, -1, 0.05, 110, 1),
                (600, 1, 0.25, 700, -1),
                (200, -1, 0.25, 100, 1)):
            with self.subTest(start=start, direction=direction):
                self.boy.change_state(AutoRun)
                self.boy.x, self.boy.face_dir = start, direction
                self.boy.update(dt)
                self.assertAlmostEqual(self.boy.x, expected)
                self.assertEqual(self.boy.face_dir, expected_direction)
                self.assertGreaterEqual(self.boy.x, 100)
                self.assertLessEqual(self.boy.x, 700)

    def test_slow_frame_reflects_multiple_times_and_limits_motion_to_five_seconds(self):
        self.key(SDLK_a)
        self.boy.update(10.0)
        self.assertIs(self.boy.state, Idle)
        self.assertAlmostEqual(self.boy.x, 200)
        self.assertEqual(self.boy.face_dir, -1)

    def test_each_arrow_cancels_auto_and_restores_manual_speed_and_size(self):
        for key, direction in ((SDLK_LEFT, -1), (SDLK_RIGHT, 1)):
            with self.subTest(key=key):
                self.boy.change_state(Idle)
                self.boy.x = 400
                self.key(SDLK_a)
                self.key(key)
                self.assertIs(self.boy.state, Run)
                self.assertEqual(self.boy.face_dir, direction)
                self.boy.update(0.25)
                self.assertAlmostEqual(self.boy.x, 400 + direction * 50)
                self.boy.draw()
                self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (100, 100))
                self.key(key, SDL_KEYUP)
                self.assertIs(self.boy.state, Idle)

    def test_last_pressed_arrow_wins_and_release_falls_back(self):
        self.key(SDLK_LEFT)
        self.key(SDLK_RIGHT)
        self.key(SDLK_LEFT)  # A repeat must not override the most recent press.
        self.assertEqual(self.boy.face_dir, 1)
        self.assertEqual(len(self.boy.run_keys), 2)
        self.key(SDLK_RIGHT, SDL_KEYUP)
        self.assertIs(self.boy.state, Run)
        self.assertEqual(self.boy.face_dir, -1)
        self.key(SDLK_LEFT, SDL_KEYUP)
        self.assertIs(self.boy.state, Idle)

    def test_a_only_starts_from_idle_and_keyup_does_not_cancel_auto(self):
        self.key(SDLK_RIGHT)
        self.key(SDLK_a)
        self.assertIs(self.boy.state, Run)
        self.key(SDLK_RIGHT, SDL_KEYUP)
        self.key(SDLK_a)
        self.boy.update(1.0)
        self.key(SDLK_a)
        self.key(SDLK_LEFT, SDL_KEYUP)
        self.key(SDLK_a, SDL_KEYUP)
        self.assertIs(self.boy.state, AutoRun)
        self.assertAlmostEqual(self.boy.auto_elapsed, 1.0)
        self.boy.update(4.0)
        self.assertIs(self.boy.state, Idle)

    def test_entering_auto_at_manual_edge_keeps_enlarged_image_inside(self):
        for edge, expected in ((50, 100), (750, 700)):
            with self.subTest(edge=edge):
                self.boy.change_state(Idle)
                self.boy.x = edge
                self.key(SDLK_a)
                self.assertEqual(self.boy.x, expected)


if __name__ == '__main__':
    unittest.main()
