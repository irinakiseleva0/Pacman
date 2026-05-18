from __future__ import annotations

import core.raylib_api as pyray


class FontManager:
    _fonts: dict = {}
    _initialized: bool = False

    TITLE   = "title"
    MONO    = "mono"
    DEFAULT = "default"

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized:
            return
        try:
            cls._fonts[cls.TITLE] = pyray.load_font_ex("assets/fonts/Orbitron.ttf", 96)
            cls._fonts[cls.MONO]  = pyray.load_font_ex("assets/fonts/ShareTechMono.ttf", 64)
            pyray.set_texture_filter_bilinear(cls._fonts[cls.TITLE].texture)
            pyray.set_texture_filter_bilinear(cls._fonts[cls.MONO].texture)
        except Exception as e:
            print(f"[FontManager] Failed to load custom fonts: {e}")
        cls._initialized = True

    @classmethod
    def get(cls, name: str):
        return cls._fonts.get(name)

    @classmethod
    def draw(cls, font_name: str, text: str, x: float, y: float,
             size: float, color, spacing: float = 1.5) -> None:
        font = cls._fonts.get(font_name)
        if font is None:
            pyray.draw_text(text, int(x), int(y), int(size), color)
            return
        pyray.draw_text_ex(font, text, x, y, size, spacing, color)

    @classmethod
    def measure(cls, font_name: str, text: str, size: float,
                spacing: float = 1.5) -> tuple[float, float]:
        font = cls._fonts.get(font_name)
        if font is None:
            w = pyray.measure_text(text, int(size))
            return float(w), float(size)
        return pyray.measure_text_ex(font, text, size, spacing)

    @classmethod
    def draw_centered(cls, font_name: str, text: str, center_x: float,
                      y: float, size: float, color, spacing: float = 1.5) -> None:
        w, _ = cls.measure(font_name, text, size, spacing)
        cls.draw(font_name, text, center_x - w / 2, y, size, color, spacing)

    @classmethod
    def shutdown(cls) -> None:
        for font in cls._fonts.values():
            try:
                pyray.unload_font(font)
            except Exception:
                pass
        cls._fonts.clear()
        cls._initialized = False