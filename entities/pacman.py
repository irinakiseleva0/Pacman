from __future__ import annotations

import pyray

from cell import Cell
from animated_sprite import Sprite
from assets.assets import Assets

from entities.wall import Wall
from entities.door import Door


class State:
    UP = "UP"
    RIGHT = "RIGHT"
    DOWN = "DOWN"
    LEFT = "LEFT"
    DEAD = "DEATH"
    NONE = "NONE"


class Pacman(Cell):
    DEATH_FPS = 1
    _images_cache = None

    def __init__(self, ctx):
        super().__init__(ctx)

        self.state = State.UP
        self.rage = False
        self.rage_timer = 0
        self.death_timer = 0

        if Pacman._images_cache is None:
            Pacman._images_cache = self._load_images()

        self.pacman_sprite = Sprite(Pacman._images_cache)
        self.pacman_sprite.set_key(self.state, True)

    @staticmethod
    def _load_images():
        base = "sprites/pacman/"
        paths = {
            "UP": [f"{base}pacman_pos_1_up.png", f"{base}pacman_pos_2_up.png"],
            "DOWN": [f"{base}pacman_pos_1_down.png", f"{base}pacman_pos_2_down.png"],
            "LEFT": [f"{base}pacman_pos_1_left.png", f"{base}pacman_pos_2_left.png"],
            "RIGHT": [f"{base}pacman_pos_1_right.png", f"{base}pacman_pos_2_right.png"],
            "DEATH": [f"{base}death/death_{i}.png" for i in range(1, 11)],
            "NONE": [],
        }
        return {k: [Assets.texture(p) for p in v] for k, v in paths.items()}

    def draw(self) -> None:
        if self.state == State.NONE:
            return
        cfg = self.ctx.cfg
        self.pacman_sprite.draw((self.x * cfg.RES, self.y * cfg.RES))

    def process(self) -> None:
        if self.state in (State.NONE, State.DEAD):
            return

        dx, dy = 0, 0
        if self.state == State.RIGHT: dx = 1
        elif self.state == State.LEFT: dx = -1
        elif self.state == State.UP: dy = -1
        elif self.state == State.DOWN: dy = 1
        m = self.ctx.game_map
        if not m:
            return

        res = m.try_move(self, dx, dy)
        if res.moved:
            self.processed = True
            self.pacman_sprite.move_forward()

    def frame(self, x: int, y: int) -> None:
        super().frame(x, y)

        if self.state == State.NONE:
            return

        if self.state == State.DEAD:
            self.death_timer += 1
            if self.death_timer % Pacman.DEATH_FPS == 0:
                self.pacman_sprite.move_forward()
                frames = self.pacman_sprite.texture_dictionary[self.state]
                if self.pacman_sprite.frame_index == len(frames) - 1:
                    self.state = State.NONE
            return

        if self.rage_timer > 0:
            self.rage_timer -= 1
            if self.rage_timer == 0:
                self.rage = False

        keys = {
            pyray.KEY_W: State.UP,
            pyray.KEY_A: State.LEFT,
            pyray.KEY_S: State.DOWN,
            pyray.KEY_D: State.RIGHT,
        }
        for key, st in keys.items():
            if pyray.is_key_pressed(key):
                self.state = st
                self.pacman_sprite.set_key(self.state, False)
