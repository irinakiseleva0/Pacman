from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CyberColors:
    bg_top: tuple[int, int, int, int] = (8, 6, 4, 255)
    bg_mid: tuple[int, int, int, int] = (5, 4, 2, 255)
    bg_bottom: tuple[int, int, int, int] = (2, 1, 0, 255)

    panel_outer: tuple[int, int, int, int] = (14, 10, 6, 220)
    panel_inner: tuple[int, int, int, int] = (10, 7, 4, 200)
    panel_strong: tuple[int, int, int, int] = (18, 12, 6, 230)

    panel_accent: tuple[int, int, int, int] = (252, 176, 64, 180)
    glass_edge: tuple[int, int, int, int] = (252, 176, 64, 60)

    text_primary: tuple[int, int, int, int] = (245, 235, 210, 255)
    text_dim: tuple[int, int, int, int] = (180, 160, 120, 255)
    text_muted: tuple[int, int, int, int] = (100, 85, 60, 255)

    live_cyan: tuple[int, int, int, int] = (82, 226, 255, 255)
    live_pink: tuple[int, int, int, int] = (255, 46, 160, 255)
    live_gold: tuple[int, int, int, int] = (252, 176, 64, 255)
    live_red: tuple[int, int, int, int] = (255, 60, 80, 255)
    live_green: tuple[int, int, int, int] = (80, 230, 150, 255)

    button_idle: tuple[int, int, int, int] = (14, 10, 6, 255)
    button_active: tuple[int, int, int, int] = (50, 32, 4, 255)
    button_hover: tuple[int, int, int, int] = (30, 20, 4, 255)

    wall_tint: tuple[int, int, int, int] = (20, 40, 80, 255)
    wall_edge_dim: tuple[int, int, int, int] = (60, 160, 220, 255)
    wall_bg: tuple[int, int, int, int] = (4, 4, 8, 255)


@dataclass(frozen=True)
class CyberTypography:
    title: int = 82
    screen_title: int = 50
    section: int = 18
    body: int = 16
    small: int = 12
    button: int = 20


@dataclass(frozen=True)
class CyberSpacing:
    xs: int = 6
    sm: int = 10
    md: int = 16
    lg: int = 24
    xl: int = 32
    panel_pad: int = 24
    button_gap: int = 10
    section_gap: int = 18


@dataclass(frozen=True)
class CyberSizes:
    menu_panel_width: int = 460
    menu_panel_height: int = 720
    button_width: int = 320
    button_height: int = 44
    button_height_primary: int = 44
    button_height_compact: int = 44
    badge_height: int = 28
    progress_height: int = 12


@dataclass(frozen=True)
class CyberMotion:
    intro_seconds: float = 0.9
    menu_item_stagger: float = 0.035
    slow_pulse: float = 2.2
    button_pulse: float = 4.8
    scanline_speed: float = 22.0
    hover_scale: float = 1.018
    focus_scale: float = 1.03
    glow_idle: int = 2
    glow_hover: int = 7
    glow_focus: int = 14


@dataclass(frozen=True)
class CyberStyle:
    colors: CyberColors = CyberColors()
    typography: CyberTypography = CyberTypography()
    spacing: CyberSpacing = CyberSpacing()
    sizes: CyberSizes = CyberSizes()
    motion: CyberMotion = CyberMotion()


UI_STYLE = CyberStyle()