from __future__ import annotations

import json
from pathlib import Path

import pygame

from utils.spritesheet import Spritesheet


class Assets:
    """
    Centralized pygame.Surface cache for image assets.

    Usage:
        surface = Assets.texture("sprites/pacman/pacman_pos_1_up.png")
        ...
        Assets.unload_all()
    """

    _textures: dict[str, pygame.Surface] = {}
    _wall_atlas_surface: pygame.Surface | None = None
    _wall_atlas: dict[str, dict[str, int]] | None = None
    _entity_atlas_surface: pygame.Surface | None = None
    _entity_atlas_map: dict[str, int] | None = None
    _entity_spritesheet: Spritesheet | None = None

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

        surface = cls._texture_from_wall_atlas(key)
        if surface is not None:
            cls._textures[key] = surface
            return surface

        surface = pygame.image.load(key)
        try:
            surface = surface.convert_alpha()
        except pygame.error:
            surface = surface.copy()
        cls._textures[key] = surface
        return surface

    @classmethod
    def _texture_from_wall_atlas(cls, key: str) -> pygame.Surface | None:
        normalized = key.replace("\\", "/")
        if not normalized.startswith("sprites/walls/"):
            return None
        return cls._wall_atlas_frame(normalized)

    @classmethod
    def _load_wall_atlas(cls) -> dict[str, dict[str, int]]:
        atlas_path = Path("sprites/walls_atlas.png")
        json_path = Path("sprites/walls_atlas.json")
        if not atlas_path.exists() or not json_path.exists():
            return {}

        if cls._wall_atlas is None:
            try:
                cls._wall_atlas = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                cls._wall_atlas = {}
        return cls._wall_atlas

    @classmethod
    def _wall_atlas_frame(cls, normalized: str) -> pygame.Surface | None:
        rect = cls._load_wall_atlas().get(normalized)
        if rect is None:
            return None

        if cls._wall_atlas_surface is None:
            cls._wall_atlas_surface = pygame.image.load("sprites/walls_atlas.png")
            try:
                cls._wall_atlas_surface = cls._wall_atlas_surface.convert_alpha()
            except pygame.error:
                cls._wall_atlas_surface = cls._wall_atlas_surface.copy()

        area = pygame.Rect(int(rect["x"]), int(rect["y"]), int(rect["w"]), int(rect["h"]))
        return cls._wall_atlas_surface.subsurface(area).copy()

    @classmethod
    def wall_atlas_textures(cls) -> dict[str, pygame.Surface]:
        return {
            path: texture
            for path in sorted(cls._load_wall_atlas())
            if (texture := cls._wall_atlas_frame(path)) is not None
        }

    @classmethod
    def load_entity_atlas(cls) -> Spritesheet | None:
        if cls._entity_spritesheet is not None:
            return cls._entity_spritesheet

        atlas_path = Path("assets/sprites/atlas.png")
        map_path = Path("assets/sprites/atlas_map.json")
        if not atlas_path.exists() or not map_path.exists():
            return None

        try:
            cls._entity_atlas_map = json.loads(map_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cls._entity_atlas_map = {}
            return None

        cls._entity_atlas_surface = pygame.image.load(str(atlas_path))
        try:
            cls._entity_atlas_surface = cls._entity_atlas_surface.convert_alpha()
        except pygame.error:
            cls._entity_atlas_surface = cls._entity_atlas_surface.copy()
        cols = max(1, cls._entity_atlas_surface.get_width() // 16)
        cls._entity_spritesheet = Spritesheet(cls._entity_atlas_surface, 16, 16, cols)
        return cls._entity_spritesheet

    @classmethod
    def entity_spritesheet(cls) -> Spritesheet | None:
        return cls.load_entity_atlas()

    @classmethod
    def entity_sprite_index(cls, key: str) -> int | None:
        if cls._entity_atlas_map is None:
            cls.load_entity_atlas()
        if cls._entity_atlas_map is None:
            return None
        value = cls._entity_atlas_map.get(key)
        return int(value) if value is not None else None

    @classmethod
    def unload_texture(cls, path: str | bytes | Path) -> None:
        cls._textures.pop(cls._to_path(path), None)

    @classmethod
    def unload_all(cls) -> None:
        cls._textures.clear()
        cls._wall_atlas_surface = None
        cls._wall_atlas = None
        cls._entity_atlas_surface = None
        cls._entity_atlas_map = None
        cls._entity_spritesheet = None

    @classmethod
    def clear_cache(cls) -> None:
        cls._textures.clear()
        cls._wall_atlas_surface = None
        cls._wall_atlas = None
        cls._entity_atlas_surface = None
        cls._entity_atlas_map = None
        cls._entity_spritesheet = None

    @classmethod
    def load_texture(cls, path: str | bytes | Path) -> pygame.Surface:
        """Alias to support old code style: Assets.load_texture(...)."""
        return cls.texture(path)
