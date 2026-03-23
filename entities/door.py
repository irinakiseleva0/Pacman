from __future__ import annotations

from entities.cell import Cell, Actor
from utils.animated_sprite import Sprite
from assets.assets import Assets


class Door(Cell):
    TEXTURE_PATH = "sprites/walls/ghost_door_full.png"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)

        texture = Assets.texture(self.TEXTURE_PATH)
        self.sprite = Sprite({"door": [texture]})
        self.sprite.set_key("door", True)

    def is_blocking(self, actor: Actor) -> bool:
        return getattr(actor, "kind", None) == "pacman"

    def draw(self) -> None:
        cfg = self.ctx.cfg
        scale = cfg.tile_size / 16
        pos = (self.x * cfg.tile_size, self.y * cfg.tile_size)
        self.sprite.draw_specified("door", 0, pos, scale=scale)
