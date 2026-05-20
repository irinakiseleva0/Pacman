from __future__ import annotations

import unittest
from copy import deepcopy

from core.achievements import ACHIEVEMENTS, AchievementManager
from core.context import GameContext
from utils.profile_storage import DEFAULT_PROFILE


class AchievementManagerTests(unittest.TestCase):
    def _fresh_context(self) -> GameContext:
        ctx = GameContext()
        ctx.profile = deepcopy(DEFAULT_PROFILE)
        ctx.profile_service.save = lambda: None
        return ctx

    def test_has_required_achievement_catalog(self) -> None:
        titles = {achievement.title for achievement in ACHIEVEMENTS}

        self.assertEqual(len(ACHIEVEMENTS), 15)
        self.assertTrue({"First Blood", "Ghost Buster", "Speed Run", "Pacifist"}.issubset(titles))

    def test_unlocks_are_saved_once_in_profile(self) -> None:
        ctx = self._fresh_context()
        manager = AchievementManager()
        ctx.run_stats.ghosts_eaten = 1

        first_unlocks = manager.check_all(ctx)
        second_unlocks = manager.check_all(ctx)

        self.assertIn("first_blood", ctx.profile["achievements"])
        self.assertEqual([achievement.key for achievement in first_unlocks], ["first_blood"])
        self.assertEqual(second_unlocks, [])

    def test_level_clear_unlocks_speed_run_and_pacifist(self) -> None:
        ctx = self._fresh_context()
        ctx.run_stats.level_elapsed_seconds = 12.0

        ctx.record_level_cleared()

        self.assertEqual(ctx.profile["achievements"]["speed_run"], 1)
        self.assertEqual(ctx.profile["achievements"]["pacifist"], 1)


if __name__ == "__main__":
    unittest.main()
