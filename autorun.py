class AutoRun:
    """Behavior and lifecycle of the automatic running state."""

    def enter(self, boy):
        boy.frame = 0
        boy.move_dir = boy.face_dir
        boy.pressed_directions.clear()

    def exit(self, boy):
        pass

    def update(self, boy, dt):
        pass

    def draw(self, boy):
        boy.draw_running()
