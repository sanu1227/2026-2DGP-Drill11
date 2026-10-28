from pathlib import Path

from pico2d import (SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT,
                    get_canvas_width, load_image)

RUN_SPEED = 200.0
NORMAL_SIZE = 100
ANIMATION_FPS = 10.0


class Idle:
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
        self.frame = (self.frame + ANIMATION_FPS * dt) % 8
        self.state.update(self, dt)

    def draw(self):
        size = NORMAL_SIZE
        row = 300 if self.face_dir == 1 else 200
        if self.state is not Idle:
            row -= 200
        self.image.clip_draw(int(self.frame) * 100, row, 100, 100,
                             self.x, 40 + size / 2, size, size)
