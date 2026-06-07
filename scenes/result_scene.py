from __future__ import annotations

import math

import core.raylib_api as pyray
from core import colors

from core.scene import Scene
from core.scene_ids import DIALOGUE_SCENE, GAME_SCENE, MENU_SCENE, REPLAY_VIEWER_SCENE
from ui.components import ProgressBar, StatusBadge
from ui.navigation import ButtonNavigator
from ui.style import UI_STYLE
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK, PANEL_ACCENT, TEXT_DIM, button_clicked, centered_rect, draw_arcade_background, draw_button, draw_cinematic_menu_background, draw_dashboard_rail, draw_glass_card, draw_panel, draw_presentation_bars, draw_scene_footer, draw_scene_scan_intro, draw_text_centered, draw_title_glitch_pass
from utils.score_storage import save_high_score


class ResultScene(Scene):
    BTN_W = UI_STYLE.sizes.button_width
    BTN_H = UI_STYLE.sizes.button_height
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.btn_action = None
        self.btn_save_replay = None
        self.btn_watch_replay = None
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
        panel_width = min(620, cfg.window_width - 120)
        panel_height = min(760, cfg.window_height - 80)
        panel_x = cx - panel_width // 2
        panel_y = max(44, int((cfg.window_height - panel_height) / 2))
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

        button_y = int(panel_y + panel_height - 76)
        action_w = min(220, self.BTN_W)
        small_w = 150
        gap = 12
        self.btn_save_replay = pyray.Rectangle(cx - small_w - gap - action_w // 2, button_y, small_w, self.BTN_H)
        self.btn_action = centered_rect(cx, button_y, action_w, self.BTN_H)
        self.btn_watch_replay = pyray.Rectangle(cx + action_w // 2 + gap, button_y, small_w, self.BTN_H)
        self.navigator = ButtonNavigator(3, initial_index=1)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        self.intro_timer = max(0.0, self.intro_timer - dt)
        self.navigator.move_vertical()

        if button_clicked(self.btn_save_replay):
            self.navigator.focus_index = 0
            self._save_replay()
        if button_clicked(self.btn_action):
            self.navigator.focus_index = 1
            self._activate_primary_action()
        if button_clicked(self.btn_watch_replay):
            self.navigator.focus_index = 2
            self._watch_replay()
        if self.navigator.move_horizontal_within(3):
            self.ctx.play_sfx("ui_confirm")
        if self.navigator.confirm_pressed():
            if self.navigator.focus_index == 0:
                self._save_replay()
            elif self.navigator.focus_index == 2:
                self._watch_replay()
            else:
                self._activate_primary_action()

    def _save_replay(self) -> None:
        recorder = self.ctx.replay_recorder
        if recorder is None or not recorder.frames:
            self.ctx.play_sfx("ui_back")
            return
        path = recorder.save(score=self.ctx.score, seed=self.ctx.current_level_seed())
        self.ctx.selected_replay_path = str(path)
        self.ctx.play_sfx("ui_confirm")
        if self.ctx.notification_manager is not None:
            self.ctx.notification_manager.push("Replay Saved", path.name)

    def _watch_replay(self) -> None:
        recorder = self.ctx.replay_recorder
        if self.ctx.selected_replay_path is None and recorder is not None and recorder.saved_path is not None:
            self.ctx.selected_replay_path = str(recorder.saved_path)
        if self.ctx.selected_replay_path is None:
            self._save_replay()
        if self.ctx.selected_replay_path is None:
            return
        self.ctx.play_sfx("ui_confirm")
        self.request_switch(REPLAY_VIEWER_SCENE)

    def _activate_primary_action(self) -> None:
        if self.ctx.last_result == "level_complete":
            self.ctx.play_sfx("ui_confirm")
            self.ctx.play_transition_effect(LIVE_CYAN, 0.4, 0.5, 3.0, 0.4)
            if self.ctx.queue_dialogue_for_level_clear():
                self.request_switch(DIALOGUE_SCENE)
                return
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
        compact = panel.height < 720

        draw_text_centered("RUN REPORT", center_x, int(panel.y + 24), 16, PANEL_ACCENT)
        draw_text_centered(result_text, center_x, int(panel.y + 54), 36 if compact else 42, result_color)
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
        draw_text_centered(report_subtitle, center_x, int(panel.y + 98), 14, TEXT_DIM)
        draw_dashboard_rail(center_x, int(panel.y + 116), 280, label="RUN SUMMARY", accent_color=result_color, time_s=self.ctx.visual_time)

        content_x = panel.x + 40
        content_w = int(panel.width - 80)
        score_y = int(panel.y + 146 if compact else panel.y + 150)
        score_h = 138 if compact else 156
        summary_y_pos = score_y + score_h + 12
        summary_h = 104 if compact else 118
        breakdown_y_pos = summary_y_pos + summary_h + 12
        breakdown_h = 78 if compact else 92
        profile_y_pos = breakdown_y_pos + breakdown_h + 12
        profile_h = 68 if compact else 82

        score_card = pyray.Rectangle(content_x, score_y, content_w, score_h)
        draw_glass_card(score_card, accent_color=result_color, glow_alpha=10, time_s=self.ctx.visual_time)
        score_label = "CURRENT SCORE" if self.ctx.last_result == "level_complete" else "FINAL SCORE"
        draw_text_centered(score_label, center_x, int(score_card.y + 16), 15, TEXT_DIM)
        draw_text_centered(str(self.ctx.score), center_x, int(score_card.y + 40), 54 if compact else 64, colors.WHITE)
        draw_text_centered(f"HIGH SCORE {self.ctx.high_score}", center_x, int(score_card.y + score_card.height - 34), 16, LIVE_GOLD)
        draw_text_centered(f"SEED {self.ctx.current_level_seed():06d}", center_x, int(score_card.y + score_card.height - 56), 14, LIVE_CYAN)
        score_target = max(1, self.ctx.high_score, self.ctx.score)
        ProgressBar(
            pyray.Rectangle(score_card.x + 42, score_card.y + score_card.height - 18, score_card.width - 84, 10),
            self.ctx.score / score_target,
            result_color,
        ).draw()

        summary_card = pyray.Rectangle(content_x, summary_y_pos, content_w, summary_h)
        draw_glass_card(summary_card, accent_color=result_color, glow_alpha=8, time_s=self.ctx.visual_time)
        draw_text_centered(self._status_label(), center_x, int(summary_card.y + 14), 16, TEXT_DIM)

        summary_y = int(summary_card.y + 38)
        for line in self._summary_lines()[:3]:
            draw_text_centered(line, center_x, summary_y, 15, TEXT_DIM)
            summary_y += 20 if compact else 22

        breakdown_card = pyray.Rectangle(content_x, breakdown_y_pos, content_w, breakdown_h)
        draw_glass_card(breakdown_card, accent_color=PANEL_ACCENT, glow_alpha=6, fill_alpha=150, time_s=self.ctx.visual_time)
        draw_text_centered("RUN BREAKDOWN", center_x, int(breakdown_card.y + 12), 15, TEXT_DIM)
        breakdown_y = int(breakdown_card.y + 34)
        for line in self._breakdown_lines():
            draw_text_centered(line, center_x, breakdown_y, 14, colors.WHITE if breakdown_y == int(breakdown_card.y + 34) else TEXT_DIM)
            breakdown_y += 15 if compact else 17

        profile_card = pyray.Rectangle(content_x, profile_y_pos, content_w, profile_h)
        draw_glass_card(profile_card, accent_color=self._progression_accent(), glow_alpha=6, time_s=self.ctx.visual_time)
        draw_text_centered("PROGRESSION UPDATE", center_x, int(profile_card.y + 12), 15, TEXT_DIM)
        StatusBadge(
            pyray.Rectangle(profile_card.x + profile_card.width - 132, profile_card.y + 10, 102, 42),
            "Grade",
            self.ctx.current_run_grade(self.ctx.last_result),
            self._progression_accent(),
        ).draw(time_s=self.ctx.visual_time)
        profile_y = int(profile_card.y + 34)
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
        for line in profile_lines[:2 if compact else 3]:
            draw_text_centered(line, center_x - 34, profile_y, 14, TEXT_DIM)
            profile_y += 15 if compact else 17

        draw_text_centered("REPLAY / CONTINUE", center_x, int(self.btn_action.y - 24), 15, TEXT_DIM)
        draw_button(self.btn_save_replay, "SAVE REPLAY", focused=self.navigator.focus_index == 0, time_s=self.ctx.visual_time)
        draw_button(self.btn_action, button_text, focused=self.navigator.focus_index == 1, time_s=self.ctx.visual_time)
        draw_button(self.btn_watch_replay, "WATCH REPLAY", focused=self.navigator.focus_index == 2, time_s=self.ctx.visual_time)
        if self.intro_timer > 0.0:
            draw_scene_scan_intro(cfg.window_width, cfg.window_height, intro_progress, accent_color=result_color, time_s=self.ctx.visual_time)
        draw_scene_footer(panel)
        draw_presentation_bars(cfg.window_width, cfg.window_height)
