from __future__ import annotations

import unittest

from core.context import GameContext
from core.scene_ids import RESULT_SCENE
from scenes import game_flow
from scenes.game_scene import GameScene


class GameFlowTests(unittest.TestCase):
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
