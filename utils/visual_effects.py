from __future__ import annotations

import pyray
from raylib import colors
from typing import List
import random
import math


def with_alpha(color, alpha: int):
    alpha = max(0, min(255, int(alpha)))

    if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
        color_type = type(color)
        return color_type(color.r, color.g, color.b, alpha)

    if isinstance(color, (tuple, list)) and len(color) >= 3:
        return (int(color[0]), int(color[1]), int(color[2]), alpha)

    raise TypeError(f"Unsupported color value: {color!r}")


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, lifetime: float, color, size: float = 2.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.base_color = color
        self.color = with_alpha(color, 255)
        self.size = size

    def update(self, dt: float) -> bool:
        """Update particle. Returns False if particle should be removed."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

        # Fade out as lifetime decreases
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            self.color = with_alpha(self.base_color, 255 * alpha)
            return True
        return False

    def draw(self) -> None:
        if self.lifetime > 0:
            pyray.draw_circle(int(self.x), int(self.y), self.size, self.color)

    def draw_with_offset(self, offset_x: float, offset_y: float) -> None:
        if self.lifetime > 0:
            px = int(self.x + offset_x)
            py = int(self.y + offset_y)
            pyray.draw_circle(px, py, self.size, self.color)


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def add_particle(self, particle: Particle) -> None:
        self.particles.append(particle)

    def create_dot_eat_effect(self, x: int, y: int) -> None:
        """Create particles when eating a dot."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        # Create 3-5 small particles
        num_particles = random.randint(3, 5)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 40)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.3, 0.6)

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                colors.YELLOW, random.uniform(1, 2)
            ))

    def create_large_seed_eat_effect(self, x: int, y: int) -> None:
        """Create particles when eating a large seed/power pellet."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        # Create more particles with different colors
        num_particles = random.randint(8, 12)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 60)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.5, 1.0)

            # Mix of white and yellow particles
            particle_color = colors.WHITE if random.random() < 0.5 else colors.YELLOW

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                particle_color, random.uniform(2, 4)
            ))

    def create_cherry_eat_effect(self, x: int, y: int) -> None:
        """Create a warm, fruit-like burst when eating a cherry."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        num_particles = random.randint(10, 14)
        palette = (colors.RED, colors.PINK, colors.GOLD, colors.ORANGE)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(35, 70)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.45, 0.9)
            particle_color = random.choice(palette)

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                particle_color, random.uniform(2, 4)
            ))

    def create_cherry_respawn_effect(self, x: int, y: int) -> None:
        """Create a softer sparkle when a cherry returns."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        num_particles = random.randint(6, 9)
        palette = (colors.GOLD, colors.PINK, colors.WHITE)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(18, 35)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.35, 0.65)
            particle_color = random.choice(palette)

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                particle_color, random.uniform(1, 3)
            ))

    def create_ghost_eat_effect(self, x: int, y: int) -> None:
        """Create particles when eating a ghost."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        # Create explosion-like effect
        num_particles = random.randint(10, 15)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.6, 1.2)

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                colors.BLUE, random.uniform(3, 5)
            ))

    def update(self, dt: float) -> None:
        """Update all particles and remove dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw_with_offset(offset_x, offset_y)


class ScreenShake:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0

    def shake(self, intensity: float, duration: float) -> None:
        """Start screen shake with given intensity and duration."""
        self.intensity = intensity
        self.duration = duration

    def update(self, dt: float) -> None:
        """Update shake effect."""
        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:
                self.duration = 0
                self.offset_x = 0
                self.offset_y = 0
            else:
                # Random shake offset
                self.offset_x = (random.random() - 0.5) * self.intensity
                self.offset_y = (random.random() - 0.5) * self.intensity
        else:
            self.offset_x = 0
            self.offset_y = 0

    def get_offset(self) -> tuple[float, float]:
        """Get current shake offset."""
        return self.offset_x, self.offset_y


class FloatingText:
    def __init__(self, text: str, x: int, y: int, color, lifetime: float = 1.5, font_size: int = 16):
        self.text = text
        self.x = x
        self.y = y
        self.start_y = y
        self.base_color = color
        self.color = with_alpha(color, 255)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.font_size = font_size

    def update(self, dt: float) -> bool:
        """Update floating text. Returns False if should be removed."""
        self.lifetime -= dt
        # Float upward
        self.y = self.start_y - (1 - self.lifetime / self.max_lifetime) * 30

        # Fade out
        if self.lifetime > 0:
            alpha = min(1.0, self.lifetime / self.max_lifetime)
            self.color = with_alpha(self.base_color, 255 * alpha)
            return True
        return False

    def draw(self) -> None:
        if self.lifetime > 0:
            pyray.draw_text(self.text, int(self.x), int(
                self.y), self.font_size, self.color)

    def draw_with_offset(self, offset_x: float, offset_y: float) -> None:
        if self.lifetime > 0:
            tx = int(self.x + offset_x)
            ty = int(self.y + offset_y)
            pyray.draw_text(self.text, tx, ty, self.font_size, self.color)


class FloatingTextSystem:
    def __init__(self):
        self.texts: List[FloatingText] = []

    def add_text(self, text: str, x: int, y: int, color, lifetime: float = 1.5, font_size: int = 16) -> None:
        self.texts.append(FloatingText(text, x, y, color, lifetime, font_size))

    def add_score_text(self, points: int, x: int, y: int) -> None:
        """Add floating score text."""
        color = colors.YELLOW
        if points >= 500:  # Cherry or higher
            color = colors.GOLD
        elif points >= 200:  # Ghost
            color = colors.RED

        self.add_text(f"+{points}", x * 16, y * 16 - 10, color, 1.2, 14)

    def update(self, dt: float) -> None:
        """Update all floating texts."""
        self.texts = [t for t in self.texts if t.update(dt)]

    def draw(self, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw all floating texts."""
        for text in self.texts:
            text.draw_with_offset(offset_x, offset_y)


class ScreenFlash:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.color = colors.WHITE

    def flash(self, color, intensity: float, duration: float) -> None:
        """Start screen flash effect."""
        self.color = color
        self.intensity = intensity
        self.duration = duration

    def update(self, dt: float) -> None:
        """Update flash effect."""
        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:
                self.duration = 0
                self.intensity = 0

    def draw(self) -> None:
        """Draw flash overlay if active."""
        if self.duration > 0 and self.intensity > 0:
            flash_color = with_alpha(self.color, int(255 * self.intensity))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(0, 0, 448, 496),
                flash_color,
            )
