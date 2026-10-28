from math import pi
from pathlib import Path

from pico2d import (SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a,
                    get_canvas_width, load_image)

RUN_SPEED = 200.0
NORMAL_SIZE = 100
AUTO_SPEED = RUN_SPEED * 2
AUTO_SIZE = NORMAL_SIZE * 2
AUTO_DURATION = 5.0
SLEEP_DELAY = 5.0
ANIMATION_FPS = 10.0


class Idle:
    @staticmethod
    def enter(boy):
        boy.idle_elapsed = 0.0

    @staticmethod
    def update(boy, dt):
        boy.idle_elapsed += dt
        if boy.idle_elapsed >= SLEEP_DELAY:
            boy.change_state(Sleep)


class Sleep:
    @staticmethod
    def enter(boy):
        pass

    @staticmethod
    def update(boy, dt):
        pass


class Run:
    @staticmethod
    def enter(boy):
        pass

    @staticmethod
    def update(boy, dt):
        half = NORMAL_SIZE / 2
        boy.x = max(half, min(get_canvas_width() - half,
                             boy.x + boy.face_dir * RUN_SPEED * dt))


class AutoRun:
    @staticmethod
    def enter(boy):
        boy.auto_elapsed = 0.0
        boy.run_keys.clear()
        half = AUTO_SIZE / 2
        boy.x = max(half, min(get_canvas_width() - half, boy.x))

    @staticmethod
    def update(boy, dt):
        # Move only for the remaining AutoRun time, even after a slow frame.
        move_dt = min(dt, AUTO_DURATION - boy.auto_elapsed)
        boy.auto_elapsed += dt
        boy.x += boy.face_dir * AUTO_SPEED * move_dt
        left, right = AUTO_SIZE / 2, get_canvas_width() - AUTO_SIZE / 2
        # Reflect overshoot so movement remains consistent across frame rates.
        while boy.x < left or boy.x > right:
            if boy.x > right:
                boy.x = 2 * right - boy.x
                boy.face_dir = -1
            elif boy.x < left:
                boy.x = 2 * left - boy.x
                boy.face_dir = 1
        if boy.x == left:
            boy.face_dir = 1
        elif boy.x == right:
            boy.face_dir = -1
        if boy.auto_elapsed >= AUTO_DURATION:
            boy.change_state(Idle)


class Boy:
    def __init__(self):
        self.x = get_canvas_width() / 2
        self.frame = 0.0
        self.face_dir = 1
        self.run_keys = []
        self.image = load_image(str(Path(__file__).with_name('animation_sheet.png')))
        self.change_state(Idle)

    def change_state(self, state):
        self.state = state
        self.frame = 0.0
        state.enter(self)

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE and self.state is Sleep:
            self.change_state(Idle)
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_a:
            if self.state is Idle:
                self.change_state(AutoRun)
            return
        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return
        if event.type == SDL_KEYDOWN:
            if event.key not in self.run_keys:
                self.run_keys.append(event.key)
            self.face_dir = 1 if self.run_keys[-1] == SDLK_RIGHT else -1
            if self.state is not Run:
                self.change_state(Run)
        else:
            if event.key in self.run_keys:
                self.run_keys.remove(event.key)
            if self.state is Run:
                if self.run_keys:
                    self.face_dir = 1 if self.run_keys[-1] == SDLK_RIGHT else -1
                else:
                    self.change_state(Idle)

    def update(self, dt):
        if self.state is not Sleep:
            self.frame = (self.frame + ANIMATION_FPS * dt) % 8
        self.state.update(self, dt)

    def draw(self):
        size = AUTO_SIZE if self.state is AutoRun else NORMAL_SIZE
        row = 300 if self.face_dir == 1 else 200
        if self.state is Sleep:
            self.image.clip_composite_draw(int(self.frame) * 100, row, 100, 100,
                                           self.face_dir * pi / 2, '', self.x, 70,
                                           NORMAL_SIZE, NORMAL_SIZE)
            return
        if self.state is not Idle:
            row -= 200
        # The sprite's feet sit about 13 pixels above the 100-pixel cell bottom.
        self.image.clip_draw(int(self.frame) * 100, row, 100, 100,
                             self.x, 53 + size * 0.37, size, size)
