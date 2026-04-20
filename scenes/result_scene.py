from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import GAME_SCENE, MENU_SCENE
from ui.navigation import ButtonNavigator
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK, PANEL_ACCENT, TEXT_DIM, button_clicked, centered_rect, draw_arcade_background, draw_button, draw_cinematic_menu_background, draw_dashboard_rail, draw_glass_card, draw_panel, draw_presentation_bars, draw_scene_footer, draw_scene_scan_intro, draw_text_centered, draw_title_glitch_pass
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
        self.intro_timer = 0.0

    def enter_tree(self) -> None:
        # Save high score when entering result screen
        save_high_score(self.ctx.high_score)
        if self.ctx.last_result in {"game_won", "lose", "challenge_failed", "abandon"}:
            self.ctx.finalize_run_result(self.ctx.last_result)
        self.intro_timer = 1.0

        cfg = self.ctx.cfg
        cx = cfg.window_width // 2
        panel_width = min(560, cfg.window_width - 120)
        panel_height = min(820, cfg.window_height - 96)
        panel_x = cx - panel_width // 2
        panel_y = max(44, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        self.btn_action = centered_rect(cx, int(panel_y + panel_height - 118), self.BTN_W, self.BTN_H)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        self.intro_timer = max(0.0, self.intro_timer - dt)
        self.navigator.move_vertical()

        if button_clicked(self.btn_action) or self.navigator.confirm_pressed():
            self._activate_primary_action()

    def _activate_primary_action(self) -> None:
        if self.ctx.last_result == "level_complete":
            self.ctx.play_sfx("ui_confirm")
            self.ctx.play_transition_effect(LIVE_CYAN, 0.4, 0.5, 3.0, 0.4)
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
            if self.ctx.game_mode == "Arcade":
                chapter = self.ctx.arcade_campaign_chapter()
                if chapter is not None:
                    return [
                        f"{chapter.subtitle.title()} secured.",
                        chapter.briefing.capitalize() + ".",
                        self.ctx.arcade_chapter_reward_line() or "Move to the next campaign district.",
                    ]
            if self.ctx.game_mode == "Endless":
                tier = self.ctx.endless_tier()
                return [
                    f"{tier.title.title()} secured.",
                    "Lives carry forward into the next wave.",
                    "Deeper districts hit harder and pay more.",
                ]
            if self.ctx.game_mode == "Time Attack":
                return [
                    "District clock beaten cleanly.",
                    f"Bank {math.ceil(self.ctx.time_attack_clear_bonus_seconds())} extra seconds for the next board.",
                    "Tempo routes matter more than safe resets.",
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
            if self.ctx.game_mode == "Arcade":
                return [
                    "Campaign run completed across all districts.",
                    "Your arcade file records a full clear.",
                    "Return to menu to launch another campaign.",
                ]
            if self.ctx.game_mode == "Time Attack":
                return [
                    "Clock run completed across all three districts.",
                    "Your fastest tempo clear has been logged.",
                    "Return to menu to race another route.",
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

        if self.ctx.last_result == "abandon":
            return [
                "Run closed by operator input.",
                "Score and progression up to this point were recorded.",
                "Return to menu to queue the next district.",
            ]

        if self.ctx.game_mode == "Time Attack":
            return [
                "The district clock hit zero.",
                "Your score and mastery gain were still recorded.",
                "Return to menu to queue another clock run.",
            ]
        return [
            "Pacman ran out of lives.",
            "Your high score has been saved.",
            "Return to menu to try again.",
        ]

    def _result_header(self) -> tuple[str, object, str]:
        if self.ctx.last_result == "level_complete":
            if self.ctx.game_mode == "Endless":
                return ("DISTRICT SECURED", LIVE_CYAN, "NEXT LOOP")
            if self.ctx.game_mode == "Time Attack":
                return ("CLOCK DISTRICT CLEARED", LIVE_GOLD, "BANK TIME")
            return (f"LEVEL {self.ctx.current_level} COMPLETE!", LIVE_CYAN, "NEXT LEVEL")

        if self.ctx.last_result == "game_won":
            if self.ctx.game_mode == "Challenge":
                return ("TRIAL CLEARED", LIVE_GOLD, "BACK TO MENU")
            if self.ctx.game_mode == "Time Attack":
                return ("CLOCK RUN COMPLETE", LIVE_GOLD, "BACK TO MENU")
            if self.ctx.game_mode == "Arcade":
                return ("CAMPAIGN COMPLETE", LIVE_GOLD, "BACK TO MENU")
            return ("FULL RUN CLEAR", LIVE_GOLD, "BACK TO MENU")

        if self.ctx.last_result == "challenge_failed":
            return ("TRIAL FAILED", LIVE_PINK, "BACK TO MENU")
        if self.ctx.last_result == "abandon":
            return ("RUN ABORTED", LIVE_PINK, "BACK TO MENU")

        if self.ctx.game_mode == "Time Attack":
            return ("TIME OUT", LIVE_GOLD, "BACK TO MENU")
        return ("GAME OVER", LIVE_PINK, "BACK TO MENU")

    def _status_label(self) -> str:
        if self.ctx.last_result == "level_complete":
            return "CLEAR STATUS"
        if self.ctx.last_result == "game_won":
            return "RUN STATUS"
        if self.ctx.last_result == "challenge_failed":
            return "TRIAL STATUS"
        if self.ctx.last_result == "abandon":
            return "RUN STATUS"
        return "FAIL STATUS"

    def _progression_accent(self):
        if self.ctx.last_result in {"lose", "challenge_failed", "abandon"}:
            return LIVE_GOLD if self.ctx.game_mode == "Time Attack" else LIVE_PINK
        if self.ctx.game_mode == "Challenge":
            return LIVE_PINK
        if self.ctx.game_mode == "Time Attack":
            return LIVE_GOLD
        return LIVE_PINK

    def _breakdown_lines(self) -> tuple[str, str, str]:
        stats = self.ctx.run_stats
        trait = self.ctx.current_map_trait()
        medals = self.ctx.earned_style_medals(self.ctx.last_result)
        score_line = self.ctx.score_focus_summary_lines()[0]
        medal_line = " | ".join(medals[:2]) if medals else self.ctx.score_focus_summary_lines()[2]
        grade = self.ctx.current_run_grade(self.ctx.last_result)
        if self.ctx.last_result == "level_complete":
            return (
                f"{trait.title}  |  {self.ctx.current_map_scene_tag()}  |  Grade {grade}",
                score_line,
                medal_line,
            )
        if self.ctx.last_result == "game_won":
            return (
                f"Run Won  |  {self.ctx.mode_label()}  |  Grade {grade}",
                score_line,
                medal_line,
            )
        if self.ctx.last_result == "challenge_failed":
            return (
                f"Trial Missed  |  {self.ctx.challenge_preset().title}  |  Grade {grade}",
                self.ctx.score_focus_summary_lines()[1],
                medal_line,
            )
        if self.ctx.last_result == "abandon":
            return (
                f"Run Aborted  |  {self.ctx.mode_label()}  |  Grade {grade}",
                self.ctx.score_focus_summary_lines()[1],
                medal_line,
            )
        killer_map = {
            "Blinky": "Blinky cut the route",
            "Pinky": "Pinky held the front",
            "Inky": "Inky slipped the flank",
            "Clyde": "Clyde flipped the read",
        }
        return (
            f"Run Lost  |  {self.ctx.mode_label()}  |  Grade {grade}",
            self.ctx.death_reason_detail(),
            medal_line,
        )

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
        draw_panel(panel, "RUN REPORT", time_s=self.ctx.visual_time)
        result_text, result_color, button_text = self._result_header()
        intro_progress = min(1.0, 1.0 - self.intro_timer / 1.0) if self.intro_timer > 0.0 else 1.0

        draw_text_centered("RUN REPORT", center_x, int(panel.y + 24), 18, PANEL_ACCENT)
        draw_text_centered(result_text, center_x, int(panel.y + 54), 42, result_color)
        if self.intro_timer > 0.0:
            draw_title_glitch_pass(center_x, int(panel.y + 70), 380, intro_progress, accent_color=result_color, time_s=self.ctx.visual_time)
        report_subtitle = "NEON DISTRICT REPORT"
        if self.ctx.game_mode == "Arcade":
            chapter = self.ctx.arcade_campaign_chapter()
            if chapter is not None:
                report_subtitle = f"{chapter.title}  |  {chapter.subtitle}"
        elif self.ctx.game_mode == "Endless":
            tier = self.ctx.endless_tier()
            report_subtitle = f"{tier.title}  |  {tier.subtitle.upper()}"
        elif self.ctx.game_mode == "Time Attack":
            report_subtitle = f"TIME ATTACK  |  T-{max(0, math.ceil(self.ctx.time_attack_seconds)):02d} BANKED"
        draw_text_centered(report_subtitle, center_x, int(panel.y + 98), 16, TEXT_DIM)
        draw_dashboard_rail(center_x, int(panel.y + 116), 280, label="RUN SUMMARY", accent_color=result_color, time_s=self.ctx.visual_time)

        score_card = pyray.Rectangle(panel.x + 34, panel.y + 152, int(panel.width - 68), 118)
        draw_glass_card(score_card, accent_color=result_color, glow_alpha=16, time_s=self.ctx.visual_time)
        score_label = "CURRENT SCORE" if self.ctx.last_result == "level_complete" else "FINAL SCORE"
        draw_text_centered(score_label, center_x, int(score_card.y + 18), 18, TEXT_DIM)
        draw_text_centered(str(self.ctx.score), center_x, int(score_card.y + 48), 34, colors.WHITE)
        draw_text_centered(f"HIGH SCORE {self.ctx.high_score}", center_x, int(score_card.y + 84), 20, LIVE_GOLD)

        summary_card = pyray.Rectangle(panel.x + 34, panel.y + 292, int(panel.width - 68), 132)
        draw_glass_card(summary_card, accent_color=result_color, glow_alpha=14, time_s=self.ctx.visual_time)
        draw_text_centered(self._status_label(), center_x, int(summary_card.y + 16), 18, TEXT_DIM)

        summary_y = int(summary_card.y + 52)
        for line in self._summary_lines():
            draw_text_centered(line, center_x, summary_y, 16, TEXT_DIM)
            summary_y += 24

        breakdown_card = pyray.Rectangle(panel.x + 34, panel.y + 438, int(panel.width - 68), 94)
        draw_glass_card(breakdown_card, accent_color=PANEL_ACCENT, glow_alpha=10, fill_alpha=150, time_s=self.ctx.visual_time)
        draw_text_centered("RUN BREAKDOWN", center_x, int(breakdown_card.y + 12), 16, TEXT_DIM)
        breakdown_y = int(breakdown_card.y + 34)
        for line in self._breakdown_lines():
            draw_text_centered(line, center_x, breakdown_y, 15, colors.WHITE if breakdown_y == int(breakdown_card.y + 34) else TEXT_DIM)
            breakdown_y += 18

        profile_card = pyray.Rectangle(panel.x + 34, panel.y + 546, int(panel.width - 68), 102)
        draw_glass_card(profile_card, accent_color=self._progression_accent(), glow_alpha=12, time_s=self.ctx.visual_time)
        draw_text_centered("PROGRESSION UPDATE", center_x, int(profile_card.y + 14), 18, TEXT_DIM)
        profile_y = int(profile_card.y + 40)
        mastery_gain = self.ctx.mode_mastery_gain(self.ctx.last_result)
        grade = self.ctx.current_run_grade(self.ctx.last_result)
        record_lines = self.ctx.record_book_summary_lines()
        daily_lines = self.ctx.daily_directive_summary_lines()
        if self.ctx.game_mode == "Challenge":
            credit_gain = self.ctx.challenge_credit_reward(self.ctx.last_result)
            profile_lines = (
                f"{self.ctx.challenge_preset().title}  |  Grade {grade}  |  +{credit_gain}C",
                record_lines[1],
                daily_lines[0],
            )
        else:
            profile_lines = (
                f"{self.ctx.game_mode} {self.ctx.mode_mastery_rank(self.ctx.game_mode)} +{mastery_gain}  |  Grade {grade}",
                record_lines[0],
                daily_lines[0],
            )
        for line in profile_lines:
            draw_text_centered(line, center_x, profile_y, 16, TEXT_DIM)
            profile_y += 22

        unlock_card = pyray.Rectangle(panel.x + 34, panel.y + 664, int(panel.width - 68), 94)
        reward_accent = LIVE_GOLD if self.ctx.last_unlocks_are_new else PANEL_ACCENT
        reward_label = "NEW REWARDS" if self.ctx.last_unlocks_are_new else "NEXT REWARDS"
        draw_glass_card(unlock_card, accent_color=reward_accent, glow_alpha=10, fill_alpha=148, time_s=self.ctx.visual_time)
        draw_text_centered(reward_label, center_x, int(unlock_card.y + 12), 16, TEXT_DIM)
        unlock_y = int(unlock_card.y + 34)
        for line in self.ctx.reward_showcase_lines():
            if not line:
                continue
            draw_text_centered(line, center_x, unlock_y, 14, colors.WHITE)
            unlock_y += 18

        draw_text_centered("CONTINUE", center_x, int(panel.y + panel.height - 136), 18, TEXT_DIM)
        draw_button(self.btn_action, button_text, focused=True, time_s=self.ctx.visual_time)
        if self.intro_timer > 0.0:
            draw_scene_scan_intro(cfg.window_width, cfg.window_height, intro_progress, accent_color=result_color, time_s=self.ctx.visual_time)
        draw_scene_footer(panel)
        draw_presentation_bars(cfg.window_width, cfg.window_height)
