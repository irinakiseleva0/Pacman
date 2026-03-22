from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import GAME_SCENE, MENU_SCENE
from ui.ui import button_clicked, draw_button
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
        if button_clicked(self.btn_action):
            if self.ctx.last_result == "level_complete":
                # Check if there are more levels
                if self.ctx.current_level < self.TOTAL_LEVELS:
                    # Add level transition effects
                    self.ctx.screen_flash.flash(colors.GREEN, 0.4, 0.5)
                    self.ctx.screen_shake.shake(3.0, 0.4)

                    # Go to next level
                    self.ctx.next_level()
                    self.request_switch(GAME_SCENE)
                else:
                    # All levels complete - game won entirely
                    self.ctx.last_result = "game_won"
            elif self.ctx.last_result == "game_won":
                # Back to menu after winning all levels
                self.ctx.reset_run_state()
                self.request_switch(MENU_SCENE)
            else:  # "lose"
                # Back to menu after losing
                self.ctx.reset_run_state()
                self.request_switch(MENU_SCENE)

    def _summary_lines(self) -> list[str]:
        if self.ctx.last_result == "level_complete":
            if self.ctx.current_level < self.TOTAL_LEVELS:
                return [
                    "Board cleared successfully.",
                    "Carry your score into the next level.",
                    "Take a breath, the ghosts will reset.",
                ]
            return [
                "Final level cleared.",
                "One more step to close out the run.",
                "Your score is locked in.",
            ]

        if self.ctx.last_result == "game_won":
            return [
                "All levels completed.",
                "A full win has been recorded.",
                "Return to menu to start a new run.",
            ]

        return [
            "Pacman ran out of lives.",
            "Your high score has been saved.",
            "Return to menu to try again.",
        ]

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
            f"High Score: {self.ctx.high_score}", 120, 202, 24, colors.YELLOW
        )

        summary_y = 242
        for line in self._summary_lines():
            pyray.draw_text(line, 72, summary_y, 18, colors.LIGHTGRAY)
            summary_y += 24

        draw_button(self.btn_action, button_text)
