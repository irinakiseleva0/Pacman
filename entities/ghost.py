from __future__ import annotations

import pyray
from raylib import colors

from entities.cell import Cell


class Ghost(Cell):
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.kind = "ghost"
        self.spawn_x = 0
        self.spawn_y = 0

    def set_spawn(self, x: int, y: int) -> None:
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y

    def reset_to_spawn(self) -> None:
        self.x = self.spawn_x
        self.y = self.spawn_y

    def draw(self) -> None:
        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = self.x * tile + tile // 2
        py = self.y * tile + tile // 2

        color = colors.BLUE if getattr(self.ctx.pacman, "rage", False) else colors.RED
        pyray.draw_circle(px, py, tile // 2 - 2, color)

    def process(self) -> None:
        game_map = self.ctx.game_map
        pacman = self.ctx.pacman

        if game_map is None or pacman is None:
            return

        if getattr(pacman, "state", None) in ("DEATH", "NONE"):
            return

        dx = 0
        dy = 0

        if pacman.x > self.x:
            dx = 1
        elif pacman.x < self.x:
            dx = -1

        if pacman.y > self.y:
            dy = 1
        elif pacman.y < self.y:
            dy = -1

        moves: list[tuple[int, int]] = []

        if abs(pacman.x - self.x) >= abs(pacman.y - self.y):
            if dx != 0:
                moves.append((dx, 0))
            if dy != 0:
                moves.append((0, dy))
        else:
            if dy != 0:
                moves.append((0, dy))
            if dx != 0:
                moves.append((dx, 0))

        moves.extend([
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ])

        used = set()
        for move_dx, move_dy in moves:
            if (move_dx, move_dy) in used:
                continue
            used.add((move_dx, move_dy))

            result = game_map.try_move(self, move_dx, move_dy)
            if result.moved:
                return