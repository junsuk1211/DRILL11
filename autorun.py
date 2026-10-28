from pico2d import get_canvas_width


class AutoRun:
    """Behavior and lifecycle of the automatic running state."""

    SPEED = 600.0
    SCALE = 1.5

    def enter(self, boy):
        boy.frame = 0
        boy.move_dir = boy.face_dir
        boy.pressed_directions.clear()

    def exit(self, boy):
        pass

    def update(self, boy, dt):
        boy.x += boy.move_dir * self.SPEED * dt

    def draw(self, boy):
        boy.draw_running(scale=self.SCALE)
