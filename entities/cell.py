from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol, Optional
from core.context import GameContext

class Actor(Protocol):
    x: int
    y: int
    ctx: GameContext

class Cell(ABC):
    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.x = 0
        self.y = 0
        self.processed = False

    def frame(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    # если клетка “проходимая” — actor может войти
    def is_blocking(self, actor: Actor) -> bool:
        return False

    # событие “актер вошел в клетку”
    def on_enter(self, actor: Actor) -> None:
        return

    @abstractmethod
    def draw(self) -> None: ...
