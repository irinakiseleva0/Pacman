from __future__ import annotations

from typing import Dict, List, Optional, Any

from core.raylib_api import draw_texture_ex
from raylib import colors


class Sprite:
    def __init__(self, texture_dictionary: Optional[Dict[str, List[Any]]] = None):
        self.texture_dictionary: Dict[str, List[Any]] = texture_dictionary or {}
        self.current_key: Optional[str] = None
        self.frame_index: int = 0

    def has_animation(self, key: str) -> bool:
        return key in self.texture_dictionary and len(self.texture_dictionary[key]) > 0

    def get_texture(self):
        if not self.current_key:
            raise ValueError("Sprite.current_key is not set. Call set_key(...) first.")
        if not self.has_animation(self.current_key):
            raise KeyError(f"Animation '{self.current_key}' is missing or empty.")

        frames = self.texture_dictionary[self.current_key]
        self.frame_index %= len(frames)
        return frames[self.frame_index]

    def draw(self, position, rotation: float = 0.0, scale: float = 1.0):
        draw_texture_ex(self.get_texture(), position, rotation, scale, colors.WHITE)

    def draw_specified(
        self,
        key: str,
        frame: int,
        position,
        rotation: float = 0.0,
        scale: float = 1.0,
    ):
        draw_texture_ex(self.texture_dictionary[key][frame], position, rotation, scale, colors.WHITE)

    def move_forward(self):
        if not self.current_key:
            return
        if not self.has_animation(self.current_key):
            return
        self.frame_index = (self.frame_index + 1) % len(self.texture_dictionary[self.current_key])

    def add_animation(self, key: str, frames):
        if frames is None or len(frames) == 0:
            raise ValueError("frames must be a non-empty list/sequence of textures.")
        self.texture_dictionary[key] = list(frames)

    def set_key(self, key: str, reset_index: bool = True):
        if key not in self.texture_dictionary:
            raise KeyError(f"Animation '{key}' does not exist. Add it with add_animation(...).")
        if reset_index:
            self.frame_index = 0
        self.current_key = key
