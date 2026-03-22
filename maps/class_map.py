from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from core.context import GameContext
from cell import Cell, Actor

@dataclass(frozen=True)
class MoveResult:
    moved: bool
    blocked: bool = False
    reason: str = ""

class Map:
    def __init__(self, ctx: GameContext, path: str = "maps/pacman_map.txt"):
        self.ctx = ctx
        self.s_layer: List[List[Cell]] = []
        self.dynamic: List[Actor] = []
        self.ctx.game_map = self
        self.load(path)

    @property
    def width(self) -> int:
        return len(self.s_layer[0]) if self.s_layer else 0

    @property
    def height(self) -> int:
        return len(self.s_layer)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= y < self.height and 0 <= x < self.width

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        if not self.in_bounds(x, y):
            return None
        return self.s_layer[y][x]

    def try_move(self, actor: Actor, dx: int, dy: int) -> MoveResult:
        if dx == 0 and dy == 0:
            return MoveResult(False, False, "idle")

        nx, ny = actor.x + dx, actor.y + dy

        # тут можно сделать wrap по краям, если надо:
        # nx %= self.width; ny %= self.height

        cell = self.get_cell(nx, ny)
        if cell is None:
            return MoveResult(False, True, "out_of_bounds")

        if cell.is_blocking(actor):
            return MoveResult(False, True, "blocked")

        # move
        actor.x, actor.y = nx, ny

        # событие входа
        cell.on_enter(actor)

        return MoveResult(True)

    def draw(self) -> None:
        for row in self.s_layer:
            for c in row:
                c.draw()
        for a in self.dynamic:
            a.draw()  # у актера есть draw

    # tick/frame ты можешь оставить как раньше, но движения теперь через try_move
