from __future__ import annotations

import unittest
from copy import deepcopy
from types import SimpleNamespace

from core.context import GameContext
from core.core_loop import current_core_loop_focus
from utils.profile_storage import DEFAULT_PROFILE


class _Ghost:
    kind = "ghost"

    def __init__(self, x: int, y: int, harmless: bool = False) -> None:
        self.x = x
        self.y = y
        self._harmless = harmless

    def is_harmless(self) -> bool:
        return self._harmless


class _MapStub:
    def __init__(self, *, seeds: int = 5, cherry_ready: bool = False, actors=None) -> None:
        self._seeds = seeds
        self._cherry_ready = cherry_ready
        self.dynamic_actors = actors or []

    def cherry_status(self):
        return (self._cherry_ready, 1) if self._cherry_ready else None

    def remaining_seeds(self) -> int:
        return self._seeds


class CoreLoopTests(unittest.TestCase):
    def _fresh_context(self) -> GameContext:
        ctx = GameContext()
        ctx.profile = deepcopy(DEFAULT_PROFILE)
        ctx.profile_service.save = lambda: None
        return ctx

    def test_core_loop_prioritizes_chase_when_rage_active(self) -> None:
        ctx = self._fresh_context()
        ctx.runtime.pacman = SimpleNamespace(x=5, y=5, rage=True)
        ctx.run.ghost_combo = 2

        focus = current_core_loop_focus(ctx, _MapStub())

        self.assertEqual(focus.phase, "CHASE")

    def test_core_loop_prioritizes_avoid_when_ghost_is_close(self) -> None:
        ctx = self._fresh_context()
        ctx.runtime.pacman = SimpleNamespace(x=5, y=5, rage=False)

        focus = current_core_loop_focus(ctx, _MapStub(actors=[_Ghost(6, 5)]))

        self.assertEqual(focus.phase, "AVOID")

    def test_core_loop_prioritizes_eat_when_bonus_or_end_board_is_live(self) -> None:
        ctx = self._fresh_context()
        ctx.runtime.pacman = SimpleNamespace(x=5, y=5, rage=False)

        focus = current_core_loop_focus(ctx, _MapStub(seeds=2))

        self.assertEqual(focus.phase, "EAT")
