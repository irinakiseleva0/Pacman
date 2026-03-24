from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import CAREER_SCENE
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


class RunHistoryScene(Scene):
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
        if pyray.is_key_pressed(pyray.KEY_ESCAPE):
            self.ctx.play_sfx("ui_back")
            self.request_switch(CAREER_SCENE)
            return
        self.navigator.move_vertical()
        if self.navigator.confirm_pressed() or button_clicked(self.btn_back):
            self.ctx.play_sfx("ui_back")
            self.request_switch(CAREER_SCENE)

    def draw(self) -> None:
        cfg = self.ctx.cfg
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)

        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "RUN HISTORY")
        draw_scene_header(panel, "RUN HISTORY", "RUN HISTORY", "RECENT RUNS", title_size=40)

        summary = pyray.Rectangle(panel.x + 24, panel.y + 122, panel.width - 48, 92)
        draw_glass_card(summary, accent_color=colors.SKYBLUE, glow_alpha=12)
        center_x = int(summary.x + summary.width / 2)
        line_y = int(summary.y + 18)
        for line in self.ctx.run_history_summary_lines():
            draw_text_centered(line, center_x, line_y, 17, colors.WHITE if line_y == int(summary.y + 18) else TEXT_DIM)
            line_y += 22

        entries = self.ctx.run_history_entries()
        if entries:
            self._draw_entries(panel, entries)
        else:
            draw_text_centered("NO RUNS LOGGED YET", cfg.window_width // 2, int(panel.y + 308), 22, colors.WHITE)
            draw_text_centered("FINISH A RUN TO BUILD YOUR JOURNAL", cfg.window_width // 2, int(panel.y + 340), 16, TEXT_DIM)

        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == 0)
        draw_scene_footer(panel)

    def _draw_entries(self, panel, entries: list[dict]) -> None:
        if self.ctx.cfg.layout_name == "desktop":
            col_w = int((panel.width - 78) / 2)
            left = entries[:6]
            right = entries[6:12]
            self._draw_column(panel.x + 24, panel.y + 232, col_w, left)
            self._draw_column(panel.x + 42 + col_w, panel.y + 232, col_w, right)
        else:
            self._draw_column(panel.x + 18, panel.y + 228, panel.width - 36, entries[:7], compact=True)

    def _draw_column(self, x: int, start_y: int, width: int, entries: list[dict], compact: bool = False) -> None:
        card_h = 62 if compact else 66
        gap = 10
        for entry in entries:
            rect = pyray.Rectangle(x, start_y, width, card_h)
            result = str(entry.get("result", "lose"))
            accent = colors.GOLD if result == "game_won" else colors.RED if result in {"lose", "challenge_failed"} else colors.GREEN
            draw_glass_card(rect, accent_color=accent, glow_alpha=10, fill_alpha=154)
            mode_tag = str(entry.get("challenge") or entry.get("mode", "Arcade"))
            line1 = f"{mode_tag} / {entry.get('difficulty', 'Normal')}"
            result_tag = result.replace("_", " ").upper()
            line2 = f"SCORE {int(entry.get('score', 0))}  LEVEL {int(entry.get('level', 1))}"
            pyray.draw_text(line1, int(rect.x + 14), int(rect.y + 10), 17 if not compact else 15, colors.WHITE)
            pyray.draw_text(line2, int(rect.x + 14), int(rect.y + 32), 14 if not compact else 13, TEXT_DIM)
            draw_text_centered(result_tag, int(rect.x + rect.width - 70), int(rect.y + 18), 13, accent)
            start_y += card_h + gap
