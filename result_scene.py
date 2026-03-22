from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from utils.score_storage import save_high_score


class ResultScene(Scene):
    BTN_W = 180
    BTN_H = 50
    TOTAL_LEVELS = 3

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.btn_action = None

    def enter_tree(self) -> None:
        # Save high score when entering result screen
        save_high_score(self.ctx.high_score)

        cx = self.ctx.cfg.window_width // 2
        cy = self.ctx.cfg.window_height // 2

        self.btn_action = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy + 100,
            self.BTN_W,
            self.BTN_H,
        )

    def update(self, dt: float) -> None:
        if self._button_clicked(self.btn_action):
            if self.ctx.last_result == "level_complete":
                # Check if there are more levels
                if self.ctx.current_level < self.TOTAL_LEVELS:
                    # Add level transition effects
                    self.ctx.screen_flash.flash(colors.GREEN, 0.4, 0.5)
                    self.ctx.screen_shake.shake(3.0, 0.4)

                    # Go to next level
                    self.ctx.next_level()
                    self.request_switch(1)  # Back to game
                else:
                    # All levels complete - game won entirely
                    self.ctx.last_result = "game_won"
            elif self.ctx.last_result == "game_won":
                # Back to menu after winning all levels
                self.ctx.reset_run_state()
                self.request_switch(0)
            else:  # "lose"
                # Back to menu after losing
                self.ctx.reset_run_state()
                self.request_switch(0)

    def draw(self) -> None:
        if self.ctx.last_result == "level_complete":
            result_text = f"LEVEL {self.ctx.current_level} COMPLETE!"
            result_color = colors.GREEN
            button_text = "NEXT LEVEL" if self.ctx.current_level < self.TOTAL_LEVELS else "FINISH GAME"
        elif self.ctx.last_result == "game_won":
            result_text = "YOU WON THE GAME!"
            result_color = colors.GOLD
            button_text = "BACK TO MENU"
        else:  # "lose"
            result_text = "GAME OVER"
            result_color = colors.RED
            button_text = "BACK TO MENU"

        pyray.draw_text(result_text, 60, 100, 48, result_color)

        if self.ctx.last_result == "level_complete":
            pyray.draw_text(
                f"Current Score: {self.ctx.score}", 120, 170, 24, colors.WHITE)
        else:
            pyray.draw_text(
                f"Final Score: {self.ctx.score}", 120, 170, 24, colors.WHITE)

        pyray.draw_text(
            f"High Score: {self.ctx.high_score}", 120, 210, 24, colors.YELLOW
        )

        self._draw_button(self.btn_action, button_text)

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
