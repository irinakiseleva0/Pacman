from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass
class Vec2:
    x: float
    y: float


def _with_alpha(color, alpha: float):
    alpha_value = max(0, min(255, int(255 * max(0.0, min(1.0, alpha)))))

    if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
        color_type = type(color)
        return color_type(color.r, color.g, color.b, alpha_value)

    if isinstance(color, (tuple, list)) and len(color) >= 3:
        return (int(color[0]), int(color[1]), int(color[2]), alpha_value)

    return color


class FloatingText:
    def __init__(self, text: str, pos, color, lifetime: float = 1.0) -> None:
        self.text = text
        self.pos = Vec2(float(pos[0]), float(pos[1])) if isinstance(pos, (tuple, list)) else Vec2(float(pos.x), float(pos.y))
        self.base_color = color
        self.color = _with_alpha(color, 1.0)
        self.lifetime = max(0.01, float(lifetime))
        self.remaining = self.lifetime
        self.alpha = 1.0

    def update(self, dt: float) -> bool:
        self.remaining = max(0.0, self.remaining - dt)
        self.pos.y -= 40.0 * dt
        self.alpha = self.remaining / self.lifetime
        self.color = _with_alpha(self.base_color, self.alpha)
        return self.remaining > 0.0


class CameraShake:
    def __init__(self) -> None:
        self.camera = None
        self.intensity = 0.0
        self.duration = 0.0
        self.remaining = 0.0
        self._base_offset = (0.0, 0.0)
        self._shake_offset = (0.0, 0.0)

    def set_camera(self, camera) -> None:
        self._restore_offset()
        self.camera = camera
        if camera is not None:
            self._base_offset = (float(camera.offset.x), float(camera.offset.y))
        self._shake_offset = (0.0, 0.0)

    def shake(self, intensity: float, duration: float) -> None:
        if self.camera is None or intensity <= 0 or duration <= 0:
            return

        self._restore_offset()
        self.intensity = float(intensity)
        self.duration = float(duration)
        self.remaining = float(duration)
        self._shake_offset = (0.0, 0.0)

    def update(self, dt: float) -> None:
        if self.camera is None:
            return

        self._restore_offset()
        if self.remaining <= 0:
            return

        self.remaining = max(0.0, self.remaining - dt)
        if self.remaining <= 0:
            self._shake_offset = (0.0, 0.0)
            return

        fade = self.remaining / max(self.duration, 0.0001)
        amount = self.intensity * fade
        self._shake_offset = (
            random.uniform(-amount, amount),
            random.uniform(-amount, amount),
        )
        self.camera.offset.x = self._base_offset[0] + self._shake_offset[0]
        self.camera.offset.y = self._base_offset[1] + self._shake_offset[1]

    def reset(self) -> None:
        self.remaining = 0.0
        self._restore_offset()

    def _restore_offset(self) -> None:
        if self.camera is None:
            return
        self.camera.offset.x = self._base_offset[0]
        self.camera.offset.y = self._base_offset[1]
        self._shake_offset = (0.0, 0.0)


class GlitchEffect:
    def __init__(self, duration: float = 1.5) -> None:
        self.duration = max(0.01, float(duration))
        self.remaining = 0.0
        self.intensity = 0.0

    def trigger(self, duration: float | None = None) -> None:
        if duration is not None:
            self.duration = max(0.01, float(duration))
        self.remaining = self.duration
        self.intensity = 0.0

    def update(self, dt: float) -> None:
        if self.remaining <= 0.0:
            self.intensity = 0.0
            return

        self.remaining = max(0.0, self.remaining - dt)
        elapsed = self.duration - self.remaining
        if elapsed <= 0.5:
            self.intensity = min(1.0, elapsed / 0.5)
            return

        fade_duration = max(0.01, self.duration - 0.5)
        self.intensity = max(0.0, self.remaining / fade_duration)

    def is_active(self) -> bool:
        return self.remaining > 0.0 and self.intensity > 0.0

    def reset(self) -> None:
        self.remaining = 0.0
        self.intensity = 0.0


camera_shake = CameraShake()
glitch_effect = GlitchEffect()


def set_camera(camera) -> None:
    camera_shake.set_camera(camera)


def shake_camera(intensity: float, duration: float) -> None:
    camera_shake.shake(intensity, duration)


def update_camera_shake(dt: float) -> None:
    camera_shake.update(dt)


def reset_camera_shake() -> None:
    camera_shake.reset()


def trigger_glitch(duration: float = 1.5) -> None:
    glitch_effect.trigger(duration)


def update_glitch(dt: float) -> None:
    glitch_effect.update(dt)


def reset_glitch() -> None:
    glitch_effect.reset()
