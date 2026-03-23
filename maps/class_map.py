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
            ghost.reset_to_spawn()
            self.ctx.score += self.ctx.cfg.ghost_score

            # Add visual effects
            self.ctx.particles.create_ghost_eat_effect(ghost.x, ghost.y)
            self.ctx.floating_text.add_score_text(
                self.ctx.cfg.ghost_score, ghost.x, ghost.y)
            self.ctx.screen_shake.shake(4.0, 0.3)
        else:
            # Ghost eats Pacman
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

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as file:
            lines = [line.rstrip("\n") for line in file]

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
