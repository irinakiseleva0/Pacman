from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from typing import Iterable


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width - 1

    @property
    def bottom(self) -> int:
        return self.y + self.height - 1

    @property
    def center(self) -> tuple[int, int]:
        return self.x + self.width // 2, self.y + self.height // 2


@dataclass
class Leaf:
    rect: Rect
    left: "Leaf | None" = None
    right: "Leaf | None" = None
    room: Rect | None = None

    def rooms(self) -> list[Rect]:
        if self.room is not None:
            return [self.room]
        result: list[Rect] = []
        if self.left is not None:
            result.extend(self.left.rooms())
        if self.right is not None:
            result.extend(self.right.rooms())
        return result


class BSPMazeGenerator:
    WALL = 1
    FLOOR = 0

    def __init__(
        self,
        width: int = 28,
        height: int = 30,
        *,
        seed: int | None = None,
        min_leaf_size: int = 5,
        min_room_size: int = 3,
    ) -> None:
        if width < min_leaf_size + 2 or height < min_leaf_size + 2:
            raise ValueError("BSP map must be large enough to contain a bordered leaf")
        if min_leaf_size < 5:
            raise ValueError("min_leaf_size must be at least 5")
        if min_room_size < 3:
            raise ValueError("min_room_size must be at least 3")

        self.seed = random.randint(0, 999999) if seed is None else int(seed)
        self.width = width
        self.height = height
        self.min_leaf_size = min_leaf_size
        self.min_room_size = min_room_size
        self.random = random.Random(self.seed)
        self.rooms: list[Rect] = []
        self.boss_room: Rect | None = None
        self.pacman_spawn: tuple[int, int] | None = None
        self.ghost_spawns: list[tuple[int, int]] = []

    def generate(self) -> list[list[int]]:
        random.seed(self.seed)
        self.random.seed(self.seed)
        grid = [[self.WALL for _x in range(self.width)] for _y in range(self.height)]
        root = Leaf(Rect(1, 1, self.width - 2, self.height - 2))

        self._split_leaf(root)
        self.rooms = []
        self.boss_room = None
        self._create_rooms(root, grid)
        self._connect_children(root, grid)
        self._create_boss_room(grid)
        self._place_spawns(grid)
        self._ensure_reachable(grid)
        return grid

    def generate_map_lines(self) -> list[str]:
        return self.to_map_lines(self.generate())

    def to_map_lines(self, grid: list[list[int]]) -> list[str]:
        self._validate_grid_shape(grid)
        pacman_spawn = self.pacman_spawn
        ghost_spawns = set(self.ghost_spawns)
        lines: list[str] = []

        for y, row in enumerate(grid):
            chars: list[str] = []
            for x, value in enumerate(row):
                pos = (x, y)
                if value == self.WALL:
                    chars.append("#")
                elif pos == pacman_spawn:
                    chars.append("p")
                elif pos in ghost_spawns:
                    chars.append("g")
                else:
                    chars.append(".")
            lines.append("".join(chars))
        return lines

    def is_fully_connected(self, grid: list[list[int]]) -> bool:
        floors = {(x, y) for y, row in enumerate(grid) for x, value in enumerate(row) if value == self.FLOOR}
        if not floors:
            return False
        return self._reachable_from(next(iter(floors)), grid) == floors

    def _split_leaf(self, leaf: Leaf) -> None:
        rect = leaf.rect
        can_split_h = rect.height >= self.min_leaf_size * 2
        can_split_v = rect.width >= self.min_leaf_size * 2
        if not can_split_h and not can_split_v:
            return

        if can_split_h and can_split_v:
            split_horizontal = self.random.choice((True, False))
        else:
            split_horizontal = can_split_h

        if split_horizontal:
            split = self.random.randint(self.min_leaf_size, rect.height - self.min_leaf_size)
            leaf.left = Leaf(Rect(rect.x, rect.y, rect.width, split))
            leaf.right = Leaf(Rect(rect.x, rect.y + split, rect.width, rect.height - split))
        else:
            split = self.random.randint(self.min_leaf_size, rect.width - self.min_leaf_size)
            leaf.left = Leaf(Rect(rect.x, rect.y, split, rect.height))
            leaf.right = Leaf(Rect(rect.x + split, rect.y, rect.width - split, rect.height))

        self._split_leaf(leaf.left)
        self._split_leaf(leaf.right)

    def _create_rooms(self, leaf: Leaf, grid: list[list[int]]) -> None:
        if leaf.left is not None and leaf.right is not None:
            self._create_rooms(leaf.left, grid)
            self._create_rooms(leaf.right, grid)
            return

        rect = leaf.rect
        room_width = self.random.randint(self.min_room_size, max(self.min_room_size, rect.width - 1))
        room_height = self.random.randint(self.min_room_size, max(self.min_room_size, rect.height - 1))
        room_x = self.random.randint(rect.x, rect.x + rect.width - room_width)
        room_y = self.random.randint(rect.y, rect.y + rect.height - room_height)
        room = Rect(room_x, room_y, room_width, room_height)
        leaf.room = room
        self.rooms.append(room)
        self._carve_room(grid, room)

    def _connect_children(self, leaf: Leaf, grid: list[list[int]]) -> None:
        if leaf.left is None or leaf.right is None:
            return

        self._connect_children(leaf.left, grid)
        self._connect_children(leaf.right, grid)
        left_room = self.random.choice(leaf.left.rooms())
        right_room = self.random.choice(leaf.right.rooms())
        self._carve_corridor(grid, left_room.center, right_room.center)

    def _carve_room(self, grid: list[list[int]], room: Rect) -> None:
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                grid[y][x] = self.FLOOR

    def _create_boss_room(self, grid: list[list[int]]) -> None:
        room_width = min(8, max(5, self.width // 3))
        room_height = min(8, max(5, self.height // 4))
        room_x = max(1, self.width // 2 - room_width // 2)
        room_y = max(1, self.height // 2 - room_height // 2)
        room = Rect(room_x, room_y, room_width, room_height)
        self.boss_room = room
        self._carve_room(grid, room)
        if self.rooms:
            nearest = min(self.rooms, key=lambda existing: self._distance(existing.center, room.center))
            self._carve_corridor(grid, nearest.center, room.center)

    def _carve_corridor(self, grid: list[list[int]], start: tuple[int, int], end: tuple[int, int]) -> None:
        x1, y1 = start
        x2, y2 = end
        if self.random.choice((True, False)):
            self._carve_h_line(grid, x1, x2, y1)
            self._carve_v_line(grid, y1, y2, x2)
        else:
            self._carve_v_line(grid, y1, y2, x1)
            self._carve_h_line(grid, x1, x2, y2)

    def _carve_h_line(self, grid: list[list[int]], x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y][x] = self.FLOOR

    def _carve_v_line(self, grid: list[list[int]], y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x] = self.FLOOR

    def _place_spawns(self, grid: list[list[int]]) -> None:
        floors = [(x, y) for y, row in enumerate(grid) for x, value in enumerate(row) if value == self.FLOOR]
        if len(floors) < 5:
            raise ValueError("Generated map does not have enough floor cells for required spawns")

        center = (self.width // 2, self.height // 2)
        ghost_candidates = sorted(floors, key=lambda pos: self._distance(pos, center))
        self.ghost_spawns = []
        for pos in ghost_candidates:
            if all(self._distance(pos, chosen) >= 2 for chosen in self.ghost_spawns):
                self.ghost_spawns.append(pos)
                if len(self.ghost_spawns) == 4:
                    break
        if len(self.ghost_spawns) < 4:
            self.ghost_spawns = ghost_candidates[:4]

        ghost_set = set(self.ghost_spawns)
        self.pacman_spawn = max(
            (pos for pos in floors if pos not in ghost_set),
            key=lambda pos: min(self._distance(pos, ghost) for ghost in self.ghost_spawns),
        )

    def _ensure_reachable(self, grid: list[list[int]]) -> None:
        if self.pacman_spawn is None:
            raise ValueError("Pac-Man spawn was not placed")
        if len(self.ghost_spawns) != 4:
            raise ValueError("Expected exactly 4 ghost spawns")
        if not self.is_fully_connected(grid):
            raise ValueError("Generated BSP map is not fully connected")

        reachable = self._reachable_from(self.pacman_spawn, grid)
        for spawn in self.ghost_spawns:
            if spawn not in reachable:
                raise ValueError(f"Ghost spawn {spawn} is not reachable from Pac-Man")

    def _reachable_from(self, start: tuple[int, int], grid: list[list[int]]) -> set[tuple[int, int]]:
        if grid[start[1]][start[0]] != self.FLOOR:
            return set()

        seen = {start}
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            for nx, ny in self._neighbors(x, y):
                if (nx, ny) in seen or grid[ny][nx] != self.FLOOR:
                    continue
                seen.add((nx, ny))
                queue.append((nx, ny))
        return seen

    def _neighbors(self, x: int, y: int) -> Iterable[tuple[int, int]]:
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < self.width and 0 <= ny < self.height:
                yield nx, ny

    def _validate_grid_shape(self, grid: list[list[int]]) -> None:
        if len(grid) != self.height or any(len(row) != self.width for row in grid):
            raise ValueError(f"Expected grid shape {self.width}x{self.height}")

    def _distance(self, a: tuple[int, int], b: tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
