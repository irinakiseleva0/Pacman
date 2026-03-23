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

    def update(self, dt: float) -> None:
        # ESC or P -> resume back to game
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or pyray.is_key_pressed(pyray.KEY_P):
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        # mouse buttons
        mx, my = pyray.get_mouse_position().x, pyray.get_mouse_position().y

        # Resume button
        if button_clicked(pyray.Rectangle(154, 220, 140, 45)):
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        # Back to Menu button
        if button_clicked(pyray.Rectangle(154, 280, 140, 45)):
            self.ctx.reset_run_state()
            self.request_switch(MENU_SCENE)
            return

        # Exit button
        if button_clicked(pyray.Rectangle(154, 340, 140, 45)):
            self.request_switch(EXIT_SCENE)
            return

    def draw(self) -> None:
        # Dark overlay over game
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, 0, 448, 496),
            with_alpha(colors.BLACK, 160)
        )

        draw_text_centered("PAUSED", self.ctx.cfg.window_width // 2, 150, 40, colors.YELLOW)
        self._draw_summary()

        draw_button(pyray.Rectangle(154, 220, 140, 45), "RESUME")
        draw_button(pyray.Rectangle(154, 280, 140, 45), "MENU")
        draw_button(pyray.Rectangle(154, 340, 140, 45), "EXIT")

        draw_text_centered("ESC or P = RESUME", self.ctx.cfg.window_width // 2, 410, 16, colors.WHITE)

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
