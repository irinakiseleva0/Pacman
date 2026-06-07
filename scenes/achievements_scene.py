from __future__ import annotations

import core.raylib_api as pyray
from core import colors

from core.scene import Scene
from core.scene_ids import CAREER_SCENE
from ui import gamepad
from ui.navigation import ButtonNavigator
from ui.ui import (
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


class AchievementsScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(1)
        self.panel = None
        self.btn_back = None

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        self.navigator.reset(0)
        panel_width = min(1040, cfg.window_width - 80) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 32)
        panel_height = min(840, cfg.window_height - 90)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(34, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)
        self.btn_back = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 88), 240, 54)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
            self.ctx.play_sfx("ui_back")
            self.request_switch(getattr(self.ctx.run, "achievement_return_scene", CAREER_SCENE))
            return

        self.navigator.move_vertical()
        if self.navigator.confirm_pressed() or button_clicked(self.btn_back):
            self.ctx.play_sfx("ui_back")
            self.request_switch(getattr(self.ctx.run, "achievement_return_scene", CAREER_SCENE))

    def draw(self) -> None:
        cfg = self.ctx.cfg
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)

        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "DISTRICT ACHIEVEMENTS")
        draw_scene_header(panel, "DISTRICT ACHIEVEMENTS", "ACHIEVEMENTS", "CAREER GOALS", title_size=40)

        summary = pyray.Rectangle(panel.x + 24, panel.y + 120, panel.width - 48, 92)
        draw_glass_card(summary, accent_color=colors.GOLD, glow_alpha=12)
        center_x = int(summary.x + summary.width / 2)
        draw_text_centered("PROGRESS", center_x, int(summary.y + 14), 18, colors.WHITE)
        line_y = int(summary.y + 42)
        for line in self.ctx.achievement_summary_lines():
            draw_text_centered(line, center_x, line_y, 16, TEXT_DIM)
            line_y += 18

        self._draw_entries(panel)
        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == 0)
        draw_scene_footer(panel)

    def _draw_entries(self, panel) -> None:
        entries = self.ctx.achievement_entries()
        if self.ctx.cfg.layout_name == "desktop":
            left = entries[:5]
            right = entries[5:]
            self._draw_column(panel.x + 24, panel.y + 232, int((panel.width - 72) / 2), left)
            self._draw_column(panel.x + 48 + int((panel.width - 72) / 2), panel.y + 232, int((panel.width - 72) / 2), right)
        else:
            self._draw_column(panel.x + 18, panel.y + 228, panel.width - 36, entries, compact=True)

    def _draw_column(self, x: int, start_y: int, width: int, entries, compact: bool = False) -> None:
        height = 56 if compact else 62
        gap = 10
        for title, detail, unlocked in entries:
            rect = pyray.Rectangle(x, start_y, width, height)
            accent = colors.GREEN if unlocked else colors.MAGENTA
            fill_alpha = 168 if unlocked else 124
            draw_glass_card(rect, accent_color=accent, glow_alpha=10, fill_alpha=fill_alpha)
            status = "DONE" if unlocked else "LOCKED"
            title_color = colors.WHITE if unlocked else TEXT_DIM
            pyray.draw_text(title, int(rect.x + 14), int(rect.y + 10), 18 if not compact else 16, title_color)
            pyray.draw_text(detail, int(rect.x + 14), int(rect.y + 30), 14 if not compact else 13, TEXT_DIM)
            draw_text_centered(status, int(rect.x + rect.width - 48), int(rect.y + 16), 13, accent)
            start_y += height + gap
