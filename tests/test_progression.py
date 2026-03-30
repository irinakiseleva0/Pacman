from __future__ import annotations

import unittest
from copy import deepcopy

from core.context import GameContext
from utils.profile_storage import DEFAULT_PROFILE


class ProgressionTests(unittest.TestCase):
    def _fresh_context(self) -> GameContext:
        ctx = GameContext()
        ctx.profile = deepcopy(DEFAULT_PROFILE)
        ctx.profile_service.save = lambda: None
        ctx.run.high_score = 0
        return ctx

    def test_theme_unlock_progression_rules(self) -> None:
        ctx = self._fresh_context()
        self.assertTrue(ctx.theme_unlocked("Neon District"))
        self.assertFalse(ctx.theme_unlocked("Cool Summer"))

        ctx.profile["total_levels_cleared"] = 3
        self.assertTrue(ctx.theme_unlocked("Cool Summer"))

        ctx.profile["best_score"] = 4200
        self.assertTrue(ctx.theme_unlocked("Solar Pulse"))

    def test_finalize_run_result_updates_challenge_progress(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Challenge"
        ctx.challenge_name = "One Life District"
        ctx.score = 3200
        ctx.current_level = 1
        ctx.pre_run_unlock_snapshot = ctx.unlock_snapshot()
        ctx.run_stats.ghosts_eaten = 2
        ctx.run_stats.dots_eaten = 40

        ctx.finalize_run_result("game_won")

        self.assertEqual(ctx.profile["total_wins"], 1)
        self.assertEqual(ctx.profile["challenge_credits"], 3)
        self.assertEqual(ctx.profile["challenge_clears"], 1)
        self.assertEqual(ctx.profile["challenge_rewards"]["One Life District"], 1)
        self.assertEqual(ctx.profile["run_history"][0]["mode"], "Challenge")
        self.assertTrue(ctx.last_unlock_lines[0] != "")

    def test_start_new_game_tracks_selected_mode_run(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Endless"
        ctx.difficulty = "Hard"
        ctx.score = 999

        ctx.start_new_game()

        self.assertEqual(ctx.profile["total_runs"], 1)
        self.assertEqual(ctx.profile["mode_runs"]["Endless"], 1)
        self.assertEqual(ctx.profile["difficulty_runs"]["Hard"], 1)
        self.assertEqual(ctx.score, 0)
        self.assertEqual(ctx.current_level, 1)

    def test_directive_pack_unlocks_follow_style_medals(self) -> None:
        ctx = self._fresh_context()

        self.assertEqual(ctx.directive_pack_names(), {"Core Directives"})

        ctx.profile["style_medals"]["No Panic Clear"] = 1
        ctx.profile["style_medals"]["Line Master"] = 1
        self.assertIn("Style Circuit", ctx.directive_pack_names())

        ctx.profile["style_medals"]["Predator Run"] = 2
        self.assertIn("Predator Protocol", ctx.directive_pack_names())
