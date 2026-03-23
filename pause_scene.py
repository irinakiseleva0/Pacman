from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE, MENU_SCENE
from ui.ui import button_clicked, draw_button, draw_text_centered
from utils.visual_effects import with_alpha


class PauseScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.focus_index = 0

    def enter_tree(self) -> None:
        self.focus_index = 0

    def update(self, dt: float) -> None:
        # ESC or P -> resume back to game
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or pyray.is_key_pressed(pyray.KEY_P):
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        self._handle_keyboard_navigation()

        # Resume button
        if button_clicked(pyray.Rectangle(154, 220, 140, 45)):
            self.focus_index = 0
            self._activate_focused_action()
            return

        # Back to Menu button
        if button_clicked(pyray.Rectangle(154, 280, 140, 45)):
            self.focus_index = 1
            self._activate_focused_action()
            return

        # Exit button
        if button_clicked(pyray.Rectangle(154, 340, 140, 45)):
            self.focus_index = 2
            self._activate_focused_action()
            return

    def _handle_keyboard_navigation(self) -> None:
        if pyray.is_key_pressed(pyray.KEY_UP) or pyray.is_key_pressed(pyray.KEY_W):
            self.focus_index = (self.focus_index - 1) % 3
        elif pyray.is_key_pressed(pyray.KEY_DOWN) or pyray.is_key_pressed(pyray.KEY_S):
            self.focus_index = (self.focus_index + 1) % 3

        if (
            pyray.is_key_pressed(pyray.KEY_ENTER)
            or pyray.is_key_pressed(pyray.KEY_KP_ENTER)
            or pyray.is_key_pressed(pyray.KEY_SPACE)
        ):
            self._activate_focused_action()

    def _activate_focused_action(self) -> None:
        if self.focus_index == 0:
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        if self.focus_index == 1:
            self.ctx.reset_run_state()
            self.request_switch(MENU_SCENE)
            return

        self.request_switch(EXIT_SCENE)

    def draw(self) -> None:
        # Dark overlay over game
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, 0, 448, 496),
            with_alpha(colors.BLACK, 160)
        )

        draw_text_centered("PAUSED", self.ctx.cfg.window_width // 2, 150, 40, colors.YELLOW)
        self._draw_summary()

        draw_button(pyray.Rectangle(154, 220, 140, 45), "RESUME", focused=self.focus_index == 0)
        draw_button(pyray.Rectangle(154, 280, 140, 45), "MENU", focused=self.focus_index == 1)
        draw_button(pyray.Rectangle(154, 340, 140, 45), "EXIT", focused=self.focus_index == 2)

        draw_text_centered("ESC or P = RESUME", self.ctx.cfg.window_width // 2, 410, 16, colors.WHITE)
        draw_text_centered("W/S or Arrows to move, Enter to confirm", self.ctx.cfg.window_width // 2, 430, 16, colors.LIGHTGRAY)

    def _draw_summary(self) -> None:
        ghost_chase_ticks, ghost_scatter_ticks = self.ctx.effective_ghost_cycle()
        summary_lines = [
            f"Score: {self.ctx.score}",
            f"Lives: {self.ctx.lives}",
            f"Level: {self.ctx.current_level}",
            f"Mode: {self.ctx.difficulty.upper()}",
            f"Ghosts: {self.ctx.ghost_mode.upper()}",
            f"Cycle: {ghost_chase_ticks}/{ghost_scatter_ticks}",
            f"Rage: {self.ctx.effective_rage_duration()}",
            f"Cherry: {self.ctx.effective_cherry_respawn()}",
        ]

        if getattr(self.ctx.pacman, "rage", False):
            summary_lines.append(
                f"Combo: x{self.ctx.ghost_combo + 1} -> {self.ctx.next_ghost_combo_score()}"
            )

        item_counts = self.ctx.effective_item_counts()
        if item_counts is not None:
            dots, large_seeds, cherries = item_counts
            summary_lines.append(f"Items: .{dots} s{large_seeds} c{cherries}")

        y = 182
        for line in summary_lines:
            draw_text_centered(line, self.ctx.cfg.window_width // 2, y, 18, colors.LIGHTGRAY)
            y += 18
