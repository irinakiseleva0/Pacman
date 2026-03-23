from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE, MENU_SCENE
from ui.navigation import ButtonNavigator
from ui.ui import button_clicked, centered_rect, draw_button, draw_text_centered
from utils.visual_effects import with_alpha


class PauseScene(Scene):
    BTN_W = 140
    BTN_H = 45

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(3)
        self.btn_resume = None
        self.btn_menu = None
        self.btn_exit = None

    def enter_tree(self) -> None:
        self.navigator.reset(0)
        center_x = self.ctx.cfg.window_width // 2
        self.btn_resume = centered_rect(center_x, 220, self.BTN_W, self.BTN_H)
        self.btn_menu = centered_rect(center_x, 280, self.BTN_W, self.BTN_H)
        self.btn_exit = centered_rect(center_x, 340, self.BTN_W, self.BTN_H)

    def update(self, dt: float) -> None:
        # ESC or P -> resume back to game
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or pyray.is_key_pressed(pyray.KEY_P):
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        self._handle_keyboard_navigation()

        # Resume button
        if button_clicked(self.btn_resume):
            self.navigator.focus_index = 0
            self._activate_focused_action()
            return

        # Back to Menu button
        if button_clicked(self.btn_menu):
            self.navigator.focus_index = 1
            self._activate_focused_action()
            return

        # Exit button
        if button_clicked(self.btn_exit):
            self.navigator.focus_index = 2
            self._activate_focused_action()
            return

    def _handle_keyboard_navigation(self) -> None:
        self.navigator.move_vertical()

        if self.navigator.confirm_pressed():
            self._activate_focused_action()

    def _activate_focused_action(self) -> None:
        if self.navigator.focus_index == 0:
            self.ctx.should_resume_game = True
            self.request_switch(GAME_SCENE)
            return

        if self.navigator.focus_index == 1:
            self.ctx.reset_run_state()
            self.request_switch(MENU_SCENE)
            return

        self.request_switch(EXIT_SCENE)

    def draw(self) -> None:
        # Dark overlay over game
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, 0, self.ctx.cfg.window_width, self.ctx.cfg.window_height),
            with_alpha(colors.BLACK, 160)
        )

        draw_text_centered("PAUSED", self.ctx.cfg.window_width // 2, 150, 40, colors.YELLOW)
        self._draw_summary()

        draw_button(self.btn_resume, "RESUME", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_menu, "MENU", focused=self.navigator.focus_index == 1)
        draw_button(self.btn_exit, "EXIT", focused=self.navigator.focus_index == 2)

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
            f"Release: {self.ctx.effective_ghost_release_interval()} +{self.ctx.cfg.ghost_fright_release_stall_ticks}",
            f"Rage: {self.ctx.effective_rage_duration()} / {self.ctx.effective_large_seed_score()}",
            f"Cherry: {self.ctx.effective_cherry_respawn()} / {self.ctx.effective_cherry_score()}",
        ]

        if getattr(self.ctx.pacman, "rage", False):
            summary_lines.append(
                f"Combo: x{self.ctx.ghost_combo + 1} -> {self.ctx.next_ghost_combo_score()}"
            )

        item_counts = self.ctx.effective_item_counts()
        if item_counts is not None:
            dots, large_seeds, cherries = item_counts
            summary_lines.append(f"Items: .{dots} s{large_seeds} c{cherries}")

        game_map = self.ctx.game_map
        if game_map is not None:
            release_status = game_map.ghost_release_status()
            if release_status is not None:
                pending_ghosts, total_ghosts = release_status
                summary_lines.append(f"Deploying: {pending_ghosts}/{total_ghosts}")

            return_status = game_map.ghost_return_status()
            if return_status is not None:
                returning_ghosts, total_ghosts = return_status
                summary_lines.append(f"Returning: {returning_ghosts}/{total_ghosts}")

        y = 182
        for line in summary_lines:
            draw_text_centered(line, self.ctx.cfg.window_width // 2, y, 18, colors.LIGHTGRAY)
            y += 18
