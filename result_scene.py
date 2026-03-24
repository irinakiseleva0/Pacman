from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import GAME_SCENE, MENU_SCENE
from ui.navigation import ButtonNavigator
from ui.ui import PANEL_ACCENT, TEXT_DIM, button_clicked, centered_rect, draw_arcade_background, draw_button, draw_cinematic_menu_background, draw_glass_card, draw_panel, draw_scene_footer, draw_text_centered
from utils.score_storage import save_high_score


class ResultScene(Scene):
    BTN_W = 240
    BTN_H = 58
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.btn_action = None
        self.navigator = ButtonNavigator(1)
        self.panel = None

    def enter_tree(self) -> None:
        # Save high score when entering result screen
        save_high_score(self.ctx.high_score)
        if self.ctx.last_result in {"game_won", "lose", "challenge_failed"}:
            self.ctx.finalize_run_result(self.ctx.last_result)

        cfg = self.ctx.cfg
        cx = cfg.window_width // 2
        panel_width = min(560, cfg.window_width - 120)
        panel_height = min(760, cfg.window_height - 120)
        panel_x = cx - panel_width // 2
        panel_y = max(44, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        self.btn_action = centered_rect(cx, int(panel_y + panel_height - 118), self.BTN_W, self.BTN_H)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        self.navigator.move_vertical()

        if button_clicked(self.btn_action) or self.navigator.confirm_pressed():
            self._activate_primary_action()

    def _activate_primary_action(self) -> None:
        if self.ctx.last_result == "level_complete":
            self.ctx.play_sfx("ui_confirm")
            self.ctx.play_transition_effect(colors.GREEN, 0.4, 0.5, 3.0, 0.4)
            self.ctx.next_level()
            self.request_switch(GAME_SCENE)
            return

        if self.ctx.last_result in {"lose", "challenge_failed"}:
            self.ctx.play_sfx("lose")
        else:
            self.ctx.play_sfx("ui_back")
        self.ctx.reset_run_state()
        self.request_switch(MENU_SCENE)

    def _summary_lines(self) -> list[str]:
        if self.ctx.last_result == "level_complete":
            if self.ctx.game_mode == "Endless":
                return [
                    "District cleared. The loop keeps going.",
                    "Your remaining lives carry forward.",
                    "Push deeper for a bigger score run.",
                ]
            return [
                "Board cleared successfully.",
                "Carry your score into the next level.",
                "Take a breath, the ghosts will reset.",
            ]

        if self.ctx.last_result == "game_won":
            if self.ctx.game_mode == "Challenge":
                return [
                    "Challenge district cleared in one life.",
                    "This counts as a prestige run clear.",
                    "Return to menu to queue another test.",
                ]
            return [
                "All levels completed.",
                "A full win has been recorded.",
                "Return to menu to start a new run.",
            ]

        if self.ctx.last_result == "challenge_failed":
            preset = self.ctx.challenge_preset()
            if preset.target_score > 0:
                return [
                    "Board cleared, but score target was missed.",
                    f"Needed {preset.target_score} score for the clear.",
                    "Return to menu and arm another trial.",
                ]
            if preset.target_ghosts > 0:
                return [
                    "Board cleared, but ghost quota was missed.",
                    f"Needed {preset.target_ghosts} ghosts eaten in-run.",
                    "Return to menu and queue another hunt.",
                ]
            return [
                "Challenge target missed.",
                "The trial did not count as a clear.",
                "Return to menu to try again.",
            ]

        return [
            "Pacman ran out of lives.",
            "Your high score has been saved.",
            "Return to menu to try again.",
        ]

    def draw(self) -> None:
        cfg = self.ctx.cfg
        center_x = cfg.window_width // 2
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "RUN REPORT")

        if self.ctx.last_result == "level_complete":
            result_text = f"LEVEL {self.ctx.current_level} COMPLETE!"
            result_color = colors.GREEN
            button_text = "NEXT LOOP" if self.ctx.game_mode == "Endless" else "NEXT LEVEL"
        elif self.ctx.last_result == "game_won":
            result_text = "CHALLENGE CLEARED!" if self.ctx.game_mode == "Challenge" else "YOU WON THE GAME!"
            result_color = colors.GOLD
            button_text = "BACK TO MENU"
        elif self.ctx.last_result == "challenge_failed":
            result_text = "CHALLENGE FAILED"
            result_color = colors.RED
            button_text = "BACK TO MENU"
        else:  # "lose"
            result_text = "GAME OVER"
            result_color = colors.RED
            button_text = "BACK TO MENU"

        draw_text_centered("RUN REPORT", center_x, int(panel.y + 24), 18, PANEL_ACCENT)
        draw_text_centered(result_text, center_x, int(panel.y + 54), 42, result_color)
        draw_text_centered("NEON DISTRICT REPORT", center_x, int(panel.y + 98), 16, TEXT_DIM)

        score_card = pyray.Rectangle(panel.x + 34, panel.y + 152, int(panel.width - 68), 118)
        draw_glass_card(score_card, accent_color=result_color, glow_alpha=16)
        score_label = "CURRENT SCORE" if self.ctx.last_result == "level_complete" else "FINAL SCORE"
        draw_text_centered(score_label, center_x, int(score_card.y + 18), 18, TEXT_DIM)
        draw_text_centered(str(self.ctx.score), center_x, int(score_card.y + 48), 34, colors.WHITE)
        draw_text_centered(f"HIGH SCORE {self.ctx.high_score}", center_x, int(score_card.y + 84), 20, colors.YELLOW)

        summary_card = pyray.Rectangle(panel.x + 34, panel.y + 292, int(panel.width - 68), 148)
        draw_glass_card(summary_card, accent_color=PANEL_ACCENT, glow_alpha=14)
        draw_text_centered("STATUS", center_x, int(summary_card.y + 16), 18, TEXT_DIM)

        summary_y = int(summary_card.y + 52)
        for line in self._summary_lines():
            draw_text_centered(line, center_x, summary_y, 18, TEXT_DIM)
            summary_y += 28

        profile_card = pyray.Rectangle(panel.x + 34, panel.y + 456, int(panel.width - 68), 120)
        draw_glass_card(profile_card, accent_color=colors.MAGENTA, glow_alpha=12)
        draw_text_centered("PROGRESSION", center_x, int(profile_card.y + 16), 18, TEXT_DIM)
        profile_y = int(profile_card.y + 48)
        mastery_gain = self.ctx.mode_mastery_gain(self.ctx.last_result)
        if self.ctx.game_mode == "Challenge":
            credit_gain = self.ctx.challenge_credit_reward(self.ctx.last_result)
            profile_lines = (
                f"Challenge {self.ctx.challenge_track_rank()} +{credit_gain}C",
                self.ctx.challenge_progress_lines()[1],
                self.ctx.profile_summary_lines()[1],
            )
        else:
            profile_lines = (
                f"{self.ctx.game_mode} {self.ctx.mode_mastery_rank(self.ctx.game_mode)} +{mastery_gain}",
                self.ctx.profile_summary_lines()[0],
                self.ctx.profile_summary_lines()[1],
            )
        tag = self.ctx.challenge_preset().title if self.ctx.game_mode == "Challenge" else self.ctx.mode_label()
        profile_lines = (f"{tag} / {self.ctx.rank_title()}",) + profile_lines[:2]
        for line in profile_lines:
            draw_text_centered(line, center_x, profile_y, 16, TEXT_DIM)
            profile_y += 22

        unlock_card = pyray.Rectangle(panel.x + 34, panel.y + 592, int(panel.width - 68), 92)
        draw_glass_card(unlock_card, accent_color=PANEL_ACCENT, glow_alpha=10, fill_alpha=148)
        draw_text_centered("UNLOCKS", center_x, int(unlock_card.y + 12), 16, TEXT_DIM)
        unlock_y = int(unlock_card.y + 34)
        for line in self.ctx.last_unlock_lines:
            if not line:
                continue
            draw_text_centered(line, center_x, unlock_y, 14, colors.WHITE)
            unlock_y += 18

        draw_text_centered("CONTINUE", center_x, int(panel.y + panel.height - 156), 18, TEXT_DIM)
        draw_button(self.btn_action, button_text, focused=True)
        draw_scene_footer(panel)
