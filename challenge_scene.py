from __future__ import annotations

import pyray
from raylib import colors

from core.context import CHALLENGE_PRESETS
from core.scene import Scene
from core.scene_ids import MODES_SCENE
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
        panel_height = min(860, cfg.window_height - 72)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(30, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        self.challenge_buttons = []
        if cfg.layout_name == "desktop":
            self.columns = 2
            gap_x = 20
            gap_y = 18
            width = int((panel_width - 80 - gap_x) / 2)
            height = 152
            start_y = int(panel_y + 142)
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
        if pyray.is_key_pressed(pyray.KEY_ESCAPE):
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
        draw_scene_header(panel, "CHALLENGE BOARD", "SELECT CHALLENGE", "ARM A TRIAL", title_size=40)

        for index, challenge_name in enumerate(self.CHALLENGES):
            self._draw_card(self.challenge_buttons[index], challenge_name, focused=self.navigator.focus_index == index)

        draw_button(self.btn_back, "BACK", focused=self.navigator.focus_index == len(self.CHALLENGES))
        draw_scene_footer(panel)

    def _draw_card(self, rect, challenge_name: str, *, focused: bool) -> None:
        preset = CHALLENGE_PRESETS[challenge_name]
        unlocked = self.ctx.challenge_unlocked(challenge_name)
        reward_unlocked = self.ctx.challenge_reward_unlocked(challenge_name)
        active = self.ctx.game_mode == "Challenge" and self.ctx.challenge_name == challenge_name
        accent = preset.accent if unlocked else colors.GRAY
        draw_glass_card(rect, accent_color=accent, glow_alpha=18 if focused or active else 10, fill_alpha=182 if active else 144)

        center_x = int(rect.x + rect.width / 2)
        title_size = 20 if rect.height > 140 else 18
        subtitle_size = 12
        line_size = 13 if rect.height > 140 else 12
        line_step = 20 if rect.height > 140 else 18
        title_color = colors.WHITE if unlocked and (active or focused) else TEXT_DIM
        draw_text_centered(preset.title, center_x, int(rect.y + 12), title_size, title_color)
        draw_text_centered((preset.subtitle if unlocked else preset.unlock_text).upper(), center_x, int(rect.y + 38), subtitle_size, accent)
        reward_text = preset.reward_title
        draw_text_centered(reward_text, center_x, int(rect.y + 84), 11, colors.WHITE if reward_unlocked else TEXT_DIM)
        if unlocked:
            footer = "TROPHY EARNED" if reward_unlocked else "ACTIVE" if active else "PRESS ENTER"
            footer_color = colors.WHITE if active else accent
        else:
            footer = "LOCKED"
            footer_color = accent
        draw_text_centered(footer, center_x, int(rect.y + rect.height - 18), 12, footer_color)

    def _move_focus(self) -> None:
        total = len(self.CHALLENGES)
        back_index = total
        focus = self.navigator.focus_index

        if focus == back_index:
            if pyray.is_key_pressed(pyray.KEY_UP) or pyray.is_key_pressed(pyray.KEY_W):
                self.navigator.focus_index = total - 1
            return

        if pyray.is_key_pressed(pyray.KEY_LEFT) or pyray.is_key_pressed(pyray.KEY_A):
            if focus > 0:
                self.navigator.focus_index = focus - 1
            return
        if pyray.is_key_pressed(pyray.KEY_RIGHT) or pyray.is_key_pressed(pyray.KEY_D):
            if focus < total - 1:
                self.navigator.focus_index = focus + 1
            return
        if pyray.is_key_pressed(pyray.KEY_UP) or pyray.is_key_pressed(pyray.KEY_W):
            next_index = focus - self.columns
            if next_index >= 0:
                self.navigator.focus_index = next_index
            return
        if pyray.is_key_pressed(pyray.KEY_DOWN) or pyray.is_key_pressed(pyray.KEY_S):
            next_index = focus + self.columns
            if next_index < total:
                self.navigator.focus_index = next_index
            else:
                self.navigator.focus_index = back_index
