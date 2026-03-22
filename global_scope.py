from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from Map import Map
    from Game import Game
    from Pacman import Pacman


class GlobalScope:
    # --- CONFIG ---
    FPS: int = 16

    WIDTH: int = 28
    HEIGHT: int = 31
    RES: int = 16

    # --- WINDOW ---
    @classmethod
    def window_width(cls) -> int:
        return cls.WIDTH * cls.RES

    @classmethod
    def window_height(cls) -> int:
        return cls.HEIGHT * cls.RES

    # --- GAME STATE ---
    score: int = 0
    nick: str = ""

    # --- REFERENCES ---
    game_map: Optional["Map"] = None
    game: Optional["Game"] = None
    pacman: Optional["Pacman"] = None

    # --- HELPERS ---
    @classmethod
    def reset(cls) -> None:
        """Reset game state for new run"""
        cls.score = 0
        cls.nick = ""
        cls.game_map = None
        cls.game = None
        cls.pacman = None