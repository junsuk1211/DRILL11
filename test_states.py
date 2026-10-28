import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import boy as module
import autorun


class StateTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        for target, value in (
            ('boy.load_image', Mock()), ('boy.get_canvas_width', 800),
            ('autorun.get_canvas_width', 800),
        ):
            patcher = patch(target, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for target in ('boy.monotonic', 'autorun.monotonic'):
            patcher = patch(target, side_effect=lambda: self.now)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.boy = module.Boy()

    def key(self, code, down=True):
        self.boy.handle_event(SimpleNamespace(
            type=module.SDL_KEYDOWN if down else module.SDL_KEYUP, key=code))

    def advance(self, seconds):
        self.now += seconds
        self.boy.update()

    def test_sleep_and_space(self):
        self.advance(4.999)
        self.assertEqual(self.boy.state, 'IDLE')
        self.advance(.001)
        self.assertEqual(self.boy.state, 'SLEEP')
        self.key(module.SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_manual_keys_and_boundaries(self):
        self.key(module.SDLK_LEFT)
        self.advance(2)
        self.assertEqual(self.boy.x, 50)
        self.key(module.SDLK_RIGHT)
        self.key(module.SDLK_LEFT)  # Repeated keydown does not override latest press.
        self.assertEqual(self.boy.move_dir, 1)
        self.advance(3)
        self.assertEqual(self.boy.x, 750)
        self.key(module.SDLK_RIGHT, False)
        self.assertEqual(self.boy.move_dir, -1)
        self.key(module.SDLK_LEFT, False)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_sleep_to_run(self):
        self.advance(5)
        self.key(module.SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'RUN')


if __name__ == '__main__':
    unittest.main()
