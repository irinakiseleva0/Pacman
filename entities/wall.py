# entities/wall.py
from __future__ import annotations
from cell import Cell
from animated_sprite import Sprite
from assets.assets import Assets


class Wall(Cell):
    BASE_KEY = "00000000"
    BASE_PATH = "sprites/walls/0/0000/wall_00000000.png"

    _shared_sprite: Sprite | None = None

    def __init__(self, ctx):
        super().__init__(ctx)
        self.wall_key: str = Wall.BASE_KEY
        self.cars: int = 0
        self.car: str = "0000"

    @classmethod
    def _sprite(cls) -> Sprite:
        if cls._shared_sprite is None:
            cls._shared_sprite = Sprite(
                {cls.BASE_KEY: [Assets.texture(cls.BASE_PATH)]})
            cls._shared_sprite.set_key(cls.BASE_KEY, True)
        return cls._shared_sprite

    @classmethod
    def _ensure_key(cls, key: str, cars: int, car: str) -> None:
        spr = cls._sprite()
        if key in spr.texture_dictionary:
            return
        path = f"sprites/walls/{cars}/{car}/wall_{key}.png"
        try:
            spr.texture_dictionary[key] = [Assets.texture(path)]
        except Exception:
            spr.texture_dictionary[key] = [Assets.texture(cls.BASE_PATH)]

    @staticmethod
    def compute_key_for(layer, y: int, x: int) -> tuple[str, int, str]:
        h = len(layer)
        w = len(layer[0]) if h else 0

        def is_wall(yy: int, xx: int) -> int:
            if xx < 0 or xx >= w or yy < 0 or yy >= h:
                return 0
            return 1 if isinstance(layer[yy][xx], Wall) else 0

        _1 = is_wall(y - 1, x)
        _2 = is_wall(y - 1, x + 1)
        _3 = is_wall(y,     x + 1)
        _4 = is_wall(y + 1, x + 1)
        _5 = is_wall(y + 1, x)
        _6 = is_wall(y + 1, x - 1)
        _7 = is_wall(y,     x - 1)
        _8 = is_wall(y - 1, x - 1)

        cars = _1 + _3 + _5 + _7
        car = f"{_1}{_3}{_5}{_7}"
        key = f"{_1}{_2}{_3}{_4}{_5}{_6}{_7}{_8}"
        return key, cars, car

    def set_key_from_map(self, layer) -> None:
        key, cars, car = Wall.compute_key_for(layer, self.y, self.x)
        self.wall_key = key
        self.cars = cars
        self.car = car
        Wall._ensure_key(key, cars, car)

    def process(self) -> None:
        return

    def draw(self) -> None:
        cfg = self.ctx.cfg
        m = self.ctx.game_map
        if not m:
            return
        key, cars, car = Wall.compute_key_for(m.s_layer, self.y, self.x)
        Wall._ensure_key(key, cars, car)
        Wall._sprite().draw_specified(key, 0, (self.x * cfg.RES, self.y * cfg.RES))
