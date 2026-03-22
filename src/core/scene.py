from __future__ import annotations
from abc import ABC, abstractmethod

class Scene(ABC):
    def __init__(self):
        self._switch_request: int | None = None

    def request_switch(self, index: int) -> None:
        self._switch_request = index

    def consume_switch_request(self) -> int | None:
        v = self._switch_request
        self._switch_request = None
        return v

    def enter_tree(self) -> None:
        pass

    def exit_tree(self) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None: ...
    @abstractmethod
    def draw(self) -> None: ...
