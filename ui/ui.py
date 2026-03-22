from __future__ import annotations

import pyray
from raylib import colors


def button_clicked(rect) -> bool:
    mouse = pyray.get_mouse_position()
    hovered = pyray.check_collision_point_rec(mouse, rect)
    return hovered and pyray.is_mouse_button_pressed(0)


def draw_button(rect, text: str) -> None:
    mouse = pyray.get_mouse_position()
    hovered = pyray.check_collision_point_rec(mouse, rect)

    pyray.draw_rectangle_rec(rect, colors.DARKGRAY if hovered else colors.GRAY)
    pyray.draw_rectangle_lines_ex(rect, 2, colors.WHITE)

    tw = pyray.measure_text(text, 20)
    tx = int(rect.x + (rect.width - tw) / 2)
    ty = int(rect.y + (rect.height - 20) / 2)
    pyray.draw_text(text, tx, ty, 20, colors.WHITE)
