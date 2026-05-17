from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from entities.cell import Cell
from utils.visual_effects import with_alpha


class Seed(Cell):
    """Small seed/dot that Pacman can eat for points."""

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.enabled = True

    def is_blocking(self, actor) -> bool:
        return False

    def on_enter(self, actor) -> None:
        if getattr(actor, "kind", None) == "pacman" and self.enabled:
            palette = self.ctx.effect_palette()
            score_value = self.ctx.effective_seed_score()
            self.enabled = False
            self.ctx.score += score_value
            self.ctx.record_dot_eaten()
            self.ctx.play_sfx("pellet_eat")
            route_chain_count, route_bonus = self.ctx.register_route_chain_dot()
            line_count, line_bonus = self.ctx.register_line_bonus_dot(
                getattr(actor, "last_dx", 0),
                getattr(actor, "last_dy", 0),
            )

            # Add visual effects
            self.ctx.particles.create_dot_eat_effect(self.x, self.y, palette["dot"])
            self.ctx.visual.light_bursts.add_grid_burst(self.x, self.y, palette["dot"], 16, 0.9, 0.16)
            self.ctx.floating_text.add_score_text(
                score_value, self.x, self.y)
            dot_count = self.ctx.run_stats.dots_eaten
            link_step = self.ctx.map_link_bonus_step()
            link_bonus = self.ctx.map_link_bonus_value()
            if link_step > 0:
                level_dots = self.ctx.level_progress_snapshot()["dots"]
                if level_dots > 0 and level_dots % link_step == 0:
                    self.ctx.score += link_bonus
                    self.ctx.floating_text.add_text(
                        f"LINK +{link_bonus}",
                        self.x * 16 - 18,
                        self.y * 16 - 22,
                        palette["power"],
                        0.95,
                        12,
                    )
                    self.ctx.trigger_screen_flash(palette["dot"], 0.05, 0.06)
            if route_bonus > 0:
                self.ctx.score += route_bonus
                self.ctx.run_stats.route_bonus_score += route_bonus
                self.ctx.floating_text.add_text(
                    f"ROUTE {route_chain_count} +{route_bonus}",
                    self.x * 16 - 22,
                    self.y * 16 - 38,
                    palette["power"],
                    0.88,
                    12,
                )
                self.ctx.trigger_screen_shake(1.8, 0.07)
                self.ctx.trigger_screen_flash(palette["dot"], 0.055, 0.05)
            if line_bonus > 0:
                self.ctx.score += line_bonus
                self.ctx.run_stats.line_bonus_score += line_bonus
                self.ctx.floating_text.add_text(
                    f"LINE {line_count} +{line_bonus}",
                    self.x * 16 - 20,
                    self.y * 16 - 52,
                    colors.SKYBLUE,
                    0.82,
                    11,
                )
                self.ctx.trigger_screen_flash(colors.SKYBLUE, 0.04, 0.04)
            if dot_count % 6 == 0:
                self.ctx.trigger_screen_shake(1.4, 0.05)
                self.ctx.trigger_screen_flash(palette["dot"], 0.035, 0.045)
                self.ctx.trigger_action_juice(slow_scale=0.94, slow_duration=0.025)
            elif dot_count % 3 == 0:
                self.ctx.trigger_screen_flash(palette["dot"], 0.02, 0.03)
            else:
                self.ctx.trigger_action_juice(slow_scale=0.97, slow_duration=0.018)

            pressure_step = self.ctx.map_pressure_spike_step()
            if pressure_step > 0:
                level_dots = self.ctx.level_progress_snapshot()["dots"]
                if level_dots > 0 and level_dots % pressure_step == 0:
                    game_map = self.ctx.game_map
                    if game_map is not None:
                        surge = self.ctx.map_release_surge_amount()
                        if surge > 0:
                            game_map.nudge_pending_ghosts(surge)
                            label = "LANE SURGE" if self.ctx.current_map_number() == 2 else "OVERRUN"
                            self.ctx.floating_text.add_text(
                                label,
                                self.x * 16 - 18,
                                self.y * 16 - 24,
                                palette["ghost"],
                                0.9,
                                12,
                            )
                            self.ctx.trigger_screen_flash(palette["ghost"], 0.06, 0.05)
                            self.ctx.trigger_screen_shake(1.8, 0.08)

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = cfg.board_offset_x + self.x * tile + tile // 2
        py = cfg.board_offset_y + self.y * tile + tile // 2
        pulse = 0.5 + 0.5 * __import__("math").sin(getattr(self.ctx, "visual_time", 0.0) * 6.0 + self.x * 0.5 + self.y * 0.25)
        pyray.draw_circle(px, py, 3 + pulse, with_alpha(colors.YELLOW, 36))
        pyray.draw_circle(px, py, 2, colors.YELLOW)


class LargeSeed(Cell):
    """Large seed/power-up that Pacman can eat to enter rage mode."""

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.enabled = True

    def is_blocking(self, actor) -> bool:
        return False

    def on_enter(self, actor) -> None:
        if getattr(actor, "kind", None) == "pacman" and self.enabled:
            palette = self.ctx.effect_palette()
            score_value = self.ctx.effective_large_seed_score()
            already_raging = bool(getattr(actor, "rage", False))
            chain_level, chain_bonus, rage_bonus, keep_combo = self.ctx.trigger_power_chain(already_raging)
            hunt_bonus, hunt_rage_bonus = self.ctx.consume_hunt_window_bonus()
            self.enabled = False
            self.ctx.score += score_value + chain_bonus + hunt_bonus
            self.ctx.run_stats.ghost_bonus_score += chain_bonus
            self.ctx.run_stats.risk_bonus_score += hunt_bonus
            self.ctx.record_power_seed_eaten()
            self.ctx.play_sfx("power_eat")
            actor.enable_rage(self.ctx.effective_rage_duration() + rage_bonus + hunt_rage_bonus, keep_combo=keep_combo)

            game_map = self.ctx.game_map
            if game_map is not None:
                game_map.stall_unreleased_ghosts(
                    self.ctx.cfg.ghost_fright_release_stall_ticks
                )

            # Add visual effects
            self.ctx.particles.create_large_seed_eat_effect(self.x, self.y, (palette["power"], colors.WHITE))
            self.ctx.visual.light_bursts.add_grid_burst(self.x, self.y, palette["power_flash"], 36, 1.65, 0.28)
            self.ctx.floating_text.add_score_text(
                score_value, self.x, self.y)
            if chain_bonus > 0:
                self.ctx.floating_text.add_text(
                    f"CHAIN {chain_level} +{chain_bonus}",
                    self.x * 16 - 28,
                    self.y * 16 - 28,
                    palette["power"],
                    1.0,
                    12,
                )
            if hunt_bonus > 0:
                self.ctx.floating_text.add_text(
                    f"HUNT +{hunt_bonus}",
                    self.x * 16 - 22,
                    self.y * 16 - 42,
                    palette["power"],
                    0.96,
                    12,
                )
            if keep_combo and self.ctx.ghost_combo > 0:
                self.ctx.floating_text.add_text(
                    "COMBO HELD",
                    self.x * 16 - 20,
                    self.y * 16 - 42,
                    colors.GOLD,
                    0.9,
                    11,
                )
            self.ctx.trigger_screen_shake(8.2, 0.5)
            self.ctx.trigger_screen_flash(palette["power_flash"], 0.34, 0.2)
            self.ctx.trigger_freeze(2)
            self.ctx.trigger_action_juice(hitstop=0.055, slow_scale=0.58, slow_duration=0.12)

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = cfg.board_offset_x + self.x * tile + tile // 2
        py = cfg.board_offset_y + self.y * tile + tile // 2
        pulse = 0.5 + 0.5 * __import__("math").sin(getattr(self.ctx, "visual_time", 0.0) * 8.0 + self.x + self.y)
        pyray.draw_circle(px, py, 8 + pulse * 3, with_alpha(colors.MAGENTA, 42))
        pyray.draw_circle(px, py, 4 + pulse, colors.MAGENTA)
