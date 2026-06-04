from __future__ import annotations

from pathlib import Path

import pygame


class Assets:
    """
    Centralized pygame.Surface cache for image assets.

    Usage:
        surface = Assets.texture("sprites/pacman/pacman_pos_1_up.png")
        ...
        Assets.unload_all()
    """

    _textures: dict[str, pygame.Surface] = {}

    @staticmethod
    def _to_path(path: str | bytes | Path) -> str:
        if isinstance(path, bytes):
            return path.decode("utf-8")
        return str(path)

    @classmethod
    def texture(cls, path: str | bytes | Path) -> pygame.Surface:
        """
        Load an image once as a pygame.Surface and return the cached surface.
        """
        key = cls._to_path(path)
        surface = cls._textures.get(key)
        if surface is not None:
            return surface

        surface = pygame.image.load(key)
        try:
            surface = surface.convert_alpha()
        except pygame.error:
            surface = surface.copy()
        cls._textures[key] = surface
        return surface

    @classmethod
    def unload_texture(cls, path: str | bytes | Path) -> None:
        cls._textures.pop(cls._to_path(path), None)

    @classmethod
    def unload_all(cls) -> None:
        cls._textures.clear()

    @classmethod
    def clear_cache(cls) -> None:
        cls._textures.clear()

    @classmethod
    def load_texture(cls, path: str | bytes | Path) -> pygame.Surface:
        """Alias to support old code style: Assets.load_texture(...)."""
        return cls.texture(path)
