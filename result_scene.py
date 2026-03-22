from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from utils.score_storage import save_high_score


class ResultScene(Scene):
    BTN_W = 180
    BTN_H = 50

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.btn_menu = None

    def enter_tree(self) -> None:
        # Save high score when entering result screen
        save_high_score(self.ctx.high_score)

        cx = self.ctx.cfg.window_width // 2
        cy = self.ctx.cfg.window_height // 2

        self.btn_menu = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy + 100,
            self.BTN_W,
            self.BTN_H,
        )

    def update(self, dt: float) -> None:
        if self._button_clicked(self.btn_menu):
            self.request_switch(0)

    def draw(self) -> None:
        # Draw result based on last_result
        result_text = "YOU WIN!" if self.ctx.last_result == "win" else "GAME OVER"
        result_color = colors.GREEN if self.ctx.last_result == "win" else colors.RED

        pyray.draw_text(result_text, 120, 100, 48, result_color)
        pyray.draw_text(
            f"Final Score: {self.ctx.score}", 150, 170, 24, colors.WHITE)
        pyray.draw_text(
            f"High Score: {self.ctx.high_score}", 150, 210, 24, colors.YELLOW
        )

        self._draw_button(self.btn_menu, "BACK TO MENU")

    def _button_clicked(self, rect) -> bool:
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)
        return hovered and pyray.is_mouse_button_pressed(0)

    def _draw_button(self, rect, text: str) -> None:
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)

        pyray.draw_rectangle_rec(
            rect, colors.DARKGRAY if hovered else colors.GRAY
        )
        pyray.draw_rectangle_lines_ex(rect, 2, colors.WHITE)

        tw = pyray.measure_text(text, 20)
        pyray.draw_text(
            text,
            int(rect.x + rect.width / 2 - tw / 2),
            int(rect.y + rect.height / 2 - 10),
            20,
            colors.WHITE,
        )
