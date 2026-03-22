from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from utils.score_storage import load_high_score


@dataclass
class Config:
    fps: int = 16
    tile_size: int = 16
    map_width: int = 28
    map_height: int = 31

    @property
    def window_width(self) -> int:
        return self.map_width * self.tile_size

    @property
    def window_height(self) -> int:
        return self.map_height * self.tile_size


@dataclass
class GameContext:
    cfg: Config = field(default_factory=Config)

    score: int = 0
    high_score: int = field(default_factory=load_high_score)
    lives: int = 3
    last_result: str = ""

    pacman: Optional[object] = None
    game_map: Optional[object] = None
