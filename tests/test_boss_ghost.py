from __future__ import annotations

import unittest
from copy import deepcopy
from unittest.mock import patch

from core.context import GameContext
from entities.boss_ghost import BossGhost
from entities.pacman import Pacman, State
from maps.class_map import Map
from maps.generator import BSPMazeGenerator
from utils.profile_storage import DEFAULT_PROFILE


class BossGhostTests(unittest.TestCase):
    def _fresh_context(self) -> GameContext:
        ctx = GameContext()
        ctx.profile = deepcopy(DEFAULT_PROFILE)
        ctx.profile_service.save = lambda: None
        return ctx

    def _fake_pacman_frames(self):
        return {
            State.UP: [object()],
            State.RIGHT: [object()],
            State.DOWN: [object()],
            State.LEFT: [object()],
            State.DEAD: [object()],
            State.NONE: [],
        }

    def test_first_ghost_spawn_becomes_boss_every_fifth_level(self) -> None:
        ctx = self._fresh_context()
        ctx.current_level = 5
        game_map = Map.__new__(Map)
        game_map.ctx = ctx
        game_map.ghost_counter = 0
        game_map.boss_spawned = False

        actor = game_map._create_actor("g")

        self.assertIsInstance(actor, BossGhost)
        self.assertTrue(game_map.boss_spawned)

    def test_boss_takes_rage_hits_splits_and_unlocks_skin_on_defeat(self) -> None:
        ctx = self._fresh_context()
        with patch.object(Pacman, "_load_images", return_value=self._fake_pacman_frames()):
            pacman = Pacman(ctx)
        pacman.set_spawn(5, 5)
        pacman.rage = True
        pacman.rage_timer = 60
        boss = BossGhost(ctx)
        boss.set_spawn(5, 5)

        game_map = Map.__new__(Map)
        game_map.ctx = ctx
        game_map.dynamic_actors = [pacman, boss]
        game_map.add_actor = lambda actor: game_map.dynamic_actors.append(actor)
        game_map.get_cell = lambda x, y: None

        game_map._resolve_collision(pacman, boss)
        self.assertEqual(boss.hp, 2)
        self.assertEqual(boss.phase, "split")

        boss.hp = 1
        boss.respawn_lock_ticks = 0
        game_map._resolve_collision(pacman, boss)

        self.assertFalse(game_map.boss_alive())
        self.assertEqual(ctx.profile["unlocked_skins"]["Intruder Husk"], 1)
        self.assertGreaterEqual(ctx.run.score, BossGhost.HIT_SCORE + BossGhost.DEFEAT_SCORE)

    def test_bsp_generator_marks_center_boss_room(self) -> None:
        generator = BSPMazeGenerator(seed=42)
        grid = generator.generate()

        self.assertIsNotNone(generator.boss_room)
        room = generator.boss_room
        assert room is not None
        self.assertLessEqual(abs(room.center[0] - generator.width // 2), 1)
        self.assertLessEqual(abs(room.center[1] - generator.height // 2), 1)
        self.assertEqual(grid[room.center[1]][room.center[0]], BSPMazeGenerator.FLOOR)


if __name__ == "__main__":
    unittest.main()
