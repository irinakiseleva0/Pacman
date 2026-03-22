from __future__ import annotations

import pyray
from raylib import colors
import scene


class PauseScene(scene.Scene):
    def __init__(self):
        super().__init__()
        self._pressed_resume = False
        self._pressed_menu = False
        self._pressed_exit = False

    def update(self, dt: float) -> None:
        # ESC -> resume
        if pyray.is_key_pressed(pyray.KEY_ESCAPE):
            self.request_pop()
            return

        # mouse buttons (простые зоны)
        mx, my = pyray.get_mouse_position().x, pyray.get_mouse_position().y

        # кнопки прямоугольниками
        if self._click_in_rect(mx, my, 154, 220, 140, 45):
            self.request_pop()           # Resume
        if self._click_in_rect(mx, my, 154, 280, 140, 45):
            self.request_switch(0)       # Back to menu
        if self._click_in_rect(mx, my, 154, 340, 140, 45):
            self.request_exit()          # Exit

    def draw(self) -> None:
        # затемнение поверх игры
        pyray.draw_rectangle_rec(pyray.Rectangle(
            0, 0, 448, 496), colors.Color(0, 0, 0, 160))

        pyray.draw_text("PAUSED", 150, 150, 40, colors.YELLOW)

        self._draw_button(154, 220, "RESUME")
        self._draw_button(154, 280, "MENU")
        self._draw_button(154, 340, "EXIT")

        pyray.draw_text("ESC = RESUME", 150, 410, 18, colors.WHITE)

    def _draw_button(self, x: int, y: int, text: str):
        rect = pyray.Rectangle(x, y, 140, 45)
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)

        pyray.draw_rectangle_rec(
            rect, colors.DARKGRAY if hovered else colors.GRAY)
        pyray.draw_rectangle_lines_ex(rect, 2, colors.WHITE)

        tw = pyray.measure_text(text, 20)
        pyray.draw_text(text, x + (140 - tw) // 2, y + 12, 20, colors.WHITE)

    def _click_in_rect(self, mx, my, x, y, w, h) -> bool:
        rect = pyray.Rectangle(x, y, w, h)
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)
        return hovered and pyray.is_mouse_button_pressed(0)
