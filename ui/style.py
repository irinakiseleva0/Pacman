from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CyberColors:
    bg_top: tuple[int, int, int, int] = (6, 8, 18, 255)
    bg_mid: tuple[int, int, int, int] = (4, 6, 14, 255)
    bg_bottom: tuple[int, int, int, int] = (1, 2, 8, 255)

    panel_outer: tuple[int, int, int, int] = (8, 12, 24, 220)
    panel_inner: tuple[int, int, int, int] = (5, 9, 20, 200)
    panel_strong: tuple[int, int, int, int] = (6, 11, 22, 220)

    panel_accent: tuple[int, int, int, int] = (32, 200, 220, 90)

    glass_edge: tuple[int, int, int, int] = (80, 180, 200, 70)

    text_primary: tuple[int, int, int, int] = (210, 230, 245, 255)
    text_dim: tuple[int, int, int, int] = (130, 165, 195, 255)
    text_muted: tuple[int, int, int, int] = (70, 100, 130, 255)

    live_cyan: tuple[int, int, int, int] = (0, 220, 245, 255)
 
    live_pink: tuple[int, int, int, int] = (220, 40, 170, 255)

    live_gold: tuple[int, int, int, int] = (240, 185, 60, 255)
  
    live_red: tuple[int, int, int, int] = (230, 70, 100, 255)
    live_green: tuple[int, int, int, int] = (80, 230, 150, 255)

    button_idle: tuple[int, int, int, int] = (8, 14, 26, 255)
    button_active: tuple[int, int, int, int] = (0, 40, 60, 255)
    button_hover: tuple[int, int, int, int] = (12, 32, 50, 255)


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