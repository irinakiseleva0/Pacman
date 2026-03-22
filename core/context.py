from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from utils.score_storage import load_high_score


@dataclass
class Config:
    # Display & Map
    fps: int = 16
    tile_size: int = 16
    map_width: int = 28
    map_height: int = 31

    # Game Speed & Timing
    logic_tick_rate: int = 3
    death_animation_fps: int = 1
    rage_duration_ticks: int = 300
    cherry_respawn_ticks: int = 150

    # Score Values
    seed_score: int = 10
    large_seed_score: int = 50
    cherry_score: int = 500
    ghost_score: int = 200

    # Game State
    initial_lives: int = 3

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
    lives: int = field(default=3)
    current_level: int = 1
    last_result: str = ""

    pacman: Optional[object] = None
    game_map: Optional[object] = None

    def __post_init__(self):
        # Initialize lives from config if not already set
        if self.lives == 3:
            self.lives = self.cfg.initial_lives

    def get_map_path(self, level: Optional[int] = None) -> str:
        """Get the map file path for a given level (1-indexed)."""
        level = level or self.current_level
        if level == 1:
            return "maps/pacman_map.txt"
        return f"maps/pacman_map{level}.txt"

    def next_level(self) -> None:
        """Advance to the next level."""
        self.current_level += 1
        self.lives = self.cfg.initial_lives
