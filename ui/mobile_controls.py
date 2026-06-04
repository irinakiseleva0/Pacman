from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from entities.pacman import State
from ui import pygame_primitives as pgui
from utils.visual_effects import with_alpha


def _button_rects(cfg) -> dict[str, object]:
    panel_x = cfg.hud_x
    panel_y = cfg.hud_y
    panel_w = cfg.hud_width
    panel_h = cfg.hud_height

    controls_w = min(220, max(180, panel_w // 2))
    area_x = panel_x + panel_w - controls_w + 10
    area_y = panel_y + 12
    size = min(56, max(44, cfg.tile_size * 2))
    gap = 12
    center_x = area_x + controls_w // 2
    mid_y = area_y + 58

    return {
        "up": pyray.Rectangle(center_x - size // 2, mid_y - size - gap, size, size),
        "left": pyray.Rectangle(center_x - size - gap, mid_y, size, size),
        "right": pyray.Rectangle(center_x + gap, mid_y, size, size),
        "down": pyray.Rectangle(center_x - size // 2, mid_y + size + gap, size, size),
        "pause": pyray.Rectangle(area_x + controls_w - 74, area_y, 62, 36),
        "area": pyray.Rectangle(area_x, panel_y, controls_w, panel_h),
    }


def handle_mobile_controls(ctx) -> str | None:
    if ctx.cfg.layout_name != "mobile":
        return None

    if not pyray.is_mouse_button_down(0) and not pyray.is_mouse_button_pressed(0):
        return None

    mouse = pyray.get_mouse_position()
    rects = _button_rects(ctx.cfg)

    if pyray.check_collision_point_rec(mouse, rects["pause"]):
        if pyray.is_mouse_button_pressed(0):
            return "pause"
        return None

    pacman = ctx.pacman
    if pacman is None:
        return None

    direction_map = {
        "up": State.UP,
        "left": State.LEFT,
        "right": State.RIGHT,
        "down": State.DOWN,
    }
    for key, state in direction_map.items():
        if pyray.check_collision_point_rec(mouse, rects[key]):
            pacman.queue_direction(state)
            return key

    return None


def draw_mobile_controls(ctx) -> None:
    if ctx.cfg.layout_name != "mobile":
        return

    rects = _button_rects(ctx.cfg)
    area = rects["area"]
    pgui.draw_rect(area, with_alpha(colors.BLACK, 40))
    pgui.draw_text_centered("TOUCH", int(area.x + area.width / 2), int(area.y + 6), 16, colors.LIGHTGRAY)

    mouse = pyray.get_mouse_position()
    direction_labels = {
        "up": "U",
        "left": "L",
        "right": "R",
        "down": "D",
    }

    for key, label in direction_labels.items():
        rect = rects[key]
        active = pyray.check_collision_point_rec(mouse, rect) and pyray.is_mouse_button_down(0)
        fill = colors.DARKBLUE if active else colors.DARKGRAY
        border = colors.YELLOW if active else colors.LIGHTGRAY
        pgui.draw_rect(rect, fill)
        pgui.draw_rect(rect, border, 2)
        pgui.draw_text_centered(
            label,
            int(rect.x + rect.width / 2),
            int(rect.y + rect.height / 2 - 10),
            24,
            colors.WHITE,
        )

    pause_rect = rects["pause"]
    pause_active = pyray.check_collision_point_rec(mouse, pause_rect) and pyray.is_mouse_button_down(0)
    pause_fill = colors.MAROON if pause_active else colors.DARKGRAY
    pause_border = colors.YELLOW if pause_active else colors.WHITE
    pgui.draw_rect(pause_rect, pause_fill)
    pgui.draw_rect(pause_rect, pause_border, 2)
    pgui.draw_text_centered(
        "PAUSE",
        int(pause_rect.x + pause_rect.width / 2),
        int(pause_rect.y + 8),
        14,
        colors.WHITE,
    )
