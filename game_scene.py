from __future__ import annotations

import pyray
from raylib import colors

from core.scene import Scene
from ClassMap import Map


class GameScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.current_tick = 0
        self.tickrate = 3

    def enter_tree(self) -> None:
        self.current_tick = 0
        self.ctx.game_map = Map(self.ctx)

    def update(self, dt: float) -> None:
        self.current_tick += 1

        self.ctx.game_map.frame()

        if self.current_tick % self.tickrate == 0:
            self.current_tick = 0
            self.ctx.game_map.process()

    def draw(self) -> None:
        self.ctx.game_map.draw()
