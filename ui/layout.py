from __future__ import annotations

from dataclasses import dataclass

import core.raylib_api as pyray
from utils.config_resources import load_config_json


_LAYOUT_FALLBACK = {
    "default_layout": "desktop",
    "profiles": {
        "desktop": {
            "name": "desktop",
            "tile_size": 38,
            "hud_mode": "side",
            "hud_extent": 430,
            "menu_button_width": 340,
            "menu_button_height": 80,
            "menu_title_size": 118,
            "menu_heading_size": 38,
            "menu_body_size": 28,
            "menu_footer_size": 22,
            "hud_font_size": 28,
            "hud_line_height": 36,
            "hud_columns": 1,
        },
        "mobile": {
            "name": "mobile",
            "tile_size": 18,
            "hud_mode": "bottom",
            "hud_extent": 190,
            "menu_button_width": 240,
            "menu_button_height": 60,
            "menu_title_size": 58,
            "menu_heading_size": 24,
            "menu_body_size": 18,
            "menu_footer_size": 16,
            "hud_font_size": 18,
            "hud_line_height": 24,
            "hud_columns": 2,
        },
    },
}


def _load_layout_data() -> dict:
    data = load_config_json("layouts.json")
    try:
        if isinstance(data, dict) and isinstance(data.get("profiles"), dict):
            return data
    except (TypeError, ValueError):
        pass
    return _LAYOUT_FALLBACK


_LAYOUT_DATA = _load_layout_data()


@dataclass(frozen=True)
class LayoutProfile:
    name: str
    tile_size: int
    hud_mode: str
    hud_extent: int
    menu_button_width: int
    menu_button_height: int
    menu_title_size: int
    menu_heading_size: int
    menu_body_size: int
    menu_footer_size: int
    hud_font_size: int
    hud_line_height: int
    hud_columns: int


def _build_layout_profiles() -> dict[str, LayoutProfile]:
    profiles: dict[str, LayoutProfile] = {}
    raw_profiles = _LAYOUT_DATA.get("profiles", {})
    for name, values in raw_profiles.items():
        profiles[name] = LayoutProfile(
            name=values["name"],
            tile_size=values["tile_size"],
            hud_mode=values["hud_mode"],
            hud_extent=values["hud_extent"],
            menu_button_width=values["menu_button_width"],
            menu_button_height=values["menu_button_height"],
            menu_title_size=values["menu_title_size"],
            menu_heading_size=values["menu_heading_size"],
            menu_body_size=values["menu_body_size"],
            menu_footer_size=values["menu_footer_size"],
            hud_font_size=values["hud_font_size"],
            hud_line_height=values["hud_line_height"],
            hud_columns=values["hud_columns"],
        )
    return profiles


LAYOUT_PROFILES: dict[str, LayoutProfile] = _build_layout_profiles()
DEFAULT_LAYOUT = _LAYOUT_DATA.get("default_layout", "desktop")


def centered_rect(center_x: int, y: int, width: int, height: int):
    return pyray.Rectangle(center_x - width // 2, y, width, height)


def vertical_stack(x: int, y: int, width: int, heights: list[int], gap: int) -> list[object]:
    rects = []
    current_y = y
    for height in heights:
        rects.append(pyray.Rectangle(x, current_y, width, height))
        current_y += height + gap
    return rects


def centered_vertical_stack(center_x: int, y: int, width: int, heights: list[int], gap: int) -> list[object]:
    return vertical_stack(center_x - width // 2, y, width, heights, gap)
