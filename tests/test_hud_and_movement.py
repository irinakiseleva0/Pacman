from __future__ import annotations

import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from core.context import GameContext
from core.gameplay_view_models import build_hud_model, build_live_feedback_model
from entities.ghost import Blinky
from entities.pacman import Pacman, State
from maps.class_map import Map, MoveResult
from utils.profile_storage import DEFAULT_PROFILE


class _HudMapStub:
    def __init__(
        self,
        *,
        seeds: int = 8,
        cherry_status=None,
        ghost_release_status=None,
        ghost_return_status=None,
        actors=None,
    ) -> None:
        self._seeds = seeds
        self._cherry_status = cherry_status
        self._ghost_release_status = ghost_release_status
        self._ghost_return_status = ghost_return_status
        self.dynamic_actors = actors or []

    def remaining_seeds(self) -> int:
        return self._seeds

    def cherry_status(self):
        return self._cherry_status

    def ghost_release_status(self):
        return self._ghost_release_status

    def ghost_return_status(self):
        return self._ghost_return_status


class _MapCell:
    def __init__(self, *, blocking: bool) -> None:
        self._blocking = blocking

    def is_blocking(self, actor) -> bool:
        return self._blocking

    def on_enter(self, actor) -> None:
        return None


class _MovementMapStub:
    def __init__(self, blocked_cells=None) -> None:
        self.blocked_cells = set(blocked_cells or [])
        self.try_move_calls: list[tuple[int, int]] = []

    def get_cell(self, x: int, y: int) -> _MapCell:
        return _MapCell(blocking=(x, y) in self.blocked_cells)

    def try_move(self, actor, dx: int, dy: int) -> MoveResult:
        self.try_move_calls.append((dx, dy))
        target = (actor.x + dx, actor.y + dy)
        if target in self.blocked_cells:
            return MoveResult(moved=False, blocked=True, reason="blocked")
        actor.x, actor.y = target
        return MoveResult(moved=True)


class _DelayedTurnMapStub(_MovementMapStub):
    def __init__(self) -> None:
        super().__init__(blocked_cells={(6, 5)})
        self._up_checks = 0

    def get_cell(self, x: int, y: int) -> _MapCell:
        if (x, y) == (5, 4):
            self._up_checks += 1
            return _MapCell(blocking=self._up_checks == 1)
        return super().get_cell(x, y)


class HudModelTests(unittest.TestCase):
    def _fresh_context(self) -> GameContext:
        ctx = GameContext()
        ctx.profile = deepcopy(DEFAULT_PROFILE)
        ctx.profile_service.save = lambda: None
        return ctx

    def test_hud_signal_section_keeps_focus_and_bonus_lines(self) -> None:
        ctx = self._fresh_context()
        ctx.run.route_chain_count = 4
        ctx.run.route_chain_window = 10
        ctx.runtime.pacman = SimpleNamespace(x=5, y=5, rage=False)
        game_map = _HudMapStub(
            cherry_status=(True, 2),
            ghost_release_status=(2, 4),
            ghost_return_status=(1, 4),
        )

        model = build_hud_model(ctx, game_map)

        signal_section = model.sections[2]
        self.assertEqual(signal_section.title, "EAT")
        self.assertEqual(signal_section.lines[0][0], "BONUS ROUTE OPEN  |  CHERRY READY")
        self.assertEqual(
            [line for line, _color in signal_section.lines[1:]],
            [
                "Returning: 1/4",
                "Deploying: 2/4",
                "Cherry: READY x2",
                "Route: x4",
            ],
        )

    def test_hud_signal_section_preserves_rage_warning(self) -> None:
        ctx = self._fresh_context()
        ctx.run.ghost_combo = 1
        ctx.run.power_chain_level = 2
        ctx.runtime.pacman = SimpleNamespace(
            x=5,
            y=5,
            rage=True,
            rage_timer=20,
        )
        game_map = _HudMapStub(actors=[SimpleNamespace(kind="ghost", x=6, y=5, is_harmless=lambda: False)])

        model = build_hud_model(ctx, game_map)

        signal_lines = [line for line, _color in model.sections[2].lines]
        self.assertEqual(signal_lines[0], "GHOSTS VULNERABLE  |  COMBO X2")
        self.assertIn("Rage: ON", signal_lines)
        self.assertIn("Combo: x2", signal_lines)
        self.assertIn("Chain: 2", signal_lines)
        self.assertIn("Rage ending soon!", signal_lines)

    def test_live_feedback_uses_nerve_chain_copy_when_active(self) -> None:
        ctx = self._fresh_context()
        scene = SimpleNamespace(
            ctx=ctx,
            near_miss_timer=0.4,
            danger_chain_count=3,
        )

        feedback = build_live_feedback_model(scene)

        self.assertIsNotNone(feedback.near_miss_card)
        self.assertEqual(feedback.near_miss_card.headline, "NERVE CHAIN 3")
        self.assertIn("nerve chain x3", feedback.near_miss_card.detail)


class MovementAndCollisionTests(unittest.TestCase):
    def _fresh_context(self) -> GameContext:
        ctx = GameContext()
        ctx.profile = deepcopy(DEFAULT_PROFILE)
        ctx.profile_service.save = lambda: None
        return ctx

    def _make_pacman(self, ctx: GameContext) -> Pacman:
        fake_frames = {
            State.UP: [object()],
            State.RIGHT: [object()],
            State.DOWN: [object()],
            State.LEFT: [object()],
            State.DEAD: [object()],
            State.NONE: [],
        }
        with patch.object(Pacman, "_load_images", return_value=fake_frames):
            pacman = Pacman(ctx)
        pacman.set_spawn(5, 5)
        return pacman

    def test_pacman_buffered_turn_applies_before_forward_move(self) -> None:
        ctx = self._fresh_context()
        pacman = self._make_pacman(ctx)
        game_map = _MovementMapStub()
        ctx.runtime.game_map = game_map

        pacman.state = State.RIGHT
        pacman.next_state = State.UP
        pacman.turn_buffer_timer = 0.2

        pacman.process()

        self.assertEqual(pacman.state, State.UP)
        self.assertEqual((pacman.x, pacman.y), (5, 4))
        self.assertEqual(game_map.try_move_calls, [(0, -1)])

    def test_pacman_blocked_move_can_retry_with_buffered_turn(self) -> None:
        ctx = self._fresh_context()
        pacman = self._make_pacman(ctx)
        game_map = _DelayedTurnMapStub()
        ctx.runtime.game_map = game_map

        pacman.state = State.RIGHT
        pacman.next_state = State.UP
        pacman.turn_grace_timer = 0.05

        pacman.process()

        self.assertEqual(pacman.state, State.UP)
        self.assertEqual((pacman.x, pacman.y), (5, 4))
        self.assertEqual(game_map.try_move_calls, [(1, 0), (0, -1)])

    def test_abilities_unlock_from_career_rank_and_dash_moves_extra_steps(self) -> None:
        ctx = self._fresh_context()
        ctx.profile["best_score"] = 15000
        pacman = self._make_pacman(ctx)
        game_map = _MovementMapStub()
        ctx.runtime.game_map = game_map

        self.assertEqual([ability.name for ability in pacman.abilities], ["Dash", "Shield", "Slow"])
        self.assertTrue(all(ability.unlocked for ability in pacman.abilities))

        self.assertTrue(pacman.activate_ability_slot(0))
        pacman.state = State.RIGHT
        pacman.next_state = State.RIGHT
        pacman.process()

        self.assertEqual((pacman.x, pacman.y), (8, 5))
        self.assertEqual(game_map.try_move_calls, [(1, 0), (1, 0), (1, 0)])

    def test_shield_blocks_death_collision(self) -> None:
        ctx = self._fresh_context()
        ctx.profile["best_score"] = 15000
        pacman = self._make_pacman(ctx)
        ctx.runtime.pacman = pacman
        ghost = Blinky(ctx)
        ghost.set_spawn(5, 5)
        pacman.activate_ability_slot(1)

        game_map = Map.__new__(Map)
        game_map.ctx = ctx
        game_map.dynamic_actors = [pacman, ghost]

        game_map._resolve_collision(pacman, ghost)

        self.assertNotEqual(pacman.state, State.DEAD)

    def test_slow_ability_skips_every_other_ghost_step(self) -> None:
        ctx = self._fresh_context()
        ctx.profile["best_score"] = 15000
        pacman = self._make_pacman(ctx)
        ctx.runtime.pacman = pacman
        game_map = _MovementMapStub()
        ctx.runtime.game_map = game_map
        ghost = Blinky(ctx)
        ghost.set_spawn(7, 5)

        self.assertTrue(pacman.activate_ability_slot(2))
        with patch.object(Blinky, "get_best_move", return_value=(-1, 0)):
            ghost.process()
            ghost.process()

        self.assertEqual((ghost.x, ghost.y), (6, 5))
        self.assertEqual(game_map.try_move_calls, [(-1, 0)])

    def test_collision_with_raging_pacman_scores_and_sends_ghost_home(self) -> None:
        ctx = self._fresh_context()
        pacman = self._make_pacman(ctx)
        pacman.rage = True
        pacman.rage_timer = 30
        ctx.runtime.pacman = pacman

        ghost = Blinky(ctx)
        ghost.set_spawn(5, 5)
        ghost.x = 5
        ghost.y = 5

        game_map = Map.__new__(Map)
        game_map.ctx = ctx
        game_map.dynamic_actors = [pacman, ghost]
        expected_score = ctx.next_ghost_combo_score()

        game_map._resolve_collision(pacman, ghost)

        self.assertEqual(ctx.run.score, expected_score)
        self.assertEqual(ctx.run.ghost_combo, 1)
        self.assertEqual(ctx.run_stats.ghosts_eaten, 1)
        self.assertTrue(ghost.returning_home)
        self.assertEqual(ctx.run.last_killer_name, "")

    def test_collision_with_dangerous_ghost_kills_pacman(self) -> None:
        ctx = self._fresh_context()
        pacman = self._make_pacman(ctx)
        ctx.runtime.pacman = pacman
        ctx.run.ghost_combo = 3

        ghost = Blinky(ctx)
        ghost.set_spawn(5, 5)
        ghost.x = 5
        ghost.y = 5

        game_map = Map.__new__(Map)
        game_map.ctx = ctx
        game_map.dynamic_actors = [pacman, ghost]

        game_map._resolve_collision(pacman, ghost)

        self.assertEqual(pacman.state, State.DEAD)
        self.assertEqual(pacman.next_state, State.DEAD)
        self.assertEqual(ctx.run.ghost_combo, 0)
        self.assertEqual(ctx.run.last_killer_name, "Blinky")


if __name__ == "__main__":
    unittest.main()
