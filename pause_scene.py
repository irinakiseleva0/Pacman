from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE, MENU_SCENE
from utils.visual_effects import with_alpha


class PauseScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def update(self, dt: float) -> None:
        # ESC or P -> resume back to game
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or pyray.is_key_pressed(pyray.KEY_P):
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        # mouse buttons
        mx, my = pyray.get_mouse_position().x, pyray.get_mouse_position().y

        # Resume button
        if self._click_in_rect(mx, my, 154, 220, 140, 45):
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        # Back to Menu button
        if self._click_in_rect(mx, my, 154, 280, 140, 45):
            self.ctx.reset_run_state()
            self.request_switch(MENU_SCENE)
            return

        # Exit button
        if self._click_in_rect(mx, my, 154, 340, 140, 45):
            self.request_switch(EXIT_SCENE)
            return

    def draw(self) -> None:
        # Dark overlay over game
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, 0, 448, 496),
            with_alpha(colors.BLACK, 160)
        )

        pyray.draw_text("PAUSED", 150, 150, 40, colors.YELLOW)

        self._draw_button(154, 220, "RESUME")
        self._draw_button(154, 280, "MENU")
        self._draw_button(154, 340, "EXIT")

        pyray.draw_text("ESC or P = RESUME", 130, 410, 16, colors.WHITE)

    def _draw_button(self, x: int, y: int, text: str):
        rect = pyray.Rectangle(x, y, 140, 45)
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)

        pyray.draw_rectangle_rec(
            rect, colors.DARKGRAY if hovered else colors.GRAY
        )
        pyray.draw_rectangle_lines_ex(rect, 2, colors.WHITE)

        tw = pyray.measure_text(text, 20)
        pyray.draw_text(
            text, x + (140 - tw) // 2, y + 12, 20, colors.WHITE
        )

    def _click_in_rect(self, mx, my, x, y, w, h) -> bool:
        rect = pyray.Rectangle(x, y, w, h)
        mouse = pyray.get_mouse_position()
        hovered = pyray.check_collision_point_rec(mouse, rect)
        return hovered and pyray.is_mouse_button_pressed(0)
