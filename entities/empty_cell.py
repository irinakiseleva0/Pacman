from __future__ import annotations


from entities.cell import Cell


class EmptyCell(Cell):
    """Represents walkable empty space (floor) on the map."""

    def draw(self) -> None:
        # Empty cells don't draw anything visible
        pass
