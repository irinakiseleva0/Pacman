from __future__ import annotations

import pyray
from raylib import colors
from typing import Tuple

from entities.cell import Actor


class Ghost(Actor):
    FRIGHTENED_BLINK_TICKS = 60
    FRIGHTENED_BLINK_INTERVAL = 8
    EATEN_RESPAWN_TICKS = 12

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.kind = "ghost"
        self.color = colors.RED  # Default color
        self.target_x = 0
        self.target_y = 0
        self.mode = "chase"  # chase, scatter, frightened
        self.scatter_target = (0, 0)
        self.respawn_lock_ticks = 0
        self.release_delay_ticks = 0

    def _get_draw_color(self):
        if self.respawn_lock_ticks > 0:
            if (self.respawn_lock_ticks // 2) % 2 == 0:
                return colors.WHITE
            return colors.SKYBLUE

        if self.release_delay_ticks > 0:
            return colors.GRAY

        pacman = self.ctx.pacman
        if not getattr(pacman, "rage", False):
            return self.color

        rage_timer = getattr(pacman, "rage_timer", 0)
        if (
            rage_timer > 0
            and rage_timer <= self.FRIGHTENED_BLINK_TICKS
            and (rage_timer // self.FRIGHTENED_BLINK_INTERVAL) % 2 == 0
        ):
            return colors.WHITE

        return colors.BLUE

    def draw(self) -> None:
        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = self.x * tile + tile // 2
        py = self.y * tile + tile // 2

        pyray.draw_circle(px, py, tile // 2 - 2, self._get_draw_color())

    def update_target(self) -> None:
        """Override in subclasses for different AI behaviors"""
        pacman = self.ctx.pacman
        if pacman:
            self.target_x = pacman.x
            self.target_y = pacman.y

    def on_eaten(self) -> None:
        self.reset_to_spawn()
        self.respawn_lock_ticks = self.EATEN_RESPAWN_TICKS
        self.last_dx = 0
        self.last_dy = 0

    def set_release_delay(self, ticks: int) -> None:
        self.release_delay_ticks = max(0, ticks)

    def _update_mode(self) -> None:
        pacman = self.ctx.pacman
        if getattr(pacman, "rage", False):
            self.mode = "frightened"
            return

        self.mode = self.ctx.ghost_mode

    def _is_reverse_direction(self, dx: int, dy: int) -> bool:
        return (dx, dy) == (-self.last_dx, -self.last_dy) and (self.last_dx, self.last_dy) != (0, 0)

    def get_best_move(self, game_map) -> Tuple[int, int]:
        """Find the best move towards the target using simple pathfinding"""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)
                      ]  # Up, Down, Left, Right
        best_score = float('inf')
        best_move = (0, 0)
        reverse_move = (0, 0)
        reverse_score = float('inf')

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy

            # Check if move is valid
            if not game_map.in_bounds(new_x, new_y):
                continue

            cell = game_map.get_cell(new_x, new_y)
            if cell is None or cell.is_blocking(self):
                continue

            distance = abs(new_x - self.target_x) + abs(new_y - self.target_y)
            score = -distance if self.mode == "frightened" else distance

            # Prefer continuing in current direction, then shortest distance
            if (dx, dy) == (self.last_dx, self.last_dy):
                score -= 0.5  # Slight preference for current direction

            if self._is_reverse_direction(dx, dy):
                if score < reverse_score:
                    reverse_score = score
                    reverse_move = (dx, dy)
                continue

            if score < best_score:
                best_score = score
                best_move = (dx, dy)

        if best_move != (0, 0):
            return best_move

        return reverse_move

    def process(self) -> None:
        game_map = self.ctx.game_map
        pacman = self.ctx.pacman

        if game_map is None or pacman is None:
            return

        if self.release_delay_ticks > 0:
            self.release_delay_ticks -= 1
            return

        if self.respawn_lock_ticks > 0:
            self.respawn_lock_ticks -= 1
            return

        if getattr(pacman, "state", None) in ("DEATH", "NONE"):
            return

        self._update_mode()

        if self.mode == "scatter":
            self.target_x, self.target_y = self.scatter_target
        else:
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
        self.scatter_target = (self.ctx.cfg.map_width - 2, 1)

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
        self.scatter_target = (1, 1)

    def update_target(self) -> None:
        """Target 4 tiles ahead of Pacman's direction"""
        pacman = self.ctx.pacman
        if pacman:
            self.target_x = pacman.x + pacman.last_dx * 4
            self.target_y = pacman.y + pacman.last_dy * 4


class Inky(Ghost):
    """Cyan ghost - Uses complex targeting"""

    def __init__(self, ctx):
        super().__init__(ctx)
        self.color = colors.SKYBLUE
        self.last_dx = 0
        self.last_dy = 0
        self.scatter_target = (self.ctx.cfg.map_width - 2, self.ctx.cfg.map_height - 2)

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
        self.scatter_target = (1, self.ctx.cfg.map_height - 2)

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
