from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE


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
        if self._button_clicked(self.btn_easy):
            self.difficulty = "Easy"
        if self._button_clicked(self.btn_normal):
            self.difficulty = "Normal"
        if self._button_clicked(self.btn_hard):
            self.difficulty = "Hard"
        if self._button_clicked(self.btn_start):
            self._apply_difficulty()
            # Add start game effect
            self.ctx.screen_flash.flash(colors.YELLOW, 0.3, 0.4)
            self.request_switch(GAME_SCENE)
        if self._button_clicked(self.btn_exit):
            self.request_switch(EXIT_SCENE)

    def _apply_difficulty(self) -> None:
        """Apply difficulty settings to the game config."""
        if self.difficulty == "Easy":
            self.ctx.cfg.logic_tick_rate = 2  # Slower game
            self.ctx.cfg.rage_duration_ticks = 450  # Longer power-ups
            self.ctx.cfg.cherry_respawn_ticks = 200  # Slower cherry respawn
            self.ctx.cfg.ghost_chase_ticks = 90
            self.ctx.cfg.ghost_scatter_ticks = 70
            self.ctx.cfg.initial_lives = 5  # More lives
            # Higher scores for easy mode
            self.ctx.cfg.seed_score = 15
            self.ctx.cfg.large_seed_score = 75
            self.ctx.cfg.cherry_score = 750
            self.ctx.cfg.ghost_score = 300
        elif self.difficulty == "Normal":
            self.ctx.cfg.logic_tick_rate = 3
            self.ctx.cfg.rage_duration_ticks = 300
            self.ctx.cfg.cherry_respawn_ticks = 150
            self.ctx.cfg.ghost_chase_ticks = 120
            self.ctx.cfg.ghost_scatter_ticks = 40
            self.ctx.cfg.initial_lives = 3
            self.ctx.cfg.seed_score = 10
            self.ctx.cfg.large_seed_score = 50
            self.ctx.cfg.cherry_score = 500
            self.ctx.cfg.ghost_score = 200
        elif self.difficulty == "Hard":
            self.ctx.cfg.logic_tick_rate = 4  # Faster game
            self.ctx.cfg.rage_duration_ticks = 200  # Shorter power-ups
            self.ctx.cfg.cherry_respawn_ticks = 100  # Faster cherry respawn
            self.ctx.cfg.ghost_chase_ticks = 150
            self.ctx.cfg.ghost_scatter_ticks = 25
            self.ctx.cfg.initial_lives = 2  # Fewer lives
            # Lower scores for hard mode
            self.ctx.cfg.seed_score = 5
            self.ctx.cfg.large_seed_score = 25
            self.ctx.cfg.cherry_score = 250
            self.ctx.cfg.ghost_score = 100

        self.ctx.start_new_game()

    def draw(self) -> None:
        pyray.draw_text("PACMAN", 140, 90, 48, colors.YELLOW)

        # Difficulty selection
        pyray.draw_text("Select Difficulty:", 120, 140, 24, colors.WHITE)
        self._draw_button(self.btn_easy, "EASY")
        self._draw_button(self.btn_normal, "NORMAL")
        self._draw_button(self.btn_hard, "HARD")

        # Show selected difficulty
        selected_color = colors.GREEN if self.difficulty == "Easy" else \
            colors.YELLOW if self.difficulty == "Normal" else \
            colors.RED
        pyray.draw_text(f"Selected: {self.difficulty}",
                        120, 280, 20, selected_color)

        # Action buttons
        self._draw_button(self.btn_start, "START GAME")
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
