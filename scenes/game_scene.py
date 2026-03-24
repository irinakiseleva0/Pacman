from __future__ import annotations

from dataclasses import dataclass

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import MENU_SCENE, PAUSE_SCENE, RESULT_SCENE
from maps.class_map import Map
from entities.pacman import State
from scenes import game_view
from ui import gamepad
from ui.mobile_controls import handle_mobile_controls


@dataclass
class SceneTransition:
    kind: str
    ticks: float
    result: str = ""


class GameScene(Scene):
    TOTAL_LEVELS = 3

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.logic_accumulator = 0.0
        self.transition: SceneTransition | None = None
        self.visual_time = 0.0
        self.tutorial_stage = 0
        self.failure_reason = ""
        self.near_miss_timer = 0.0
        self.near_miss_cooldown = 0.0

    def _tutorial_step_total(self) -> int:
        return 4

    def _tutorial_progress_index(self) -> int:
        if self.tutorial_stage <= 0:
            return self._tutorial_step_total()
        return min(self._tutorial_step_total(), self.tutorial_stage)

    def enter_tree(self) -> None:
        self.logic_accumulator = 0.0
        self.transition = None
        self.visual_time = 0.0
        self.ctx.visual_time = 0.0
        self.tutorial_stage = 1 if self._tutorial_active() else 0
        self.failure_reason = ""
        self.near_miss_timer = 0.0
        self.near_miss_cooldown = 0.0

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
        self.transition = SceneTransition("ready", self.ctx.cfg.legacy_frames_to_seconds(self.ctx.cfg.ready_duration_ticks))

    def update(self, dt: float) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
            self.request_switch(MENU_SCENE)
            return

        if pyray.is_key_pressed(pyray.KEY_P) or gamepad.pause_pressed():
            self.request_switch(PAUSE_SCENE)
            return

        mobile_action = handle_mobile_controls(self.ctx)
        if mobile_action == "pause":
            self.request_switch(PAUSE_SCENE)
            return

        self.visual_time += dt
        self.ctx.visual_time = self.visual_time
        self.ctx.tick_power_chain_window()
        self.ctx.tick_route_chain_window()
        self.near_miss_timer = max(0.0, self.near_miss_timer - dt)
        self.near_miss_cooldown = max(0.0, self.near_miss_cooldown - dt)

        game_map.frame()

        self._update_tutorial_state(mobile_action)

        if self.transition is not None:
            self.transition.ticks -= dt
            if self.transition.ticks <= 0:
                self.finish_transition()
            return

        if self.ctx.game_mode == "Time Attack":
            self.ctx.time_attack_seconds = max(0.0, self.ctx.time_attack_seconds - dt)
            if self.ctx.time_attack_seconds <= 0:
                self.start_timeout_transition()
                return

        self.logic_accumulator += dt
        logic_step = self.ctx.cfg.logic_step_seconds()
        processed_steps = 0
        while self.logic_accumulator >= logic_step and processed_steps < 4:
            self.logic_accumulator -= logic_step
            processed_steps += 1
            pressure_changed = self.ctx.advance_ghost_mode_cycle(
                game_map.remaining_pickups(),
                getattr(game_map, "total_pickups", 0),
            )
            if pressure_changed and self.ctx.pressure_stage > 0:
                palette = self.ctx.effect_palette()
                flash_strength = 0.04 + self.ctx.pressure_stage * 0.02
                shake_strength = 1.8 + self.ctx.pressure_stage * 0.7
                if self.ctx.elite_pressure_active():
                    flash_strength += 0.04
                    shake_strength += 1.2
                self.ctx.trigger_screen_flash(palette["ghost"], flash_strength, 0.05)
                self.ctx.trigger_screen_shake(shake_strength, 0.08)
                surge = self.ctx.map_release_surge_amount()
                if self.ctx.elite_pressure_active():
                    surge += 2
                if surge > 0:
                    game_map.nudge_pending_ghosts(surge)
                    self.ctx.floating_text.add_text(
                        "ELITE SURGE" if self.ctx.elite_pressure_active() else "SURGE",
                        int(self.ctx.cfg.board_width * 0.48),
                        24,
                        palette["ghost"],
                        0.75,
                        12,
                    )
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
        if pacman is not None and self.transition is None:
            self._check_near_miss()
        if pacman is not None and pacman.state == State.NONE and self.transition is None:
            self.start_death_transition()
            return

        if game_map.remaining_seeds() == 0 and self.transition is None:
            self.start_level_complete_transition()
            return

    def start_death_transition(self) -> None:
        self.failure_reason = ""
        self.ctx.play_sfx("death")
        self.ctx.play_transition_effect(self.ctx.effect_palette()["death_flash"], 0.3, 0.2, 8.0, 0.5)

        self.ctx.lives -= 1

        if self.ctx.lives <= 0:
            self.transition = SceneTransition("death", self.ctx.cfg.legacy_frames_to_seconds(self.ctx.cfg.game_over_pause_ticks), "lose")
            return

        self.transition = SceneTransition("death", self.ctx.cfg.legacy_frames_to_seconds(self.ctx.cfg.death_pause_ticks), "reload")

    def start_timeout_transition(self) -> None:
        self.failure_reason = "timeout"
        self.ctx.play_sfx("death")
        self.ctx.reset_ghost_combo()
        self.ctx.play_transition_effect(colors.ORANGE, 0.34, 0.22, 9.0, 0.45)
        self.transition = SceneTransition("death", self.ctx.cfg.legacy_frames_to_seconds(self.ctx.cfg.game_over_pause_ticks), "lose")

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
            self.logic_accumulator = 0.0
            self.transition = SceneTransition("ready", self.ctx.cfg.legacy_frames_to_seconds(self.ctx.cfg.ready_duration_ticks))
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
        if self.ctx.game_mode == "Time Attack" and self.ctx.game_map is not None and self.ctx.pacman is not None:
            bonus_seconds = math.ceil(self.ctx.time_attack_clear_bonus_seconds())
            self.ctx.floating_text.add_text(
                f"+{bonus_seconds}S",
                self.ctx.pacman.x * 16 + 18,
                self.ctx.pacman.y * 16 - 62,
                colors.ORANGE,
                1.1,
                14,
            )
        self.ctx.play_sfx("win")
        self.ctx.record_level_cleared()
        self.ctx.reset_ghost_combo()
        self.ctx.play_transition_effect(self.ctx.effect_palette()["win_flash"], 0.25, 0.2, 3.0, 0.2)
        self.transition = SceneTransition(
            "level_complete",
            self.ctx.cfg.legacy_frames_to_seconds(self.ctx.cfg.level_complete_duration_ticks),
            transition_result,
        )

    def _check_near_miss(self) -> None:
        if self.near_miss_cooldown > 0:
            return

        game_map = self.ctx.game_map
        pacman = self.ctx.pacman
        if game_map is None or pacman is None or getattr(pacman, "rage", False):
            return

        closest_distance = None
        for actor in game_map.dynamic_actors:
            if getattr(actor, "kind", None) != "ghost":
                continue
            if getattr(actor, "is_harmless", lambda: False)():
                continue
            distance = abs(actor.x - pacman.x) + abs(actor.y - pacman.y)
            if closest_distance is None or distance < closest_distance:
                closest_distance = distance

        if closest_distance != 1:
            return

        palette = self.ctx.effect_palette()
        self.near_miss_timer = 0.55
        self.near_miss_cooldown = 1.1
        self.ctx.trigger_screen_flash(palette["ghost"], 0.05, 0.06)
        self.ctx.trigger_screen_shake(1.4, 0.08)
        self.ctx.floating_text.add_text(
            "CLOSE CALL",
            pacman.x * 16 - 18,
            pacman.y * 16 - 20,
            colors.WHITE,
            0.48,
            12,
        )

    def draw(self) -> None:
        game_view.draw_scene(self)

    def draw_hud(self) -> None:
        game_view.draw_hud(self)

    def draw_live_feedback(self) -> None:
        game_view.draw_live_feedback(self)

    def _draw_pressure_overlay(self, board_rect) -> None:
        game_view.draw_pressure_overlay(self, board_rect)

    def _draw_transition_card(self, headline: str, detail: str, accent_color, *, width: int = 360) -> None:
        game_view.draw_transition_card(self, headline, detail, accent_color, width=width)

    def draw_ready_overlay(self) -> None:
        game_view.draw_ready_overlay(self)

    def draw_death_overlay(self) -> None:
        game_view.draw_death_overlay(self)

    def draw_level_complete_overlay(self) -> None:
        game_view.draw_level_complete_overlay(self)

    def _tutorial_active(self) -> bool:
        return self.ctx.tutorial_enabled() and not self.ctx.tutorial_seen()

    def _movement_pressed(self) -> bool:
        return any(
            pyray.is_key_pressed(key)
            for key in (pyray.KEY_W, pyray.KEY_A, pyray.KEY_S, pyray.KEY_D, pyray.KEY_UP, pyray.KEY_DOWN, pyray.KEY_LEFT, pyray.KEY_RIGHT)
        ) or gamepad.movement_direction() is not None

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
            or gamepad.confirm_pressed()
        )

    def draw_tutorial_overlay(self) -> None:
        game_view.draw_tutorial_overlay(self)
