from __future__ import annotations

import unittest

from utils.effects import GlitchEffect


class GlitchEffectTests(unittest.TestCase):
    def test_glitch_intensity_ramps_then_fades(self) -> None:
        effect = GlitchEffect(duration=1.5)
        effect.trigger()

        effect.update(0.25)
        self.assertAlmostEqual(effect.intensity, 0.5)
        self.assertTrue(effect.is_active())

        effect.update(0.25)
        self.assertAlmostEqual(effect.intensity, 1.0)

        effect.update(0.5)
        self.assertAlmostEqual(effect.intensity, 0.5)

        effect.update(0.5)
        self.assertEqual(effect.intensity, 0.0)
        self.assertFalse(effect.is_active())


if __name__ == "__main__":
    unittest.main()
