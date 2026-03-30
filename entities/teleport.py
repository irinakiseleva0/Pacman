from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from entities.cell import Cell, Actor
from utils.visual_effects import with_alpha


class Teleport(Cell):
    def draw(self) -> None:
        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = cfg.board_offset_x + self.x * tile + tile // 2
        py = cfg.board_offset_y + self.y * tile + tile // 2
        time_s = getattr(self.ctx, "visual_time", 0.0)
        pulse = 0.5 + 0.5 * math.sin(time_s * 5.4 + self.x * 0.8)
        accent = self.ctx.current_map_trait().accent

        outer_alpha = 18 if self.ctx.map_has_teleport_pressure() else 10
        line_alpha = 130 if self.ctx.map_has_teleport_pressure() else 72
        pyray.draw_circle(px, py, max(8, tile // 2 + pulse * 4), with_alpha(accent, outer_alpha))
        pyray.draw_circle_lines(px, py, max(5, tile // 3 + pulse * 2), with_alpha(accent, line_alpha))
        pyray.draw_circle(px, py, 2 + pulse, with_alpha(colors.WHITE, 180))

    def on_enter(self, actor: Actor) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        if getattr(actor, "kind", None) != "pacman":
            return

        risk_ghosts = 0
        for other in game_map.dynamic_actors:
            if getattr(other, "kind", None) != "ghost":
                continue
            if getattr(other, "is_harmless", lambda: False)():
                continue
            if abs(other.x - actor.x) + abs(other.y - actor.y) <= 4:
                risk_ghosts += 1

        if actor.x == 0:
            actor.x = game_map.width - 2
        elif actor.x == game_map.width - 1:
            actor.x = 1

        self.ctx.visual.light_bursts.add_grid_burst(self.x, self.y, self.ctx.current_map_trait().accent, 20, 1.0, 0.16)
        if self.ctx.map_has_teleport_pressure() and risk_ghosts > 0:
            bonus = self.ctx.map_teleport_bonus_value() + (risk_ghosts - 1) * 40
            self.ctx.score += bonus
            self.ctx.visual.floating_text.add_text(
                f"SLIP EXIT +{bonus}",
                actor.x * 16 - 22,
                actor.y * 16 - 24,
                self.ctx.current_map_trait().accent,
                0.92,
                12,
            )
            self.ctx.trigger_screen_flash(self.ctx.current_map_trait().accent, 0.08, 0.06)
            self.ctx.trigger_screen_shake(2.2, 0.08)
            self.ctx.trigger_action_juice(slow_scale=0.86, slow_duration=0.04)
