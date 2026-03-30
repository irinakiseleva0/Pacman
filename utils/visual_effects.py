from __future__ import annotations

import core.raylib_api as pyray
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

    def draw_with_offset(self, offset_x: float, offset_y: float, scale: float = 1.0) -> None:
        if self.lifetime > 0:
            px = int(self.x * scale + offset_x)
            py = int(self.y * scale + offset_y)
            pyray.draw_circle(px, py, self.size * scale, self.color)


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def add_particle(self, particle: Particle) -> None:
        self.particles.append(particle)

    def create_dot_eat_effect(self, x: int, y: int, color=colors.YELLOW) -> None:
        """Create particles when eating a dot."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        highlight = colors.WHITE

        # Create a tighter burst with a few bright sparks.
        num_particles = random.randint(6, 9)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(26, 54)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.18, 0.42)
            particle_color = color if random.random() > 0.3 else highlight

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                particle_color, random.uniform(1.2, 2.6)
            ))

        # Add a couple of softer trailing motes so the pickup doesn't feel too abrupt.
        for _ in range(2):
            angle = random.uniform(-0.8, 0.8)
            speed = random.uniform(10, 22)
            self.add_particle(Particle(
                center_x,
                center_y,
                math.cos(angle) * speed,
                -abs(math.sin(angle) * speed) - random.uniform(8, 16),
                random.uniform(0.28, 0.5),
                color,
                random.uniform(0.8, 1.6),
            ))

    def create_large_seed_eat_effect(self, x: int, y: int, palette: tuple | None = None) -> None:
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
            palette_colors = palette or (colors.WHITE, colors.YELLOW)
            particle_color = random.choice(palette_colors)

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                particle_color, random.uniform(2, 4)
            ))

    def create_cherry_eat_effect(self, x: int, y: int, palette: tuple | None = None) -> None:
        """Create a warm, fruit-like burst when eating a cherry."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        num_particles = random.randint(10, 14)
        palette = palette or (colors.RED, colors.PINK, colors.GOLD, colors.ORANGE)
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

    def create_cherry_respawn_effect(self, x: int, y: int, palette: tuple | None = None) -> None:
        """Create a softer sparkle when a cherry returns."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        num_particles = random.randint(6, 9)
        palette = palette or (colors.GOLD, colors.PINK, colors.WHITE)
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

    def create_ghost_eat_effect(self, x: int, y: int, color=colors.BLUE) -> None:
        """Create particles when eating a ghost."""
        center_x = x * 16 + 8
        center_y = y * 16 + 8

        # Create a more dramatic burst with a bright core and trailing fragments.
        num_particles = random.randint(16, 22)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(44, 92)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.45, 0.95)
            particle_color = color if random.random() > 0.28 else colors.WHITE

            self.add_particle(Particle(
                center_x, center_y, vx, vy, lifetime,
                particle_color, random.uniform(2.8, 5.4)
            ))

        for _ in range(4):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(12, 28)
            self.add_particle(Particle(
                center_x,
                center_y,
                math.cos(angle) * speed,
                math.sin(angle) * speed - random.uniform(10, 24),
                random.uniform(0.35, 0.65),
                colors.WHITE,
                random.uniform(1.2, 2.4),
            ))

    def update(self, dt: float) -> None:
        """Update all particles and remove dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, offset_x: float = 0, offset_y: float = 0, scale: float = 1.0) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw_with_offset(offset_x, offset_y, scale)


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

    def draw_with_offset(self, offset_x: float, offset_y: float, scale: float = 1.0) -> None:
        if self.lifetime > 0:
            tx = int(self.x * scale + offset_x)
            ty = int(self.y * scale + offset_y)
            font_size = max(12, int(self.font_size * scale))
            pyray.draw_text(self.text, tx, ty, font_size, self.color)


class FloatingTextSystem:
    def __init__(self):
        self.texts: List[FloatingText] = []

    def add_text(self, text: str, x: int, y: int, color, lifetime: float = 1.5, font_size: int = 16) -> None:
        self.texts.append(FloatingText(text, x, y, color, lifetime, font_size))

    def add_score_text(self, points: int, x: int, y: int) -> None:
        """Add floating score text."""
        color = colors.YELLOW
        lifetime = 1.2
        font_size = 14
        x_offset = 0
        y_offset = -10

        if points <= 25:
            color = colors.YELLOW
            lifetime = 0.55
            font_size = 10
            x_offset = 3
            y_offset = -6
        if points >= 500:  # Cherry or higher
            color = colors.GOLD
            lifetime = 1.2
            font_size = 14
        elif points >= 200:  # Ghost
            color = colors.RED
            lifetime = 1.2
            font_size = 14

        self.add_text(f"+{points}", x * 16 + x_offset, y * 16 + y_offset, color, lifetime, font_size)

    def add_ghost_combo_text(self, combo_step: int, points: int, x: int, y: int) -> None:
        """Add a stronger callout for chained ghost scores."""
        if combo_step <= 1:
            return

        combo_color = colors.GOLD if combo_step >= 3 else colors.WHITE
        self.add_text(
            f"x{combo_step} GHOST!",
            x * 16 - 10,
            y * 16 - 28,
            combo_color,
            1.05,
            13,
        )
        self.add_text(
            f"{points}!",
            x * 16 + 4,
            y * 16 - 46,
            combo_color,
            0.95,
            18,
        )

    def update(self, dt: float) -> None:
        """Update all floating texts."""
        self.texts = [t for t in self.texts if t.update(dt)]

    def draw(self, offset_x: float = 0, offset_y: float = 0, scale: float = 1.0) -> None:
        """Draw all floating texts."""
        for text in self.texts:
            text.draw_with_offset(offset_x, offset_y, scale)


class ScreenFlash:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.color = colors.WHITE
        self.width = 448
        self.height = 496

    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

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
                pyray.Rectangle(0, 0, self.width, self.height),
                flash_color,
            )


class LightBurst:
    def __init__(self, x: float, y: float, radius: float, color, intensity: float = 1.0, lifetime: float = 0.22):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        return self.lifetime > 0

    def draw_with_offset(self, offset_x: float, offset_y: float, scale: float = 1.0) -> None:
        if self.lifetime <= 0:
            return
        t = self.lifetime / max(0.001, self.max_lifetime)
        pulse = 1.0 - t
        radius = self.radius * (0.7 + pulse * 0.7) * scale
        alpha = int(255 * self.intensity * t * 0.12)
        cx = int(self.x * scale + offset_x)
        cy = int(self.y * scale + offset_y)
        pyray.draw_circle(cx, cy, radius * 1.4, with_alpha(self.color, alpha))
        pyray.draw_circle(cx, cy, radius * 0.8, with_alpha(self.color, int(alpha * 1.3)))


class LightBurstSystem:
    def __init__(self):
        self.bursts: List[LightBurst] = []

    def add_burst(self, x: float, y: float, radius: float, color, intensity: float = 1.0, lifetime: float = 0.22) -> None:
        self.bursts.append(LightBurst(x, y, radius, color, intensity, lifetime))

    def add_grid_burst(self, x: int, y: int, color, radius: float = 18.0, intensity: float = 1.0, lifetime: float = 0.22) -> None:
        self.add_burst(x * 16 + 8, y * 16 + 8, radius, color, intensity, lifetime)

    def update(self, dt: float) -> None:
        self.bursts = [burst for burst in self.bursts if burst.update(dt)]

    def draw(self, offset_x: float = 0, offset_y: float = 0, scale: float = 1.0) -> None:
        for burst in self.bursts:
            burst.draw_with_offset(offset_x, offset_y, scale)
