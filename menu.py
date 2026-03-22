from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE
from ui.ui import button_clicked, draw_button


class Menu(Scene):
    BTN_W = 140
    BTN_H = 50

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.difficulty = "Normal"  # Default
        self.btn_easy = None
        self.btn_normal = None
        self.btn_hard = None
        self.btn_start = None
        self.btn_exit = None

    def enter_tree(self) -> None:
        cx = self.ctx.cfg.window_width // 2
        cy = self.ctx.cfg.window_height // 2

        # Difficulty buttons
        self.btn_easy = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy - 80 - self.BTN_H,
            self.BTN_W,
            self.BTN_H,
        )
        self.btn_normal = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy - 20 - self.BTN_H,
            self.BTN_W,
            self.BTN_H,
        )
        self.btn_hard = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy + 40 - self.BTN_H,
            self.BTN_W,
            self.BTN_H,
        )

        # Action buttons
        self.btn_start = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy + 120 - self.BTN_H,
            self.BTN_W,
            self.BTN_H,
        )
        self.btn_exit = pyray.Rectangle(
            cx - self.BTN_W // 2,
            cy + 180 - self.BTN_H,
            self.BTN_W,
            self.BTN_H,
        )

    def update(self, dt: float) -> None:
        if button_clicked(self.btn_easy):
            self.difficulty = "Easy"
        if button_clicked(self.btn_normal):
            self.difficulty = "Normal"
        if button_clicked(self.btn_hard):
            self.difficulty = "Hard"
        if button_clicked(self.btn_start):
            self._apply_difficulty()
            # Add start game effect
            self.ctx.screen_flash.flash(colors.YELLOW, 0.3, 0.4)
            self.request_switch(GAME_SCENE)
        if button_clicked(self.btn_exit):
            self.request_switch(EXIT_SCENE)

    def _apply_difficulty(self) -> None:
        """Apply difficulty settings to the game config."""
        self.ctx.apply_difficulty(self.difficulty)
        self.ctx.start_new_game()

    def _difficulty_summary_lines(self) -> list[str]:
        return list(self.ctx.difficulty_summary_lines(self.difficulty))

    def draw(self) -> None:
        pyray.draw_text("PACMAN", 140, 90, 48, colors.YELLOW)

        # Difficulty selection
        pyray.draw_text("Select Difficulty:", 120, 140, 24, colors.WHITE)
        draw_button(self.btn_easy, "EASY")
        draw_button(self.btn_normal, "NORMAL")
        draw_button(self.btn_hard, "HARD")

        # Show selected difficulty
        selected_color = colors.GREEN if self.difficulty == "Easy" else \
            colors.YELLOW if self.difficulty == "Normal" else \
            colors.RED
        pyray.draw_text(f"Selected: {self.difficulty}",
                        120, 280, 20, selected_color)

        summary_y = 308
        for line in self._difficulty_summary_lines():
            pyray.draw_text(line, 100, summary_y, 18, colors.LIGHTGRAY)
            summary_y += 22

        # Action buttons
        draw_button(self.btn_start, "START GAME")
        draw_button(self.btn_exit, "EXIT")
