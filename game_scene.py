from __future__ import annotations

from dataclasses import dataclass

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import MENU_SCENE, PAUSE_SCENE, RESULT_SCENE
from maps.class_map import Map
from entities.pacman import State
from ui.hud import draw_game_hud
from ui.ui import draw_shadowed_text_centered, draw_text_centered


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

    def enter_tree(self) -> None:
        self.tick_counter = 0
        self.transition = None

        if self.ctx.should_resume_game and self.ctx.game_map is not None:
            self.ctx.should_resume_game = False
            return

        self.ctx.play_transition_effect(colors.BLUE, 0.2, 0.6)
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

        self.tick_counter += 1
        game_map.frame()

        if self.transition is not None:
            self.transition.ticks -= 1
            if self.transition.ticks == 0:
                self.finish_transition()
            return

        if self.tick_counter >= self.ctx.cfg.logic_tick_rate:
            self.tick_counter = 0
            self.ctx.advance_ghost_mode_cycle()
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
        self.ctx.play_transition_effect(colors.RED, 0.3, 0.2, 8.0, 0.5)

        self.ctx.lives -= 1

        if self.ctx.lives <= 0:
            self.transition = SceneTransition("death", self.ctx.cfg.game_over_pause_ticks, "lose")
            return

        self.transition = SceneTransition("death", self.ctx.cfg.death_pause_ticks, "reload")

    def finish_transition(self) -> None:
        if self.transition is None:
            return

        if self.transition.kind == "ready":
            self.ctx.play_transition_effect(colors.WHITE, 0.15, 0.12)
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
        if self.ctx.current_level >= self.TOTAL_LEVELS:
            transition_result = "game_won"
        self.ctx.reset_ghost_combo()
        self.ctx.play_transition_effect(colors.GREEN, 0.25, 0.2, 3.0, 0.2)
        self.transition = SceneTransition(
            "level_complete",
            self.ctx.cfg.level_complete_duration_ticks,
            transition_result,
        )

    def draw(self) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        # Apply screen shake offset
        shake_x, shake_y = self.ctx.screen_shake.get_offset()

        game_map.draw()

        # Draw particles with shake offset
        self.ctx.particles.draw(shake_x, shake_y)

        # Draw floating text with shake offset
        self.ctx.floating_text.draw(shake_x, shake_y)

        # Draw HUD (not affected by shake)
        self.draw_hud()

        if self.transition is not None and self.transition.kind == "ready":
            self.draw_ready_overlay()
        elif self.transition is not None and self.transition.kind == "death":
            self.draw_death_overlay()
        elif self.transition is not None and self.transition.kind == "level_complete":
            self.draw_level_complete_overlay()

        # Draw screen flash overlay
        self.ctx.screen_flash.draw()

    def draw_hud(self) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        draw_game_hud(
            self.ctx,
            game_map.remaining_seeds(),
            game_map.cherry_status(),
            game_map.ghost_release_status(),
            game_map.ghost_return_status(),
        )

    def draw_ready_overlay(self) -> None:
        message = "READY!"
        text_size = 36
        y = self.ctx.cfg.window_height // 2 - 18

        draw_shadowed_text_centered(
            message,
            self.ctx.cfg.window_width // 2,
            y,
            text_size,
            colors.YELLOW,
        )

    def draw_death_overlay(self) -> None:
        center_x = self.ctx.cfg.window_width // 2
        y = self.ctx.cfg.window_height // 2 - 18

        if self.transition is not None and self.transition.result == "lose":
            message = "GAME OVER"
            message_color = colors.RED
        else:
            message = "LIFE LOST"
            message_color = colors.RED

        draw_shadowed_text_centered(message, center_x, y, 34, message_color)

    def draw_level_complete_overlay(self) -> None:
        center_x = self.ctx.cfg.window_width // 2
        y = self.ctx.cfg.window_height // 2 - 24

        transition_result = self.transition.result if self.transition is not None else ""
        if transition_result == "game_won":
            headline = "ALL CLEAR!"
            headline_color = colors.GOLD
            detail = "Final result incoming..."
        else:
            headline = "LEVEL CLEAR!"
            headline_color = colors.GREEN
            detail = "Preparing result..."

        draw_shadowed_text_centered(headline, center_x, y, 38, headline_color)
        draw_text_centered(detail, center_x, y + 42, 18, colors.WHITE)
