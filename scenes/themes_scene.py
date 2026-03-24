from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.game_data import THEME_PRESETS
from core.scene import Scene
from core.scene_ids import OPTIONS_SCENE
from ui import gamepad
from ui.navigation import ButtonNavigator
from ui.ui import PANEL_ACCENT, TEXT_DIM, button_clicked, centered_rect, draw_arcade_background, draw_button, draw_cinematic_menu_background, draw_glass_card, draw_panel, draw_scene_footer, draw_scene_header, draw_text_centered


class ThemesScene(Scene):
    THEMES = tuple(THEME_PRESETS.keys())

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(len(self.THEMES) + 1)
        self.panel = None
        self.theme_buttons: list[pyray.Rectangle] = []
        self.btn_back = None

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        self.navigator.reset(0)
        panel_width = min(980, cfg.window_width - 100) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 36)
        panel_height = min(760, cfg.window_height - 100)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(42, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)
        self.theme_buttons = []
        start_y = int(panel_y + 150)
        for index in range(len(self.THEMES)):
            self.theme_buttons.append(pyray.Rectangle(panel_x + 28, start_y + index * 112, panel_width - 56, 92))
        self.btn_back = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 92), 240, 54)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
            self.ctx.play_sfx("ui_back")
            self.request_switch(OPTIONS_SCENE)
            return
        self.navigator.move_vertical()
        if self.navigator.confirm_pressed():
            self._activate_focused()
        for index, rect in enumerate(self.theme_buttons):
            if button_clicked(rect):
                self.navigator.focus_index = index
                self._select_theme(self.THEMES[index])
        if button_clicked(self.btn_back):
            self.navigator.focus_index = len(self.THEMES)
            self.ctx.play_sfx("ui_back")
            self.request_switch(OPTIONS_SCENE)

    def _activate_focused(self) -> None:
        if self.navigator.focus_index < len(self.THEMES):
            self._select_theme(self.THEMES[self.navigator.focus_index])
            return
        self.ctx.play_sfx("ui_back")
        self.request_switch(OPTIONS_SCENE)

    def _select_theme(self, theme_name: str) -> None:
        if not self.ctx.theme_unlocked(theme_name):
            self.ctx.play_sfx("ui_back")
            return
        self.ctx.set_theme_name(theme_name)
        self.ctx.play_sfx("ui_confirm")

    def draw(self) -> None:
        cfg = self.ctx.cfg
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "VISUAL THEMES")
        draw_scene_header(panel, "VISUAL THEMES", "THEMES", "VISUAL PACKS")
        self._draw_goal_preview(panel)
        for index, theme_name in enumerate(self.THEMES):
            self._draw_theme_card(self.theme_buttons[index], theme_name, focused=self.navigator.focus_index == index)
        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == len(self.THEMES))
        draw_scene_footer(panel)

    def _draw_goal_preview(self, panel) -> None:
        preview = pyray.Rectangle(panel.x + 28, panel.y + 86, panel.width - 56, 52)
        draw_glass_card(preview, accent_color=PANEL_ACCENT, glow_alpha=8, fill_alpha=132)
        center_x = int(preview.x + preview.width / 2)
        lines = self.ctx.next_unlock_spotlight_lines()
        draw_text_centered("NEXT UNLOCK", center_x, int(preview.y + 8), 13, TEXT_DIM)
        draw_text_centered(lines[0].upper(), center_x, int(preview.y + 26), 14, colors.WHITE)

    def _draw_theme_card(self, rect, theme_name: str, *, focused: bool) -> None:
        preset = THEME_PRESETS[theme_name]
        unlocked = self.ctx.theme_unlocked(theme_name)
        active = self.ctx.theme_name() == theme_name
        accent = PANEL_ACCENT if unlocked else colors.GRAY
        draw_glass_card(rect, accent_color=accent, glow_alpha=16 if focused or active else 10, fill_alpha=176 if active else 150)
        center_x = int(rect.x + rect.width / 2)
        draw_text_centered(preset.title, center_x, int(rect.y + 14), 24, colors.WHITE if unlocked else TEXT_DIM)
        draw_text_centered((preset.subtitle if unlocked else preset.unlock_text).upper(), center_x, int(rect.y + 42), 14, accent)
        footer = "EQUIPPED" if active else "AVAILABLE" if unlocked else "LOCKED"
        draw_text_centered(footer, center_x, int(rect.y + 64), 14, colors.WHITE if active else accent)
