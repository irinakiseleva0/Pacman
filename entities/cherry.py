from __future__ import annotations

import math

import core.raylib_api as pyray
from core import colors

from assets.assets import Assets
from entities.cell import Actor, Cell
from utils.animated_sprite import Sprite
from utils.visual_effects import with_alpha


class Cherry(Cell):
    TEX = "sprites/consumables/cherry.png"

    def __init__(self, ctx):
        super().__init__(ctx)
        self.enabled = True
        self.timer = 0
        self.sprite = Sprite({"cherry": [Assets.texture(self.TEX)]})
        self.sprite.set_key("cherry", True)

    def on_enter(self, actor: Actor) -> None:
        if not self.enabled:
            return
        if getattr(actor, "kind", None) != "pacman":
            return
        palette = self.ctx.effect_palette()

        score_value = self.ctx.effective_cherry_score()
        self.enabled = False
        self.ctx.score += score_value
        self.ctx.record_cherry_eaten()
        self.ctx.play_sfx("cherry")
        self.timer = self.ctx.effective_cherry_respawn()
        market_bonus = self.ctx.map_cherry_bonus_value()
        market_window_bonus = self.ctx.consume_market_window_bonus()
        if market_bonus > 0:
            self.ctx.score += market_bonus
            self.ctx.run_stats.cherry_bonus_score += market_bonus
        if market_window_bonus > 0:
            self.ctx.score += market_window_bonus
            self.ctx.run_stats.cherry_bonus_score += market_window_bonus

        self.ctx.particles.create_cherry_eat_effect(self.x, self.y, palette["cherry"])
        self.ctx.floating_text.add_score_text(
            score_value, self.x, self.y
        )
        if market_bonus > 0:
            self.ctx.floating_text.add_text(
                f"MARKET +{market_bonus}",
                self.x * 16 - 22,
                self.y * 16 - 28,
                palette["respawn"][0],
                1.0,
                12,
            )
            self.ctx.trigger_screen_flash(palette["respawn"][0], 0.06, 0.08)
        if market_window_bonus > 0:
            self.ctx.floating_text.add_text(
                f"JACKPOT +{market_window_bonus}",
                self.x * 16 - 26,
                self.y * 16 - 42,
                palette["cherry"][1],
                1.05,
                12,
            )
            self.ctx.trigger_screen_flash(palette["cherry"][1], 0.09, 0.09)
        self.ctx.trigger_screen_shake(5.0, 0.35)

    def tick(self) -> None:
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                palette = self.ctx.effect_palette()
                self.enabled = True
                self.ctx.particles.create_cherry_respawn_effect(self.x, self.y, palette["respawn"])
                self.ctx.floating_text.add_text(
                    "CHERRY",
                    self.x * 16 - 4,
                    self.y * 16 - 12,
                    palette["respawn"][0],
                    0.9,
                    12,
                )

    def draw(self) -> None:
        if not self.enabled:
            return

        cfg = self.ctx.cfg
        scale = cfg.tile_size / 16
        base_x = cfg.board_offset_x + self.x * cfg.tile_size
        base_y = cfg.board_offset_y + self.y * cfg.tile_size
        px = base_x + cfg.tile_size // 2
        py = base_y + cfg.tile_size // 2
        pulse = 0.5 + 0.5 * math.sin(getattr(self.ctx, "visual_time", 0.0) * 5.5 + self.x * 0.6)
        pyray.draw_circle(px, py, cfg.tile_size // 2 + 4 + pulse * 3, with_alpha(colors.RED, 14))
        pyray.draw_circle(px, py, cfg.tile_size // 2 - 1 + pulse * 4, with_alpha(colors.RED, 28))
        self.sprite.draw_specified("cherry", 0, (base_x, base_y), scale=scale)
