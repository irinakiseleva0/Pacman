from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.game_data import CHALLENGE_PRESETS
from core.scene import Scene
from core.scene_ids import MODES_SCENE
from ui import gamepad
from ui.navigation import ButtonNavigator
from ui.ui import (
    LIVE_CYAN,
    LIVE_GOLD,
    LIVE_PINK,
    TEXT_DIM,
    button_clicked,
    centered_rect,
    draw_arcade_background,
    draw_button,
    draw_cinematic_menu_background,
    draw_dashboard_rail,
    draw_mission_frame,
    draw_panel,
    draw_scene_footer,
    draw_scene_header,
    draw_text_centered,
)


class ChallengeScene(Scene):
    CHALLENGES = tuple(CHALLENGE_PRESETS.keys())

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.navigator = ButtonNavigator(len(self.CHALLENGES) + 1)
        self.panel = None
        self.challenge_buttons: list[pyray.Rectangle] = []
        self.btn_back = None
        self.columns = 3

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        self.navigator.reset(0)
        panel_width = min(1120, cfg.window_width - 88) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 36)
        panel_height = min(820, cfg.window_height - 80)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(30, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        self.challenge_buttons = []
        if cfg.layout_name == "desktop":
            self.columns = 2
            gap_x = 18
            gap_y = 16
            width = int((panel_width - 84 - gap_x) / 2)
            height = 138
            start_y = int(panel_y + 232)
            for index in range(len(self.CHALLENGES)):
                row = index // self.columns
                col = index % self.columns
                x = int(panel_x + 30 + col * (width + gap_x))
                y = int(start_y + row * (height + gap_y))
                self.challenge_buttons.append(pyray.Rectangle(x, y, width, height))
        else:
            self.columns = 2
            gap_x = 12
            gap_y = 12
            width = int((panel_width - 52 - gap_x) / 2)
            height = 116
            start_y = int(panel_y + 132)
            for index in range(len(self.CHALLENGES)):
                row = index // self.columns
                col = index % self.columns
                x = int(panel_x + 20 + col * (width + gap_x))
                y = int(start_y + row * (height + gap_y))
                self.challenge_buttons.append(pyray.Rectangle(x, y, width, height))

        self.btn_back = centered_rect(cfg.window_width // 2, int(panel_y + panel_height - 92), 240, 54)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
            self.ctx.play_sfx("ui_back")
            self.request_switch(MODES_SCENE)
            return

        self._move_focus()
        if self.navigator.confirm_pressed():
            self._activate_focused()

        for index, rect in enumerate(self.challenge_buttons):
            if button_clicked(rect):
                self.navigator.focus_index = index
                self._select_challenge(self.CHALLENGES[index])
        if button_clicked(self.btn_back):
            self.navigator.focus_index = len(self.CHALLENGES)
            self.ctx.play_sfx("ui_back")
            self.request_switch(MODES_SCENE)

    def _activate_focused(self) -> None:
        if self.navigator.focus_index < len(self.CHALLENGES):
            self._select_challenge(self.CHALLENGES[self.navigator.focus_index])
            return
        self.ctx.play_sfx("ui_back")
        self.request_switch(MODES_SCENE)

    def _select_challenge(self, challenge_name: str) -> None:
        if not self.ctx.challenge_unlocked(challenge_name):
            self.ctx.play_sfx("ui_back")
            return
        self.ctx.set_game_mode("Challenge")
        self.ctx.set_challenge(challenge_name)
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
        draw_panel(panel, "CHALLENGE BOARD")
        draw_scene_header(panel, "CHALLENGE BOARD", "SELECT CHALLENGE", "CURATED TRIAL BOARD", title_size=40)
        draw_dashboard_rail(int(panel.x + panel.width / 2), int(panel.y + 110), 280, label="TRIAL GRID", accent_color=LIVE_PINK, support_color=LIVE_CYAN, time_s=self.ctx.visual_time)
        self._draw_board_briefing(panel)

        for index, challenge_name in enumerate(self.CHALLENGES):
            self._draw_card(self.challenge_buttons[index], challenge_name, focused=self.navigator.focus_index == index)

        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == len(self.CHALLENGES))
        draw_scene_footer(panel)

    def _draw_board_briefing(self, panel) -> None:
        selected_index = min(self.navigator.focus_index, len(self.CHALLENGES) - 1)
        selected_name = self.CHALLENGES[selected_index]
        preset = CHALLENGE_PRESETS[selected_name]
        unlocked = self.ctx.challenge_unlocked(selected_name)
        reward_unlocked = self.ctx.challenge_reward_unlocked(selected_name)

        summary = pyray.Rectangle(panel.x + 30, panel.y + 126, int(panel.width * 0.28), 90)
        briefing = pyray.Rectangle(summary.x + summary.width + 18, panel.y + 126, panel.width - summary.width - 78, 90)
        draw_mission_frame(summary, accent_color=LIVE_PINK, support_color=LIVE_CYAN, glow_alpha=10, fill_alpha=144)
        draw_mission_frame(
            briefing,
            accent_color=preset.accent if unlocked else colors.GRAY,
            support_color=LIVE_CYAN,
            glow_alpha=12,
            fill_alpha=150,
        )

        summary_x = int(summary.x + summary.width / 2)
        draw_text_centered("BOARD STATUS", summary_x, int(summary.y + 16), 14, LIVE_PINK)
        line_y = int(summary.y + 38)
        summary_lines = self.ctx.challenge_board_summary_lines()
        summary_lines = (summary_lines[0], summary_lines[1], self.ctx.next_challenge_unlock_goal() or summary_lines[2])
        for line in summary_lines:
            draw_text_centered(line, summary_x, line_y, 12, colors.WHITE)
            line_y += 16

        briefing_x = int(briefing.x + briefing.width / 2)
        draw_dashboard_rail(briefing_x, int(briefing.y + 8), int(briefing.width * 0.42), accent_color=preset.accent if unlocked else LIVE_PINK, support_color=LIVE_CYAN, time_s=self.ctx.visual_time)
        draw_text_centered(f"{preset.board_tag}  |  {preset.threat_label}", briefing_x, int(briefing.y + 14), 13, preset.accent if unlocked else colors.GRAY)
        draw_text_centered(preset.title, briefing_x, int(briefing.y + 32), 24, colors.WHITE if unlocked else TEXT_DIM)
        middle_line = preset.subtitle if unlocked else preset.unlock_text
        draw_text_centered(middle_line.upper(), briefing_x, int(briefing.y + 58), 12, preset.accent if unlocked else colors.GRAY)
        footer = f"REWARD {preset.reward_title}" if not reward_unlocked else f"TROPHY EARNED {preset.reward_title}"
        draw_text_centered(footer, briefing_x, int(briefing.y + 76), 11, colors.WHITE if reward_unlocked else TEXT_DIM)

    def _draw_card(self, rect, challenge_name: str, *, focused: bool) -> None:
        preset = CHALLENGE_PRESETS[challenge_name]
        unlocked = self.ctx.challenge_unlocked(challenge_name)
        reward_unlocked = self.ctx.challenge_reward_unlocked(challenge_name)
        active = self.ctx.game_mode == "Challenge" and self.ctx.challenge_name == challenge_name
        accent = preset.accent if unlocked else colors.GRAY
        draw_mission_frame(
            rect,
            accent_color=accent if unlocked else LIVE_PINK,
            support_color=LIVE_CYAN,
            glow_alpha=18 if focused or active else 10,
            fill_alpha=174 if active else 136,
        )

        center_x = int(rect.x + rect.width / 2)
        title_size = 22
        title_color = colors.WHITE if unlocked and (active or focused) else TEXT_DIM
        draw_dashboard_rail(center_x, int(rect.y + 8), int(rect.width * 0.48), accent_color=accent if unlocked else LIVE_PINK, support_color=LIVE_CYAN, time_s=self.ctx.visual_time)
        draw_text_centered(preset.board_tag, center_x, int(rect.y + 14), 10, accent)
        draw_text_centered(preset.title, center_x, int(rect.y + 30), title_size, title_color)
        draw_text_centered(preset.threat_label, center_x, int(rect.y + 58), 10, accent)
        state_line = preset.subtitle if unlocked else preset.unlock_text
        draw_text_centered(state_line.upper(), center_x, int(rect.y + 82), 11, colors.WHITE if unlocked else TEXT_DIM)
        reward_text = preset.reward_title if reward_unlocked else "REWARD " + preset.reward_title
        draw_text_centered(reward_text, center_x, int(rect.y + 106), 10, LIVE_GOLD if reward_unlocked else TEXT_DIM)
        if unlocked:
            footer = "TROPHY EARNED" if reward_unlocked else "ACTIVE" if active else "PRESS ENTER"
            footer_color = colors.WHITE if active else accent
        else:
            footer = "LOCKED"
            footer_color = accent
        draw_text_centered(footer, center_x, int(rect.y + rect.height - 20), 11, footer_color)

    def _move_focus(self) -> None:
        total = len(self.CHALLENGES)
        back_index = total
        focus = self.navigator.focus_index

        if focus == back_index:
            if pyray.is_key_pressed(pyray.KEY_UP) or pyray.is_key_pressed(pyray.KEY_W) or gamepad.up_pressed():
                self.navigator.focus_index = total - 1
            return

        if pyray.is_key_pressed(pyray.KEY_LEFT) or pyray.is_key_pressed(pyray.KEY_A) or gamepad.left_pressed():
            if focus > 0:
                self.navigator.focus_index = focus - 1
            return
        if pyray.is_key_pressed(pyray.KEY_RIGHT) or pyray.is_key_pressed(pyray.KEY_D) or gamepad.right_pressed():
            if focus < total - 1:
                self.navigator.focus_index = focus + 1
            return
        if pyray.is_key_pressed(pyray.KEY_UP) or pyray.is_key_pressed(pyray.KEY_W) or gamepad.up_pressed():
            next_index = focus - self.columns
            if next_index >= 0:
                self.navigator.focus_index = next_index
            return
        if pyray.is_key_pressed(pyray.KEY_DOWN) or pyray.is_key_pressed(pyray.KEY_S) or gamepad.down_pressed():
            next_index = focus + self.columns
            if next_index < total:
                self.navigator.focus_index = next_index
            else:
                self.navigator.focus_index = back_index
