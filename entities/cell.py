from __future__ import annotations

from abc import ABC, abstractmethod

from core.context import GameContext


class Actor(ABC):
    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx
        self.x = 0
        self.y = 0

    def frame(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    @abstractmethod
    def draw(self) -> None:
        pass


class Cell(ABC):
    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx
        self.x = 0
        self.y = 0

    def frame(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def is_blocking(self, actor: Actor) -> bool:
        return False

    def on_enter(self, actor: Actor) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass
