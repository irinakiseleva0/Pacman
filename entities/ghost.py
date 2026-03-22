from __future__ import annotations

import pyray
from raylib import colors
from typing import Tuple

from entities.cell import Actor


class Ghost(Actor):
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.kind = "ghost"
        self.spawn_x = 0
        self.spawn_y = 0
        self.color = colors.RED  # Default color
        self.target_x = 0
        self.target_y = 0
        self.mode = "chase"  # chase, scatter, frightened

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

        # Use different color when frightened
        if getattr(self.ctx.pacman, "rage", False):
            color = colors.BLUE
        else:
            color = self.color

        pyray.draw_circle(px, py, tile // 2 - 2, color)

    def update_target(self) -> None:
        """Override in subclasses for different AI behaviors"""
        pacman = self.ctx.pacman
        if pacman:
            self.target_x = pacman.x
            self.target_y = pacman.y

    def get_best_move(self, game_map) -> Tuple[int, int]:
        """Find the best move towards the target using simple pathfinding"""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)
                      ]  # Up, Down, Left, Right
        best_distance = float('inf')
        best_move = (0, 0)

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy

            # Check if move is valid
            if not game_map.in_bounds(new_x, new_y):
                continue

            cell = game_map.get_cell(new_x, new_y)
            if cell is None or cell.is_blocking(self):
                continue

            # Calculate distance to target
            distance = abs(new_x - self.target_x) + abs(new_y - self.target_y)

            # Prefer continuing in current direction, then shortest distance
            if (dx, dy) == (self.last_dx, self.last_dy):
                distance -= 0.5  # Slight preference for current direction

            if distance < best_distance:
                best_distance = distance
                best_move = (dx, dy)

        return best_move

    def process(self) -> None:
        game_map = self.ctx.game_map
        pacman = self.ctx.pacman

        if game_map is None or pacman is None:
            return

        if getattr(pacman, "state", None) in ("DEATH", "NONE"):
            return

        # Update target based on personality
        self.update_target()

        # Get best move towards target
        dx, dy = self.get_best_move(game_map)

        # Try to move
        result = game_map.try_move(self, dx, dy)
        if result.moved:
            self.last_dx = dx
            self.last_dy = dy


class Blinky(Ghost):
    """Red ghost - Aggressive chaser"""

    def __init__(self, ctx):
        super().__init__(ctx)
        self.color = colors.RED
        self.last_dx = 0
        self.last_dy = 0

    def update_target(self) -> None:
        """Always target Pacman's current position"""
        pacman = self.ctx.pacman
        if pacman:
            self.target_x = pacman.x
            self.target_y = pacman.y


class Pinky(Ghost):
    """Pink ghost - Ambushes ahead of Pacman"""

    def __init__(self, ctx):
        super().__init__(ctx)
        self.color = colors.MAGENTA  # Pink-ish
        self.last_dx = 0
        self.last_dy = 0

    def update_target(self) -> None:
        """Target 4 tiles ahead of Pacman's direction"""
        pacman = self.ctx.pacman
        if pacman:
            # Get Pacman's direction (simplified)
            if hasattr(pacman, 'last_dx') and hasattr(pacman, 'last_dy'):
                target_x = pacman.x + pacman.last_dx * 4
                target_y = pacman.y + pacman.last_dy * 4
            else:
                target_x = pacman.x
                target_y = pacman.y

            self.target_x = target_x
            self.target_y = target_y


class Inky(Ghost):
    """Cyan ghost - Uses complex targeting"""

    def __init__(self, ctx):
        super().__init__(ctx)
        self.color = colors.SKYBLUE
        self.last_dx = 0
        self.last_dy = 0

    def update_target(self) -> None:
        """Target based on Pacman's position and Blinky's position"""
        pacman = self.ctx.pacman
        if pacman:
            # Find Blinky (first red ghost)
            blinky = None
            for actor in self.ctx.game_map.dynamic_actors:
                if isinstance(actor, Blinky):
                    blinky = actor
                    break

            if blinky:
                # Target is Pacman's position + (Pacman to Blinky vector)
                vector_x = pacman.x - blinky.x
                vector_y = pacman.y - blinky.y
                self.target_x = pacman.x + vector_x
                self.target_y = pacman.y + vector_y
            else:
                # Fallback to simple chase
                self.target_x = pacman.x
                self.target_y = pacman.y


class Clyde(Ghost):
    """Orange ghost - Cowardly, switches between chase and scatter"""

    def __init__(self, ctx):
        super().__init__(ctx)
        self.color = colors.ORANGE
        self.last_dx = 0
        self.last_dy = 0
        self.scatter_target = (0, 30)  # Bottom-left corner

    def update_target(self) -> None:
        """Chase when far from Pacman, scatter when close"""
        pacman = self.ctx.pacman
        if pacman:
            distance = abs(pacman.x - self.x) + abs(pacman.y - self.y)

            if distance > 8:  # Far from Pacman - chase
                self.target_x = pacman.x
                self.target_y = pacman.y
            else:  # Close to Pacman - scatter to corner
                self.target_x = self.scatter_target[0]
                self.target_y = self.scatter_target[1]
