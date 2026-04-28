from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CyberColors:
    bg_top: tuple[int, int, int, int] = (8, 10, 26, 255)
    bg_mid: tuple[int, int, int, int] = (5, 8, 18, 255)
    bg_bottom: tuple[int, int, int, int] = (1, 3, 10, 255)
    panel_outer: tuple[int, int, int, int] = (7, 10, 22, 242)
    panel_inner: tuple[int, int, int, int] = (4, 8, 18, 230)
    panel_strong: tuple[int, int, int, int] = (5, 10, 22, 242)
    panel_accent: tuple[int, int, int, int] = (52, 240, 255, 255)
    glass_edge: tuple[int, int, int, int] = (138, 246, 255, 255)
    text_primary: tuple[int, int, int, int] = (242, 250, 255, 255)
    text_dim: tuple[int, int, int, int] = (178, 204, 232, 255)
    text_muted: tuple[int, int, int, int] = (105, 132, 164, 255)
    live_cyan: tuple[int, int, int, int] = (32, 244, 255, 255)
    live_pink: tuple[int, int, int, int] = (255, 46, 199, 255)
    live_gold: tuple[int, int, int, int] = (255, 211, 86, 255)
    live_red: tuple[int, int, int, int] = (255, 82, 116, 255)
    live_green: tuple[int, int, int, int] = (96, 255, 166, 255)
    button_idle: tuple[int, int, int, int] = (10, 18, 34, 255)
    button_active: tuple[int, int, int, int] = (16, 34, 54, 255)
    button_hover: tuple[int, int, int, int] = (28, 42, 66, 255)


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
    glow_idle: int = 4
    glow_hover: int = 10
    glow_focus: int = 18


@dataclass(frozen=True)
class CyberStyle:
    colors: CyberColors = CyberColors()
    typography: CyberTypography = CyberTypography()
    spacing: CyberSpacing = CyberSpacing()
    sizes: CyberSizes = CyberSizes()
    motion: CyberMotion = CyberMotion()


UI_STYLE = CyberStyle()
