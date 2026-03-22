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
            self.ctx.score += 10

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
            self.enabled = False
            self.ctx.score += 50
            if hasattr(actor, "enable_rage"):
                actor.enable_rage(300)  # 300 ticks = ~18 seconds at 16 fps

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = self.x * tile + tile // 2
        py = self.y * tile + tile // 2
        pyray.draw_circle(px, py, 4, colors.MAGENTA)
