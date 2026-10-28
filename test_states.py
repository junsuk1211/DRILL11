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


class AutoRunTests(StateTests):
    def activate(self):
        self.key(module.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTORUN')

    def test_activation_and_speed(self):
        self.activate()
        self.assertTrue(self.boy.invincible)
        self.advance(.1)
        self.assertAlmostEqual(self.boy.x, 460)
        self.assertGreater(autorun.AutoRun.SPEED, module.RUN_SPEED)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (150, 150))

    def test_both_walls_and_overshoot(self):
        self.activate()
        self.boy.x = 720
        self.advance(.1)
        self.assertAlmostEqual(self.boy.x, 670)
        self.assertEqual(self.boy.face_dir, -1)
        self.boy.x = 80
        self.advance(.1)
        self.assertAlmostEqual(self.boy.x, 130)
        self.assertEqual(self.boy.face_dir, 1)
        self.advance(3)
        self.assertTrue(75 <= self.boy.x <= 725)

    def test_timeout_and_idle_timer_restart(self):
        self.activate()
        self.advance(4.999)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.advance(.001)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertFalse(self.boy.invincible)
        self.assertEqual(self.boy.move_dir, 0)
        self.boy.draw()
        self.assertEqual(len(self.boy.image.clip_draw.call_args.args), 6)
        self.advance(4.999)
        self.assertEqual(self.boy.state, 'IDLE')
        self.advance(.001)
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_cancel_in_either_direction(self):
        for code, direction in ((module.SDLK_LEFT, -1), (module.SDLK_RIGHT, 1)):
            self.activate()
            self.key(code)
            self.assertEqual(self.boy.state, 'RUN')
            self.assertEqual(self.boy.move_dir, direction)
            self.assertFalse(self.boy.invincible)
            start = self.boy.x
            self.advance(.1)
            self.assertAlmostEqual(self.boy.x, start + direction * 30)
            self.key(code, False)
            self.assertEqual(self.boy.state, 'IDLE')

    def test_a_does_not_restart_duration(self):
        self.activate()
        self.advance(4)
        self.key(module.SDLK_a)
        self.advance(1)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_activation_clamps_enlarged_bounds_and_keeps_facing(self):
        self.boy.x = 50
        self.boy.face_dir = -1
        self.activate()
        self.assertEqual(self.boy.x, 75)
        self.assertEqual(self.boy.move_dir, -1)
        self.advance(.01)
        self.assertGreaterEqual(self.boy.x, 75)
        self.assertEqual(self.boy.move_dir, 1)

    def test_a_is_ignored_during_manual_run(self):
        self.key(module.SDLK_LEFT)
        self.key(module.SDLK_a)
        self.assertEqual(self.boy.state, 'RUN')
        self.assertFalse(self.boy.invincible)

    def test_sleep_a_wakes_into_autorun_in_facing_direction(self):
        self.boy.face_dir = -1
        self.advance(5)
        self.assertEqual(self.boy.state, 'SLEEP')
        self.key(module.SDLK_a, False)
        self.assertEqual(self.boy.state, 'SLEEP')
        self.key(module.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.assertTrue(self.boy.invincible)
        self.assertEqual(self.boy.move_dir, -1)
        self.advance(.1)
        self.assertAlmostEqual(self.boy.x, 340)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (150, 150))

    def test_sleep_a_starts_fresh_five_second_duration(self):
        self.advance(20)
        self.assertEqual(self.boy.state, 'SLEEP')
        self.key(module.SDLK_a)
        self.advance(4.999)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.advance(.001)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertFalse(self.boy.invincible)
        self.advance(4.999)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_sleep_autorun_can_be_cancelled_by_either_direction(self):
        for code, direction in ((module.SDLK_LEFT, -1), (module.SDLK_RIGHT, 1)):
            self.advance(5)
            self.assertEqual(self.boy.state, 'SLEEP')
            self.key(module.SDLK_a)
            self.key(code)
            self.assertEqual(self.boy.state, 'RUN')
            self.assertEqual(self.boy.move_dir, direction)
            self.assertFalse(self.boy.invincible)
            self.key(code, False)
            self.assertEqual(self.boy.state, 'IDLE')

    def test_keyup_does_not_cancel_autorun(self):
        self.activate()
        self.key(module.SDLK_LEFT, False)
        self.assertEqual(self.boy.state, 'AUTORUN')


if __name__ == '__main__':
    unittest.main()
