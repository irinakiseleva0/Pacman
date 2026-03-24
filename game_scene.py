from __future__ import annotations

from dataclasses import dataclass
import math

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import MENU_SCENE, PAUSE_SCENE, RESULT_SCENE
from maps.class_map import Map
from entities.pacman import State
from ui.hud import draw_game_hud
from ui.mobile_controls import draw_mobile_controls, handle_mobile_controls
from ui.ui import PANEL_ACCENT, TEXT_DIM, draw_glass_card, draw_live_board_backdrop, draw_live_game_background, draw_live_panel_accent, draw_panel, draw_shadowed_text_centered, draw_text_centered
from utils.visual_effects import with_alpha


@dataclass
class SceneTransition:
    kind: str
    ticks: int
    result: str = ""


class GameScene(Scene):
    TOTAL_LEVELS = 3

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.tick_counter = 0
        self.transition: SceneTransition | None = None
        self.visual_time = 0.0
        self.tutorial_stage = 0

    def enter_tree(self) -> None:
        self.tick_counter = 0
        self.transition = None
        self.visual_time = 0.0
        self.ctx.visual_time = 0.0
        self.tutorial_stage = 1 if self._tutorial_active() else 0

        if self.ctx.should_resume_game and self.ctx.game_map is not None:
            self.ctx.should_resume_game = False
            return

        self.ctx.play_transition_effect(self.ctx.effect_palette()["ready_flash"], 0.2, 0.6)
        self.ctx.last_result = ""

        # Load the current level's map
        map_path = self.ctx.get_map_path()
        self.ctx.reset_ghost_mode_cycle()
        self.ctx.game_map = Map(self.ctx, path=map_path)
        self.ctx.should_resume_game = False
        self.transition = SceneTransition("ready", self.ctx.cfg.ready_duration_ticks)

    def update(self, dt: float) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        if pyray.is_key_pressed(pyray.KEY_ESCAPE):
            self.request_switch(MENU_SCENE)
            return

        if pyray.is_key_pressed(pyray.KEY_P):
            self.request_switch(PAUSE_SCENE)
            return

        mobile_action = handle_mobile_controls(self.ctx)
        if mobile_action == "pause":
            self.request_switch(PAUSE_SCENE)
            return

        self.visual_time += dt
        self.ctx.visual_time = self.visual_time

        self.tick_counter += 1
        game_map.frame()

        self._update_tutorial_state(mobile_action)

        if self.transition is not None:
            self.transition.ticks -= 1
            if self.transition.ticks == 0:
                self.finish_transition()
            return

        if self.tick_counter >= self.ctx.cfg.logic_tick_rate:
            self.tick_counter = 0
            pressure_changed = self.ctx.advance_ghost_mode_cycle(
                game_map.remaining_pickups(),
                getattr(game_map, "total_pickups", 0),
            )
            if pressure_changed and self.ctx.pressure_stage > 0:
                palette = self.ctx.effect_palette()
                flash_strength = 0.04 + self.ctx.pressure_stage * 0.02
                shake_strength = 1.8 + self.ctx.pressure_stage * 0.7
                self.ctx.trigger_screen_flash(palette["ghost"], flash_strength, 0.05)
                self.ctx.trigger_screen_shake(shake_strength, 0.08)
            game_map.process()

        # Update visual effects
        dt = pyray.get_frame_time()
        self.ctx.particles.update(dt)
        self.ctx.screen_shake.update(dt)
        self.ctx.floating_text.update(dt)
        self.ctx.screen_flash.update(dt)

        if self.ctx.score > self.ctx.high_score:
            self.ctx.high_score = self.ctx.score

        pacman = self.ctx.pacman
        if pacman is not None and pacman.state == State.NONE and self.transition is None:
            self.start_death_transition()
            return

        if game_map.remaining_seeds() == 0 and self.transition is None:
            self.start_level_complete_transition()
            return

    def start_death_transition(self) -> None:
        self.ctx.play_sfx("death")
        self.ctx.play_transition_effect(self.ctx.effect_palette()["death_flash"], 0.3, 0.2, 8.0, 0.5)

        self.ctx.lives -= 1

        if self.ctx.lives <= 0:
            self.transition = SceneTransition("death", self.ctx.cfg.game_over_pause_ticks, "lose")
            return

        self.transition = SceneTransition("death", self.ctx.cfg.death_pause_ticks, "reload")

    def finish_transition(self) -> None:
        if self.transition is None:
            return

        if self.transition.kind == "ready":
            self.ctx.play_transition_effect(self.ctx.effect_palette()["power_flash"], 0.15, 0.12)
            self.transition = None
            return

        if self.transition.kind == "death" and self.transition.result == "lose":
            self.ctx.last_result = "lose"
            self.request_switch(RESULT_SCENE)
            self.transition = None
            return

        if self.transition.kind == "death":
            map_path = self.ctx.get_map_path()
            self.ctx.reset_ghost_mode_cycle()
            self.ctx.game_map = Map(self.ctx, path=map_path)
            self.tick_counter = 0
            self.transition = SceneTransition("ready", self.ctx.cfg.ready_duration_ticks)
            return

        if self.transition.kind == "level_complete":
            self.ctx.last_result = self.transition.result or "level_complete"
            self.request_switch(RESULT_SCENE)
            self.transition = None

    def start_level_complete_transition(self) -> None:
        transition_result = "level_complete"
        if self.ctx.game_mode == "Challenge":
            transition_result = self.ctx.challenge_result_on_clear()
        elif self.ctx.run_won_on_level_clear():
            transition_result = "game_won"
        clear_bonus = self.ctx.mode_clear_bonus()
        directive_bonus = self.ctx.directive_clear_bonus()
        if clear_bonus > 0:
            self.ctx.score += clear_bonus
            if self.ctx.game_map is not None and self.ctx.pacman is not None:
                self.ctx.floating_text.add_text(
                    f"CLEAR +{clear_bonus}",
                    self.ctx.pacman.x * 16 - 10,
                    self.ctx.pacman.y * 16 - 26,
                    colors.GOLD,
                    1.1,
                    14,
                )
        if directive_bonus > 0 and self.ctx.game_map is not None and self.ctx.pacman is not None:
            self.ctx.score += directive_bonus
            directive = self.ctx.current_run_directive()
            self.ctx.floating_text.add_text(
                f"{directive.title} +{directive_bonus}",
                self.ctx.pacman.x * 16 - 18,
                self.ctx.pacman.y * 16 - 44,
                directive.accent,
                1.2,
                14,
            )
        self.ctx.play_sfx("win")
        self.ctx.record_level_cleared()
        self.ctx.reset_ghost_combo()
        self.ctx.play_transition_effect(self.ctx.effect_palette()["win_flash"], 0.25, 0.2, 3.0, 0.2)
        self.transition = SceneTransition(
            "level_complete",
            self.ctx.cfg.level_complete_duration_ticks,
            transition_result,
        )

    def draw(self) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return
        cfg = self.ctx.cfg

        # Apply screen shake offset
        shake_x, shake_y = self.ctx.screen_shake.get_offset()
        board_rect = pyray.Rectangle(cfg.board_offset_x, cfg.board_offset_y, cfg.board_width, cfg.board_height)

        draw_live_game_background(cfg.window_width, cfg.window_height, self.visual_time)
        draw_live_board_backdrop(board_rect, self.visual_time)

        game_map.draw()

        # Draw particles with shake offset
        effect_scale = cfg.tile_size / 16
        self.ctx.particles.draw(cfg.board_offset_x + shake_x, cfg.board_offset_y + shake_y, effect_scale)

        # Draw floating text with shake offset
        self.ctx.floating_text.draw(cfg.board_offset_x + shake_x, cfg.board_offset_y + shake_y, effect_scale)

        # Draw HUD (not affected by shake)
        self.draw_hud()

        if self.transition is None:
            self.draw_live_feedback()

        if self.transition is not None and self.transition.kind == "ready":
            self.draw_ready_overlay()
        elif self.transition is not None and self.transition.kind == "death":
            self.draw_death_overlay()
        elif self.transition is not None and self.transition.kind == "level_complete":
            self.draw_level_complete_overlay()

        if self.tutorial_stage > 0:
            self.draw_tutorial_overlay()

        # Draw screen flash overlay
        self.ctx.screen_flash.draw()

    def draw_hud(self) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        cfg = self.ctx.cfg
        hud_rect = pyray.Rectangle(cfg.hud_x, cfg.hud_y, cfg.hud_width, cfg.hud_height)
        draw_live_panel_accent(hud_rect, self.visual_time)
        draw_panel(hud_rect, "RUN STATUS")

        if cfg.hud_mode == "side":
            pyray.draw_rectangle_rec(
                pyray.Rectangle(cfg.hud_x - 3, 0, 3, cfg.window_height),
                PANEL_ACCENT,
            )
        else:
            pyray.draw_rectangle_rec(
                pyray.Rectangle(0, cfg.hud_y - 3, cfg.window_width, 3),
                PANEL_ACCENT,
            )

        hud_x = cfg.hud_x + 12
        hud_y = 52 if cfg.hud_mode == "side" else cfg.hud_y + 52
        hud_width = cfg.hud_width - 24
        hud_columns = cfg.hud_columns

        if cfg.layout_name == "mobile":
            controls_width = min(220, max(180, cfg.hud_width // 2))
            hud_width = max(150, cfg.hud_width - controls_width - 28)
            hud_columns = 1

        draw_game_hud(
            self.ctx,
            game_map.remaining_seeds(),
            game_map.cherry_status(),
            game_map.ghost_release_status(),
            game_map.ghost_return_status(),
            x=hud_x,
            y=hud_y,
            width=hud_width,
            height=cfg.hud_height - 60,
            font_size=cfg.hud_font_size,
            line_height=cfg.hud_line_height,
            columns=hud_columns,
        )

        draw_mobile_controls(self.ctx)

    def draw_live_feedback(self) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        palette = self.ctx.effect_palette()
        pulse = 0.5 + 0.5 * math.sin(self.visual_time * 4.2)
        center_x = self.ctx.cfg.window_width // 2
        top_y = 24

        pressure_stage = getattr(self.ctx, "pressure_stage", 0)
        rage_active = bool(getattr(self.ctx.pacman, "rage", False))

        if pressure_stage > 0:
            widths = {1: 220, 2: 250, 3: 278}
            labels = {
                1: ("PRESSURE RISING", "ghost routes tightening"),
                2: ("DANGER WINDOW", "late-board pressure live"),
                3: ("OVERRUN", "district at peak threat"),
            }
            accent = palette["ghost"]
            width = widths.get(pressure_stage, 278)
            headline, detail = labels.get(pressure_stage, labels[3])
            panel = pyray.Rectangle(center_x - width // 2, top_y, width, 54)
            draw_glass_card(panel, accent_color=accent, glow_alpha=int(12 + pulse * 16), fill_alpha=150)
            draw_text_centered(headline, center_x, int(panel.y + 10), 16, colors.WHITE)
            draw_text_centered(detail.upper(), center_x, int(panel.y + 30), 12, accent)

            if pressure_stage >= 2:
                edge_alpha = int(12 + pulse * 18)
                danger_color = colors.RED if pressure_stage >= 3 else accent
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(0, 0, self.ctx.cfg.window_width, 8),
                    with_alpha(danger_color, edge_alpha),
                )

        if rage_active:
            rage_timer = getattr(self.ctx.pacman, "rage_timer", 0)
            accent = palette["power_flash"]
            width = 248
            panel = pyray.Rectangle(center_x - width // 2, top_y + (66 if pressure_stage > 0 else 0), width, 54)
            draw_glass_card(panel, accent_color=accent, glow_alpha=int(16 + pulse * 14), fill_alpha=162)
            draw_text_centered("RAGE ACTIVE", center_x, int(panel.y + 10), 16, colors.WHITE)
            combo_text = f"combo x{self.ctx.ghost_combo + 1}" if self.ctx.ghost_combo > 0 else "ghosts vulnerable"
            if 0 < rage_timer <= 45:
                combo_text = "window collapsing"
            draw_text_centered(combo_text.upper(), center_x, int(panel.y + 30), 12, colors.GOLD)

        release_status = game_map.ghost_release_status()
        if release_status is not None and not rage_active:
            pending, total = release_status
            width = 188
            panel = pyray.Rectangle(24, 24, width, 46)
            draw_glass_card(panel, accent_color=PANEL_ACCENT, glow_alpha=10, fill_alpha=138)
            draw_text_centered("DEPLOYING", int(panel.x + panel.width / 2), int(panel.y + 10), 14, colors.WHITE)
            draw_text_centered(f"{pending}/{total} GHOSTS", int(panel.x + panel.width / 2), int(panel.y + 28), 12, TEXT_DIM)

    def _draw_transition_card(self, headline: str, detail: str, accent_color, *, width: int = 360) -> None:
        cfg = self.ctx.cfg
        center_x = cfg.window_width // 2
        center_y = cfg.window_height // 2
        card_h = 108 if detail else 84
        rect = pyray.Rectangle(center_x - width // 2, center_y - card_h // 2 - 8, width, card_h)
        draw_glass_card(rect, accent_color=accent_color, glow_alpha=20, fill_alpha=186)

        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x + 22, rect.y + 18, max(80, rect.width * 0.28), 2),
            accent_color,
        )
        draw_shadowed_text_centered(headline, center_x, int(rect.y + 20), 28, accent_color)
        if detail:
            draw_text_centered(detail, center_x, int(rect.y + 58), 15, colors.WHITE)

    def draw_ready_overlay(self) -> None:
        modifier = self.ctx.district_modifier()
        directive = self.ctx.current_run_directive()
        map_trait = self.ctx.current_map_trait()
        self._draw_transition_card(
            "READY",
            f"{map_trait.title}  |  {directive.title}",
            map_trait.accent,
            width=430,
        )

    def draw_death_overlay(self) -> None:
        if self.transition is not None and self.transition.result == "lose":
            self._draw_transition_card(
                "GAME OVER",
                "RUN TERMINATED",
                self.ctx.effect_palette()["death_flash"],
                width=380,
            )
        else:
            self._draw_transition_card(
                "LIFE LOST",
                "RELOADING DISTRICT",
                self.ctx.effect_palette()["death_flash"],
                width=380,
            )

    def draw_level_complete_overlay(self) -> None:
        transition_result = self.transition.result if self.transition is not None else ""
        if transition_result == "game_won":
            headline = "RUN CLEARED"
            headline_color = self.ctx.effect_palette()["win_flash"]
            detail = "FINALIZING RESULTS"
        elif transition_result == "challenge_failed":
            headline = "TRIAL FAILED"
            headline_color = self.ctx.effect_palette()["death_flash"]
            detail = "TARGET MISSED"
        else:
            headline = "LEVEL CLEAR"
            headline_color = self.ctx.effect_palette()["win_flash"]
            detail = "SYNCING NEXT REPORT"

        self._draw_transition_card(headline, detail, headline_color, width=420)

    def _tutorial_active(self) -> bool:
        return self.ctx.tutorial_enabled() and not self.ctx.tutorial_seen()

    def _movement_pressed(self) -> bool:
        return any(
            pyray.is_key_pressed(key)
            for key in (pyray.KEY_W, pyray.KEY_A, pyray.KEY_S, pyray.KEY_D, pyray.KEY_UP, pyray.KEY_DOWN, pyray.KEY_LEFT, pyray.KEY_RIGHT)
        )

    def _advance_tutorial(self, next_stage: int) -> None:
        self.tutorial_stage = next_stage
        if next_stage == 0:
            self.ctx.mark_tutorial_seen()

    def _update_tutorial_state(self, mobile_action: str | None) -> None:
        if self.tutorial_stage <= 0:
            return

        if self.transition is not None and self.transition.kind == "death":
            self._advance_tutorial(0)
            return

        if self.tutorial_stage == 1 and (self._movement_pressed() or mobile_action in {"up", "left", "right", "down"}):
            self._advance_tutorial(2)
            return

        if self.tutorial_stage == 2 and self.ctx.run_stats.dots_eaten > 0:
            self._advance_tutorial(3)
            return

        if self.tutorial_stage == 3 and self.ctx.run_stats.power_seeds_eaten > 0:
            self._advance_tutorial(4)
            return

        if self.tutorial_stage == 4 and self.navigator_confirm_like():
            self._advance_tutorial(0)

    def navigator_confirm_like(self) -> bool:
        enter_key = getattr(pyray, "KEY_ENTER", 257)
        kp_enter_key = getattr(pyray, "KEY_KP_ENTER", 335)
        space_key = getattr(pyray, "KEY_SPACE", 32)
        return (
            pyray.is_key_pressed(enter_key)
            or pyray.is_key_pressed(kp_enter_key)
            or pyray.is_key_pressed(space_key)
        )

    def draw_tutorial_overlay(self) -> None:
        cfg = self.ctx.cfg
        panel_w = min(520, cfg.window_width - 120)
        panel_h = 126
        panel = pyray.Rectangle(cfg.window_width // 2 - panel_w // 2, cfg.window_height - panel_h - 34, panel_w, panel_h)
        draw_glass_card(panel, accent_color=PANEL_ACCENT, glow_alpha=14, fill_alpha=176)

        if cfg.layout_name == "mobile":
            move_hint = "TOUCH THE D-PAD"
            pause_hint = "PAUSE BUTTON OPENS MENU"
        else:
            move_hint = "MOVE WITH WASD OR ARROWS"
            pause_hint = "PRESS P TO PAUSE OR ESC FOR MENU"

        headline = "NEON DISTRICT TUTORIAL"
        if self.tutorial_stage == 1:
            detail = move_hint
            footer = "START MOVING TO CONTINUE"
        elif self.tutorial_stage == 2:
            detail = "EAT DOTS TO BUILD SCORE AND CLEAR THE BOARD"
            footer = "GRAB YOUR FIRST DOT"
        elif self.tutorial_stage == 3:
            detail = "POWER SEEDS TURN THE HUNTERS INTO PREY"
            footer = "FIND A LARGE SEED TO TRIGGER RAGE"
        else:
            detail = pause_hint
            footer = "PRESS ENTER OR SPACE AFTER YOU'RE READY"

        center_x = int(panel.x + panel.width / 2)
        draw_text_centered(headline, center_x, int(panel.y + 16), 20, colors.WHITE)
        draw_text_centered(detail, center_x, int(panel.y + 50), 18, PANEL_ACCENT)
        draw_text_centered(footer, center_x, int(panel.y + 82), 16, TEXT_DIM)
