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
        self.assertEqual(ctx.profile["run_history"][0]["grade"], "A")
        self.assertTrue(ctx.last_unlock_lines[0] != "")

    def test_finalize_run_result_updates_grades_and_records(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Arcade"
        ctx.score = 5200
        ctx.current_level = 3
        ctx.start_seeded_run(2468)
        ctx.run_stats.ghosts_eaten = 6
        ctx.run_stats.line_bonuses = 3
        ctx.pre_run_unlock_snapshot = ctx.unlock_snapshot()

        ctx.finalize_run_result("game_won")

        self.assertEqual(ctx.profile["mode_records"]["Arcade"]["best_score"], 5200)
        self.assertEqual(ctx.profile["mode_records"]["Arcade"]["best_grade"], "S")
        self.assertEqual(ctx.profile["mode_records"]["Arcade"]["wins"], 1)
        self.assertEqual(ctx.profile["district_records"]["5"]["best_mode_scores"]["Arcade"], 5200)
        self.assertEqual(ctx.profile["run_history"][0]["map"], 5)
        self.assertEqual(ctx.profile["run_history"][0]["seed"], 2470)

    def test_start_new_game_uses_requested_seed(self) -> None:
        ctx = self._fresh_context()
        ctx.set_requested_seed(123456)

        ctx.start_new_game()

        self.assertEqual(ctx.run.run_seed, 123456)
        self.assertEqual(ctx.current_level_seed(), 123456)
        self.assertEqual(ctx.profile["last_seed"], 123456)

    def test_daily_challenge_consumes_one_attempt_per_day(self) -> None:
        ctx = self._fresh_context()
        ctx._today_iso = lambda: "2026-05-17"
        ctx.game_mode = "DailyChallenge"

        self.assertTrue(ctx.start_new_game())
        self.assertEqual(ctx.run.run_seed, ctx.daily_seed())
        self.assertEqual(ctx.profile["daily_challenge_last_date"], "2026-05-17")

        self.assertFalse(ctx.start_new_game())

    def test_daily_directives_and_series_progress_update_on_finalize(self) -> None:
        ctx = self._fresh_context()
        ctx._today_iso = lambda: "2026-04-20"
        ctx._daily_directive_pool = lambda: (
            ("clear-run", "Finish any run", 1, "Clear any district result screen"),
            ("score-2200", "Reach 2200 score", 2200, "Push one run above 2200"),
            ("ghosts-4", "Eat 4 ghosts", 4, "Convert two power windows cleanly"),
        )
        ctx.profile["daily_progress"]["date"] = "2026-04-20"
        ctx.profile["daily_progress"]["completed"] = ["score-2200", "ghosts-4"]
        ctx.game_mode = "Arcade"
        ctx.score = 4100
        ctx.current_level = 2
        ctx.run_stats.ghosts_eaten = 5
        ctx.run_stats.near_misses = 1
        ctx.pre_run_unlock_snapshot = ctx.unlock_snapshot()

        ctx.finalize_run_result("game_won")

        self.assertEqual(ctx.profile["daily_progress"]["streak"], 1)
        self.assertIn("clear-run", ctx.profile["daily_progress"]["completed"])
        self.assertEqual(ctx.profile["series_progress"]["clear_streak"], 1)
        self.assertEqual(ctx.profile["series_progress"]["grade_streak"], 1)

    def test_score_focus_summary_highlights_real_score_drivers(self) -> None:
        ctx = self._fresh_context()
        ctx.run_stats.ghost_bonus_score = 1200
        ctx.run_stats.route_bonus_score = 340
        ctx.run_stats.risk_bonus_score = 180

        lines = ctx.score_focus_summary_lines()

        self.assertIn("Ghost Hunt +1200", lines[0])
        self.assertIn("Route Control +340", lines[1])

    def test_death_reason_detail_reflects_pressure_stage(self) -> None:
        ctx = self._fresh_context()
        ctx.run.last_killer_name = "Blinky"
        ctx.run.ghost_mode = "chase"
        ctx.run.pressure_stage = 3

        detail = ctx.death_reason_detail()

        self.assertIn("BLINKY", detail)
        self.assertIn("PRESSURE STAGE 3", detail)

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
