from __future__ import annotations

import unittest
from unittest.mock import patch

from core.context import GameContext
from core.scene_ids import RESULT_SCENE
from scenes import game_flow
from scenes.game_scene import GameScene


class GameFlowTests(unittest.TestCase):
    def _near_miss_scene(self, *, game_mode: str = "Arcade") -> tuple[GameContext, GameScene]:
        ctx = GameContext()
        ctx.game_mode = game_mode
        scene = GameScene(ctx)
        pacman = type("PacmanStub", (), {"x": 5, "y": 5, "rage": False, "turn_feedback_timer": 0.0})()
        ghost = type("GhostStub", (), {"kind": "ghost", "x": 6, "y": 5, "is_harmless": lambda self: False})()
        map_stub = type(
            "MapStub",
            (),
            {
                "dynamic_actors": [ghost],
                "nudge_pending_ghosts": lambda self, ticks: None,
                "remaining_pickups": lambda self: 24,
            },
        )()
        ctx.runtime.pacman = pacman
        ctx.runtime.game_map = map_stub
        return ctx, scene

    def test_second_near_miss_starts_nerve_chain_bonus(self) -> None:
        ctx, scene = self._near_miss_scene()

        game_flow.check_near_miss(scene)
        first_score = ctx.run.score
        self.assertEqual(scene.danger_chain_count, 1)

        scene.near_miss_cooldown = 0.0
        expected_bonus = ctx.danger_chain_bonus_value(2, risk_turn=False)
        game_flow.check_near_miss(scene)

        self.assertEqual(scene.danger_chain_count, 2)
        self.assertEqual(ctx.run.score, first_score + expected_bonus)

    def test_timer_system_expires_nerve_chain(self) -> None:
        ctx = GameContext()
        scene = GameScene(ctx)
        scene.danger_chain_count = 3
        scene.danger_chain_timer = 0.1

        game_flow._timer_system(scene, 0.2, 0.2)

        self.assertEqual(scene.danger_chain_timer, 0.0)
        self.assertEqual(scene.danger_chain_count, 0)

    def test_trigger_freeze_keeps_longest_frame_count(self) -> None:
        ctx = GameContext()

        ctx.trigger_freeze(2)
        ctx.trigger_freeze(4)
        ctx.trigger_freeze(1)

        self.assertEqual(ctx.freeze_frames, 4)

    def test_update_skips_gameplay_while_freeze_frames_remain(self) -> None:
        ctx = GameContext()
        scene = GameScene(ctx)
        calls = []
        map_stub = type(
            "MapStub",
            (),
            {
                "frame": lambda self: calls.append("frame"),
                "process": lambda self: calls.append("process"),
                "remaining_pickups": lambda self: 1,
                "remaining_seeds": lambda self: 1,
            },
        )()
        ctx.runtime.game_map = map_stub
        ctx.freeze_frames = 2

        game_flow.update(scene, 1 / 60)
        game_flow.update(scene, 1 / 60)

        self.assertEqual(ctx.freeze_frames, 0)
        self.assertEqual(calls, [])

    def test_black_channel_near_miss_arms_hunt_window(self) -> None:
        ctx, scene = self._near_miss_scene(game_mode="Challenge")

        game_flow.check_near_miss(scene)

        self.assertTrue(ctx.hunt_window_active())

    def test_market_loop_near_miss_arms_market_window(self) -> None:
        ctx, scene = self._near_miss_scene(game_mode="Time Attack")

        game_flow.check_near_miss(scene)

        self.assertTrue(ctx.market_window_active())

    def test_start_death_transition_uses_reload_when_lives_remain(self) -> None:
        ctx = GameContext()
        scene = GameScene(ctx)
        ctx.run.lives = 2

        game_flow.start_death_transition(scene)

        self.assertIsNotNone(scene.transition)
        self.assertEqual(scene.transition.kind, "death")
        self.assertEqual(scene.transition.result, "reload")
        self.assertEqual(ctx.run.lives, 1)

    def test_finish_transition_routes_to_result_scene_on_loss(self) -> None:
        ctx = GameContext()
        scene = GameScene(ctx)
        scene.transition = game_flow._transition(scene, "death", 0.0, "lose")

        game_flow.finish_transition(scene)

        self.assertIsNone(scene.transition)
        self.assertEqual(ctx.last_result, "lose")
        self.assertEqual(scene.consume_switch_request(), RESULT_SCENE)

    def test_finish_transition_routes_to_result_scene_on_level_clear_result(self) -> None:
        ctx = GameContext()
        scene = GameScene(ctx)
        scene.transition = game_flow._transition(scene, "level_complete", 0.0, "game_won")

        game_flow.finish_transition(scene)

        self.assertIsNone(scene.transition)
        self.assertEqual(ctx.last_result, "game_won")
        self.assertEqual(scene.consume_switch_request(), RESULT_SCENE)

    def test_tutorial_flow_advances_through_route_power_and_risk_lessons(self) -> None:
        ctx = GameContext()
        scene = GameScene(ctx)
        scene.tutorial_stage = 1

        with patch("scenes.game_flow.movement_pressed", return_value=True):
            game_flow.update_tutorial_state(scene, None)
        self.assertEqual(scene.tutorial_stage, 2)

        ctx.run_stats.dots_eaten = 4
        game_flow.update_tutorial_state(scene, None)
        self.assertEqual(scene.tutorial_stage, 3)

        ctx.run.route_chain_count = 5
        ctx.run.route_chain_window = 20
        game_flow.update_tutorial_state(scene, None)
        self.assertEqual(scene.tutorial_stage, 4)

        ctx.run_stats.power_seeds_eaten = 1
        ctx.runtime.pacman = type("PacmanStub", (), {"x": 5, "y": 5})()
        game_flow.update_tutorial_state(scene, None)
        self.assertEqual(scene.tutorial_stage, 5)
        self.assertGreater(scene.tutorial_wow_timer, 0.0)

        scene.tutorial_stage_timer = 2.5
        game_flow.update_tutorial_state(scene, None)
        self.assertEqual(scene.tutorial_stage, 6)

        ctx.run_stats.near_misses = 1
        game_flow.update_tutorial_state(scene, None)
        self.assertEqual(scene.tutorial_stage, 7)

    def test_tutorial_death_does_not_mark_onboarding_complete(self) -> None:
        ctx = GameContext()
        ctx.profile["tutorial_seen"] = 0
        ctx.profile_service.save = lambda: None
        scene = GameScene(ctx)
        scene.tutorial_stage = 4
        scene.transition = game_flow._transition(scene, "death", 0.0, "reload")

        game_flow.update_tutorial_state(scene, None)

        self.assertEqual(scene.tutorial_stage, 1)
        self.assertFalse(ctx.tutorial_seen())
