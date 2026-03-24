from __future__ import annotations

from collections import deque
import core.raylib_api as pyray
from raylib import colors
from typing import Tuple

from entities.cell import Actor
from utils.visual_effects import with_alpha


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
        self.returning_home = False

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        return 0.0

    def _get_draw_color(self):
        if self.returning_home:
            return colors.WHITE

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

    def _draw_returning_home(self, px: int, py: int, tile: int) -> None:
        eye_radius = max(2, tile // 6)
        pupil_radius = max(1, eye_radius // 2)
        eye_offset_x = tile // 5
        eye_offset_y = tile // 10
        trail_radius = max(1, tile // 8)

        left_eye_x = px - eye_offset_x
        right_eye_x = px + eye_offset_x
        eye_y = py - eye_offset_y

        trail_dx = 0
        trail_dy = 0
        if self.last_dx < 0:
            trail_dx = 2
        elif self.last_dx > 0:
            trail_dx = -2

        if self.last_dy < 0:
            trail_dy = 2
        elif self.last_dy > 0:
            trail_dy = -2

        pyray.draw_circle(px + trail_dx * 2, py + trail_dy * 2, trail_radius, colors.LIGHTGRAY)
        pyray.draw_circle(px + trail_dx * 4, py + trail_dy * 4, trail_radius, colors.GRAY)

        pyray.draw_circle(left_eye_x, eye_y, eye_radius, colors.WHITE)
        pyray.draw_circle(right_eye_x, eye_y, eye_radius, colors.WHITE)

        pupil_dx = 0
        pupil_dy = 0
        if self.last_dx < 0:
            pupil_dx = -1
        elif self.last_dx > 0:
            pupil_dx = 1

        if self.last_dy < 0:
            pupil_dy = -1
        elif self.last_dy > 0:
            pupil_dy = 1

        pyray.draw_circle(left_eye_x + pupil_dx, eye_y + pupil_dy, pupil_radius, colors.BLACK)
        pyray.draw_circle(right_eye_x + pupil_dx, eye_y + pupil_dy, pupil_radius, colors.BLACK)

    def draw(self) -> None:
        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = cfg.board_offset_x + self.x * tile + tile // 2
        py = cfg.board_offset_y + self.y * tile + tile // 2
        base_color = self._get_draw_color()
        time_s = getattr(self.ctx, "visual_time", 0.0)

        if self.returning_home:
            self._draw_returning_home(px, py, tile)
            return

        pulse = 0.5 + 0.5 * __import__("math").sin(time_s * 5.0 + self.x + self.y)
        glow_radius = tile // 2 + 4 + int(pulse * 3)
        pyray.draw_circle(px, py, glow_radius, with_alpha(base_color, 34))
        pyray.draw_circle(px, py, tile // 2 - 2, base_color)

    def update_target(self) -> None:
        """Override in subclasses for different AI behaviors"""
        pacman = self.ctx.pacman
        if pacman:
            self.target_x = pacman.x
            self.target_y = pacman.y

    def on_eaten(self) -> None:
        self.returning_home = True
        self.respawn_lock_ticks = 0
        self.release_delay_ticks = 0
        self.last_dx = 0
        self.last_dy = 0

    def set_release_delay(self, ticks: int) -> None:
        self.release_delay_ticks = max(0, ticks)

    def stall_release(self, ticks: int) -> None:
        if self.release_delay_ticks > 0:
            self.release_delay_ticks += max(0, ticks)

    def is_harmless(self) -> bool:
        return self.returning_home or self.respawn_lock_ticks > 0 or self.release_delay_ticks > 0

    def _update_mode(self) -> None:
        pacman = self.ctx.pacman
        if getattr(pacman, "rage", False):
            self.mode = "frightened"
            return

        self.mode = self.ctx.ghost_mode

    def _is_reverse_direction(self, dx: int, dy: int) -> bool:
        if self.returning_home:
            return False
        return (dx, dy) == (-self.last_dx, -self.last_dy) and (self.last_dx, self.last_dy) != (0, 0)

    def _valid_moves(self, game_map) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            new_x = self.x + dx
            new_y = self.y + dy
            if not game_map.in_bounds(new_x, new_y):
                continue

            cell = game_map.get_cell(new_x, new_y)
            if cell is None or cell.is_blocking(self):
                continue

            moves.append((dx, dy))
        return moves

    def _should_choose_new_direction(self, valid_moves: list[tuple[int, int]]) -> bool:
        current_direction = (self.last_dx, self.last_dy)
        if current_direction == (0, 0):
            return True
        if current_direction not in valid_moves:
            return True
        if len(valid_moves) <= 2:
            return False
        return True

    def _path_distance(self, game_map, start_x: int, start_y: int, target_x: int, target_y: int, *, max_depth: int = 18) -> int:
        if (start_x, start_y) == (target_x, target_y):
            return 0

        visited = {(start_x, start_y)}
        queue = deque([(start_x, start_y, 0)])

        while queue:
            x, y, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx = x + dx
                ny = y + dy
                if (nx, ny) in visited or not game_map.in_bounds(nx, ny):
                    continue

                cell = game_map.get_cell(nx, ny)
                if cell is None or cell.is_blocking(self):
                    continue

                if (nx, ny) == (target_x, target_y):
                    return depth + 1

                visited.add((nx, ny))
                queue.append((nx, ny, depth + 1))

        return max_depth + abs(start_x - target_x) + abs(start_y - target_y)

    def _future_path_score(self, game_map, new_x: int, new_y: int, *, max_depth: int = 10) -> int:
        best = None
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx = new_x + dx
            ny = new_y + dy
            if not game_map.in_bounds(nx, ny):
                continue
            cell = game_map.get_cell(nx, ny)
            if cell is None or cell.is_blocking(self):
                continue
            dist = self._path_distance(game_map, nx, ny, self.target_x, self.target_y, max_depth=max_depth)
            if best is None or dist < best:
                best = dist
        return best if best is not None else max_depth + 6

    def get_best_move(self, game_map) -> Tuple[int, int]:
        """Find the best move towards the target using lookahead grid path scoring."""
        directions = self._valid_moves(game_map)
        if not directions:
            return 0, 0

        if not self._should_choose_new_direction(directions):
            return self.last_dx, self.last_dy

        best_score = float('inf')
        best_move = (0, 0)
        reverse_move = (0, 0)
        reverse_score = float('inf')
        pacman = self.ctx.pacman

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            path_distance = self._path_distance(game_map, new_x, new_y, self.target_x, self.target_y)
            future_distance = self._future_path_score(game_map, new_x, new_y)
            distance = abs(new_x - self.target_x) + abs(new_y - self.target_y)
            if self.mode == "frightened":
                path_away = self._path_distance(game_map, new_x, new_y, pacman.x, pacman.y, max_depth=12)
                score = -(path_away * 1.15) - distance * 0.15
            else:
                score = path_distance * 1.1 + future_distance * 0.35 + distance * 0.15

            if (dx, dy) == (self.last_dx, self.last_dy):
                score -= 0.55

            score += self.personality_score_adjustment(dx, dy, new_x, new_y, pacman)

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

        if self.returning_home:
            self.mode = "home"
            self.target_x = self.spawn_x
            self.target_y = self.spawn_y
        else:
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
            if self.returning_home and self.x == self.spawn_x and self.y == self.spawn_y:
                self.returning_home = False
                self.respawn_lock_ticks = self.EATEN_RESPAWN_TICKS
                self.last_dx = 0
                self.last_dy = 0


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

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Blinky is relentless: heavily favors direct approach and keeping pace.
        adjustment = 0.0
        if dx == pacman.last_dx and dy == pacman.last_dy:
            adjustment -= 0.9
        if abs(new_x - pacman.x) + abs(new_y - pacman.y) <= 3:
            adjustment -= 0.8
        adjustment += self.ctx.map_blinky_bias()
        return adjustment


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

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Pinky prefers turns and front-cuts over raw shortest pursuit.
        adjustment = 0.0
        if (dx, dy) != (self.last_dx, self.last_dy) and (self.last_dx, self.last_dy) != (0, 0):
            adjustment -= 0.65
        ahead_x = pacman.x + pacman.last_dx * 2
        ahead_y = pacman.y + pacman.last_dy * 2
        adjustment += (abs(new_x - ahead_x) + abs(new_y - ahead_y)) * 0.12
        if self.ctx.current_map_number() in {1, 4} and (dx, dy) != (pacman.last_dx, pacman.last_dy):
            adjustment -= 0.22
        adjustment += self.ctx.map_pinky_bias()
        return adjustment


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

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Inky is less predictable: slight sideways bias and looser pursuit.
        adjustment = 0.0
        if pacman.last_dx != 0 and dy != 0:
            adjustment -= 0.45
        if pacman.last_dy != 0 and dx != 0:
            adjustment -= 0.45
        if (new_x + new_y + self.ctx.ghost_mode_timer) % 3 == 0:
            adjustment -= 0.18
        if self.ctx.current_map_number() == 1 and abs(new_x - pacman.x) + abs(new_y - pacman.y) >= 4:
            adjustment -= 0.22
        adjustment += self.ctx.map_inky_bias()
        return adjustment


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

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Clyde is skittish and drifty, preferring exits when he's too close.
        distance = abs(pacman.x - self.x) + abs(pacman.y - self.y)
        adjustment = 0.0
        if distance <= 6:
            adjustment -= abs(new_x - self.scatter_target[0]) * 0.08
            adjustment -= abs(new_y - self.scatter_target[1]) * 0.08
        else:
            if (dx, dy) != (self.last_dx, self.last_dy) and (self.last_dx, self.last_dy) != (0, 0):
                adjustment -= 0.35
        if self.ctx.current_map_number() == 3 and distance <= 8:
            adjustment -= 0.3
        adjustment += self.ctx.map_clyde_bias()
        return adjustment
