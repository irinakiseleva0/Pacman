from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from raylib import colors

from core.context import GameContext
from entities.cell import Cell, Actor
from entities.empty_cell import EmptyCell
from entities.wall import Wall
from entities.door import Door
from entities.bonus_gate import BonusGate
from entities.teleport import Teleport
from entities.pulse_barrier import PulseBarrier
from entities.cherry import Cherry
from entities.seeds import Seed, LargeSeed
from entities.hotspot_seed import HotspotSeed
from entities.pacman import Pacman
from entities.boss_ghost import BossGhost
from entities.ghost import Ghost, Blinky, Pinky, Inky, Clyde
from ui.hud import spawn_floating_text


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
        self.boss_spawned = False
        self.total_pickups = 0
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
            if self._actors_overlap(actor, other):
                self._resolve_collision(actor, other)

    def _actors_overlap(self, a: Actor, b: Actor) -> bool:
        if isinstance(a, BossGhost):
            return a.overlaps(b)
        if isinstance(b, BossGhost):
            return b.overlaps(a)
        return a.x == b.x and a.y == b.y

    def _resolve_collision(self, a: Actor, b: Actor) -> None:
        kind_a = getattr(a, "kind", None)
        kind_b = getattr(b, "kind", None)

        if {kind_a, kind_b} != {"pacman", "ghost"}:
            return

        pacman = a if kind_a == "pacman" else b
        ghost = a if kind_a == "ghost" else b

        if isinstance(ghost, Ghost) and ghost.is_harmless():
            return

        if isinstance(ghost, BossGhost):
            self._resolve_boss_collision(pacman, ghost)
            return

        if getattr(pacman, "rage", False):
            palette = self.ctx.effect_palette()
            run = self.ctx.run
            visual = self.ctx.visual
            # Pacman eats ghost
            score_value = self.ctx.next_ghost_combo_score()
            run.ghost_combo += 1
            self.ctx.record_ghost_eaten()
            self.ctx.play_sfx("ghost_eat")
            combo_step = run.ghost_combo
            if isinstance(ghost, Ghost):
                ghost.on_eaten()
            else:
                ghost.reset_to_spawn()
            run.score += score_value
            self.ctx.run_stats.ghost_bonus_score += score_value
            rage_extension = self.ctx.map_ghost_rage_extension()
            if rage_extension > 0 and getattr(pacman, "rage", False):
                pacman.rage_timer += rage_extension

            # Add visual effects
            visual.particles.create_ghost_eat_effect(ghost.x, ghost.y, palette["ghost"])
            visual.light_bursts.add_grid_burst(ghost.x, ghost.y, palette["ghost"], 26, 1.4, 0.22)
            visual.floating_text.add_score_text(
                score_value, ghost.x, ghost.y)
            visual.floating_text.add_ghost_combo_text(
                combo_step, score_value, ghost.x, ghost.y)
            text = f"+{score_value}" if combo_step <= 1 else f"+{score_value} x{combo_step}!"
            spawn_floating_text(
                text,
                (
                    self.ctx.cfg.board_offset_x + ghost.x * self.ctx.cfg.tile_size + self.ctx.cfg.tile_size / 2,
                    self.ctx.cfg.board_offset_y + ghost.y * self.ctx.cfg.tile_size - 8,
                ),
                colors.SKYBLUE,
            )
            if rage_extension > 0:
                visual.floating_text.add_text(
                    "OVERCLOCK",
                    ghost.x * 16 - 16,
                    ghost.y * 16 - 40,
                    colors.WHITE,
                    0.9,
                    12,
                )
            flash_strength = 0.22 if combo_step <= 1 else min(0.36, 0.22 + combo_step * 0.035)
            shake_strength = 6.8 if combo_step <= 1 else min(10.5, 6.8 + combo_step * 1.15)
            self.ctx.trigger_screen_flash(palette["ghost"], flash_strength, 0.08)
            self.ctx.trigger_screen_shake(shake_strength, 0.26)
            self.ctx.trigger_freeze()
            self.ctx.trigger_action_juice(
                hitstop=0.07 if combo_step <= 1 else min(0.095, 0.07 + combo_step * 0.006),
                slow_scale=0.48 if combo_step <= 1 else 0.42,
                slow_duration=0.11 if combo_step <= 1 else 0.13,
            )
        else:
            # Ghost eats Pacman
            self.ctx.reset_ghost_combo()
            self.ctx.run.last_killer_name = getattr(type(ghost), "__name__", "Ghost")
            pacman.kill()

    def _resolve_boss_collision(self, pacman: Actor, boss: BossGhost) -> None:
        if boss.defeated:
            return

        if getattr(pacman, "rage", False):
            palette = self.ctx.effect_palette()
            score_value = boss.on_eaten(self)
            self.ctx.run.score += score_value
            self.ctx.run_stats.ghost_bonus_score += score_value
            if boss.defeated:
                self.ctx.record_ghost_eaten()
                self.ctx.visual.floating_text.add_text(
                    f"INTRUDER DOWN +{score_value}",
                    boss.x * 16 - 34,
                    boss.y * 16 - 34,
                    colors.GOLD,
                    1.35,
                    14,
                )
                self.ctx.trigger_screen_flash(colors.GOLD, 0.34, 0.18)
                self.ctx.trigger_screen_shake(9.0, 0.28)
                self.dynamic_actors[:] = [
                    actor for actor in self.dynamic_actors
                    if not (isinstance(actor, BossGhost) and actor.defeated)
                ]
            else:
                self.ctx.visual.floating_text.add_text(
                    f"BOSS HIT +{score_value}",
                    boss.x * 16 - 20,
                    boss.y * 16 - 28,
                    palette["ghost"],
                    0.9,
                    13,
                )
                self.ctx.trigger_screen_flash(palette["ghost"], 0.2, 0.08)
                self.ctx.trigger_screen_shake(6.0, 0.16)
            self.ctx.trigger_freeze(5)
            return

        self.ctx.reset_ghost_combo()
        self.ctx.run.last_killer_name = "BossGhost"
        pacman.kill()

    def frame(self) -> None:
        for actor in self.dynamic_actors:
            actor.frame(actor.x, actor.y)

    def process(self) -> None:
        for row in self.static_layer:
            for cell in row:
                cell.tick()

        for actor in list(self.dynamic_actors):
            actor.process()
        self.dynamic_actors[:] = [
            actor for actor in self.dynamic_actors
            if not (isinstance(actor, BossGhost) and actor.defeated)
        ]

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

    def remaining_pickups(self) -> int:
        total = 0
        for row in self.static_layer:
            for cell in row:
                if isinstance(cell, Seed) and getattr(cell, "enabled", False):
                    total += 1
                elif isinstance(cell, LargeSeed) and getattr(cell, "enabled", False):
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

    def ghost_release_status(self) -> tuple[int, int] | None:
        total_ghosts = 0
        pending_releases = 0

        for actor in self.dynamic_actors:
            if isinstance(actor, Ghost):
                total_ghosts += 1
                if actor.release_delay_ticks > 0:
                    pending_releases += 1

        if total_ghosts == 0 or pending_releases == 0:
            return None

        return pending_releases, total_ghosts

    def ghost_return_status(self) -> tuple[int, int] | None:
        total_ghosts = 0
        returning_ghosts = 0

        for actor in self.dynamic_actors:
            if isinstance(actor, Ghost):
                total_ghosts += 1
                if actor.returning_home:
                    returning_ghosts += 1

        if total_ghosts == 0 or returning_ghosts == 0:
            return None

        return returning_ghosts, total_ghosts

    def boss_alive(self) -> bool:
        return any(isinstance(actor, BossGhost) and not actor.defeated for actor in self.dynamic_actors)

    def stall_unreleased_ghosts(self, ticks: int) -> None:
        for actor in self.dynamic_actors:
            if isinstance(actor, Ghost):
                actor.stall_release(ticks)

    def nudge_pending_ghosts(self, ticks: int) -> None:
        for actor in self.dynamic_actors:
            if isinstance(actor, Ghost) and actor.release_delay_ticks > 0:
                actor.release_delay_ticks = max(0, actor.release_delay_ticks - max(0, ticks))

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
        self.ctx.runtime.pacman = None
        self.ghost_counter = 0
        self.boss_spawned = False

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
                        self.ctx.runtime.pacman = actor

            self.static_layer.append(row)

        for row in self.static_layer:
            for cell in row:
                if isinstance(cell, Wall):
                    cell.set_key_from_map(self.static_layer)

        dots, large_seeds, _ = self.item_counts()
        self.total_pickups = dots + large_seeds
        if self.boss_spawned:
            self._announce_boss_spawn()

    def _announce_boss_spawn(self) -> None:
        self.ctx.trigger_screen_flash(colors.RED, 0.28, 0.18)
        self.ctx.trigger_screen_shake(5.5, 0.2)
        self.ctx.visual.floating_text.add_text(
            "INTRUDER DETECTED",
            int(self.ctx.cfg.board_width * 0.42),
            28,
            colors.RED,
            1.8,
            16,
        )

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

        allowed_symbols = {"#", "d", "b", "t", "v", ".", "x", "s", "c", "p", "g", "_"}
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
        if symbol == "b":
            return BonusGate(self.ctx)
        if symbol == "t":
            return Teleport(self.ctx)
        if symbol == "v":
            return PulseBarrier(self.ctx)
        if symbol == ".":
            return Seed(self.ctx)
        if symbol == "x":
            return HotspotSeed(self.ctx)
        if symbol == "s":
            return LargeSeed(self.ctx)
        if symbol == "c":
            return Cherry(self.ctx)

        return EmptyCell(self.ctx)

    def _create_actor(self, symbol: str) -> Optional[Actor]:
        if symbol == "p":
            return Pacman(self.ctx)
        if symbol == "g":
            if self._boss_level_active() and not self.boss_spawned:
                self.boss_spawned = True
                boss = BossGhost(self.ctx)
                boss.set_release_delay(0)
                return boss
            # Create different ghost personalities in order
            ghost_classes = [Blinky, Pinky, Inky, Clyde]
            ghost_index = self.ghost_counter
            ghost_class = ghost_classes[ghost_index % len(ghost_classes)]
            self.ghost_counter += 1
            ghost = ghost_class(self.ctx)
            ghost.set_release_delay(ghost_index * self.ctx.effective_ghost_release_interval())
            return ghost
        return None

    def _boss_level_active(self) -> bool:
        return max(1, int(getattr(self.ctx, "current_level", 1))) % 5 == 0
