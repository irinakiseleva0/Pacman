from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import CAREER_SCENE, MENU_SCENE, THEMES_SCENE
from ui.navigation import ButtonNavigator
from ui.ui import PANEL_ACCENT, TEXT_DIM, button_clicked, centered_rect, draw_arcade_background, draw_button, draw_cinematic_menu_background, draw_glass_card, draw_panel, draw_scene_footer, draw_scene_header, draw_text_centered


class OptionsScene(Scene):
    FOCUS_ORDER = ("Fx", "Flash", "Shake", "Music", "Sfx", "Tutorial", "Themes", "Career", "Back")

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(len(self.FOCUS_ORDER))
        self.panel = None
        self.btn_fx = None
        self.btn_flash = None
        self.btn_shake = None
        self.btn_music = None
        self.btn_sfx = None
        self.btn_tutorial = None
        self.btn_themes = None
        self.btn_career = None
        self.btn_back = None

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        self.navigator.reset(0)
        panel_width = min(980, cfg.window_width - 120) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 40)
        panel_height = min(820, cfg.window_height - 120)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(42, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        settings_x = panel_x + panel_width - 300 if cfg.layout_name == "desktop" else panel_x + 26
        settings_w = 250 if cfg.layout_name == "desktop" else panel_width - 52
        start_y = panel_y + 138
        self.btn_fx = pyray.Rectangle(settings_x, start_y, settings_w, 54)
        self.btn_flash = pyray.Rectangle(settings_x, start_y + 76, settings_w, 54)
        self.btn_shake = pyray.Rectangle(settings_x, start_y + 152, settings_w, 54)
        self.btn_music = pyray.Rectangle(settings_x, start_y + 228, settings_w, 54)
        self.btn_sfx = pyray.Rectangle(settings_x, start_y + 304, settings_w, 54)
        self.btn_tutorial = pyray.Rectangle(settings_x, start_y + 380, settings_w, 54)
        self.btn_themes = pyray.Rectangle(settings_x, start_y + 456, settings_w, 48)
        self.btn_career = pyray.Rectangle(settings_x, start_y + 516, settings_w, 48)
        self.btn_back = centered_rect(int(settings_x + settings_w / 2), int(panel_y + panel_height - 92), settings_w, 54)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt

        if pyray.is_key_pressed(pyray.KEY_ESCAPE):
            self.ctx.play_sfx("ui_back")
            self.request_switch(MENU_SCENE)
            return

        self.navigator.move_vertical()
        if self.navigator.confirm_pressed():
            self._activate_focused()

        if button_clicked(self.btn_fx):
            self.navigator.focus_index = 0
            self._cycle_fx()
        if button_clicked(self.btn_flash):
            self.navigator.focus_index = 1
            self.ctx.set_screen_flash_enabled(not self.ctx.screen_flash_enabled())
        if button_clicked(self.btn_shake):
            self.navigator.focus_index = 2
            self.ctx.set_screen_shake_enabled(not self.ctx.screen_shake_enabled())
        if button_clicked(self.btn_music):
            self.navigator.focus_index = 3
            self.ctx.set_music_enabled(not self.ctx.music_enabled())
        if button_clicked(self.btn_sfx):
            self.navigator.focus_index = 4
            self.ctx.set_sfx_enabled(not self.ctx.sfx_enabled())
        if button_clicked(self.btn_tutorial):
            self.navigator.focus_index = 5
            self.ctx.set_tutorial_enabled(not self.ctx.tutorial_enabled())
        if button_clicked(self.btn_themes):
            self.navigator.focus_index = 6
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(THEMES_SCENE)
        if button_clicked(self.btn_career):
            self.navigator.focus_index = 7
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(CAREER_SCENE)
        if button_clicked(self.btn_back):
            self.navigator.focus_index = 8
            self.ctx.play_sfx("ui_back")
            self.request_switch(MENU_SCENE)

    def _activate_focused(self) -> None:
        if self.navigator.focus_index == 0:
            self._cycle_fx()
        elif self.navigator.focus_index == 1:
            self.ctx.set_screen_flash_enabled(not self.ctx.screen_flash_enabled())
            self.ctx.play_sfx("ui_confirm")
        elif self.navigator.focus_index == 2:
            self.ctx.set_screen_shake_enabled(not self.ctx.screen_shake_enabled())
            self.ctx.play_sfx("ui_confirm")
        elif self.navigator.focus_index == 3:
            self.ctx.set_music_enabled(not self.ctx.music_enabled())
            self.ctx.play_sfx("ui_confirm")
        elif self.navigator.focus_index == 4:
            self.ctx.set_sfx_enabled(not self.ctx.sfx_enabled())
            self.ctx.play_sfx("ui_confirm")
        elif self.navigator.focus_index == 5:
            self.ctx.set_tutorial_enabled(not self.ctx.tutorial_enabled())
            self.ctx.play_sfx("ui_confirm")
        elif self.navigator.focus_index == 6:
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(THEMES_SCENE)
        elif self.navigator.focus_index == 7:
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(CAREER_SCENE)
        else:
            self.ctx.play_sfx("ui_back")
            self.request_switch(MENU_SCENE)

    def _cycle_fx(self) -> None:
        values = ["Low", "Medium", "High"]
        current = self.ctx.fx_intensity()
        index = values.index(current) if current in values else 2
        self.ctx.set_fx_intensity(values[(index + 1) % len(values)])
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
        draw_panel(panel, "DISTRICT CONTROL")
        draw_scene_header(panel, "DISTRICT CONTROL", "OPTIONS", "SYSTEM, CAREER, THEMES", title_size=44)

        if cfg.layout_name == "desktop":
            self._draw_desktop_content(panel)
        else:
            self._draw_mobile_content(panel)

    def _draw_desktop_content(self, panel) -> None:
        left_x = panel.x + 30
        left_w = panel.width - 390

        stats_card = pyray.Rectangle(left_x, panel.y + 132, left_w, 146)
        milestones_card = pyray.Rectangle(left_x, panel.y + 296, left_w, 260)
        settings_card = pyray.Rectangle(panel.x + panel.width - 330, panel.y + 132, 280, 572)

        draw_glass_card(stats_card, accent_color=PANEL_ACCENT, glow_alpha=14)
        draw_glass_card(milestones_card, accent_color=colors.MAGENTA, glow_alpha=12)
        draw_glass_card(settings_card, accent_color=colors.WHITE, glow_alpha=10)

        center_x = int(stats_card.x + stats_card.width / 2)
        draw_text_centered(self.ctx.rank_title(), center_x, int(stats_card.y + 18), 26, colors.WHITE)
        summary_y = int(stats_card.y + 56)
        for line in self.ctx.profile_summary_lines():
            draw_text_centered(line, center_x, summary_y, 18, TEXT_DIM)
            summary_y += 28

        draw_text_centered("MILESTONES", int(milestones_card.x + milestones_card.width / 2), int(milestones_card.y + 18), 18, TEXT_DIM)
        milestone_y = int(milestones_card.y + 56)
        for title, detail in self.ctx.unlocked_milestones()[-6:]:
            pyray.draw_text(title, int(milestones_card.x + 24), milestone_y, 18, colors.WHITE)
            pyray.draw_text(detail, int(milestones_card.x + 24), milestone_y + 22, 14, TEXT_DIM)
            milestone_y += 42

        draw_text_centered("SETTINGS", int(settings_card.x + settings_card.width / 2), int(settings_card.y + 18), 18, TEXT_DIM)
        draw_button(self.btn_fx, f"FX {self.ctx.fx_intensity().upper()}", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_flash, f"FLASH {'ON' if self.ctx.screen_flash_enabled() else 'OFF'}", focused=self.navigator.focus_index == 1)
        draw_button(self.btn_shake, f"SHAKE {'ON' if self.ctx.screen_shake_enabled() else 'OFF'}", focused=self.navigator.focus_index == 2)
        draw_button(self.btn_music, f"MUSIC {'ON' if self.ctx.music_enabled() else 'OFF'}", focused=self.navigator.focus_index == 3)
        draw_button(self.btn_sfx, f"SFX {'ON' if self.ctx.sfx_enabled() else 'OFF'}", focused=self.navigator.focus_index == 4)
        draw_button(self.btn_tutorial, f"TUTORIAL {'ON' if self.ctx.tutorial_enabled() else 'OFF'}", focused=self.navigator.focus_index == 5)
        draw_button(self.btn_themes, f"THEME {self.ctx.theme_name().upper()}", focused=self.navigator.focus_index == 6)
        draw_button(self.btn_career, "CAREER", focused=self.navigator.focus_index == 7)
        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == 8)
        draw_text_centered("ENTER OR CLICK", int(settings_card.x + settings_card.width / 2), int(settings_card.y + settings_card.height - 28), 14, TEXT_DIM)

    def _draw_mobile_content(self, panel) -> None:
        center_x = int(panel.x + panel.width / 2)
        top_card = pyray.Rectangle(panel.x + 20, panel.y + 132, panel.width - 40, 128)
        mid_card = pyray.Rectangle(panel.x + 20, panel.y + 278, panel.width - 40, 180)
        draw_glass_card(top_card, accent_color=PANEL_ACCENT, glow_alpha=12)
        draw_glass_card(mid_card, accent_color=colors.MAGENTA, glow_alpha=10)
        draw_text_centered(self.ctx.rank_title(), center_x, int(top_card.y + 18), 22, colors.WHITE)
        line_y = int(top_card.y + 52)
        for line in self.ctx.profile_summary_lines():
            draw_text_centered(line, center_x, line_y, 16, TEXT_DIM)
            line_y += 22
        draw_text_centered("MILESTONES", center_x, int(mid_card.y + 18), 18, TEXT_DIM)
        milestone_y = int(mid_card.y + 48)
        for title, _detail in self.ctx.unlocked_milestones()[-4:]:
            draw_text_centered(title, center_x, milestone_y, 16, colors.WHITE)
            milestone_y += 30

        draw_button(self.btn_fx, f"FX {self.ctx.fx_intensity().upper()}", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_flash, f"FLASH {'ON' if self.ctx.screen_flash_enabled() else 'OFF'}", focused=self.navigator.focus_index == 1)
        draw_button(self.btn_shake, f"SHAKE {'ON' if self.ctx.screen_shake_enabled() else 'OFF'}", focused=self.navigator.focus_index == 2)
        draw_button(self.btn_music, f"MUSIC {'ON' if self.ctx.music_enabled() else 'OFF'}", focused=self.navigator.focus_index == 3)
        draw_button(self.btn_sfx, f"SFX {'ON' if self.ctx.sfx_enabled() else 'OFF'}", focused=self.navigator.focus_index == 4)
        draw_button(self.btn_tutorial, f"TUTORIAL {'ON' if self.ctx.tutorial_enabled() else 'OFF'}", focused=self.navigator.focus_index == 5)
        draw_button(self.btn_themes, f"THEME {self.ctx.theme_name().upper()}", focused=self.navigator.focus_index == 6)
        draw_button(self.btn_career, "CAREER", focused=self.navigator.focus_index == 7)
        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == 8)
        draw_scene_footer(panel)
