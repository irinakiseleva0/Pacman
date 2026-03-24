from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE, MENU_SCENE
from ui import gamepad
from ui.navigation import ButtonNavigator
from ui.ui import PANEL_ACCENT, TEXT_DIM, button_clicked, centered_rect, draw_arcade_background, draw_button, draw_cinematic_menu_background, draw_glass_card, draw_panel, draw_presentation_bars, draw_scene_footer, draw_scene_header, draw_text_centered
from utils.visual_effects import with_alpha


class PauseScene(Scene):
    BTN_W = 220
    BTN_H = 52

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(3)
        self.btn_resume = None
        self.btn_menu = None
        self.btn_exit = None
        self.panel = None

    def enter_tree(self) -> None:
        self.navigator.reset(0)
        cfg = self.ctx.cfg
        center_x = cfg.window_width // 2
        panel_width = min(520, cfg.window_width - 120)
        panel_height = min(760, cfg.window_height - 120)
        panel_x = center_x - panel_width // 2
        panel_y = max(48, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        button_y = int(panel_y + panel_height - 200)
        self.btn_resume = centered_rect(center_x, button_y, self.BTN_W, self.BTN_H)
        self.btn_menu = centered_rect(center_x, button_y + 70, self.BTN_W, self.BTN_H)
        self.btn_exit = centered_rect(center_x, button_y + 140, self.BTN_W, 46)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        # ESC or P -> resume back to game
        if (
            pyray.is_key_pressed(pyray.KEY_ESCAPE)
            or pyray.is_key_pressed(pyray.KEY_P)
            or gamepad.back_pressed()
            or gamepad.pause_pressed()
        ):
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
        cfg = self.ctx.cfg
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, 0, cfg.window_width, cfg.window_height),
            with_alpha(colors.BLACK, 110)
        )

        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "RUN PAUSED")
        draw_scene_header(panel, "RUN PAUSED", "PAUSED", "NEON DISTRICT HOLD", title_size=50)
        self._draw_summary()

        draw_text_centered("CONTINUE", cfg.window_width // 2, int(self.btn_resume.y - 28), 16, TEXT_DIM)
        draw_button(self.btn_resume, "RESUME RUN", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_menu, "BACK TO MENU", focused=self.navigator.focus_index == 1)
        draw_button(self.btn_exit, "EXIT", focused=self.navigator.focus_index == 2)

        draw_scene_footer(panel, "ESC OR P TO RESUME")
        draw_presentation_bars(cfg.window_width, cfg.window_height)

    def _draw_summary(self) -> None:
        if self.panel is None:
            return

        ghost_chase_ticks, ghost_scatter_ticks = self.ctx.effective_ghost_cycle()
        left_lines = [
            ("SCORE", str(self.ctx.score), colors.WHITE),
            ("LIVES", str(self.ctx.lives), colors.WHITE),
            ("LEVEL", str(self.ctx.current_level), colors.SKYBLUE),
            ("DIFFICULTY", self.ctx.difficulty.upper(), colors.YELLOW),
            ("THEME", self.ctx.theme_name().upper(), PANEL_ACCENT),
        ]
        right_lines = [
            ("GHOSTS", self.ctx.ghost_mode.upper(), colors.RED if self.ctx.ghost_mode == "chase" else colors.SKYBLUE),
            ("CYCLE", f"{ghost_chase_ticks}/{ghost_scatter_ticks}", TEXT_DIM),
            ("RELEASE", f"{self.ctx.effective_ghost_release_interval()} +{self.ctx.cfg.ghost_fright_release_stall_ticks}", TEXT_DIM),
            ("CHERRY", f"{self.ctx.effective_cherry_respawn()} / {self.ctx.effective_cherry_score()}", colors.GOLD),
        ]

        if getattr(self.ctx.pacman, "rage", False):
            right_lines.append(
                ("COMBO", f"x{self.ctx.ghost_combo + 1} -> {self.ctx.next_ghost_combo_score()}", colors.GOLD)
            )

        item_counts = self.ctx.effective_item_counts()
        if item_counts is not None:
            dots, large_seeds, cherries = item_counts
            left_lines.append(("ITEMS", f".{dots} s{large_seeds} c{cherries}", TEXT_DIM))

        game_map = self.ctx.game_map
        if game_map is not None:
            release_status = game_map.ghost_release_status()
            if release_status is not None:
                pending_ghosts, total_ghosts = release_status
                right_lines.append(("DEPLOY", f"{pending_ghosts}/{total_ghosts}", TEXT_DIM))

            return_status = game_map.ghost_return_status()
            if return_status is not None:
                returning_ghosts, total_ghosts = return_status
                right_lines.append(("RETURN", f"{returning_ghosts}/{total_ghosts}", colors.WHITE))

        panel = self.panel
        card_y = int(panel.y + 152)
        card_w = int((panel.width - 78) / 2)
        left_card = pyray.Rectangle(panel.x + 26, card_y, card_w, 238)
        right_card = pyray.Rectangle(panel.x + panel.width - 26 - card_w, card_y, card_w, 238)
        draw_glass_card(left_card, accent_color=PANEL_ACCENT, glow_alpha=16)
        draw_glass_card(right_card, accent_color=colors.MAGENTA, glow_alpha=16)

        self._draw_stat_card(left_card, "RUN", left_lines)
        self._draw_stat_card(right_card, "SYSTEM", right_lines)

    def _draw_stat_card(self, rect, title: str, lines: list[tuple[str, str, object]]) -> None:
        pyray.draw_text(title, int(rect.x + 18), int(rect.y + 14), 18, TEXT_DIM)
        y = int(rect.y + 46)
        for label, value, color in lines[:6]:
            pyray.draw_text(label, int(rect.x + 18), y, 16, TEXT_DIM)
            value_width = pyray.measure_text(value, 18)
            pyray.draw_text(value, int(rect.x + rect.width - value_width - 18), y - 1, 18, color)
            y += 28
