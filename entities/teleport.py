from __future__ import annotations

from entities.cell import Cell, Actor


class Teleport(Cell):
    def draw(self) -> None:
        pass

    def on_enter(self, actor: Actor) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        if getattr(actor, "kind", None) != "pacman":
            return

        if actor.x == 0:
            actor.x = game_map.width - 2
        elif actor.x == game_map.width - 1:
            actor.x = 1