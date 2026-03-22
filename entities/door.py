from __future__ import annotations

from cell import Cell
from animated_sprite import Sprite
from assets.assets import Assets


class Door(Cell):
    TEXTURE_PATH = "sprites/walls/ghost_door_full.png"

    def __init__(self, ctx):
        super().__init__(ctx)

        tex = Assets.texture(self.TEXTURE_PATH)
        self.sprite = Sprite({"door": [tex]})
        self.sprite.set_key("door", True)

    def process(self) -> None:
        return

    def draw(self) -> None:
        cfg = self.ctx.cfg
        pos = (self.x * cfg.RES, self.y * cfg.RES)
        self.sprite.draw_specified("door", 0, pos)
