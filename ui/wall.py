from __future__ import annotations

import math

import pygame

import core.raylib_api as pyray

from entities.cell import Cell, Actor
from utils.animated_sprite import Sprite
from assets.assets import Assets
from ui.ui import LIVE_CYAN
from utils.visual_effects import with_alpha


def _draw_rect(x: float, y: float, width: float, height: float, color) -> None:
    surface = pyray.get_drawing_surface()
    rect = pygame.Rect(int(x), int(y), int(width), int(height))
    if len(color) >= 4 and color[3] < 255:
        layer = pygame.Surface((max(1, rect.width), max(1, rect.height)), pygame.SRCALPHA)
        pygame.draw.rect(layer, color, layer.get_rect())
        surface.blit(layer, rect.topleft)
        return
    pygame.draw.rect(surface, color, rect)


def _draw_line(x1: float, y1: float, x2: float, y2: float, color, width: int) -> None:
    surface = pyray.get_drawing_surface()
    start = (int(x1), int(y1))
    end = (int(x2), int(y2))
    if len(color) >= 4 and color[3] < 255:
        line_width = max(1, int(width))
        pad = line_width + 1
        left = min(start[0], end[0]) - pad
        top = min(start[1], end[1]) - pad
        right = max(start[0], end[0]) + pad
        bottom = max(start[1], end[1]) + pad
        layer = pygame.Surface((max(1, right - left), max(1, bottom - top)), pygame.SRCALPHA)
        pygame.draw.line(layer, color, (start[0] - left, start[1] - top), (end[0] - left, end[1] - top), line_width)
        surface.blit(layer, (left, top))
        return
    pygame.draw.line(surface, color, start, end, max(1, int(width)))


class Wall(Cell):
    BASE_KEY = "00000000"
    BASE_PATH = "sprites/walls/0/0000/wall_00000000.png"

    _shared_sprite: Sprite | None = None

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.wall_key: str = Wall.BASE_KEY
        self.cardinal_count: int = 0
        self.cardinal_mask: str = "0000"

    def is_blocking(self, actor: Actor) -> bool:
        return True

    @classmethod
    def _sprite(cls) -> Sprite:
        if cls._shared_sprite is None:
            textures = {}
            for path, surface in Assets.wall_atlas_textures().items():
                name = path.rsplit("/", 1)[-1]
                if not name.startswith("wall_") or not name.endswith(".png"):
                    continue
                key = name[5:-4]
                textures.setdefault(key, []).append(surface)

            if not textures:
                textures[cls.BASE_KEY] = [Assets.texture(cls.BASE_PATH)]
            elif cls.BASE_KEY not in textures:
                textures[cls.BASE_KEY] = [Assets.texture(cls.BASE_PATH)]

            cls._shared_sprite = Sprite(textures)
            cls._shared_sprite.set_key(cls.BASE_KEY, True)
        return cls._shared_sprite

    @classmethod
    def _ensure_key(cls, key: str, cardinal_count: int, cardinal_mask: str) -> None:
        sprite = cls._sprite()
        if key in sprite.texture_dictionary:
            return

        path = f"sprites/walls/{cardinal_count}/{cardinal_mask}/wall_{key}.png"
        try:
            sprite.texture_dictionary[key] = [Assets.texture(path)]
        except Exception:
            sprite.texture_dictionary[key] = [Assets.texture(cls.BASE_PATH)]

    @staticmethod
    def compute_key_for(layer, y: int, x: int) -> tuple[str, int, str]:
        height = len(layer)
        width = len(layer[0]) if height else 0

        def is_wall(yy: int, xx: int) -> int:
            if xx < 0 or xx >= width or yy < 0 or yy >= height:
                return 0
            return 1 if isinstance(layer[yy][xx], Wall) else 0

        n = is_wall(y - 1, x)
        ne = is_wall(y - 1, x + 1)
        e = is_wall(y, x + 1)
        se = is_wall(y + 1, x + 1)
        s = is_wall(y + 1, x)
        sw = is_wall(y + 1, x - 1)
        w = is_wall(y, x - 1)
        nw = is_wall(y - 1, x - 1)

        cardinal_count = n + e + s + w
        cardinal_mask = f"{n}{e}{s}{w}"
        key = f"{n}{ne}{e}{se}{s}{sw}{w}{nw}"
        return key, cardinal_count, cardinal_mask

    def set_key_from_map(self, layer) -> None:
        key, cardinal_count, cardinal_mask = Wall.compute_key_for(layer, self.y, self.x)
        self.wall_key = key
        self.cardinal_count = cardinal_count
        self.cardinal_mask = cardinal_mask
        Wall._ensure_key(key, cardinal_count, cardinal_mask)

    def draw(self) -> None:
        cfg = self.ctx.cfg
        time_s = getattr(self.ctx, "visual_time", 0.0)
        scale = cfg.tile_size / 16
        px = cfg.board_offset_x + self.x * cfg.tile_size
        py = cfg.board_offset_y + self.y * cfg.tile_size
        tile = cfg.tile_size
        pulse = 0.5 + 0.5 * math.sin(time_s * 2.6 + self.x * 0.37 + self.y * 0.21)

        _draw_rect(px - 2, py - 2, tile + 4, tile + 4, with_alpha(LIVE_CYAN, int(12 + pulse * 8)))
        _draw_rect(px + 2, py + 2, tile - 4, tile - 4, with_alpha((6, 8, 22, 255), 240))

        Wall._sprite().draw_specified(
            self.wall_key,
            0,
            (px, py),
            scale=scale,
            tint=(28, 52, 96, 255),
        )

        n_open = "1" not in self.cardinal_mask[:1]
        e_open = "1" not in self.cardinal_mask[1:2]
        s_open = "1" not in self.cardinal_mask[2:3]
        w_open = "1" not in self.cardinal_mask[3:4]

        edge_glow = with_alpha(LIVE_CYAN, int(20 + pulse * 14))  
        edge_main = with_alpha(LIVE_CYAN, int(90 + pulse * 30)) 
        edge_soft = with_alpha(LIVE_CYAN, int(30 + pulse * 12))   

        if n_open:
            _draw_line(px - 1, py + 1, px + tile + 1, py + 1, edge_glow, 7)
            _draw_line(px + 2, py + 2, px + tile - 2, py + 2, edge_main, 2)
            _draw_line(px + 4, py + 3, px + tile - 4, py + 3, edge_soft, 1)
        if s_open:
            _draw_line(px - 1, py + tile - 2, px + tile + 1, py + tile - 2, edge_glow, 7)
            _draw_line(px + 2, py + tile - 2, px + tile - 2, py + tile - 2, edge_main, 2)
        if w_open:
            _draw_line(px + 1, py - 1, px + 1, py + tile + 1, edge_glow, 7)
            _draw_line(px + 2, py + 2, px + 2, py + tile - 2, edge_main, 2)
        if e_open:
            _draw_line(px + tile - 2, py - 1, px + tile - 2, py + tile + 1, edge_glow, 7)
            _draw_line(px + tile - 2, py + 2, px + tile - 2, py + tile - 2, edge_main, 2)
