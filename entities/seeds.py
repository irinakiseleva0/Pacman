from __future__ import annotations

import pyray
from raylib import colors

from entities.cell import Cell


class Seed(Cell):
    """Small seed/dot that Pacman can eat for points."""

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.enabled = True

    def is_blocking(self, actor) -> bool:
        return False

    def on_enter(self, actor) -> None:
        if getattr(actor, "kind", None) == "pacman" and self.enabled:
            self.enabled = False
            self.ctx.score += self.ctx.cfg.seed_score

            # Add visual effects
            self.ctx.particles.create_dot_eat_effect(self.x, self.y)
            self.ctx.floating_text.add_score_text(
                self.ctx.cfg.seed_score, self.x, self.y)

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = self.x * tile + tile // 2
        py = self.y * tile + tile // 2
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
            score_value = self.ctx.effective_large_seed_score()
            self.enabled = False
            self.ctx.score += score_value
            actor.enable_rage(self.ctx.effective_rage_duration())

            game_map = self.ctx.game_map
            if game_map is not None:
                game_map.stall_unreleased_ghosts(
                    self.ctx.cfg.ghost_fright_release_stall_ticks
                )

            # Add visual effects
            self.ctx.particles.create_large_seed_eat_effect(self.x, self.y)
            self.ctx.floating_text.add_score_text(
                score_value, self.x, self.y)
            self.ctx.screen_shake.shake(6.0, 0.4)
            self.ctx.screen_flash.flash(colors.WHITE, 0.2, 0.15)

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = self.x * tile + tile // 2
        py = self.y * tile + tile // 2
        pyray.draw_circle(px, py, 4, colors.MAGENTA)
