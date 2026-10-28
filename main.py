from pathlib import Path
from time import monotonic

from pico2d import (SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, clear_canvas,
                    close_canvas, delay, get_events, load_image, open_canvas,
                    update_canvas)

from boy import Boy


def main():
    open_canvas(800, 600)
    try:
        grass = load_image(str(Path(__file__).with_name('grass.png')))
        boy = Boy()
        running = True
        previous = monotonic()
        while running:
            for event in get_events():
                if (event.type == SDL_QUIT or
                        event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE):
                    running = False
                else:
                    boy.handle_event(event)
            if not running:
                break
            now = monotonic()
            boy.update(now - previous)
            previous = now
            clear_canvas()
            grass.draw(400, 30)
            boy.draw()
            update_canvas()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
