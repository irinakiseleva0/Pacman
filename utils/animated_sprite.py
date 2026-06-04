from __future__ import annotations

from typing import Any

import pygame
from raylib import colors

import core.raylib_api as pyray


def _color(color) -> tuple[int, int, int, int]:
    if isinstance(color, pygame.Color):
        return color.r, color.g, color.b, color.a
    if isinstance(color, (tuple, list)):
        if len(color) >= 4:
            return int(color[0]), int(color[1]), int(color[2]), int(color[3])
        return int(color[0]), int(color[1]), int(color[2]), 255
    return 255, 255, 255, 255


def _position(position) -> tuple[int, int]:
    if hasattr(position, "x") and hasattr(position, "y"):
        return int(position.x), int(position.y)
    return int(position[0]), int(position[1])


def _draw_surface(
    surface: pygame.Surface,
    position,
    rotation: float = 0.0,
    scale: float = 1.0,
    tint=colors.WHITE,
) -> None:
    frame = surface
    if scale != 1.0:
        width = max(1, int(frame.get_width() * float(scale)))
        height = max(1, int(frame.get_height() * float(scale)))
        frame = pygame.transform.smoothscale(frame, (width, height))
    if rotation:
        frame = pygame.transform.rotate(frame, -float(rotation))

    r, g, b, a = _color(tint)
    if (r, g, b, a) != (255, 255, 255, 255):
        frame = frame.copy()
        frame.fill((r, g, b, a), special_flags=pygame.BLEND_RGBA_MULT)

    pyray.get_drawing_surface().blit(frame, _position(position))


class Sprite:
    def __init__(self, texture_dictionary: dict[str, list[Any]] | None = None):
        self.texture_dictionary: dict[str, list[pygame.Surface]] = {}
        if texture_dictionary:
            for key, frames in texture_dictionary.items():
                self.texture_dictionary[key] = [self._as_surface(frame) for frame in frames]
        self.current_key: str | None = None
        self.frame_index: int = 0

    @staticmethod
    def _as_surface(frame: Any) -> pygame.Surface:
        if isinstance(frame, pygame.Surface):
            return frame
        if hasattr(frame, "surface") and isinstance(frame.surface, pygame.Surface):
            return frame.surface
        raise TypeError(f"Unsupported sprite frame: {frame!r}")

    def has_animation(self, key: str) -> bool:
        return key in self.texture_dictionary and len(self.texture_dictionary[key]) > 0

    def get_texture(self) -> pygame.Surface:
        if not self.current_key:
            raise ValueError("Sprite.current_key is not set. Call set_key(...) first.")
        if not self.has_animation(self.current_key):
            raise KeyError(f"Animation '{self.current_key}' is missing or empty.")

        frames = self.texture_dictionary[self.current_key]
        self.frame_index %= len(frames)
        return frames[self.frame_index]

    def draw(self, position, rotation: float = 0.0, scale: float = 1.0) -> None:
        _draw_surface(self.get_texture(), position, rotation, scale, colors.WHITE)

    def draw_specified(
        self,
        key: str,
        frame: int,
        position,
        rotation: float = 0.0,
        scale: float = 1.0,
        tint=colors.WHITE,
    ) -> None:
        _draw_surface(self.texture_dictionary[key][frame], position, rotation, scale, tint)

    def move_forward(self) -> None:
        if not self.current_key:
            return
        if not self.has_animation(self.current_key):
            return
        self.frame_index = (self.frame_index + 1) % len(self.texture_dictionary[self.current_key])

    def add_animation(self, key: str, frames) -> None:
        if frames is None or len(frames) == 0:
            raise ValueError("frames must be a non-empty list/sequence of surfaces.")
        self.texture_dictionary[key] = [self._as_surface(frame) for frame in frames]

    def set_key(self, key: str, reset_index: bool = True) -> None:
        if key not in self.texture_dictionary:
            raise KeyError(f"Animation '{key}' does not exist. Add it with add_animation(...).")
        if reset_index:
            self.frame_index = 0
        self.current_key = key
