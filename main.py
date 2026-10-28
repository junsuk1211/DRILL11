from pathlib import Path
import os

from pico2d import (
    SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, open_canvas, close_canvas,
    get_events, clear_canvas, update_canvas, delay,
)

from boy import Boy
from grass import Grass


def main():
    os.chdir(Path(__file__).resolve().parent)
    open_canvas(800, 600)
    try:
        boy = Boy()
        world = [Grass(), boy]
        running = True
        while running:
            for event in get_events():
                if event.type == SDL_QUIT:
                    running = False
                elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                    running = False
                else:
                    boy.handle_event(event)
            for obj in world:
                obj.update()
            clear_canvas()
            for obj in world:
                obj.draw()
            update_canvas()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
