from __future__ import annotations

import pyray
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
            self.ctx.play_sfx("dot")

            # Add visual effects
            self.ctx.particles.create_dot_eat_effect(self.x, self.y, palette["dot"])
            self.ctx.floating_text.add_score_text(
                score_value, self.x, self.y)
            dot_count = self.ctx.run_stats.dots_eaten
            if dot_count % 6 == 0:
                self.ctx.trigger_screen_shake(1.4, 0.05)
                self.ctx.trigger_screen_flash(palette["dot"], 0.035, 0.045)
            elif dot_count % 3 == 0:
                self.ctx.trigger_screen_flash(palette["dot"], 0.02, 0.03)

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
            self.enabled = False
            self.ctx.score += score_value
            self.ctx.record_power_seed_eaten()
            self.ctx.play_sfx("power")
            actor.enable_rage(self.ctx.effective_rage_duration())

            game_map = self.ctx.game_map
            if game_map is not None:
                game_map.stall_unreleased_ghosts(
                    self.ctx.cfg.ghost_fright_release_stall_ticks
                )

            # Add visual effects
            self.ctx.particles.create_large_seed_eat_effect(self.x, self.y, (palette["power"], colors.WHITE))
            self.ctx.floating_text.add_score_text(
                score_value, self.x, self.y)
            self.ctx.trigger_screen_shake(6.0, 0.4)
            self.ctx.trigger_screen_flash(palette["power_flash"], 0.2, 0.15)

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
