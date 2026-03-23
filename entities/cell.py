from __future__ import annotations

from abc import ABC, abstractmethod

from core.context import GameContext


class Actor(ABC):
    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx
        self.x = 0
        self.y = 0
        self.spawn_x = 0
        self.spawn_y = 0

    def frame(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def set_spawn(self, x: int, y: int) -> None:
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y

    def reset_to_spawn(self) -> None:
        self.x = self.spawn_x
        self.y = self.spawn_y

    def process(self) -> None:
        pass

    def enable_rage(self, ticks: int) -> None:
        pass

    def kill(self) -> None:
        pass

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

    def tick(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass
