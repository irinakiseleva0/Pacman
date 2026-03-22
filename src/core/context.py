# core/context.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    window_width: int = 448
    window_height: int = 496
    fps: int = 16
    
    RES: int = 16
    WIDTH: int = 28
    HEIGHT: int = 31
@dataclass
class GameContext:
    cfg: Config
    game: Optional[object] = None
    score: int = 0
    high_score: int = 0

    pacman: Optional[object] = None
    game_map: Optional[object] = None
