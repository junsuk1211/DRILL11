from time import monotonic

from pico2d import get_canvas_width


class AutoRun:
    """Behavior and lifecycle of the automatic running state."""

    SPEED = 600.0
    SCALE = 1.5
    DURATION = 5.0

    def enter(self, boy):
        boy.invincible = True
        self.started_at = monotonic()
        boy.frame = 0
        boy.move_dir = boy.face_dir
        boy.pressed_directions.clear()
        half_size = 50 * self.SCALE
        boy.x = max(half_size, min(get_canvas_width() - half_size, boy.x))

    def exit(self, boy):
        boy.invincible = False

    def update(self, boy, dt):
        if monotonic() - self.started_at >= self.DURATION:
            boy.finish_autorun()
            return
        left = 50 * self.SCALE
        right = get_canvas_width() - left
        span = right - left
        if span <= 0:
            boy.x = get_canvas_width() / 2
            return
        # Reflect all overshoot, including multiple wall crossings in a long frame.
        offset = boy.x - left
        phase = offset if boy.move_dir == 1 else 2 * span - offset
        phase = (phase + self.SPEED * dt) % (2 * span)
        boy.x = left + (phase if phase < span else 2 * span - phase)
        boy.move_dir = 1 if phase < span else -1
        boy.face_dir = boy.move_dir

    def draw(self, boy):
        boy.draw_running(scale=self.SCALE)
