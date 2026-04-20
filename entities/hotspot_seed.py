from __future__ import annotations

from raylib import colors

import core.raylib_api as pyray
from entities.seeds import Seed
from utils.visual_effects import with_alpha


class HotspotSeed(Seed):
    def on_enter(self, actor) -> None:
        if getattr(actor, "kind", None) != "pacman" or not self.enabled:
            return

        super().on_enter(actor)
        game_map = self.ctx.game_map
        if game_map is None:
            return

        bonus = self.ctx.hotspot_seed_bonus_value()
        self.ctx.score += bonus
        game_map.nudge_pending_ghosts(1)
        self.ctx.floating_text.add_text(
            f"HOT +{bonus}",
            self.x * 16 - 16,
            self.y * 16 - 28,
            colors.ORANGE,
            0.84,
            12,
        )
        self.ctx.trigger_screen_flash(colors.ORANGE, 0.05, 0.05)
        self.ctx.trigger_screen_shake(1.7, 0.07)

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        tile = cfg.tile_size
        px = cfg.board_offset_x + self.x * tile + tile // 2
        py = cfg.board_offset_y + self.y * tile + tile // 2
        pulse = 0.5 + 0.5 * __import__("math").sin(getattr(self.ctx, "visual_time", 0.0) * 8.4 + self.x * 0.8 + self.y * 0.3)
        pyray.draw_circle(px, py, 5 + pulse * 2, with_alpha(colors.RED, 30))
        pyray.draw_circle(px, py, 3 + pulse, with_alpha(colors.ORANGE, 150))
        pyray.draw_circle(px, py, 2, colors.YELLOW)
