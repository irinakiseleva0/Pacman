from __future__ import annotations

import core.raylib_api as pyray


class Spritesheet:
    def __init__(self, texture, tile_w: int, tile_h: int, cols: int):
        self.texture = texture
        self.tile_w = int(tile_w)
        self.tile_h = int(tile_h)
        self.cols = max(1, int(cols))

    def get_rect(self, index: int) -> pyray.Rectangle:
        col = int(index) % self.cols
        row = int(index) // self.cols
        return pyray.Rectangle(col * self.tile_w, row * self.tile_h, self.tile_w, self.tile_h)

    def draw(self, index: int, x: float, y: float, scale: float = 1.0, tint=pyray.WHITE) -> None:
        src = self.get_rect(index)
        dst = pyray.Rectangle(x, y, self.tile_w * scale, self.tile_h * scale)
        pyray.draw_texture_pro(self.texture, src, dst, pyray.Vector2(0, 0), 0.0, tint)

    def unload(self) -> None:
        pyray.unload_texture(self.texture)
