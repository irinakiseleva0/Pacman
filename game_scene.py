from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from maps.class_map import Map
from entities.pacman import State
from entities.seeds import Seed


class GameScene(Scene):
    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.tick_counter = 0
        self.logic_tick_rate = 3

    def enter_tree(self) -> None:
        self.tick_counter = 0

        if self.ctx.last_result in ("win", "lose"):
            self.ctx.score = 0
            self.ctx.lives = 3
            self.ctx.last_result = ""

        self.ctx.game_map = Map(self.ctx)

    def update(self, dt: float) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        if pyray.is_key_pressed(pyray.KEY_ESCAPE):
            self.request_switch(0)
            return

        self.tick_counter += 1
        game_map.frame()

        if self.tick_counter >= self.logic_tick_rate:
            self.tick_counter = 0
            game_map.process()

        if self.ctx.score > self.ctx.high_score:
            self.ctx.high_score = self.ctx.score

        pacman = self.ctx.pacman
        if pacman is not None and pacman.state == State.NONE:
            self.handle_pacman_death()
            return

        if self.remaining_seeds() == 0:
            self.ctx.last_result = "win"
            self.request_switch(2)
            return

    def handle_pacman_death(self) -> None:
        self.ctx.lives -= 1

        if self.ctx.lives <= 0:
            self.ctx.last_result = "lose"
            self.request_switch(2)
            return

        self.ctx.game_map = Map(self.ctx)

    def draw(self) -> None:
        game_map = self.ctx.game_map
        if game_map is None:
            return

        game_map.draw()
        self.draw_hud()

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
            f"Rage: {rage_text}",
            10,
            58,
            20,
            colors.YELLOW if rage_text == "ON" else colors.GRAY,
        )

        pyray.draw_text(
            f"Seeds left: {self.remaining_seeds()}",
            10,
            82,
            20,
            colors.WHITE,
        )

        pyray.draw_text(
            f"High score: {self.ctx.high_score}",
            10,
            106,
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