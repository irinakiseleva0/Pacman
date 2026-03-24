from __future__ import annotations

from dataclasses import dataclass


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


LAYOUT_PROFILES: dict[str, LayoutProfile] = {
    "desktop": LayoutProfile(
        name="desktop",
        tile_size=36,
        hud_mode="side",
        hud_extent=600,
        menu_button_width=340,
        menu_button_height=80,
        menu_title_size=118,
        menu_heading_size=38,
        menu_body_size=28,
        menu_footer_size=22,
        hud_font_size=32,
        hud_line_height=44,
        hud_columns=1,
    ),
    "mobile": LayoutProfile(
        name="mobile",
        tile_size=18,
        hud_mode="bottom",
        hud_extent=190,
        menu_button_width=240,
        menu_button_height=60,
        menu_title_size=58,
        menu_heading_size=24,
        menu_body_size=18,
        menu_footer_size=16,
        hud_font_size=18,
        hud_line_height=24,
        hud_columns=2,
    ),
}


DEFAULT_LAYOUT = "desktop"
