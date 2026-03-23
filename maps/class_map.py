from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from core.context import GameContext
from entities.cell import Cell, Actor
from entities.empty_cell import EmptyCell
from entities.wall import Wall
from entities.door import Door
from entities.teleport import Teleport
from entities.cherry import Cherry
from entities.seeds import Seed, LargeSeed
from entities.pacman import Pacman
from entities.ghost import Ghost, Blinky, Pinky, Inky, Clyde


@dataclass(frozen=True)
class MoveResult:
    moved: bool
    blocked: bool = False
    reason: str = ""


class MapValidationError(ValueError):
    pass


class Map:
    def __init__(self, ctx: GameContext, path: str = "maps/pacman_map.txt") -> None:
        self.ctx = ctx
        self.static_layer: List[List[Cell]] = []
        self.dynamic_actors: List[Actor] = []
        self.ghost_counter = 0  # Track ghost creation order
        self.load(path)

    @property
    def width(self) -> int:
        return len(self.static_layer[0]) if self.static_layer else 0

    @property
    def height(self) -> int:
        return len(self.static_layer)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= y < self.height and 0 <= x < self.width

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        if not self.in_bounds(x, y):
            return None
        return self.static_layer[y][x]

    def add_actor(self, actor: Actor) -> None:
        self.dynamic_actors.append(actor)

    def try_move(self, actor: Actor, dx: int, dy: int) -> MoveResult:
        if dx == 0 and dy == 0:
            return MoveResult(moved=False, blocked=False, reason="idle")

        nx = actor.x + dx
        ny = actor.y + dy

        cell = self.get_cell(nx, ny)
        if cell is None:
            return MoveResult(moved=False, blocked=True, reason="out_of_bounds")

        if cell.is_blocking(actor):
            return MoveResult(moved=False, blocked=True, reason="blocked")

        actor.x = nx
        actor.y = ny

        cell.on_enter(actor)
        self._handle_actor_collisions(actor)

        return MoveResult(moved=True)

    def _handle_actor_collisions(self, actor: Actor) -> None:
        for other in self.dynamic_actors:
            if other is actor:
                continue
            if other.x == actor.x and other.y == actor.y:
                self._resolve_collision(actor, other)

    def _resolve_collision(self, a: Actor, b: Actor) -> None:
        kind_a = getattr(a, "kind", None)
        kind_b = getattr(b, "kind", None)

        if {kind_a, kind_b} != {"pacman", "ghost"}:
            return

        pacman = a if kind_a == "pacman" else b
        ghost = a if kind_a == "ghost" else b

        if getattr(pacman, "rage", False):
            # Pacman eats ghost
            score_value = self.ctx.next_ghost_combo_score()
            self.ctx.ghost_combo += 1
            combo_step = self.ctx.ghost_combo
            ghost.reset_to_spawn()
            self.ctx.score += score_value

            # Add visual effects
            self.ctx.particles.create_ghost_eat_effect(ghost.x, ghost.y)
            self.ctx.floating_text.add_score_text(
                score_value, ghost.x, ghost.y)
            self.ctx.floating_text.add_ghost_combo_text(
                combo_step, score_value, ghost.x, ghost.y)
            self.ctx.screen_shake.shake(4.0, 0.3)
        else:
            # Ghost eats Pacman
            self.ctx.reset_ghost_combo()
            pacman.kill()

    def frame(self) -> None:
        for actor in self.dynamic_actors:
            actor.frame(actor.x, actor.y)

    def process(self) -> None:
        for row in self.static_layer:
            for cell in row:
                cell.tick()

        for actor in self.dynamic_actors:
            actor.process()

    def draw(self) -> None:
        for row in self.static_layer:
            for cell in row:
                cell.draw()

        for actor in self.dynamic_actors:
            actor.draw()

    def remaining_seeds(self) -> int:
        total = 0
        for row in self.static_layer:
            for cell in row:
                if isinstance(cell, Seed) and getattr(cell, "enabled", False):
                    total += 1
        return total

    def cherry_status(self) -> tuple[bool, int] | None:
        ready_count = 0
        cooldown_timers: list[int] = []

        for row in self.static_layer:
            for cell in row:
                if isinstance(cell, Cherry):
                    if cell.enabled:
                        ready_count += 1
                    elif cell.timer > 0:
                        cooldown_timers.append(cell.timer)

        if ready_count > 0:
            return True, ready_count
        if cooldown_timers:
            return False, min(cooldown_timers)
        return None

    def item_counts(self) -> tuple[int, int, int]:
        dots = 0
        large_seeds = 0
        cherries = 0

        for row in self.static_layer:
            for cell in row:
                if isinstance(cell, Seed):
                    dots += 1
                elif isinstance(cell, LargeSeed):
                    large_seeds += 1
                elif isinstance(cell, Cherry):
                    cherries += 1

        return dots, large_seeds, cherries

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as file:
            raw_lines = [line.rstrip("\n") for line in file]

        self._validate_source_lines(path, raw_lines)
        lines = self._normalize_lines(raw_lines)

        self.static_layer.clear()
        self.dynamic_actors.clear()
        self.ctx.pacman = None

        for y, line in enumerate(lines):
            row: List[Cell] = []

            for x, symbol in enumerate(line):
                cell = self._create_cell(symbol)
                cell.frame(x, y)
                row.append(cell)

                actor = self._create_actor(symbol)
                if actor is not None:
                    actor.set_spawn(x, y)
                    self.add_actor(actor)

                    if isinstance(actor, Pacman):
                        self.ctx.pacman = actor

            self.static_layer.append(row)

        for row in self.static_layer:
            for cell in row:
                if isinstance(cell, Wall):
                    cell.set_key_from_map(self.static_layer)

    def _normalize_lines(self, lines: List[str]) -> List[str]:
        target_width = self.ctx.cfg.map_width
        normalized: List[str] = []
        adjusted = False

        for line in lines:
            if len(line) < target_width:
                adjusted = True
                normalized.append(line.ljust(target_width, "_"))
            else:
                adjusted = adjusted or len(line) > target_width
                normalized.append(line[:target_width])

        if adjusted:
            print(
                f"[Map] Normalized map rows to width {target_width}. "
                "Consider cleaning the source map file."
            )

        return normalized

    def _validate_source_lines(self, path: str, lines: List[str]) -> None:
        expected_height = self.ctx.cfg.map_height
        if len(lines) != expected_height:
            raise MapValidationError(
                f"{path}: expected {expected_height} rows, got {len(lines)}"
            )

        allowed_symbols = {"#", "d", "t", ".", "s", "c", "p", "g", "_"}
        pacman_count = 0
        ghost_count = 0

        for y, line in enumerate(lines, start=1):
            for x, symbol in enumerate(line, start=1):
                if symbol not in allowed_symbols:
                    raise MapValidationError(
                        f"{path}: unsupported symbol {symbol!r} at row {y}, column {x}"
                    )
                if symbol == "p":
                    pacman_count += 1
                elif symbol == "g":
                    ghost_count += 1

        if pacman_count != 1:
            raise MapValidationError(
                f"{path}: expected exactly 1 pacman spawn, got {pacman_count}"
            )
        if ghost_count < 1:
            raise MapValidationError(
                f"{path}: expected at least 1 ghost spawn, got {ghost_count}"
            )

    def _create_cell(self, symbol: str) -> Cell:
        if symbol == "#":
            return Wall(self.ctx)
        if symbol == "d":
            return Door(self.ctx)
        if symbol == "t":
            return Teleport(self.ctx)
        if symbol == ".":
            return Seed(self.ctx)
        if symbol == "s":
            return LargeSeed(self.ctx)
        if symbol == "c":
            return Cherry(self.ctx)

        return EmptyCell(self.ctx)

    def _create_actor(self, symbol: str) -> Optional[Actor]:
        if symbol == "p":
            return Pacman(self.ctx)
        if symbol == "g":
            # Create different ghost personalities in order
            ghost_classes = [Blinky, Pinky, Inky, Clyde]
            ghost_class = ghost_classes[self.ghost_counter % len(
                ghost_classes)]
            self.ghost_counter += 1
            return ghost_class(self.ctx)
        return None
