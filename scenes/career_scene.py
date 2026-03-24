from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.game_data import CHALLENGE_PRESETS, HUD_PACK_PRESETS
from core.scene import Scene
from core.scene_ids import ACHIEVEMENTS_SCENE, OPTIONS_SCENE, RUN_HISTORY_SCENE
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


class CareerScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(3)
        self.panel = None
        self.btn_achievements = None
        self.btn_history = None
        self.btn_back = None

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        self.navigator.reset(0)
        panel_width = min(1080, cfg.window_width - 80) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 36)
        panel_height = min(820, cfg.window_height - 90)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(36, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)
        self.btn_achievements = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 214), 260, 48)
        self.btn_history = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 154), 260, 48)
        self.btn_back = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 88), 240, 54)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt

        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
            self.ctx.play_sfx("ui_back")
            self.request_switch(OPTIONS_SCENE)
            return

        self.navigator.move_vertical()
        if button_clicked(self.btn_achievements):
            self.navigator.focus_index = 0
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(ACHIEVEMENTS_SCENE)
            return
        if button_clicked(self.btn_history):
            self.navigator.focus_index = 1
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(RUN_HISTORY_SCENE)
            return
        if button_clicked(self.btn_back):
            self.navigator.focus_index = 2
            self.ctx.play_sfx("ui_back")
            self.request_switch(OPTIONS_SCENE)
            return
        if self.navigator.confirm_pressed():
            if self.navigator.focus_index == 0:
                self.ctx.play_sfx("ui_confirm")
                self.request_switch(ACHIEVEMENTS_SCENE)
            elif self.navigator.focus_index == 1:
                self.ctx.play_sfx("ui_confirm")
                self.request_switch(RUN_HISTORY_SCENE)
            else:
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
        draw_panel(panel, "CAREER FILE")
        draw_scene_header(panel, "CAREER FILE", "CAREER", "RANK, GOALS, TROPHIES")

        if cfg.layout_name == "desktop":
            self._draw_desktop(panel)
        else:
            self._draw_mobile(panel)

        draw_button(self.btn_achievements, "ACHIEVEMENTS", focused=self.navigator.focus_index == 0)
        draw_button(self.btn_history, "RUN HISTORY", focused=self.navigator.focus_index == 1)
        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == 2)
        draw_scene_footer(panel)

    def _draw_desktop(self, panel) -> None:
        left_w = int(panel.width * 0.37)
        gap = 24
        right_x = panel.x + left_w + gap + 24
        right_w = panel.width - left_w - gap - 48

        top_left = pyray.Rectangle(panel.x + 24, panel.y + 130, left_w, 118)
        mid_left = pyray.Rectangle(panel.x + 24, panel.y + 264, left_w, 118)
        bottom_left = pyray.Rectangle(panel.x + 24, panel.y + 398, left_w, 118)
        trophy_left = pyray.Rectangle(panel.x + 24, panel.y + 532, left_w, 118)
        right_card = pyray.Rectangle(right_x, panel.y + 130, right_w, 520)

        draw_glass_card(top_left, accent_color=PANEL_ACCENT, glow_alpha=14)
        draw_glass_card(mid_left, accent_color=colors.GOLD, glow_alpha=12)
        draw_glass_card(bottom_left, accent_color=colors.MAGENTA, glow_alpha=12)
        draw_glass_card(trophy_left, accent_color=colors.GREEN, glow_alpha=12)
        draw_glass_card(right_card, accent_color=colors.WHITE, glow_alpha=10, fill_alpha=176)

        self._draw_labeled_lines(top_left, self.ctx.rank_title(), self.ctx.profile_summary_lines(), max_lines=1)
        self._draw_labeled_lines(mid_left, "MODE MASTERY", self.ctx.mode_mastery_summary_lines(), max_lines=1)
        self._draw_labeled_lines(bottom_left, "LIFETIME STATS", self.ctx.lifetime_stat_lines(), max_lines=1)
        hud_unlocked = sum(1 for _name, _preset, unlocked in self.ctx.hud_pack_entries() if unlocked)
        self._draw_labeled_lines(trophy_left, f"UNLOCKS {self.ctx.challenge_reward_count()}/{len(CHALLENGE_PRESETS)}", (self.ctx.challenge_progress_lines()[0], f"HUD PACKS {hud_unlocked}/{len(HUD_PACK_PRESETS)}", f"ACTIVE {self.ctx.hud_pack_name().upper()}"), max_lines=2)

        center_x = int(right_card.x + right_card.width / 2)
        draw_text_centered("NEXT GOALS", center_x, int(right_card.y + 18), 20, TEXT_DIM)

        goal_y = int(right_card.y + 54)
        for line in self.ctx.career_goal_lines():
            item = pyray.Rectangle(right_card.x + 24, goal_y, right_card.width - 48, 52)
            draw_glass_card(item, accent_color=PANEL_ACCENT, glow_alpha=8, fill_alpha=136)
            draw_text_centered(line, center_x, int(item.y + 17), 15, colors.WHITE)
            goal_y += 62

        preview = pyray.Rectangle(right_card.x + 24, goal_y + 6, right_card.width - 48, 62)
        save_card = pyray.Rectangle(right_card.x + 24, goal_y + 78, right_card.width - 48, 54)
        draw_glass_card(preview, accent_color=colors.GOLD, glow_alpha=8, fill_alpha=132)
        draw_glass_card(save_card, accent_color=PANEL_ACCENT, glow_alpha=8, fill_alpha=132)
        draw_text_centered("REWARD PROGRESS", center_x, int(preview.y + 10), 14, TEXT_DIM)
        progress_y = int(preview.y + 30)
        for line in self.ctx.reward_progress_lines()[:2]:
            draw_text_centered(line, center_x, progress_y, 13, colors.WHITE)
            progress_y += 16
        draw_text_centered("PROFILE SAVE", center_x, int(save_card.y + 10), 14, TEXT_DIM)
        save_y = int(save_card.y + 28)
        for line in self.ctx.profile_save_summary_lines()[:2]:
            draw_text_centered(line, center_x, save_y, 12, colors.WHITE)
            save_y += 14

        draw_text_centered("RECENT MILESTONES", center_x, goal_y + 146, 16, PANEL_ACCENT)
        milestone_y = goal_y + 174
        milestones = self.ctx.unlocked_milestones()
        if not milestones:
            draw_text_centered("NO MILESTONES YET", center_x, milestone_y, 18, colors.WHITE)
            draw_text_centered("START A RUN TO BEGIN YOUR FILE", center_x, milestone_y + 28, 14, TEXT_DIM)
            return

        for title, detail in milestones[-3:]:
            item = pyray.Rectangle(right_card.x + 24, milestone_y, right_card.width - 48, 44)
            draw_glass_card(item, accent_color=colors.MAGENTA, glow_alpha=8, fill_alpha=132)
            pyray.draw_text(title, int(item.x + 14), int(item.y + 8), 18, colors.WHITE)
            pyray.draw_text(detail, int(item.x + 14), int(item.y + 24), 14, TEXT_DIM)
            milestone_y += 54

    def _draw_mobile(self, panel) -> None:
        cards = [
            pyray.Rectangle(panel.x + 18, panel.y + 124, panel.width - 36, 112),
            pyray.Rectangle(panel.x + 18, panel.y + 252, panel.width - 36, 112),
            pyray.Rectangle(panel.x + 18, panel.y + 380, panel.width - 36, 112),
            pyray.Rectangle(panel.x + 18, panel.y + 508, panel.width - 36, 112),
            pyray.Rectangle(panel.x + 18, panel.y + 636, panel.width - 36, 172),
        ]
        accents = (PANEL_ACCENT, colors.GOLD, colors.MAGENTA, colors.GREEN, colors.WHITE)
        titles = ("RANK", "MODE SPLIT", "LIFETIME", "TROPHIES", "NEXT GOALS")
        linesets = (
            self.ctx.profile_summary_lines(),
            self.ctx.mode_mastery_summary_lines(),
            self.ctx.lifetime_stat_lines(),
            self.ctx.challenge_progress_lines(),
            self.ctx.career_goal_lines(),
        )

        for rect, accent, title, lines in zip(cards, accents, titles, linesets):
            draw_glass_card(rect, accent_color=accent, glow_alpha=12)
            center_x = int(rect.x + rect.width / 2)
            draw_text_centered(title if title != "RANK" else self.ctx.rank_title(), center_x, int(rect.y + 14), 18, colors.WHITE)
            if lines is not None:
                line_y = int(rect.y + 48)
                for line in lines[:2]:
                    draw_text_centered(line, center_x, line_y, 15, TEXT_DIM)
                    line_y += 22

    def _draw_labeled_lines(self, rect, title: str, lines: tuple[str, str, str], max_lines: int = 3) -> None:
        center_x = int(rect.x + rect.width / 2)
        draw_text_centered(title, center_x, int(rect.y + 18), 20, colors.WHITE)
        line_y = int(rect.y + 54)
        for line in lines[:max_lines]:
            draw_text_centered(line, center_x, line_y, 16, TEXT_DIM)
            line_y += 22
