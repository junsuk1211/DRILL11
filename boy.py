from math import pi
from time import monotonic

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE,
    get_canvas_width, load_image,
)
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.move_dir = 0
        self.pressed_directions = []
        self.image = load_image('animation_sheet.png')
        self.idle_start_time = monotonic()
        self.machine = Machine(
            model=self,
            states=[
                {'name': 'IDLE', 'on_enter': 'enter_idle'},
                {'name': 'RUN', 'on_enter': 'enter_run'},
                'SLEEP',
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        self.machine.add_transition('fall_asleep', 'IDLE', 'SLEEP')
        self.machine.add_transition('wake_up', 'SLEEP', 'IDLE')
        self.machine.add_transition('start_running', ['IDLE', 'SLEEP'], 'RUN')
        self.machine.add_transition('stop_running', 'RUN', 'IDLE')

    def enter_idle(self):
        self.frame = 0
        self.move_dir = 0
        self.idle_start_time = monotonic()

    def enter_run(self):
        self.frame = 0

    def handle_event(self, event):
        if self.state == 'SLEEP' and event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.wake_up()
            return

        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        if event.type == SDL_KEYDOWN:
            if event.key not in self.pressed_directions:
                self.pressed_directions.append(event.key)
        elif event.key in self.pressed_directions:
            self.pressed_directions.remove(event.key)

        if self.pressed_directions:
            self.move_dir = 1 if self.pressed_directions[-1] == SDLK_RIGHT else -1
            self.face_dir = self.move_dir
            if self.state in ('IDLE', 'SLEEP'):
                self.start_running()
        elif self.state == 'RUN':
            self.stop_running()

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if monotonic() - self.idle_start_time >= 5.0:
                self.fall_asleep()
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8
            self.x = max(50, min(get_canvas_width() - 50, self.x + self.move_dir * 3))

    def draw(self):
        if self.state == 'IDLE':
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(0, row, 100, 100, self.face_dir * pi / 2, '', self.x, self.y - 25, 100, 100)
