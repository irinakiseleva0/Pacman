from __future__ import annotations
import pyray
from raylib import colors
from cell import Cell, Actor
from assets.assets import Assets

class Seed(Cell):
    TEX = "sprites/consumables/small_dot.png"
    SCORE = 50

    def __init__(self, ctx):
        super().__init__(ctx)
        self.enabled = True
        self.image = Assets.texture(self.TEX)

    def on_enter(self, actor: Actor) -> None:
        if not self.enabled:
            return
        # можно ограничить: только pacman
        if getattr(actor, "kind", "pacman") != "pacman":
            return

        self.enabled = False
        self.ctx.score += self.SCORE

    def draw(self) -> None:
        if not self.enabled:
            return
        cfg = self.ctx.cfg
        pyray.draw_texture_ex(self.image, (self.x*cfg.RES, self.y*cfg.RES), 0.0, 1.0, colors.WHITE)

class LargeSeed(Seed):
    TEX = "sprites/consumables/big_dot.png"
    SCORE = 100
    RAGE_TICKS = 10

    def __init__(self, ctx):
        super().__init__(ctx)
        self.image = Assets.texture(self.TEX)

    def on_enter(self, actor: Actor) -> None:
        if not self.enabled:
            return
        if getattr(actor, "kind", "pacman") != "pacman":
            return

        self.enabled = False
        self.ctx.score += self.SCORE
        actor.rage = True
        actor.rage_timer = self.RAGE_TICKS
