from __future__ import annotations

import core.raylib_api as pyray

from entities.cell import Cell


class EmptyCell(Cell):
    """Represents walkable empty space (floor) on the map."""

    def draw(self) -> None:
        # Empty cells don't draw anything visible
        pass
