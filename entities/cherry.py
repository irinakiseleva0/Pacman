from __future__ import annotations

import pyray
from raylib import colors

from assets.assets import Assets
from entities.cell import Actor, Cell


class Cherry(Cell):
    TEX = "sprites/consumables/cherry.png"

    def __init__(self, ctx):
        super().__init__(ctx)
        self.enabled = True
        self.timer = 0
        self.image = Assets.texture(self.TEX)

    def on_enter(self, actor: Actor) -> None:
        if not self.enabled:
            return
        if getattr(actor, "kind", None) != "pacman":
            return

        self.enabled = False
        self.ctx.score += self.ctx.cfg.cherry_score
        self.timer = self.ctx.effective_cherry_respawn()

        self.ctx.particles.create_cherry_eat_effect(self.x, self.y)
        self.ctx.floating_text.add_score_text(
            self.ctx.cfg.cherry_score, self.x, self.y
        )
        self.ctx.screen_shake.shake(5.0, 0.35)

    def tick(self) -> None:
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.enabled = True
                self.ctx.particles.create_cherry_respawn_effect(self.x, self.y)
                self.ctx.floating_text.add_text(
                    "CHERRY",
                    self.x * self.ctx.cfg.tile_size - 4,
                    self.y * self.ctx.cfg.tile_size - 12,
                    colors.GOLD,
                    0.9,
                    12,
                )

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        pyray.draw_texture_ex(
            self.image,
            (self.x * cfg.tile_size, self.y * cfg.tile_size),
            0.0,
            1.0,
            colors.WHITE,
        )
