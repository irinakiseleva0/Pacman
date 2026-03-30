from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE, MODES_SCENE, OPTIONS_SCENE
from ui.layout import LAYOUT_PROFILES
from ui.navigation import ButtonNavigator
from ui.ui import LIVE_GOLD, PANEL_ACCENT, TEXT_DIM, draw_arcade_background, draw_cinematic_menu_background, draw_cinematic_title_stack, draw_panel, draw_presentation_bars, draw_scene_footer, draw_street_terminal, button_clicked, centered_rect, draw_button, draw_shadowed_text_centered, draw_text_centered


class Menu(Scene):
    FOCUS_ORDER = ("Desktop", "Mobile", "Easy", "Normal", "Hard", "Start", "Modes", "Options", "Exit")

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.difficulty = "Normal"  # Default
        self.navigator = ButtonNavigator(len(self.FOCUS_ORDER), initial_index=3)
        self.layout_name = ctx.cfg.layout_name
        self.btn_desktop = None
        self.btn_mobile = None
        self.btn_easy = None
        self.btn_normal = None
        self.btn_hard = None
        self.btn_start = None
        self.btn_modes = None
        self.btn_options = None
        self.btn_exit = None
        self.main_panel = None
        self.desktop_layout = False

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        cx = cfg.window_width // 2
        self.desktop_layout = cfg.layout_name == "desktop"
        if self.desktop_layout:
            panel_width = min(340, cfg.window_width - 140)
            panel_height = min(650, cfg.window_height - 170)
            panel_x = cfg.window_width - panel_width - 56
            panel_y = max(62, int((cfg.window_height - panel_height) / 2))
        else:
            panel_width = min(760, cfg.window_width - 220)
            panel_height = cfg.window_height - 100
            panel_x = cx - panel_width // 2
            panel_y = 48
        self.main_panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        if self.desktop_layout:
            panel_padding = 22
            btn_h = 46
            stacked_w = int(panel_width - panel_padding * 2)
            split_gap = 8
            split_w = int((stacked_w - split_gap) / 2)
            layout_y = int(panel_y + 102)
            diff_y = int(panel_y + 198)
            action_y = int(panel_y + panel_height - 212)
            self.btn_desktop = pyray.Rectangle(panel_x + panel_padding, layout_y, split_w, btn_h)
            self.btn_mobile = pyray.Rectangle(panel_x + panel_padding + split_w + split_gap, layout_y, split_w, btn_h)

            self.btn_easy = pyray.Rectangle(panel_x + panel_padding, diff_y, stacked_w, btn_h)
            self.btn_normal = pyray.Rectangle(panel_x + panel_padding, diff_y + 52, stacked_w, btn_h)
            self.btn_hard = pyray.Rectangle(panel_x + panel_padding, diff_y + 104, stacked_w, btn_h)

            self.btn_start = pyray.Rectangle(panel_x + panel_padding, action_y, stacked_w, 50)
            self.btn_modes = pyray.Rectangle(panel_x + panel_padding, action_y + 60, stacked_w, 40)
            self.btn_options = pyray.Rectangle(panel_x + panel_padding, action_y + 108, stacked_w, 40)
            self.btn_exit = pyray.Rectangle(panel_x + panel_padding, action_y + 156, stacked_w, 36)
        else:
            button_gap = 14
            btn_w = min(cfg.menu_button_width, int(panel_width * 0.42))
            btn_h = min(cfg.menu_button_height, 62)

            layout_btn_w = max(190, int(panel_width * 0.3))
            layout_gap = 24
            layout_y = int(panel_y + 165)
            self.btn_desktop = pyray.Rectangle(cx - layout_btn_w - layout_gap // 2, layout_y, layout_btn_w, btn_h)
            self.btn_mobile = pyray.Rectangle(cx + layout_gap // 2, layout_y, layout_btn_w, btn_h)

            difficulty_y = int(panel_y + 320)
            self.btn_easy = centered_rect(cx, difficulty_y, btn_w, btn_h)
            self.btn_normal = centered_rect(cx, difficulty_y + btn_h + button_gap, btn_w, btn_h)
            self.btn_hard = centered_rect(cx, difficulty_y + (btn_h + button_gap) * 2, btn_w, btn_h)

            action_gap = 14
            action_btn_w = max(200, int(panel_width * 0.32))
            actions_top = int(panel_y + panel_height - (btn_h * 4 + action_gap * 3) - 34)
            self.btn_start = centered_rect(cx, actions_top, action_btn_w, btn_h)
            self.btn_modes = centered_rect(cx, actions_top + btn_h + action_gap, action_btn_w, btn_h)
            self.btn_options = centered_rect(cx, actions_top + (btn_h + action_gap) * 2, action_btn_w, btn_h)
            self.btn_exit = centered_rect(cx, actions_top + (btn_h + action_gap) * 3, action_btn_w, btn_h)
        self.navigator.reset(3)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        self._handle_keyboard_navigation()

        if button_clicked(self.btn_desktop):
            self.navigator.focus_index = 0
            self._set_layout("desktop")
        if button_clicked(self.btn_mobile):
            self.navigator.focus_index = 1
            self._set_layout("mobile")
        if button_clicked(self.btn_easy):
            self.difficulty = "Easy"
            self.navigator.focus_index = 2
        if button_clicked(self.btn_normal):
            self.difficulty = "Normal"
            self.navigator.focus_index = 3
        if button_clicked(self.btn_hard):
            self.difficulty = "Hard"
            self.navigator.focus_index = 4
        if button_clicked(self.btn_start):
            self.navigator.focus_index = 5
            self._apply_difficulty()
            self.ctx.play_sfx("start_run")
            self.ctx.play_transition_effect(colors.YELLOW, 0.3, 0.4)
            self.request_switch(GAME_SCENE)
        if button_clicked(self.btn_modes):
            self.navigator.focus_index = 6
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(MODES_SCENE)
        if button_clicked(self.btn_options):
            self.navigator.focus_index = 7
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(OPTIONS_SCENE)
        if button_clicked(self.btn_exit):
            self.navigator.focus_index = 8
            self.ctx.play_sfx("ui_back")
            self.request_switch(EXIT_SCENE)

    def _handle_keyboard_navigation(self) -> None:
        self.navigator.move_vertical()
        if self.navigator.focus_index <= 1:
            self.navigator.move_horizontal_within(2)

        if self.navigator.focus_index <= 1:
            self.layout_name = self.FOCUS_ORDER[self.navigator.focus_index].lower()
        elif 2 <= self.navigator.focus_index <= 4:
            self.difficulty = self.FOCUS_ORDER[self.navigator.focus_index]

        if self.navigator.confirm_pressed():
            if self.navigator.focus_index <= 1:
                self._set_layout(self.layout_name)
            elif self.navigator.focus_index <= 4:
                self.difficulty = self.FOCUS_ORDER[self.navigator.focus_index]
            elif self.navigator.focus_index == 5:
                self._apply_difficulty()
                self.ctx.play_sfx("start_run")
                self.ctx.play_transition_effect(colors.YELLOW, 0.3, 0.4)
                self.request_switch(GAME_SCENE)
            elif self.navigator.focus_index == 6:
                self.ctx.play_sfx("ui_confirm")
                self.request_switch(MODES_SCENE)
            elif self.navigator.focus_index == 7:
                self.ctx.play_sfx("ui_confirm")
                self.request_switch(OPTIONS_SCENE)
            else:
                self.ctx.play_sfx("ui_back")
                self.request_switch(EXIT_SCENE)

    def _set_layout(self, layout_name: str) -> None:
        if layout_name not in LAYOUT_PROFILES:
            return

        self.layout_name = layout_name
        self.ctx.apply_layout(layout_name)
        if hasattr(pyray, "set_window_size"):
            pyray.set_window_size(self.ctx.cfg.window_width, self.ctx.cfg.window_height)
        self.enter_tree()

    def _apply_difficulty(self) -> None:
        """Apply difficulty settings to the game config."""
        self.ctx.apply_difficulty(self.difficulty)
        self.ctx.start_new_game()

    def _difficulty_summary_lines(self) -> list[str]:
        return list(self.ctx.difficulty_summary_lines(self.difficulty))

    def draw(self) -> None:
        cfg = self.ctx.cfg
        center_x = cfg.window_width // 2
        if self.desktop_layout:
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)

        if self.main_panel is None:
            self.enter_tree()
        main_panel = self.main_panel

        if self.desktop_layout:
            self._draw_desktop_menu(main_panel)
        else:
            draw_panel(main_panel)
            title_size = 44
            draw_shadowed_text_centered("PAC-MAN", center_x, int(main_panel.y + 40), title_size, colors.WHITE)
            draw_text_centered("NEON DISTRICT", center_x, int(main_panel.y + 140), 18, colors.WHITE)
            self._draw_mobile_menu(main_panel)
        draw_presentation_bars(cfg.window_width, cfg.window_height)

    def _draw_desktop_menu(self, main_panel) -> None:
        cfg = self.ctx.cfg
        draw_panel(main_panel)

        title_center_x = int(cfg.window_width * 0.24)
        title_y = int(cfg.window_height * 0.18)
        draw_cinematic_title_stack(
            title_center_x,
            title_y,
            "PAC-MAN",
            "NEON DISTRICT",
            "SYSTEM ONLINE • VER 2.047",
            self.ctx.visual_time,
            variant=self.ctx.title_variant_name(),
        )
        draw_text_centered(
            "Navigate the neon-soaked corridors of the digital underworld.",
            title_center_x,
            title_y + 174,
            16,
            TEXT_DIM,
        )

        if not self.ctx.capture_mode_enabled():
            status_card = pyray.Rectangle(int(main_panel.x), int(main_panel.y + main_panel.height + 18), int(main_panel.width), 80)
            draw_street_terminal(
                status_card,
                "PROFILE",
                self.ctx.rank_title().upper(),
                LIVE_GOLD,
                subline=f"HIGH SCORE {self.ctx.high_score}",
            )

        draw_text_centered("DISPLAY", int(main_panel.x + main_panel.width / 2), int(main_panel.y + 18), 14, TEXT_DIM)
        draw_button(self.btn_desktop, "DESKTOP", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_mobile, "MOBILE", focused=self.navigator.focus_index == 1)

        draw_text_centered("DIFFICULTY", int(main_panel.x + main_panel.width / 2), int(main_panel.y + 150), 14, TEXT_DIM)
        draw_button(self.btn_easy, "EASY", focused=self.navigator.focus_index == 2)
        draw_button(self.btn_normal, "NORMAL", focused=self.navigator.focus_index == 3)
        draw_button(self.btn_hard, "HARD", focused=self.navigator.focus_index == 4)

        draw_text_centered("PLAY", int(main_panel.x + main_panel.width / 2), int(self.btn_start.y - 28), 14, TEXT_DIM)
        draw_button(self.btn_start, "START RUN", focused=self.navigator.focus_index == 5)
        draw_button(self.btn_modes, "MODES", focused=self.navigator.focus_index == 6)
        draw_button(self.btn_options, "OPTIONS", focused=self.navigator.focus_index == 7)
        draw_button(self.btn_exit, "EXIT", focused=self.navigator.focus_index == 8)
        draw_scene_footer(main_panel)

    def _draw_mobile_menu(self, main_panel) -> None:
        cfg = self.ctx.cfg
        center_x = cfg.window_width // 2
        draw_text_centered("RUN MENU", center_x, int(main_panel.y + 18), 18, PANEL_ACCENT)
        draw_shadowed_text_centered("PAC-MAN", center_x, int(main_panel.y + 44), 42, colors.WHITE)
        draw_text_centered("NEON DISTRICT", center_x, int(main_panel.y + 92), 16, TEXT_DIM)
        draw_text_centered("LAYOUT", center_x, int(main_panel.y + 134), 20, TEXT_DIM)
        draw_button(self.btn_desktop, "DESKTOP", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_mobile, "MOBILE", focused=self.navigator.focus_index == 1)
        draw_text_centered(f"ACTIVE: {self.layout_name.upper()}", center_x, int(main_panel.y + 238), 20, TEXT_DIM)
        draw_text_centered("DIFFICULTY", center_x, int(main_panel.y + 270), 20, TEXT_DIM)
        draw_button(self.btn_easy, "EASY", focused=self.navigator.focus_index == 2)
        draw_button(self.btn_normal, "NORMAL", focused=self.navigator.focus_index == 3)
        draw_button(self.btn_hard, "HARD", focused=self.navigator.focus_index == 4)

        selected_color = colors.GREEN if self.difficulty == "Easy" else colors.YELLOW if self.difficulty == "Normal" else colors.RED
        draw_text_centered(f"Selected: {self.difficulty}", center_x, int(main_panel.y + 468), 22, selected_color)
        draw_text_centered(f"Mode: {self.ctx.mode_label()}", center_x, int(main_panel.y + 498), 20, PANEL_ACCENT)
        summary_y = int(main_panel.y + 532)
        for line in self._difficulty_summary_lines():
            draw_text_centered(line, center_x, summary_y, 18, TEXT_DIM)
            summary_y += 24
        draw_button(self.btn_start, "START GAME", focused=self.navigator.focus_index == 5)
        draw_button(self.btn_modes, "MODES", focused=self.navigator.focus_index == 6)
        draw_button(self.btn_options, "OPTIONS", focused=self.navigator.focus_index == 7)
        draw_button(self.btn_exit, "EXIT", focused=self.navigator.focus_index == 8)
        draw_scene_footer(main_panel)
