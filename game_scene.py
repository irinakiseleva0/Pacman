from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import MENU_SCENE, PAUSE_SCENE, RESULT_SCENE
from maps.class_map import Map
from entities.pacman import State
from entities.seeds import Seed


class GameScene(Scene):
    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.tick_counter = 0
        self.ready_ticks = 0

    def enter_tree(self) -> None:
        self.tick_counter = 0
        self.ready_ticks = 0

        if self.ctx.should_resume_game and self.ctx.game_map is not None:
            self.ctx.should_resume_game = False
            return

        # Add level start effect
        self.ctx.screen_flash.flash(colors.BLUE, 0.2, 0.6)
        self.ctx.last_result = ""

        # Load the current level's map
        map_path = self.ctx.get_map_path()
        self.ctx.reset_ghost_mode_cycle()
        self.ctx.game_map = Map(self.ctx, path=map_path)
        self.ctx.should_resume_game = False
        self.ready_ticks = self.ctx.cfg.ready_duration_ticks

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

        if self.ready_ticks > 0:
            self.ready_ticks -= 1
            if self.ready_ticks == 0:
                self.ctx.screen_flash.flash(colors.WHITE, 0.15, 0.12)
        elif self.tick_counter >= self.ctx.cfg.logic_tick_rate:
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
        if pacman is not None and pacman.state == State.NONE:
            self.handle_pacman_death()
            return

        if self.remaining_seeds() == 0:
            self.ctx.last_result = "level_complete"
            self.request_switch(RESULT_SCENE)
            return

    def handle_pacman_death(self) -> None:
        # Add death effects
        self.ctx.screen_shake.shake(8.0, 0.5)
        self.ctx.screen_flash.flash(colors.RED, 0.3, 0.2)

        self.ctx.lives -= 1

        if self.ctx.lives <= 0:
            self.ctx.last_result = "lose"
            self.request_switch(RESULT_SCENE)
            return

        # Reload current level's map
        map_path = self.ctx.get_map_path()
        self.ctx.reset_ghost_mode_cycle()
        self.ctx.game_map = Map(self.ctx, path=map_path)
        self.tick_counter = 0
        self.ready_ticks = self.ctx.cfg.ready_duration_ticks

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

        if self.ready_ticks > 0:
            self.draw_ready_overlay()

        # Draw screen flash overlay
        self.ctx.screen_flash.draw()

    def draw_hud(self) -> None:
        rage_text = "ON" if getattr(self.ctx.pacman, "rage", False) else "OFF"

        pyray.draw_text(
            f"Score: {self.ctx.score}",
            10,
            10,
            20,
            colors.WHITE,
        )

        pyray.draw_text(
            f"Lives: {self.ctx.lives}",
            10,
            34,
            20,
            colors.WHITE,
        )

        pyray.draw_text(
            f"Level: {self.ctx.current_level}",
            10,
            58,
            20,
            colors.SKYBLUE,
        )

        pyray.draw_text(
            f"Rage: {rage_text}",
            10,
            82,
            20,
            colors.YELLOW if rage_text == "ON" else colors.GRAY,
        )

        pyray.draw_text(
            f"Seeds left: {self.remaining_seeds()}",
            10,
            106,
            20,
            colors.WHITE,
        )

        pyray.draw_text(
            f"Ghosts: {self.ctx.ghost_mode.upper()}",
            10,
            130,
            20,
            colors.SKYBLUE if self.ctx.ghost_mode == "scatter" else colors.RED,
        )

        pyray.draw_text(
            f"Mode: {self.ctx.difficulty.upper()}",
            10,
            154,
            20,
            colors.GREEN if self.ctx.difficulty == "Easy"
            else colors.RED if self.ctx.difficulty == "Hard"
            else colors.YELLOW,
        )

        pyray.draw_text(
            f"High score: {self.ctx.high_score}",
            10,
            178,
            20,
            colors.WHITE,
        )

    def remaining_seeds(self) -> int:
        game_map = self.ctx.game_map
        if game_map is None:
            return 0

        total = 0
        for row in game_map.static_layer:
            for cell in row:
                if isinstance(cell, Seed) and getattr(cell, "enabled", False):
                    total += 1
        return total

    def draw_ready_overlay(self) -> None:
        message = "READY!"
        text_size = 36
        text_width = pyray.measure_text(message, text_size)
        x = (self.ctx.cfg.window_width - text_width) // 2
        y = self.ctx.cfg.window_height // 2 - 18

        pyray.draw_text(message, x + 2, y + 2, text_size, colors.BLACK)
        pyray.draw_text(message, x, y, text_size, colors.YELLOW)
