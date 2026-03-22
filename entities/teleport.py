from __future__ import annotations
from cell import Cell, Actor

class Teleport(Cell):
    def draw(self) -> None:
        return

    def on_enter(self, actor: Actor) -> None:
        m = self.ctx.game_map
        if not m:
            return
        if getattr(actor, "kind", "pacman") != "pacman":
            return

        # если вошел на teleport на левом краю — переносим вправо и наоборот
        if actor.x == 0:
            actor.x = m.width - 2
        elif actor.x == m.width - 1:
            actor.x = 1

