from __future__ import annotations

import core.raylib_api as pyray
from core import colors

from core.scene import Scene
from core.scene_ids import OPTIONS_SCENE
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


class JournalScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(1)
        self.panel = None
        self.btn_back = None

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        self.navigator.reset(0)
        panel_width = min(1180, cfg.window_width - 80) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 32)
        panel_height = min(860, cfg.window_height - 70)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(28, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)
        self.btn_back = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 84), 240, 54)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
            self.ctx.play_sfx("ui_back")
            self.request_switch(OPTIONS_SCENE)
            return
        self.navigator.move_vertical()
        if self.navigator.confirm_pressed() or button_clicked(self.btn_back):
            self.ctx.play_sfx("ui_back")
            self.request_switch(OPTIONS_SCENE)

    def draw(self) -> None:
        cfg = self.ctx.cfg
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)

        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "DISTRICT JOURNAL")
        draw_scene_header(panel, "DISTRICT JOURNAL", "JOURNAL", "DISTRICTS, TRIALS, GHOST FILES", title_size=40)

        summary = pyray.Rectangle(panel.x + 24, panel.y + 120, panel.width - 48, 82)
        draw_glass_card(summary, accent_color=PANEL_ACCENT, glow_alpha=12)
        center_x = int(summary.x + summary.width / 2)
        line_y = int(summary.y + 14)
        for line in self.ctx.journal_summary_lines():
            draw_text_centered(line, center_x, line_y, 16, colors.WHITE if line_y == int(summary.y + 14) else TEXT_DIM)
            line_y += 20

        if cfg.layout_name == "desktop":
            self._draw_desktop_columns(panel)
        else:
            self._draw_mobile_stack(panel)

        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == 0)
        draw_scene_footer(panel)

    def _draw_desktop_columns(self, panel) -> None:
        gap = 16
        col_w = int((panel.width - 80 - gap * 2) / 3)
        start_x = panel.x + 24
        y = panel.y + 224
        self._draw_section(
            pyray.Rectangle(start_x, y, col_w, 520),
            "DISTRICTS",
            self.ctx.district_journal_entries(),
            mode="districts",
        )
        self._draw_section(
            pyray.Rectangle(start_x + col_w + gap, y, col_w, 520),
            "TRIAL BOARD",
            self.ctx.challenge_journal_entries(),
            mode="trials",
        )
        self._draw_section(
            pyray.Rectangle(start_x + (col_w + gap) * 2, y, col_w, 520),
            "GHOST FILES",
            self.ctx.ghost_journal_entries(),
            mode="ghosts",
        )

    def _draw_mobile_stack(self, panel) -> None:
        start_y = panel.y + 220
        section_h = 170
        gap = 12
        width = panel.width - 36
        self._draw_section(pyray.Rectangle(panel.x + 18, start_y, width, section_h), "DISTRICTS", self.ctx.district_journal_entries()[:4], mode="districts")
        self._draw_section(pyray.Rectangle(panel.x + 18, start_y + section_h + gap, width, section_h), "TRIAL BOARD", self.ctx.challenge_journal_entries()[:4], mode="trials")
        self._draw_section(pyray.Rectangle(panel.x + 18, start_y + (section_h + gap) * 2, width, section_h), "GHOST FILES", self.ctx.ghost_journal_entries(), mode="ghosts")

    def _draw_section(self, rect, title: str, entries, *, mode: str) -> None:
        accent = PANEL_ACCENT if mode == "districts" else colors.MAGENTA if mode == "trials" else colors.GOLD
        draw_glass_card(rect, accent_color=accent, glow_alpha=10, fill_alpha=170)
        draw_text_centered(title, int(rect.x + rect.width / 2), int(rect.y + 14), 18, colors.WHITE)

        y = int(rect.y + 42)
        if mode == "districts":
            for title_text, subtitle, detail, line_accent, unlocked in entries:
                self._draw_entry(rect.x + 12, y, rect.width - 24, 46, title_text, subtitle if unlocked else "LOCKED DISTRICT FILE", detail if unlocked else "Advance progression to open this file", line_accent if unlocked else colors.GRAY)
                y += 54
        elif mode == "trials":
            for title_text, subtitle, reward, line_accent, unlocked in entries:
                footer = reward if unlocked else "LOCKED TRIAL"
                self._draw_entry(rect.x + 12, y, rect.width - 24, 42, title_text, subtitle if unlocked else "LOCKED BOARD FILE", footer, line_accent if unlocked else colors.GRAY)
                y += 48
        else:
            for title_text, subtitle, detail, line_accent in entries:
                self._draw_entry(rect.x + 12, y, rect.width - 24, 50, title_text, subtitle, detail, line_accent)
                y += 58

    def _draw_entry(self, x: int, y: int, width: int, height: int, title: str, subtitle: str, detail: str, accent) -> None:
        rect = pyray.Rectangle(x, y, width, height)
        draw_glass_card(rect, accent_color=accent, glow_alpha=8, fill_alpha=138)
        pyray.draw_text(title, int(rect.x + 12), int(rect.y + 8), 16, colors.WHITE)
        pyray.draw_text(subtitle, int(rect.x + 12), int(rect.y + 24), 12, accent)
        if detail:
            pyray.draw_text(detail, int(rect.x + 12), int(rect.y + 38), 10, TEXT_DIM)
