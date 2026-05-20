from __future__ import annotations

import datetime

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import ACHIEVEMENTS_SCENE, EXIT_SCENE, GAME_SCENE, MENU_SCENE, MODES_SCENE, OPTIONS_SCENE, REPLAY_VIEWER_SCENE
from ui.components import Button
from ui.layout import LAYOUT_PROFILES, centered_vertical_stack
from ui.navigation import ButtonNavigator
from ui.style import UI_STYLE
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK, PANEL_ACCENT, TEXT_DIM, draw_arcade_background, draw_cinematic_menu_background, draw_panel, draw_presentation_bars, draw_scene_footer, draw_scene_scan_intro, draw_title_glitch_pass, button_clicked, draw_shadowed_text_centered, draw_text_centered
from utils.replay import list_replays


class Menu(Scene):
    FOCUS_ORDER = ("Desktop", "Mobile", "Easy", "Normal", "Hard", "Start", "Modes", "Replays", "Achievements", "Options", "Exit")

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
        self.btn_modes = None
        self.btn_replays = None
        self.btn_achievements = None
        self.btn_options = None
        self.btn_exit = None
        self.main_panel = None
        self.desktop_layout = False
        self.intro_timer = 0.0
        self.seed_text = ""

    def enter_tree(self) -> None:
        self.intro_timer = UI_STYLE.motion.intro_seconds
        cfg = self.ctx.cfg
        cx = cfg.window_width // 2
        self.desktop_layout = cfg.layout_name == "desktop"
        if self.desktop_layout:
            panel_width = min(UI_STYLE.sizes.menu_panel_width, cfg.window_width - 120)
            panel_height = min(UI_STYLE.sizes.menu_panel_height, cfg.window_height - 160)
            panel_x = cx - panel_width // 2
            panel_y = max(40, int((cfg.window_height - panel_height) / 2))
        else:
            panel_width = min(760, cfg.window_width - 80)
            panel_height = cfg.window_height - 96
            panel_x = cx - panel_width // 2
            panel_y = 48
        self.main_panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        if self.desktop_layout:
            btn_h = UI_STYLE.sizes.button_height
            button_w = min(UI_STYLE.sizes.button_width, int(panel_width - UI_STYLE.spacing.panel_pad * 2))
            button_top = int(panel_y + 184)
            (
                self.btn_desktop,
                self.btn_mobile,
                self.btn_easy,
                self.btn_normal,
                self.btn_hard,
                self.btn_start,
                self.btn_modes,
                self.btn_replays,
                self.btn_achievements,
                self.btn_options,
                self.btn_exit,
            ) = centered_vertical_stack(
                int(panel_x + panel_width / 2),
                button_top,
                button_w,
                [btn_h] * len(self.FOCUS_ORDER),
                UI_STYLE.spacing.button_gap,
            )
        else:
            btn_w = min(UI_STYLE.sizes.button_width, int(panel_width - UI_STYLE.spacing.panel_pad * 2))
            btn_h = 40
            button_top = int(panel_y + 142)
            (
                self.btn_desktop,
                self.btn_mobile,
                self.btn_easy,
                self.btn_normal,
                self.btn_hard,
                self.btn_start,
                self.btn_modes,
                self.btn_replays,
                self.btn_achievements,
                self.btn_options,
                self.btn_exit,
            ) = centered_vertical_stack(
                cx,
                button_top,
                btn_w,
                [btn_h] * len(self.FOCUS_ORDER),
                6,
            )
        self.navigator.reset(3)
        self.seed_text = "" if self.ctx.run.requested_seed is None else f"{self.ctx.run.requested_seed:06d}"

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        self.intro_timer = max(0.0, self.intro_timer - dt)
        self._handle_seed_input()
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
            if not self._apply_difficulty():
                return
            self.ctx.play_sfx("start_run")
            self.ctx.play_transition_effect(LIVE_GOLD, 0.3, 0.4)
            self.request_switch(GAME_SCENE)
        if button_clicked(self.btn_modes):
            self.navigator.focus_index = 6
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(MODES_SCENE)
        if button_clicked(self.btn_replays):
            self.navigator.focus_index = 7
            self._open_best_replay()
        if button_clicked(self.btn_achievements):
            self.navigator.focus_index = 8
            self.ctx.play_sfx("ui_confirm")
            self.ctx.run.achievement_return_scene = MENU_SCENE
            self.request_switch(ACHIEVEMENTS_SCENE)
        if button_clicked(self.btn_options):
            self.navigator.focus_index = 9
            self.ctx.play_sfx("ui_confirm")
            self.request_switch(OPTIONS_SCENE)
        if button_clicked(self.btn_exit):
            self.navigator.focus_index = 10
            self.ctx.play_sfx("ui_back")
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
                if not self._apply_difficulty():
                    return
                self.ctx.play_sfx("start_run")
                self.ctx.play_transition_effect(LIVE_GOLD, 0.3, 0.4)
                self.request_switch(GAME_SCENE)
            elif self.navigator.focus_index == 6:
                self.ctx.play_sfx("ui_confirm")
                self.request_switch(MODES_SCENE)
            elif self.navigator.focus_index == 7:
                self._open_best_replay()
            elif self.navigator.focus_index == 8:
                self.ctx.play_sfx("ui_confirm")
                self.ctx.run.achievement_return_scene = MENU_SCENE
                self.request_switch(ACHIEVEMENTS_SCENE)
            elif self.navigator.focus_index == 9:
                self.ctx.play_sfx("ui_confirm")
                self.request_switch(OPTIONS_SCENE)
            else:
                self.ctx.play_sfx("ui_back")
                self.request_switch(EXIT_SCENE)

    def _open_best_replay(self) -> None:
        replays = list_replays(1)
        if not replays:
            self.ctx.play_sfx("ui_back")
            return
        self.ctx.selected_replay_path = str(replays[0].path)
        self.ctx.play_sfx("ui_confirm")
        self.request_switch(REPLAY_VIEWER_SCENE)

    def _set_layout(self, layout_name: str) -> None:
        if layout_name not in LAYOUT_PROFILES:
            return

        self.layout_name = layout_name
        self.ctx.apply_layout(layout_name)
        if hasattr(pyray, "set_window_size"):
            pyray.set_window_size(self.ctx.cfg.window_width, self.ctx.cfg.window_height)
        self.enter_tree()

    def _apply_difficulty(self) -> bool:
        """Apply difficulty settings to the game config."""
        self.ctx.apply_difficulty(self.difficulty)
        self.ctx.set_requested_seed(int(self.seed_text) if self.seed_text else None)
        if not self.ctx.start_new_game():
            self.ctx.play_sfx("ui_back")
            return False
        return True

    def _daily_countdown(self) -> str:
        now = datetime.datetime.now()
        tomorrow = now.date() + datetime.timedelta(days=1)
        remaining = datetime.datetime.combine(tomorrow, datetime.time.min) - now
        total_seconds = max(0, int(remaining.total_seconds()))
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _handle_seed_input(self) -> None:
        char = pyray.get_char_pressed()
        while char:
            if 48 <= char <= 57 and len(self.seed_text) < 6:
                self.seed_text += chr(char)
            char = pyray.get_char_pressed()

        if pyray.is_key_pressed(pyray.KEY_BACKSPACE) and self.seed_text:
            self.seed_text = self.seed_text[:-1]

    def _draw_button(self, rect, text: str, focus_index: int) -> None:
        elapsed = UI_STYLE.motion.intro_seconds - self.intro_timer
        delay = focus_index * UI_STYLE.motion.menu_item_stagger
        if elapsed < delay:
            return
        settle = min(1.0, (elapsed - delay) / 0.18)
        ease = 1.0 - (1.0 - settle) * (1.0 - settle)
        draw_rect = rect
        if ease < 1.0:
            draw_rect = pyray.Rectangle(rect.x, rect.y + int((1.0 - ease) * 10), rect.width, rect.height)
        Button(draw_rect, text, self.navigator.focus_index == focus_index).draw(time_s=self.ctx.visual_time)

    def _difficulty_summary_lines(self) -> list[str]:
        return list(self.ctx.difficulty_summary_lines(self.difficulty))

    def draw(self) -> None:
        cfg = self.ctx.cfg
        center_x = cfg.window_width // 2
        if self.desktop_layout:
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)

        if self.main_panel is None:
            self.enter_tree()
        main_panel = self.main_panel

        if self.desktop_layout:
            self._draw_desktop_menu(main_panel)
        else:
            draw_panel(main_panel, time_s=self.ctx.visual_time)
            title_size = 44
            draw_shadowed_text_centered("PAC-MAN", center_x, int(main_panel.y + 40), title_size, colors.WHITE)
            draw_text_centered("CYBER DISTRICT", center_x, int(main_panel.y + 140), 18, colors.WHITE)
            if self.intro_timer > 0.0:
                intro_progress = min(1.0, 1.0 - self.intro_timer / UI_STYLE.motion.intro_seconds)
                draw_title_glitch_pass(center_x, int(main_panel.y + 58), 360, intro_progress, time_s=self.ctx.visual_time)
            self._draw_mobile_menu(main_panel)
        if self.intro_timer > 0.0:
            intro_progress = min(1.0, 1.0 - self.intro_timer / UI_STYLE.motion.intro_seconds)
            draw_scene_scan_intro(cfg.window_width, cfg.window_height, intro_progress, accent_color=LIVE_PINK, time_s=self.ctx.visual_time)
        draw_presentation_bars(cfg.window_width, cfg.window_height)

    def _draw_desktop_menu(self, main_panel) -> None:
        draw_panel(main_panel, time_s=self.ctx.visual_time)

        center_x = int(main_panel.x + main_panel.width / 2)
        title_y = int(main_panel.y + 34)
        draw_text_centered("CYBER DISTRICT", center_x, title_y, UI_STYLE.typography.section, PANEL_ACCENT)
        draw_shadowed_text_centered("PAC-MAN", center_x, title_y + 28, 64, colors.WHITE)
        draw_text_centered("BLACKOUT ROUTE // ARCADE TERMINAL", center_x, title_y + 106, 13, TEXT_DIM)
        if self.intro_timer > 0.0:
            intro_progress = min(1.0, 1.0 - self.intro_timer / UI_STYLE.motion.intro_seconds)
            draw_title_glitch_pass(center_x, title_y + 42, 360, intro_progress, time_s=self.ctx.visual_time)

        status_y = int(main_panel.y + 154)
        draw_text_centered(f"{self.ctx.rank_title().upper()}  |  HIGH SCORE {self.ctx.high_score}", center_x, status_y, 12, LIVE_GOLD)
        seed_label = self.seed_text if self.seed_text else "RANDOM"
        draw_text_centered(f"SEED {seed_label}  |  TYPE DIGITS / BACKSPACE", center_x, status_y + 18, 12, LIVE_CYAN)
        if self.ctx.game_mode == "DailyChallenge":
            daily_status = "AVAILABLE" if self.ctx.daily_challenge_available() else f"NEXT IN {self._daily_countdown()}"
            draw_text_centered(f"DAILY {self.ctx.daily_seed()}  |  {daily_status}", center_x, status_y + 36, 12, LIVE_PINK)

        self._draw_button(self.btn_desktop, "DESKTOP", 0)
        self._draw_button(self.btn_mobile, "MOBILE", 1)
        self._draw_button(self.btn_easy, "EASY", 2)
        self._draw_button(self.btn_normal, "NORMAL", 3)
        self._draw_button(self.btn_hard, "HARD", 4)
        self._draw_button(self.btn_start, "START RUN", 5)
        self._draw_button(self.btn_modes, "MODES", 6)
        self._draw_button(self.btn_replays, "REPLAYS", 7)
        self._draw_button(self.btn_achievements, "ACHIEVEMENTS", 8)
        self._draw_button(self.btn_options, "OPTIONS", 9)
        self._draw_button(self.btn_exit, "EXIT", 10)
        self._draw_replay_hall(main_panel)
        draw_scene_footer(main_panel)

    def _draw_mobile_menu(self, main_panel) -> None:
        cfg = self.ctx.cfg
        center_x = cfg.window_width // 2
        draw_text_centered("RUN MENU", center_x, int(main_panel.y + 18), 18, PANEL_ACCENT)
        draw_shadowed_text_centered("PAC-MAN", center_x, int(main_panel.y + 44), 42, colors.WHITE)
        draw_text_centered("CYBER DISTRICT", center_x, int(main_panel.y + 92), 16, TEXT_DIM)
        draw_text_centered(f"{self.layout_name.upper()}  |  {self.difficulty.upper()}  |  {self.ctx.mode_label().upper()}", center_x, int(main_panel.y + 124), 14, LIVE_GOLD)
        seed_label = self.seed_text if self.seed_text else "RANDOM"
        draw_text_centered(f"SEED {seed_label}", center_x, int(main_panel.y + 144), 13, LIVE_CYAN)
        if self.ctx.game_mode == "DailyChallenge":
            daily_status = "AVAILABLE" if self.ctx.daily_challenge_available() else f"NEXT {self._daily_countdown()}"
            draw_text_centered(f"DAILY {daily_status}", center_x, int(main_panel.y + 160), 12, LIVE_PINK)
        self._draw_button(self.btn_desktop, "DESKTOP", 0)
        self._draw_button(self.btn_mobile, "MOBILE", 1)
        self._draw_button(self.btn_easy, "EASY", 2)
        self._draw_button(self.btn_normal, "NORMAL", 3)
        self._draw_button(self.btn_hard, "HARD", 4)
        self._draw_button(self.btn_start, "START GAME", 5)
        self._draw_button(self.btn_modes, "MODES", 6)
        self._draw_button(self.btn_replays, "REPLAYS", 7)
        self._draw_button(self.btn_achievements, "ACHIEVEMENTS", 8)
        self._draw_button(self.btn_options, "OPTIONS", 9)
        self._draw_button(self.btn_exit, "EXIT", 10)
        draw_scene_footer(main_panel)

    def _draw_replay_hall(self, main_panel) -> None:
        replays = list_replays(5)
        if not replays:
            return
        x = int(main_panel.x + main_panel.width + 18)
        width = 300
        if x + width > self.ctx.cfg.window_width - 18:
            return
        y = int(main_panel.y + 120)
        pyray.draw_text("REPLAY HALL", x, y, 18, LIVE_GOLD)
        y += 28
        for index, replay in enumerate(replays, start=1):
            pyray.draw_text(f"{index}. {replay.score}  seed {replay.seed:06d}", x, y, 14, colors.WHITE if index == 1 else TEXT_DIM)
            y += 20
