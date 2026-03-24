from __future__ import annotations

from typing import Dict, Any
import core.raylib_api as pyray


class Assets:
    """
    Centralized asset cache.

    Usage:
        tex = Assets.texture("sprites/pacman/pacman_pos_1_up.png")
        ...
        Assets.unload_all()
    """

    _textures: Dict[str, Any] = {}

    @staticmethod
    def _to_bytes(s: str | bytes) -> bytes:
        return s.encode("utf-8") if isinstance(s, str) else s

    @classmethod
    def texture(cls, path: str) -> Any:
        """
        Load a texture once and return cached texture on next calls.
        """
        tex = cls._textures.get(path)
        if tex is not None:
            return tex

        tex = pyray.load_texture(cls._to_bytes(path))
        cls._textures[path] = tex
        return tex

    @classmethod
    def unload_texture(cls, path: str) -> None:
        """
        Unload one texture from cache.
        """
        tex = cls._textures.pop(path, None)
        if tex is None:
            return
        try:
            pyray.unload_texture(tex)
        except Exception:
            # If window already closed or raylib already freed resources
            pass

    @classmethod
    def unload_all(cls) -> None:
        """
        Unload all cached textures.
        Call this BEFORE pyray.close_window().
        """
        for path in list(cls._textures.keys()):
            cls.unload_texture(path)

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear cache without unloading (almost never needed).
        """
        cls._textures.clear()

    # ---- Compatibility helpers (optional) ----
    @classmethod
    def load_texture(cls, path: str) -> Any:
        """Alias to support old code style: Assets.load_texture(...)"""
        return cls.texture(path)
