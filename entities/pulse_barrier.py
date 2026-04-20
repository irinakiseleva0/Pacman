from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from entities.cell import Actor, Cell
from utils.visual_effects import with_alpha


class PulseBarrier(Cell):
    def is_open(self) -> bool:
        timer = self.ctx.run.ghost_mode_timer
        cycle = self.ctx.pulse_barrier_cycle_ticks()
        closed_ticks = self.ctx.pulse_barrier_closed_ticks()
        if cycle <= 0 or closed_ticks <= 0:
            return True
        return timer % cycle >= closed_ticks

    def is_blocking(self, actor: Actor) -> bool:
        if getattr(actor, "kind", None) != "pacman":
            return False
        return not self.is_open()

    def draw(self) -> None:
        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = cfg.board_offset_x + self.x * tile + tile // 2
        py = cfg.board_offset_y + self.y * tile + tile // 2
        pulse = 0.5 + 0.5 * math.sin(getattr(self.ctx, "visual_time", 0.0) * 9.0 + self.x * 0.9)
        accent = self.ctx.current_map_trait().accent

        if self.is_open():
            pyray.draw_circle(px, py, max(5, tile // 3 + pulse * 2), with_alpha(accent, 16))
            pyray.draw_circle_lines(px, py, max(4, tile // 4), with_alpha(colors.WHITE, 90))
        else:
            pyray.draw_rectangle_rec(
                pyray.Rectangle(px - tile // 2 + 2, py - 3, tile - 4, 6),
                with_alpha(accent, 120),
            )
            pyray.draw_rectangle_rec(
                pyray.Rectangle(px - tile // 2 + 4, py - 1, tile - 8, 2),
                with_alpha(colors.WHITE, 130),
            )
