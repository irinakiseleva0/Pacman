from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from entities.cell import Actor
from ui import gamepad
from utils.animated_sprite import Sprite
from assets.assets import Assets
from utils.visual_effects import Particle, with_alpha


class State:
    UP = "UP"
    RIGHT = "RIGHT"
    DOWN = "DOWN"
    LEFT = "LEFT"
    DEAD = "DEATH"
    NONE = "NONE"


class Pacman(Actor):
    _images_cache = None

    def __init__(self, ctx) -> None:
        super().__init__(ctx)

        self.kind = "pacman"
        self.state = State.UP
        self.next_state = self.state

        self.rage = False
        self.rage_timer = 0
        self.death_timer = 0
        self.turn_feedback_timer = 0.0
        self.turn_feedback_dir = (0, -1)

        # Track last movement direction for ghost AI
        self.last_dx = 0
        self.last_dy = -1  # Start facing up

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
        return {key: [Assets.texture(path) for path in value] for key, value in paths.items()}

    def enable_rage(self, ticks: int, *, keep_combo: bool = False) -> None:
        if self.state in (State.DEAD, State.NONE):
            return

        self.rage = True
        self.rage_timer = ticks
        if not keep_combo:
            self.ctx.reset_ghost_combo()

    def kill(self) -> None:
        if self.state in (State.DEAD, State.NONE):
            return

        self.rage = False
        self.rage_timer = 0
        self.ctx.reset_ghost_combo()
        self.death_timer = 0
        self.state = State.DEAD
        self.next_state = State.DEAD
        self.pacman_sprite.set_key(State.DEAD, True)

    def draw(self) -> None:
        if self.state == State.NONE:
            return

        cfg = self.ctx.cfg
        scale = cfg.tile_size / 16
        time_s = getattr(self.ctx, "visual_time", 0.0)
        base_x = cfg.board_offset_x + self.x * cfg.tile_size
        base_y = cfg.board_offset_y + self.y * cfg.tile_size
        px = base_x + cfg.tile_size // 2
        py = base_y + cfg.tile_size // 2
        glow_radius = max(10, cfg.tile_size // 2 + int((0.5 + 0.5 * __import__("math").sin(time_s * 6.0)) * 6))
        pyray.draw_circle(px, py, glow_radius, with_alpha((255, 225, 70, 255), 44))
        if self.turn_feedback_timer > 0:
            turn_alpha = min(1.0, self.turn_feedback_timer / 0.14)
            ring_color = colors.ORANGE if not self.rage else colors.GOLD
            ring_radius = max(8, cfg.tile_size // 2 + int((1.0 - turn_alpha) * 10))
            pyray.draw_circle_lines(px, py, ring_radius, with_alpha(ring_color, 180 * turn_alpha))
            dx, dy = self.turn_feedback_dir
            if dx != 0 or dy != 0:
                dash_w = max(3, cfg.tile_size // 5)
                dash_h = max(3, cfg.tile_size // 5)
                dash_x = int(px + dx * (cfg.tile_size * 0.55) - dash_w / 2)
                dash_y = int(py + dy * (cfg.tile_size * 0.55) - dash_h / 2)
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(dash_x, dash_y, dash_w, dash_h),
                    with_alpha(colors.WHITE, 210 * turn_alpha),
                )
        self.pacman_sprite.draw(
            (base_x, base_y),
            scale=scale,
        )

    def _direction_to_delta(self, state: str) -> tuple[int, int]:
        if state == State.RIGHT:
            return 1, 0
        if state == State.LEFT:
            return -1, 0
        if state == State.UP:
            return 0, -1
        if state == State.DOWN:
            return 0, 1
        return 0, 0

    def _can_move_in_direction(self, state: str) -> bool:
        game_map = self.ctx.game_map
        if game_map is None:
            return False

        dx, dy = self._direction_to_delta(state)
        if dx == 0 and dy == 0:
            return False

        next_cell = game_map.get_cell(self.x + dx, self.y + dy)
        if next_cell is None:
            return False

        return not next_cell.is_blocking(self)

    def _apply_buffered_turn(self) -> None:
        if self.next_state in (State.NONE, State.DEAD):
            return

        if self._can_move_in_direction(self.next_state):
            if self.state != self.next_state:
                self.state = self.next_state
                self.pacman_sprite.set_key(self.state, False)
                self._trigger_turn_feedback()

    def _trigger_turn_feedback(self) -> None:
        dx, dy = self._direction_to_delta(self.state)
        self.turn_feedback_timer = 0.14
        self.turn_feedback_dir = (dx, dy)

        center_x = self.x * 16 + 8
        center_y = self.y * 16 + 8
        accent = colors.GOLD if self.rage else self.ctx.effect_palette()["dot"]
        for index in range(4):
            spread = (index - 1.5) * 0.22
            speed = 22 + index * 8
            vx = (dx + (dy * spread)) * speed
            vy = (dy - (dx * spread)) * speed
            self.ctx.particles.add_particle(
                Particle(
                    center_x,
                    center_y,
                    vx,
                    vy,
                    0.12 + index * 0.02,
                    accent if index < 3 else colors.WHITE,
                    1.0 + index * 0.2,
                )
            )
        self.ctx.trigger_screen_shake(0.5, 0.04)

    def queue_direction(self, state: str) -> None:
        if state not in (State.UP, State.DOWN, State.LEFT, State.RIGHT):
            return
        if self.state in (State.NONE, State.DEAD):
            return
        self.next_state = state

    def process(self) -> None:
        if self.state in (State.NONE, State.DEAD):
            return

        game_map = self.ctx.game_map
        if game_map is None:
            return

        self._apply_buffered_turn()

        dx, dy = self._direction_to_delta(self.state)
        result = game_map.try_move(self, dx, dy)

        if result.moved:
            self.last_dx = dx
            self.last_dy = dy
            self.pacman_sprite.move_forward()

    def frame(self, x: int, y: int) -> None:
        super().frame(x, y)

        if self.state == State.NONE:
            return

        if self.state == State.DEAD:
            self.death_timer += 1

            if self.death_timer % self.ctx.cfg.death_animation_fps == 0:
                self.pacman_sprite.move_forward()
                frames = self.pacman_sprite.texture_dictionary[State.DEAD]
                if self.pacman_sprite.frame_index >= len(frames) - 1:
                    self.state = State.NONE

            return

        if self.turn_feedback_timer > 0:
            self.turn_feedback_timer = max(0.0, self.turn_feedback_timer - pyray.get_frame_time())

        if self.rage_timer > 0:
            self.rage_timer -= 1
            if self.rage_timer == 0:
                self.rage = False
                self.ctx.begin_power_chain_window()

        keys = {
            pyray.KEY_W: State.UP,
            pyray.KEY_UP: State.UP,
            pyray.KEY_A: State.LEFT,
            pyray.KEY_LEFT: State.LEFT,
            pyray.KEY_S: State.DOWN,
            pyray.KEY_DOWN: State.DOWN,
            pyray.KEY_D: State.RIGHT,
            pyray.KEY_RIGHT: State.RIGHT,
        }

        for key, state in keys.items():
            if pyray.is_key_pressed(key):
                self.queue_direction(state)
                return

        controller_direction = gamepad.movement_direction()
        if controller_direction == "up":
            self.queue_direction(State.UP)
        elif controller_direction == "down":
            self.queue_direction(State.DOWN)
        elif controller_direction == "left":
            self.queue_direction(State.LEFT)
        elif controller_direction == "right":
            self.queue_direction(State.RIGHT)
