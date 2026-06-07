from __future__ import annotations

import math

import core.raylib_api as pyray
from core import colors

from assets.assets import Assets
from entities.cell import Actor, Cell
from utils.animated_sprite import Sprite
from utils.visual_effects import with_alpha


class BonusGate(Cell):
    TEXTURE_PATH = "sprites/walls/ghost_door_full.png"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        texture = Assets.texture(self.TEXTURE_PATH)
        self.sprite = Sprite({"gate": [texture]})
        self.sprite.set_key("gate", True)
        self.bonus_cooldown = 0

    def is_open(self) -> bool:
        return self.ctx.route_chain_active()

    def is_blocking(self, actor: Actor) -> bool:
        if getattr(actor, "kind", None) != "pacman":
            return False
        return not self.is_open()

    def on_enter(self, actor: Actor) -> None:
        if getattr(actor, "kind", None) != "pacman":
            return
        if not self.is_open() or self.bonus_cooldown > 0:
            return

        bonus = self.ctx.bonus_gate_value()
        self.ctx.score += bonus
        self.ctx.record_bonus_gate()
        self.ctx.floating_text.add_text(
            f"GATE +{bonus}",
            self.x * 16 - 18,
            self.y * 16 - 28,
            self.ctx.effect_palette()["power"],
            0.88,
            12,
        )
        self.ctx.trigger_screen_flash(self.ctx.effect_palette()["power"], 0.07, 0.06)
        self.ctx.trigger_screen_shake(2.0, 0.08)
        self.bonus_cooldown = 36

    def tick(self) -> None:
        if self.bonus_cooldown > 0:
            self.bonus_cooldown -= 1

    def draw(self) -> None:
        cfg = self.ctx.cfg
        scale = cfg.tile_size / 16
        pos = (
            cfg.board_offset_x + self.x * cfg.tile_size,
            cfg.board_offset_y + self.y * cfg.tile_size,
        )
        px = pos[0] + cfg.tile_size // 2
        py = pos[1] + cfg.tile_size // 2
        pulse = 0.5 + 0.5 * math.sin(getattr(self.ctx, "visual_time", 0.0) * 7.0 + self.x * 0.6)
        accent = self.ctx.effect_palette()["power"]
        if self.is_open():
            pyray.draw_circle(px, py, cfg.tile_size // 2 + 3 + pulse * 3, with_alpha(accent, 24))
            tint = with_alpha(colors.WHITE, 210)
        else:
            pyray.draw_circle(px, py, cfg.tile_size // 2 + 1, with_alpha(colors.RED, 14))
            tint = with_alpha(colors.LIGHTGRAY, 180)
        self.sprite.draw_specified("gate", 0, pos, scale=scale, tint=tint)
