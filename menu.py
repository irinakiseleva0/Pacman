from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import EXIT_SCENE, GAME_SCENE
from ui.layout import LAYOUT_PROFILES
from ui.navigation import ButtonNavigator
from ui.ui import button_clicked, centered_rect, draw_button, draw_text_centered


class Menu(Scene):
    FOCUS_ORDER = ("Desktop", "Mobile", "Easy", "Normal", "Hard", "Start", "Exit")

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
        self.btn_exit = None

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        cx = self.ctx.cfg.window_width // 2
        top_y = 150
        button_gap = 16
        btn_w = cfg.menu_button_width
        btn_h = cfg.menu_button_height

        layout_y = 108
        layout_gap = 20
        layout_btn_w = max(150, btn_w - 40)
        self.btn_desktop = pyray.Rectangle(cx - layout_btn_w - layout_gap // 2, layout_y, layout_btn_w, btn_h)
        self.btn_mobile = pyray.Rectangle(cx + layout_gap // 2, layout_y, layout_btn_w, btn_h)

        difficulty_y = layout_y + btn_h + 54
        self.btn_easy = centered_rect(cx, difficulty_y, btn_w, btn_h)
        self.btn_normal = centered_rect(cx, difficulty_y + btn_h + button_gap, btn_w, btn_h)
        self.btn_hard = centered_rect(cx, difficulty_y + (btn_h + button_gap) * 2, btn_w, btn_h)

        action_start_y = difficulty_y + (btn_h + button_gap) * 3 + 92
        self.btn_start = centered_rect(cx, action_start_y, btn_w, btn_h)
        self.btn_exit = centered_rect(cx, action_start_y + btn_h + button_gap, btn_w, btn_h)
        self.navigator.reset(3)

    def update(self, dt: float) -> None:
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
            self.ctx.play_transition_effect(colors.YELLOW, 0.3, 0.4)
            self.request_switch(GAME_SCENE)
        if button_clicked(self.btn_exit):
            self.navigator.focus_index = 6
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
                self.ctx.play_transition_effect(colors.YELLOW, 0.3, 0.4)
                self.request_switch(GAME_SCENE)
            else:
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
        center_x = self.ctx.cfg.window_width // 2
        draw_text_centered("PACMAN", center_x, 56, cfg.menu_title_size, colors.YELLOW)

        draw_text_centered("Select Layout", center_x, 76, cfg.menu_heading_size, colors.WHITE)
        draw_button(self.btn_desktop, "DESKTOP", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_mobile, "MOBILE", focused=self.navigator.focus_index == 1)
        active_layout_text = f"Active layout: {self.layout_name.upper()}"
        draw_text_centered(active_layout_text, center_x, 174, cfg.menu_body_size, colors.SKYBLUE)

        # Difficulty selection
        draw_text_centered("Select Difficulty", center_x, 204, cfg.menu_heading_size, colors.WHITE)
        draw_button(self.btn_easy, "EASY", focused=self.navigator.focus_index == 2)
        draw_button(self.btn_normal, "NORMAL", focused=self.navigator.focus_index == 3)
        draw_button(self.btn_hard, "HARD", focused=self.navigator.focus_index == 4)

        # Show selected difficulty
        selected_color = colors.GREEN if self.difficulty == "Easy" else \
            colors.YELLOW if self.difficulty == "Normal" else \
            colors.RED
        draw_text_centered(
            f"Selected: {self.difficulty}",
            center_x,
            422,
            cfg.menu_body_size + 2,
            selected_color,
        )

        summary_y = 454
        for line in self._difficulty_summary_lines():
            draw_text_centered(line, center_x, summary_y, cfg.menu_body_size, colors.LIGHTGRAY)
            summary_y += 24

        # Action buttons
        draw_button(self.btn_start, "START GAME", focused=self.navigator.focus_index == 5)
        draw_button(self.btn_exit, "EXIT", focused=self.navigator.focus_index == 6)
        draw_text_centered(
            "W/S or Arrows to move, Enter to confirm",
            center_x,
            self.ctx.cfg.window_height - 36,
            cfg.menu_footer_size,
            colors.LIGHTGRAY,
        )
