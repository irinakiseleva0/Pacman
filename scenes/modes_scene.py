from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import CHALLENGE_SCENE, MENU_SCENE
from core.context import GAME_MODE_PRESETS
from ui import gamepad
from ui.navigation import ButtonNavigator
from ui.ui import (
    PANEL_ACCENT,
    TEXT_DIM,
    button_clicked,
    centered_rect,
    draw_arcade_background,
    draw_button,
    draw_cinematic_menu_background,
    draw_glass_card,
    draw_panel,
    draw_scene_footer,
    draw_scene_header,
    draw_text_centered,
)


class ModesScene(Scene):
    MODES = ("Arcade", "Endless", "Challenge", "Time Attack")

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(5)
        self.panel = None
        self.mode_buttons: list[pyray.Rectangle] = []
        self.btn_back = None

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        self.navigator.reset(0)
        panel_width = min(980, cfg.window_width - 100) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 40)
        panel_height = min(760, cfg.window_height - 100)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(42, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        self.mode_buttons = []
        if cfg.layout_name == "desktop":
            card_gap = 18
            card_width = int((panel_width - 96 - card_gap) / 2)
            card_y = int(panel_y + 168)
            card_height = 198
            for index in range(4):
                row = index // 2
                col = index % 2
                x = int(panel_x + 30 + col * (card_width + card_gap))
                y = int(card_y + row * (card_height + 18))
                self.mode_buttons.append(pyray.Rectangle(x, y, card_width, card_height))
        else:
            card_y = int(panel_y + 140)
            for index in range(4):
                self.mode_buttons.append(
                    pyray.Rectangle(panel_x + 20, card_y + index * 148, panel_width - 40, 126)
                )

        self.btn_back = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 92), 240, 54)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt

        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
            self.ctx.play_sfx("ui_back")
            self.request_switch(MENU_SCENE)
            return

        self.navigator.move_vertical()
        if self.ctx.cfg.layout_name == "desktop" and self.navigator.focus_index < 4:
            self.navigator.move_horizontal_within(2)

        if self.navigator.confirm_pressed():
            self._activate_focused()

        for index, button in enumerate(self.mode_buttons):
            if button_clicked(button):
                self.navigator.focus_index = index
                self._select_mode(self.MODES[index])
        if button_clicked(self.btn_back):
            self.navigator.focus_index = 4
            self.ctx.play_sfx("ui_back")
            self.request_switch(MENU_SCENE)

    def _activate_focused(self) -> None:
        if self.navigator.focus_index < 4:
            self._select_mode(self.MODES[self.navigator.focus_index])
            return
        self.ctx.play_sfx("ui_back")
        self.request_switch(MENU_SCENE)

    def _select_mode(self, mode: str) -> None:
        self.ctx.set_game_mode(mode)
        self.ctx.play_sfx("ui_confirm")
        if mode == "Challenge":
            self.request_switch(CHALLENGE_SCENE)

    def draw(self) -> None:
        cfg = self.ctx.cfg
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)

        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "RUN MODES")
        draw_scene_header(panel, "RUN MODES", "SELECT MODE", "CHOOSE YOUR RUN")

        for index, mode in enumerate(self.MODES):
            self._draw_mode_card(self.mode_buttons[index], mode, focused=self.navigator.focus_index == index)

        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == 4)
        draw_scene_footer(panel, "ENTER OR CLICK")

    def _draw_mode_card(self, rect, mode: str, *, focused: bool) -> None:
        preset = GAME_MODE_PRESETS[mode]
        active = self.ctx.game_mode == mode
        accent = preset.accent
        glow_alpha = 20 if active or focused else 10
        fill_alpha = 182 if active else 158
        draw_glass_card(rect, accent_color=accent, glow_alpha=glow_alpha, fill_alpha=fill_alpha)

        center_x = int(rect.x + rect.width / 2)
        draw_text_centered(preset.title, center_x, int(rect.y + 18), 28, colors.WHITE if active or focused else TEXT_DIM)
        draw_text_centered(preset.subtitle.upper(), center_x, int(rect.y + 58), 14, accent)

        key_line = preset.summary_lines[0] if preset.summary_lines else ""
        draw_text_centered(key_line, center_x, int(rect.y + 118), 16, colors.WHITE)

        footer = "ACTIVE MODE" if active else "PRESS ENTER"
        footer_color = colors.WHITE if active else accent
        draw_text_centered(footer, center_x, int(rect.y + rect.height - 30), 14, footer_color)
