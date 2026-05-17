from __future__ import annotations

import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from core.context import GameContext
from entities.bonus_gate import BonusGate
from entities.hotspot_seed import HotspotSeed
from entities.pulse_barrier import PulseBarrier
from utils.effects import FloatingText
from utils.profile_storage import DEFAULT_PROFILE


class ContentMechanicsTests(unittest.TestCase):
    def _fresh_context(self) -> GameContext:
        ctx = GameContext()
        ctx.profile = deepcopy(DEFAULT_PROFILE)
        ctx.profile_service.save = lambda: None
        return ctx

    def test_gate_crasher_challenge_uses_bonus_gate_target(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Challenge"
        ctx.challenge_name = "Gate Crasher"

        ctx.run_stats.bonus_gates = 2
        self.assertEqual(ctx.challenge_result_on_clear(), "challenge_failed")

        ctx.run_stats.bonus_gates = 3
        self.assertEqual(ctx.challenge_result_on_clear(), "game_won")

    def test_multi_goal_challenge_requires_all_new_objectives(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Challenge"
        ctx.challenge_name = "Jackpot Circuit"

        ctx.run_stats.cherries_eaten = 3
        ctx.run_stats.bonus_gates = 1
        self.assertEqual(ctx.challenge_result_on_clear(), "challenge_failed")

        ctx.run_stats.bonus_gates = 2
        self.assertEqual(ctx.challenge_result_on_clear(), "game_won")

    def test_content_pass_expands_new_challenge_scenarios(self) -> None:
        scenario_names = {
            "Market Heist",
            "Thread Needle",
            "Gate Crasher",
            "Blackout Harvest",
            "Pulse Corridor",
            "Jackpot Circuit",
            "Spiral Dive",
            "Predator Window",
        }
        entries = {name for name, _preset, _is_open in self._fresh_context().challenge_entries()}

        self.assertTrue(scenario_names.issubset(entries))

    def test_bonus_gate_opens_on_route_chain_and_pays_once(self) -> None:
        ctx = self._fresh_context()
        ctx.run.route_chain_count = 4
        ctx.run.route_chain_window = 12
        pacman = SimpleNamespace(kind="pacman")

        with patch("entities.bonus_gate.Assets.texture", return_value=object()):
            gate = BonusGate(ctx)

        self.assertTrue(gate.is_open())
        self.assertFalse(gate.is_blocking(pacman))

        expected_bonus = ctx.bonus_gate_value()
        gate.on_enter(pacman)

        self.assertEqual(ctx.run.score, expected_bonus)
        self.assertEqual(ctx.run_stats.bonus_gates, 1)
        self.assertGreater(gate.bonus_cooldown, 0)

    def test_hotspot_seed_adds_extra_score_pressure(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Challenge"
        ctx.challenge_name = "Redline Protocol"
        nudge_calls: list[int] = []
        ctx.runtime.game_map = SimpleNamespace(nudge_pending_ghosts=lambda ticks: nudge_calls.append(ticks))
        pacman = SimpleNamespace(kind="pacman", last_dx=0, last_dy=0)

        seed = HotspotSeed(ctx)
        seed.frame(3, 4)
        expected_total = ctx.effective_seed_score() + ctx.hotspot_seed_bonus_value()

        seed.on_enter(pacman)

        self.assertEqual(ctx.run.score, expected_total)
        self.assertEqual(nudge_calls, [1])
        self.assertEqual(ctx.run_stats.dots_eaten, 1)

    def test_pulse_barrier_closes_and_reopens_by_map_cycle(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Challenge"
        ctx.challenge_name = "Score Rush"
        barrier = PulseBarrier(ctx)
        pacman = SimpleNamespace(kind="pacman")

        ctx.run.ghost_mode_timer = 0
        self.assertTrue(barrier.is_blocking(pacman))

        ctx.run.ghost_mode_timer = ctx.pulse_barrier_closed_ticks()
        self.assertFalse(barrier.is_blocking(pacman))

    def test_rage_and_cherry_curves_stay_readable_under_pressure(self) -> None:
        ctx = self._fresh_context()
        ctx.game_mode = "Arcade"
        ctx.current_level = 3
        ctx.run.pressure_stage = 2

        self.assertGreaterEqual(ctx.effective_rage_duration(), ctx.cfg.rage_duration_tick_min)
        self.assertGreaterEqual(ctx.effective_cherry_respawn(), ctx.cfg.cherry_respawn_tick_min)

    def test_route_and_line_scoring_triggers_earlier_than_before(self) -> None:
        ctx = self._fresh_context()

        route_bonuses = []
        for _ in range(5):
            _count, bonus = ctx.register_route_chain_dot()
            route_bonuses.append(bonus)

        line_bonuses = []
        for _ in range(6):
            _count, bonus = ctx.register_line_bonus_dot(1, 0)
            line_bonuses.append(bonus)

        self.assertGreater(route_bonuses[-1], 0)
        self.assertGreater(line_bonuses[-1], 0)

    def test_floating_text_moves_up_and_fades(self) -> None:
        text = FloatingText("+200", (100, 80), (0, 255, 255, 255), lifetime=1.0)

        self.assertTrue(text.update(0.25))

        self.assertEqual(text.pos.x, 100)
        self.assertAlmostEqual(text.pos.y, 70)
        self.assertAlmostEqual(text.alpha, 0.75)


if __name__ == "__main__":
    unittest.main()
