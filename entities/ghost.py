from __future__ import annotations

from collections import deque
import math
import core.raylib_api as pyray
from raylib import colors
from typing import Tuple

from entities.cell import Actor
from ui.ui import LIVE_CYAN, LIVE_PINK
from utils.effects import shake_camera
from utils.visual_effects import Particle, with_alpha


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
        self.slow_skip_tick = False

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        return 0.0

    def _trail_signature(self) -> tuple[object, float]:
        class_name = type(self).__name__
        if class_name == "Blinky":
            return colors.RED, 1.2
        if class_name == "Pinky":
            return LIVE_PINK, 1.0
        if class_name == "Inky":
            return LIVE_CYAN, 2.6
        if class_name == "Clyde":
            return colors.ORANGE, 1.1
        return self.color, 1.0

    def _trail_spread(self) -> int:
        if type(self).__name__ == "Inky":
            return 5
        if type(self).__name__ in {"Blinky", "Clyde"}:
            return 2
        return 3

    def _intent_body_color(self):
        return None

    def _draw_intent_cue(self, px: int, py: int, tile: int, body_radius: int, time_s: float) -> None:
        return None

    def _pacman_heading(self, pacman) -> tuple[int, int]:
        dx = getattr(pacman, "last_dx", 0)
        dy = getattr(pacman, "last_dy", 0)
        if (dx, dy) == (0, 0):
            state = getattr(pacman, "state", "")
            if state == "LEFT":
                return -1, 0
            if state == "RIGHT":
                return 1, 0
            if state == "UP":
                return 0, -1
            if state == "DOWN":
                return 0, 1
        return dx, dy

    def _is_ahead_of_pacman(self, pacman, x: int, y: int) -> bool:
        heading_dx, heading_dy = self._pacman_heading(pacman)
        if heading_dx == 0 and heading_dy == 0:
            return False
        rel_x = x - pacman.x
        rel_y = y - pacman.y
        return rel_x * heading_dx + rel_y * heading_dy > 0

    def _same_axis_as_pacman(self, pacman, x: int, y: int) -> bool:
        return x == pacman.x or y == pacman.y

    def _side_lane_bias(self, pacman, x: int, y: int) -> float:
        heading_dx, heading_dy = self._pacman_heading(pacman)
        if heading_dx != 0:
            return 0.0 if x == pacman.x else -0.5
        if heading_dy != 0:
            return 0.0 if y == pacman.y else -0.5
        return -0.15 if x != pacman.x and y != pacman.y else 0.0

    def _flank_distance_score(self, pacman, x: int, y: int) -> float:
        heading_dx, heading_dy = self._pacman_heading(pacman)
        if heading_dx == 0 and heading_dy == 0:
            return 0.0
        side_x, side_y = -heading_dy, heading_dx
        side_target_x = pacman.x + side_x * 2
        side_target_y = pacman.y + side_y * 2
        return (abs(x - side_target_x) + abs(y - side_target_y)) * 0.14

    def _behind_pacman_score(self, pacman, x: int, y: int) -> float:
        heading_dx, heading_dy = self._pacman_heading(pacman)
        if heading_dx == 0 and heading_dy == 0:
            return 0.0
        rel_x = x - pacman.x
        rel_y = y - pacman.y
        dot = rel_x * heading_dx + rel_y * heading_dy
        if dot < 0:
            return -0.75
        if dot == 0:
            return -0.2
        return 0.2

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

        pyray.draw_circle(px + trail_dx * 2, py + trail_dy * 2, trail_radius + 1, with_alpha(LIVE_CYAN, 32))
        pyray.draw_circle(px + trail_dx * 4, py + trail_dy * 4, trail_radius + 1, with_alpha(colors.WHITE, 42))

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

        pulse = 0.5 + 0.5 * math.sin(time_s * 5.0 + self.x + self.y)
        body_radius = max(6, tile // 2 - 2)
        glow_radius = body_radius + 5 + int(pulse * 3)
        dir_dx = max(-1, min(1, self.last_dx))
        dir_dy = max(-1, min(1, self.last_dy))
        trail_color, trail_scale = self._trail_signature()
        frightened = self.mode == "frightened"
        respawning = self.respawn_lock_ticks > 0 or self.release_delay_ticks > 0
        intent_color = self._intent_body_color()
        if intent_color is not None and not frightened and not respawning:
            base_color = intent_color

        accent_glow = LIVE_CYAN if self.returning_home else LIVE_PINK if base_color == colors.RED else LIVE_CYAN
        if frightened:
            accent_glow = colors.WHITE
        elif respawning:
            accent_glow = colors.SKYBLUE
        for index in range(4, 0, -1):
            spread = self._trail_spread()
            trail_x = px - dir_dx * index * spread
            trail_y = py - dir_dy * index * spread
            trail_alpha = 10 + index * 5
            if frightened:
                trail_alpha += 6 if index % 2 == 0 else -2
            if respawning:
                trail_alpha += 10 if index % 2 == 0 else 0
            pyray.draw_circle(
                trail_x,
                trail_y,
                glow_radius + 4 - index + int(trail_scale),
                with_alpha(trail_color if not frightened else colors.WHITE, trail_alpha),
            )

        outer_alpha = 12
        mid_alpha = 26
        inner_alpha = 38
        if frightened:
            flicker = 0.5 + 0.5 * math.sin(time_s * 16.0 + self.x * 0.7)
            outer_alpha = int(8 + flicker * 16)
            mid_alpha = int(16 + flicker * 20)
            inner_alpha = int(24 + flicker * 22)
        elif respawning:
            flicker = 0.5 + 0.5 * math.sin(time_s * 20.0 + self.y * 0.9)
            outer_alpha = int(10 + flicker * 20)
            mid_alpha = int(20 + flicker * 20)
            inner_alpha = int(20 + flicker * 26)

        pyray.draw_circle(px, py, glow_radius + 22, with_alpha(accent_glow, outer_alpha))
        pyray.draw_circle(px, py, glow_radius + 14, with_alpha(base_color, mid_alpha))
        pyray.draw_circle(px, py, glow_radius + 7, with_alpha(base_color, inner_alpha))
        pyray.draw_circle(px, py, body_radius, with_alpha(base_color, 228))
        if not frightened and not respawning:
            self._draw_intent_cue(px, py, tile, body_radius, time_s)
        if frightened:
            # Slight distortion band makes frightened state feel unstable.
            band_y = py + int(math.sin(time_s * 18.0 + self.x) * 2)
            pyray.draw_rectangle_rec(
                pyray.Rectangle(px - body_radius + 2, band_y, body_radius * 2 - 4, 3),
                with_alpha(colors.WHITE, 18),
            )
        elif respawning:
            glitch_x = int(math.sin(time_s * 22.0 + self.x * 0.4) * 2)
            pyray.draw_rectangle_rec(
                pyray.Rectangle(px - body_radius + glitch_x, py - 2, body_radius * 2 - 2, 2),
                with_alpha(colors.WHITE, 22),
            )
            pyray.draw_rectangle_rec(
                pyray.Rectangle(px - body_radius - glitch_x, py + 4, body_radius * 2 - 4, 2),
                with_alpha(colors.SKYBLUE, 18),
            )

        eye_glow = 20 if not frightened else 34
        pyray.draw_circle(px, py - max(1, tile // 10), max(4, body_radius - 4), with_alpha(colors.WHITE, 16))

        # Give ghosts a cleaner, more readable face and lower edge against the dark maze.
        eye_radius = max(2, tile // 7)
        pupil_radius = max(1, eye_radius // 2)
        eye_offset_x = max(3, tile // 6)
        eye_y = py - max(1, tile // 10)
        for eye_x in (px - eye_offset_x, px + eye_offset_x):
            pyray.draw_circle(eye_x, eye_y, eye_radius + 2, with_alpha(colors.WHITE, eye_glow))
            pyray.draw_circle(eye_x, eye_y, eye_radius, colors.WHITE)
            pyray.draw_circle(eye_x + dir_dx, eye_y + dir_dy, pupil_radius, colors.BLACK)

        crown_y = py - body_radius + 4
        pyray.draw_rectangle_rec(
            pyray.Rectangle(px - body_radius + 4, crown_y, body_radius * 2 - 8, 2),
            with_alpha(colors.WHITE, 26),
        )

        pyray.draw_rectangle_rec(
            pyray.Rectangle(px - body_radius + 3, py + body_radius - 4, max(4, body_radius * 2 - 6), 2),
            with_alpha(base_color, 124),
        )

    def update_target(self) -> None:
        """Override in subclasses for different AI behaviors"""
        pacman = self.ctx.pacman
        if pacman:
            self.target_x = pacman.x
            self.target_y = pacman.y

    def on_eaten(self) -> None:
        shake_camera(4, 0.15)
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

    def _shortest_path_options(
        self,
        game_map,
        target_x: int,
        target_y: int,
        *,
        max_depth: int | None = None,
    ) -> dict[tuple[int, int], int]:
        if (self.x, self.y) == (target_x, target_y):
            return {(0, 0): 0}

        depth_limit = max_depth if max_depth is not None else max(12, game_map.width * game_map.height)
        options: dict[tuple[int, int], int] = {}
        visited = {(self.x, self.y)}
        queue = deque()

        for dx, dy in self._valid_moves(game_map):
            nx = self.x + dx
            ny = self.y + dy
            visited.add((nx, ny))
            queue.append((nx, ny, 1, (dx, dy)))

        while queue:
            x, y, depth, first_move = queue.popleft()
            if depth > depth_limit:
                continue

            if (x, y) == (target_x, target_y):
                current_best = options.get(first_move)
                if current_best is None or depth < current_best:
                    options[first_move] = depth
                continue

            next_depth = depth + 1
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx = x + dx
                ny = y + dy
                if (nx, ny) in visited or not game_map.in_bounds(nx, ny):
                    continue

                cell = game_map.get_cell(nx, ny)
                if cell is None or cell.is_blocking(self):
                    continue

                visited.add((nx, ny))
                queue.append((nx, ny, next_depth, first_move))

        return options

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
        """Find the best move using shortest-path routing plus personality tie-breakers."""
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
        shortest_paths = self._shortest_path_options(game_map, self.target_x, self.target_y)
        frightened_paths = None
        if self.mode == "frightened" and pacman is not None:
            frightened_paths = self._shortest_path_options(game_map, pacman.x, pacman.y, max_depth=14)

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            path_distance = shortest_paths.get((dx, dy))
            if path_distance is None:
                path_distance = self._path_distance(game_map, new_x, new_y, self.target_x, self.target_y)
            future_distance = self._future_path_score(game_map, new_x, new_y)
            distance = abs(new_x - self.target_x) + abs(new_y - self.target_y)
            if self.mode == "frightened":
                path_away = frightened_paths.get((dx, dy)) if frightened_paths is not None else None
                if path_away is None:
                    path_away = self._path_distance(game_map, new_x, new_y, pacman.x, pacman.y, max_depth=12)
                score = -(path_away * 1.25) - distance * 0.15 + future_distance * 0.08
            else:
                score = path_distance * 1.2 + future_distance * 0.28 + distance * 0.12

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

        if getattr(pacman, "ghosts_are_slowed", lambda: False)() and not self.returning_home:
            self.slow_skip_tick = not self.slow_skip_tick
            if self.slow_skip_tick:
                return
        else:
            self.slow_skip_tick = False

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
            if dx != 0 or dy != 0:
                trail_color = colors.WHITE if self.returning_home else self._get_draw_color()
                intensity = 0.5 + self.ctx.run.pressure_stage * 0.12
                center_x = self.x * 16 + 8 - dx * 4
                center_y = self.y * 16 + 8 - dy * 4
                self.ctx.visual.light_bursts.add_burst(center_x, center_y, 8, trail_color, intensity * 0.42, 0.08)
                if self.ctx.run.pressure_stage >= 2 or self.returning_home:
                    self.ctx.visual.particles.add_particle(
                        Particle(center_x, center_y, -dx * 8, -dy * 8, 0.12, trail_color, 1.3)
                    )
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

    def _draw_intent_cue(self, px: int, py: int, tile: int, body_radius: int, time_s: float) -> None:
        if self.mode != "chase" or self.returning_home:
            return

        hunt_pulse = 0.5 + 0.5 * math.sin(time_s * 12.0)
        chase_alpha = int(36 + hunt_pulse * 42)
        pyray.draw_circle(px, py, body_radius + 15, with_alpha(colors.RED, chase_alpha))
        pyray.draw_circle(px, py, body_radius + 8, with_alpha(colors.GOLD, int(18 + hunt_pulse * 18)))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(px - body_radius + 3, py - body_radius - 4, body_radius * 2 - 6, 3),
            with_alpha(colors.GOLD, int(72 + hunt_pulse * 72)),
        )

    def update_target(self) -> None:
        """Pressure from behind and punish retreat lanes."""
        pacman = self.ctx.pacman
        if pacman:
            heading_dx, heading_dy = self._pacman_heading(pacman)
            if heading_dx == 0 and heading_dy == 0:
                self.target_x = pacman.x
                self.target_y = pacman.y
                return

            # Sit deeper behind Pac-Man's route so backing up feels dangerous.
            self.target_x = pacman.x - heading_dx * 3
            self.target_y = pacman.y - heading_dy * 3

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Blinky is the enforcer: he trails the route and punishes hesitation.
        adjustment = 0.0
        if dx == pacman.last_dx and dy == pacman.last_dy:
            adjustment -= 0.55
        adjustment += self._behind_pacman_score(pacman, new_x, new_y)
        if self._same_axis_as_pacman(pacman, new_x, new_y):
            adjustment -= 0.6
        if abs(new_x - pacman.x) + abs(new_y - pacman.y) <= 3:
            adjustment -= 1.0
        if self._is_ahead_of_pacman(pacman, new_x, new_y):
            adjustment += 0.45
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

    def _draw_intent_cue(self, px: int, py: int, tile: int, body_radius: int, time_s: float) -> None:
        if self.mode != "chase" or self.returning_home:
            return

        pacman = self.ctx.pacman
        if pacman is None:
            return

        heading_dx, heading_dy = self._pacman_heading(pacman)
        if heading_dx == 0 and heading_dy == 0:
            heading_dx, heading_dy = self.last_dx, self.last_dy
        if heading_dx == 0 and heading_dy == 0:
            return

        flash = 0.5 + 0.5 * math.sin(time_s * 18.0 + self.x * 0.6)
        marker_alpha = int(38 + flash * 76)
        for index in range(1, 4):
            marker_x = px + heading_dx * (body_radius + index * 4)
            marker_y = py + heading_dy * (body_radius + index * 4)
            marker_size = max(2, tile // 7 - index // 2)
            pyray.draw_circle(marker_x, marker_y, marker_size, with_alpha(LIVE_PINK, marker_alpha - index * 10))
        pyray.draw_circle(px, py, body_radius + 9, with_alpha(LIVE_PINK, int(18 + flash * 22)))

    def update_target(self) -> None:
        """Target well ahead of Pac-Man so Pinky reads as a cutter."""
        pacman = self.ctx.pacman
        if pacman:
            heading_dx, heading_dy = self._pacman_heading(pacman)
            lookahead = 6
            self.target_x = pacman.x + heading_dx * lookahead
            self.target_y = pacman.y + heading_dy * lookahead

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Pinky should be felt as the route-cutter living ahead of the player.
        adjustment = 0.0
        if (dx, dy) != (self.last_dx, self.last_dy) and (self.last_dx, self.last_dy) != (0, 0):
            adjustment -= 0.85
        ahead_dx, ahead_dy = self._pacman_heading(pacman)
        ahead_x = pacman.x + ahead_dx * 4
        ahead_y = pacman.y + ahead_dy * 4
        adjustment += (abs(new_x - ahead_x) + abs(new_y - ahead_y)) * 0.12
        if self._is_ahead_of_pacman(pacman, new_x, new_y):
            adjustment -= 0.95
        if self._same_axis_as_pacman(pacman, new_x, new_y):
            adjustment -= 0.5
        if self.ctx.current_map_number() in {1, 4} and (dx, dy) != (pacman.last_dx, pacman.last_dy):
            adjustment -= 0.35
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
        """Target a dirty flank vector rather than a clean direct chase."""
        pacman = self.ctx.pacman
        if pacman:
            blinky = None
            for actor in self.ctx.game_map.dynamic_actors:
                if isinstance(actor, Blinky):
                    blinky = actor
                    break

            if blinky:
                vector_x = pacman.x - blinky.x
                vector_y = pacman.y - blinky.y
                heading_dx, heading_dy = self._pacman_heading(pacman)
                side_x, side_y = -heading_dy, heading_dx
                self.target_x = pacman.x + vector_x + side_x * 3
                self.target_y = pacman.y + vector_y + side_y * 3
            else:
                heading_dx, heading_dy = self._pacman_heading(pacman)
                side_x, side_y = -heading_dy, heading_dx
                self.target_x = pacman.x + side_x * 4
                self.target_y = pacman.y + side_y * 4

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Inky should feel messy: he drifts wide, then appears from a bad flank.
        adjustment = 0.0
        adjustment += self._side_lane_bias(pacman, new_x, new_y)
        adjustment += self._flank_distance_score(pacman, new_x, new_y)
        if self._same_axis_as_pacman(pacman, new_x, new_y):
            adjustment += 0.45
        if (new_x + new_y + self.ctx.ghost_mode_timer) % 3 == 0:
            adjustment -= 0.5
        if abs(new_x - pacman.x) + abs(new_y - pacman.y) <= 2:
            adjustment += 0.65
        if self.ctx.current_map_number() == 1 and abs(new_x - pacman.x) + abs(new_y - pacman.y) >= 4:
            adjustment -= 0.35
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

    def _retreating(self) -> bool:
        pacman = self.ctx.pacman
        if pacman is None:
            return False
        rage_timer = getattr(pacman, "rage_timer", 0)
        if getattr(pacman, "rage", False) and rage_timer > 45:
            return True
        distance = abs(pacman.x - self.x) + abs(pacman.y - self.y)
        return self.mode == "scatter" or distance <= 6

    def _intent_body_color(self):
        if self._retreating():
            return colors.GOLD
        return None

    def _draw_intent_cue(self, px: int, py: int, tile: int, body_radius: int, time_s: float) -> None:
        if not self._retreating():
            return

        twitch = 0.5 + 0.5 * math.sin(time_s * 14.0 + self.y)
        pyray.draw_circle(px, py, body_radius + 12, with_alpha(colors.ORANGE, int(18 + twitch * 28)))
        pyray.draw_circle(px + body_radius - 1, py - body_radius + 1, max(2, tile // 8), with_alpha(LIVE_CYAN, 90))
        pyray.draw_circle(px + body_radius + 3, py - body_radius - 2, max(1, tile // 10), with_alpha(colors.WHITE, 72))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(px - body_radius // 2, py + body_radius // 3, body_radius, 2),
            with_alpha(colors.BLACK, 92),
        )

    def update_target(self) -> None:
        """React to Pac-Man's power state instead of following one static mood."""
        pacman = self.ctx.pacman
        if pacman:
            distance = abs(pacman.x - self.x) + abs(pacman.y - self.y)
            rage_timer = getattr(pacman, "rage_timer", 0)

            if getattr(pacman, "rage", False) and rage_timer > 45:
                # Early power state: Clyde backs off hard and protects exits.
                self.target_x = self.scatter_target[0]
                self.target_y = self.scatter_target[1]
            elif getattr(pacman, "rage", False):
                # Late power state: he starts leaning back in before the window fully closes.
                heading_dx, heading_dy = self._pacman_heading(pacman)
                self.target_x = pacman.x + heading_dx * 2
                self.target_y = pacman.y + heading_dy * 2
            elif distance > 8:
                self.target_x = pacman.x
                self.target_y = pacman.y
            else:
                self.target_x = self.scatter_target[0]
                self.target_y = self.scatter_target[1]

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        # Clyde changes personality with the power cycle: timid, then opportunistic.
        distance = abs(pacman.x - self.x) + abs(pacman.y - self.y)
        adjustment = 0.0
        rage_timer = getattr(pacman, "rage_timer", 0)

        if getattr(pacman, "rage", False) and rage_timer > 45:
            adjustment -= abs(new_x - self.scatter_target[0]) * 0.12
            adjustment -= abs(new_y - self.scatter_target[1]) * 0.12
            if self._same_axis_as_pacman(pacman, new_x, new_y):
                adjustment += 0.3
        elif getattr(pacman, "rage", False):
            adjustment -= abs(new_x - pacman.x) * 0.14
            adjustment -= abs(new_y - pacman.y) * 0.14
            if self._is_ahead_of_pacman(pacman, new_x, new_y):
                adjustment -= 0.65
        elif distance <= 6:
            adjustment -= abs(new_x - self.scatter_target[0]) * 0.08
            adjustment -= abs(new_y - self.scatter_target[1]) * 0.08
        else:
            if (dx, dy) != (self.last_dx, self.last_dy) and (self.last_dx, self.last_dy) != (0, 0):
                adjustment -= 0.5
        if self.ctx.current_map_number() == 3 and distance <= 8:
            adjustment -= 0.3
        adjustment += self.ctx.map_clyde_bias()
        return adjustment
