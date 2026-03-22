from __future__ import annotations

from entities.cell import Cell, Actor
from utils.animated_sprite import Sprite
from assets.assets import Assets


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
            cls._shared_sprite = Sprite({
                cls.BASE_KEY: [Assets.texture(cls.BASE_PATH)]
            })
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
        Wall._sprite().draw_specified(
            self.wall_key,
            0,
            (self.x * cfg.tile_size, self.y * cfg.tile_size),
        )