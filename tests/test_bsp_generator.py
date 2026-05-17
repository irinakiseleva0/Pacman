from __future__ import annotations

import unittest
from pathlib import Path
from shutil import rmtree
from unittest.mock import patch
from uuid import uuid4

from assets.assets import Assets
from core.context import GameContext
from entities.pacman import Pacman
from maps.class_map import Map
from maps.generator import BSPMazeGenerator
from maps.map_loader import generate_bsp_map_lines, write_generated_bsp_map


class BSPMazeGeneratorTests(unittest.TestCase):
    def test_generate_returns_connected_int_grid(self) -> None:
        generator = BSPMazeGenerator(28, 30, seed=7)

        grid = generator.generate()

        self.assertEqual(len(grid), 30)
        self.assertTrue(all(len(row) == 28 for row in grid))
        self.assertTrue(all(value in {0, 1} for row in grid for value in row))
        self.assertTrue(generator.is_fully_connected(grid))
        self.assertIsNotNone(generator.pacman_spawn)
        self.assertEqual(len(generator.ghost_spawns), 4)

    def test_same_seed_reproduces_same_grid(self) -> None:
        first = BSPMazeGenerator(28, 30, seed=123456)
        second = BSPMazeGenerator(28, 30, seed=123456)

        self.assertEqual(first.generate(), second.generate())
        self.assertEqual(first.seed, 123456)

    def test_none_seed_assigns_shareable_seed(self) -> None:
        generator = BSPMazeGenerator(28, 30)

        self.assertGreaterEqual(generator.seed, 0)
        self.assertLessEqual(generator.seed, 999999)

    def test_generate_map_lines_use_current_map_symbols(self) -> None:
        lines = generate_bsp_map_lines(28, 30, seed=11)
        joined = "".join(lines)

        self.assertEqual(len(lines), 30)
        self.assertTrue(all(len(line) == 28 for line in lines))
        self.assertEqual(joined.count("p"), 1)
        self.assertEqual(joined.count("g"), 4)
        self.assertGreater(joined.count("."), 0)
        self.assertTrue(set(joined).issubset({"#", ".", "p", "g"}))

    def test_generated_map_passes_runtime_loader_validation(self) -> None:
        temp_root = Path("data") / "saves" / ".test_tmp" / f"bsp-{uuid4().hex}"
        temp_root.mkdir(parents=True, exist_ok=True)
        path = temp_root / "generated_map.txt"
        try:
            write_generated_bsp_map(path, 28, 30, seed=19)
            ctx = GameContext()
            fake_frames = {
                "UP": [object()],
                "DOWN": [object()],
                "LEFT": [object()],
                "RIGHT": [object()],
                "DEATH": [object()],
                "NONE": [],
            }

            with (
                patch.object(Pacman, "_load_images", return_value=fake_frames),
                patch.object(Assets, "texture", return_value=object()),
            ):
                Pacman._images_cache = None
                game_map = Map(ctx, path=str(path))

            self.assertIsNotNone(ctx.runtime.pacman)
            self.assertEqual(sum(1 for actor in game_map.dynamic_actors if getattr(actor, "kind", None) == "ghost"), 4)
        finally:
            rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
