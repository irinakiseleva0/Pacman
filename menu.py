from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene


class Menu(Scene):
    BTN_W = 140
    BTN_H = 50

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.btn_start = None
        self.btn_exit = None

    def enter_tree(self) -> None:
        cx = self.ctx.cfg.window_width // 2
        cy = self.ctx.cfg.window_height // 2

        self.btn_start = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy - 10 - self.BTN_H,
            self.BTN_W,
            self.BTN_H,
        )
        self.btn_exit = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy + 10,
            self.BTN_W,
            self.BTN_H,
        )

    def update(self, dt: float) -> None:
        if self._button_clicked(self.btn_start):
            self.request_switch(1)
        if self._button_clicked(self.btn_exit):
            self.request_switch(-1)

    def draw(self) -> None:
        pyray.draw_text("PACMAN", 140, 90, 48, colors.YELLOW)
        self._draw_button(self.btn_start, "INSERT COIN")
        self._draw_button(self.btn_exit, "EXIT")

    def _button_clicked(self, rect) -> bool:
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)
        return hovered and pyray.is_mouse_button_pressed(0)

    def _draw_button(self, rect, text: str) -> None:
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)

        pyray.draw_rectangle_rec(
            rect, colors.DARKGRAY if hovered else colors.GRAY)
        pyray.draw_rectangle_lines_ex(rect, 2, colors.WHITE)

        tw = pyray.measure_text(text, 20)
        tx = int(rect.x + (rect.width - tw) / 2)
        ty = int(rect.y + (rect.height - 20) / 2)
        pyray.draw_text(text, tx, ty, 20, colors.WHITE)
