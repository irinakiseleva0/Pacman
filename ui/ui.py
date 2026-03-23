from __future__ import annotations

import pyray
from raylib import colors


def button_clicked(rect) -> bool:
    mouse = pyray.get_mouse_position()
    hovered = pyray.check_collision_point_rec(mouse, rect)
    return hovered and pyray.is_mouse_button_pressed(0)


def draw_button(rect, text: str, focused: bool = False) -> None:
    mouse = pyray.get_mouse_position()
    hovered = pyray.check_collision_point_rec(mouse, rect)
    is_active = hovered or focused

    fill_color = colors.DARKGRAY if is_active else colors.GRAY
    border_color = colors.YELLOW if focused else colors.WHITE

    pyray.draw_rectangle_rec(rect, fill_color)
    pyray.draw_rectangle_lines_ex(rect, 2, border_color)

    tw = pyray.measure_text(text, 20)
    tx = int(rect.x + (rect.width - tw) / 2)
    ty = int(rect.y + (rect.height - 20) / 2)
    text_color = colors.YELLOW if focused else colors.WHITE
    pyray.draw_text(text, tx, ty, 20, text_color)


def draw_text_centered(text: str, center_x: int, y: int, font_size: int, color) -> None:
    text_width = pyray.measure_text(text, font_size)
    x = int(center_x - text_width / 2)
    pyray.draw_text(text, x, y, font_size, color)
