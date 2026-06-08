from __future__ import annotations

import math
import random

import core.raylib_api as pyray

from utils.effect_budget import EFFECT_BUDGET


PELLET_COLOR = (0, 230, 200, 255)
POWER_COLOR = (220, 50, 220, 255)
CHERRY_COLOR = (220, 50, 80, 255)
GHOST_COLOR = (255, 200, 0, 255)


def _fade(color, alpha: int):
    if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
        return type(color)(color.r, color.g, color.b, alpha)
    return (int(color[0]), int(color[1]), int(color[2]), alpha)


class ScorePopup:
    LIFETIME = 1.0
    RISE_SPEED = 60

    def __init__(self, x: float, y: float, text: str, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self._age = 0.0

    def update(self, dt: float) -> bool:
        self._age += dt
        self.y -= self.RISE_SPEED * dt
        return self._age < self.LIFETIME

    def draw(self, font_size: int = 18) -> None:
        alpha = int(255 * (1.0 - self._age / self.LIFETIME))
        pyray.draw_text(self.text, int(self.x), int(self.y), font_size, _fade(self.color, alpha))


class Particle:
    def __init__(self, x: float, y: float, color):
        self.x = x
        self.y = y
        self.color = color
        self._age = 0.0
        self.lifetime = random.uniform(0.25, 0.55)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(30, 90)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.radius = random.uniform(2, 5)

    def update(self, dt: float) -> bool:
        self._age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 80 * dt
        return self._age < self.lifetime

    def draw(self) -> None:
        alpha = int(255 * (1.0 - self._age / self.lifetime))
        pyray.draw_circle(int(self.x), int(self.y), self.radius, _fade(self.color, alpha))


class PickupFeedbackSystem:
    def __init__(self) -> None:
        self._popups: list[ScorePopup] = []
        self._particles: list[Particle] = []

    def spawn(self, x: float, y: float, score: int, color, particle_count: int = 6) -> None:
        text = f"+{score}"
        offset_x = x - len(text) * 5
        self._popups.append(ScorePopup(offset_x, y - 10, text, color))
        if not EFFECT_BUDGET.particles:
            return
        for _ in range(particle_count):
            self._particles.append(Particle(x, y, color))

    def spawn_tile(self, ctx, tile_x: int, tile_y: int, score: int, color, particle_count: int = 6) -> None:
        cfg = ctx.cfg
        x = cfg.board_offset_x + tile_x * cfg.tile_size + cfg.tile_size / 2
        y = cfg.board_offset_y + tile_y * cfg.tile_size + cfg.tile_size / 2
        self.spawn(x, y, score, color, particle_count)

    def update(self, dt: float) -> None:
        self._popups = [p for p in self._popups if p.update(dt)]
        self._particles = [p for p in self._particles if p.update(dt)]

    def draw(self) -> None:
        if EFFECT_BUDGET.particles:
            for particle in self._particles:
                particle.draw()
        for popup in self._popups:
            popup.draw()

    def clear(self) -> None:
        self._popups.clear()
        self._particles.clear()


PICKUP_FEEDBACK = PickupFeedbackSystem()
