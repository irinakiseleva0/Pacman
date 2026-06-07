from __future__ import annotations

import math

import core.raylib_api as pyray
from core import colors

from ui import pygame_primitives as pgui
from ui.style import UI_STYLE
from utils.visual_effects import with_alpha


BG_TOP = UI_STYLE.colors.bg_top
BG_BOTTOM = UI_STYLE.colors.bg_bottom
PANEL_OUTER = UI_STYLE.colors.panel_outer
PANEL_INNER = UI_STYLE.colors.panel_inner
PANEL_ACCENT = UI_STYLE.colors.panel_accent
TEXT_DIM = UI_STYLE.colors.text_dim
BUTTON_IDLE = UI_STYLE.colors.button_idle
BUTTON_ACTIVE = UI_STYLE.colors.button_active
BUTTON_HOVER = UI_STYLE.colors.button_hover
LIVE_CYAN = UI_STYLE.colors.live_cyan
LIVE_PINK = UI_STYLE.colors.live_pink
LIVE_GOLD = UI_STYLE.colors.live_gold
PRIMARY_GAMEPLAY = LIVE_CYAN
SECONDARY_UI = LIVE_PINK
ACCENT_IMPORTANT = LIVE_GOLD
PANEL_PINK = (255, 86, 212, 255)
NOIR_BLUE = (4, 6, 18, 255)
STREET_BLUE = (10, 16, 38, 255)
GLASS_EDGE = UI_STYLE.colors.glass_edge
PRESENTATION_MODE = False
THEME_PRESETS = {
    "Neon District": {
        "PANEL_ACCENT": (102, 232, 255, 255),
        "LIVE_CYAN": (112, 242, 255, 255),
        "LIVE_PINK": (255, 86, 212, 255),
        "LIVE_GOLD": (255, 208, 92, 255),
        "BG_TOP": (34, 20, 72, 255),
        "NOIR_BLUE": (6, 8, 26, 255),
        "STREET_BLUE": (14, 20, 48, 255),
    },
    "Amber Rain": {
        "PANEL_ACCENT": (255, 201, 96, 255),
        "LIVE_CYAN": (255, 190, 88, 255),
        "LIVE_PINK": (255, 122, 56, 255),
        "LIVE_GOLD": (255, 227, 122, 255),
        "BG_TOP": (60, 26, 18, 255),
        "NOIR_BLUE": (18, 10, 12, 255),
        "STREET_BLUE": (32, 22, 18, 255),
    },
    "Ice Circuit": {
        "PANEL_ACCENT": (150, 240, 255, 255),
        "LIVE_CYAN": (152, 250, 255, 255),
        "LIVE_PINK": (120, 180, 255, 255),
        "LIVE_GOLD": (215, 245, 255, 255),
        "BG_TOP": (20, 42, 72, 255),
        "NOIR_BLUE": (4, 12, 24, 255),
        "STREET_BLUE": (10, 26, 40, 255),
    },
    "Velvet Alley": {
        "PANEL_ACCENT": (255, 130, 224, 255),
        "LIVE_CYAN": (196, 118, 255, 255),
        "LIVE_PINK": (255, 72, 170, 255),
        "LIVE_GOLD": (255, 166, 214, 255),
        "BG_TOP": (54, 14, 54, 255),
        "NOIR_BLUE": (18, 6, 22, 255),
        "STREET_BLUE": (28, 10, 32, 255),
    },
    "Cool Summer": {
        "PANEL_ACCENT": (120, 220, 255, 255),
        "LIVE_CYAN": (132, 238, 255, 255),
        "LIVE_PINK": (152, 122, 255, 255),
        "LIVE_GOLD": (220, 245, 255, 255),
        "BG_TOP": (18, 30, 70, 255),
        "NOIR_BLUE": (6, 12, 28, 255),
        "STREET_BLUE": (12, 24, 46, 255),
    },
    "Solar Pulse": {
        "PANEL_ACCENT": (255, 214, 94, 255),
        "LIVE_CYAN": (255, 198, 88, 255),
        "LIVE_PINK": (255, 132, 56, 255),
        "LIVE_GOLD": (255, 236, 148, 255),
        "BG_TOP": (54, 28, 14, 255),
        "NOIR_BLUE": (18, 10, 10, 255),
        "STREET_BLUE": (34, 22, 16, 255),
    },
    "Ultraviolet": {
        "PANEL_ACCENT": (196, 138, 255, 255),
        "LIVE_CYAN": (132, 166, 255, 255),
        "LIVE_PINK": (212, 88, 255, 255),
        "LIVE_GOLD": (236, 196, 255, 255),
        "BG_TOP": (34, 12, 62, 255),
        "NOIR_BLUE": (12, 6, 28, 255),
        "STREET_BLUE": (22, 12, 38, 255),
    },
    "Grid Echo": {
        "PANEL_ACCENT": (130, 232, 255, 255),
        "LIVE_CYAN": (102, 216, 255, 255),
        "LIVE_PINK": (118, 255, 172, 255),
        "LIVE_GOLD": (210, 255, 255, 255),
        "BG_TOP": (12, 34, 64, 255),
        "NOIR_BLUE": (6, 14, 24, 255),
        "STREET_BLUE": (10, 32, 48, 255),
    },
    "After Hours": {
        "PANEL_ACCENT": (255, 196, 118, 255),
        "LIVE_CYAN": (255, 184, 88, 255),
        "LIVE_PINK": (255, 114, 74, 255),
        "LIVE_GOLD": (255, 226, 140, 255),
        "BG_TOP": (34, 24, 54, 255),
        "NOIR_BLUE": (16, 12, 20, 255),
        "STREET_BLUE": (28, 20, 28, 255),
    },
    "Trial Chrome": {
        "PANEL_ACCENT": (218, 228, 246, 255),
        "LIVE_CYAN": (230, 238, 255, 255),
        "LIVE_PINK": (255, 110, 214, 255),
        "LIVE_GOLD": (255, 255, 255, 255),
        "BG_TOP": (28, 24, 44, 255),
        "NOIR_BLUE": (12, 12, 18, 255),
        "STREET_BLUE": (24, 22, 34, 255),
    },
}
DOT_MATRIX_GLYPHS = {
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def set_visual_theme(theme_name: str) -> None:
    global PANEL_ACCENT, LIVE_CYAN, LIVE_PINK, LIVE_GOLD, PRIMARY_GAMEPLAY, SECONDARY_UI, ACCENT_IMPORTANT, BG_TOP, NOIR_BLUE, STREET_BLUE
    preset = THEME_PRESETS.get(theme_name, THEME_PRESETS["Neon District"])
    PANEL_ACCENT = preset["PANEL_ACCENT"]
    LIVE_CYAN = preset["LIVE_CYAN"]
    LIVE_PINK = preset["LIVE_PINK"]
    LIVE_GOLD = preset["LIVE_GOLD"]
    PRIMARY_GAMEPLAY = LIVE_CYAN
    SECONDARY_UI = LIVE_PINK
    ACCENT_IMPORTANT = LIVE_GOLD
    BG_TOP = preset["BG_TOP"]
    NOIR_BLUE = preset["NOIR_BLUE"]
    STREET_BLUE = preset["STREET_BLUE"]


def set_presentation_mode(enabled: bool) -> None:
    global PRESENTATION_MODE
    PRESENTATION_MODE = bool(enabled)


def button_clicked(rect) -> bool:
    mouse = pyray.get_mouse_position()
    hovered = pyray.check_collision_point_rec(mouse, rect)
    return hovered and pyray.is_mouse_button_pressed(0)


def centered_rect(center_x: int, y: int, width: int, height: int):
    return pyray.Rectangle(
        center_x - width // 2,
        y,
        width,
        height,
    )


def _ui_time(time_s: float | None = None) -> float:
    if time_s is not None:
        return time_s
    getter = getattr(pyray, "get_time", None)
    return float(getter()) if getter is not None else 0.0


def _scaled_rect(rect, scale: float):
    if scale == 1.0:
        return rect
    new_w = rect.width * scale
    new_h = rect.height * scale
    return pyray.Rectangle(
        rect.x + (rect.width - new_w) / 2,
        rect.y + (rect.height - new_h) / 2,
        new_w,
        new_h,
    )


_BUTTON_STATES: dict[str, tuple[float, float, float]] = {}


def _lerp(start: float, end: float, amount: float) -> float:
    return start + (end - start) * max(0.0, min(1.0, amount))


def _blend_color(a, b, amount: float):
    amount = max(0.0, min(1.0, amount))
    return tuple(int(_lerp(a[index], b[index], amount)) for index in range(4))


def _button_state_key(rect, text: str) -> str:
    return f"{text}:{int(rect.x)}:{int(rect.y)}:{int(rect.width)}:{int(rect.height)}"


def _smooth_button_state(rect, text: str, hovered: bool, focused: bool, time_s: float) -> tuple[float, float]:
    key = _button_state_key(rect, text)
    hover_t, focus_t, last_time = _BUTTON_STATES.get(key, (0.0, 0.0, time_s))
    dt = max(0.0, min(0.08, time_s - last_time))
    speed = 9.0
    amount = 1.0 - math.exp(-speed * dt) if dt > 0.0 else 1.0
    hover_t = _lerp(hover_t, 1.0 if hovered else 0.0, amount)
    focus_t = _lerp(focus_t, 1.0 if focused else 0.0, amount)
    _BUTTON_STATES[key] = (hover_t, focus_t, time_s)
    return hover_t, focus_t


def _rare_flicker(time_s: float, seed: float = 0.0, *, threshold: float = 0.985) -> float:
    phase = math.sin(time_s * 11.0 + seed * 1.73) * 0.5 + 0.5
    if phase < threshold:
        return 0.0
    return min(1.0, (phase - threshold) / max(0.001, 1.0 - threshold))


def _draw_scanline_overlay(rect, *, alpha: int = 10, spacing: int = 6, time_s: float = 0.0) -> None:
    if rect.width <= 0 or rect.height <= 0:
        return
    offset = int((time_s * 22.0) % max(1, spacing))
    y = int(rect.y) + offset
    end_y = int(rect.y + rect.height)
    while y < end_y:
        pgui.draw_rect(
            pyray.Rectangle(rect.x + 2, y, max(0, rect.width - 4), 1),
            with_alpha(colors.WHITE, alpha),
        )
        y += spacing


def _draw_grid_overlay(rect, *, alpha: int = 8, cell: int = 28) -> None:
    if rect.width <= 0 or rect.height <= 0:
        return
    x = int(rect.x + cell)
    end_x = int(rect.x + rect.width)
    while x < end_x:
        pgui.draw_rect(
            pyray.Rectangle(x, rect.y + 2, 1, max(0, rect.height - 4)),
            with_alpha(PANEL_ACCENT, alpha),
        )
        x += cell
    y = int(rect.y + cell)
    end_y = int(rect.y + rect.height)
    while y < end_y:
        pgui.draw_rect(
            pyray.Rectangle(rect.x + 2, y, max(0, rect.width - 4), 1),
            with_alpha(LIVE_PINK, max(1, alpha - 2)),
        )
        y += cell


def _draw_corner_brackets(rect, accent_color=LIVE_CYAN, *, alpha: int = 120, length: int = 18, thickness: int = 2) -> None:
    length = max(6, min(length, int(min(rect.width, rect.height) / 2)))
    specs = (
        (rect.x, rect.y, length, thickness),
        (rect.x, rect.y, thickness, length),
        (rect.x + rect.width - length, rect.y, length, thickness),
        (rect.x + rect.width - thickness, rect.y, thickness, length),
        (rect.x, rect.y + rect.height - thickness, length, thickness),
        (rect.x, rect.y + rect.height - length, thickness, length),
        (rect.x + rect.width - length, rect.y + rect.height - thickness, length, thickness),
        (rect.x + rect.width - thickness, rect.y + rect.height - length, thickness, length),
    )
    for x, y, width, height in specs:
        pgui.draw_rect(pyray.Rectangle(x, y, width, height), with_alpha(accent_color, alpha))


def _draw_notch_marks(rect, accent_color=LIVE_PINK, *, alpha: int = 86) -> None:
    notch = max(8, min(18, int(rect.height * 0.28)))
    pgui.draw_rect(pyray.Rectangle(rect.x - 1, rect.y + notch, 2, rect.height - notch * 2), with_alpha(accent_color, alpha))
    pgui.draw_rect(pyray.Rectangle(rect.x + notch, rect.y - 1, rect.width * 0.22, 2), with_alpha(accent_color, alpha))
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - rect.width * 0.22 - notch, rect.y + rect.height - 1, rect.width * 0.22, 2),
        with_alpha(accent_color, max(24, alpha - 28)),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 2, rect.y + notch, 2, rect.height - notch * 2),
        with_alpha(LIVE_CYAN, max(24, alpha - 22)),
    )


def _draw_signal_ticks(rect, accent_color=LIVE_CYAN, *, alpha: int = 76, time_s: float = 0.0) -> None:
    tick_count = max(3, min(7, int(rect.width / 44)))
    tick_w = max(10, int((rect.width - 26) / (tick_count * 2)))
    start_x = rect.x + 13
    y = rect.y + rect.height - 10
    for index in range(tick_count):
        flicker = 0.5 + 0.5 * math.sin(time_s * 5.0 + index * 1.8 + rect.y * 0.01)
        tick_alpha = int(alpha * (0.55 + flicker * 0.45))
        color = accent_color if index % 2 == 0 else LIVE_PINK
        pgui.draw_rect(
            pyray.Rectangle(start_x + index * tick_w * 2, y, tick_w, 2),
            with_alpha(color, tick_alpha),
        )


def _draw_glitch_reveal(rect, progress: float, *, accent_color=LIVE_CYAN, time_s: float = 0.0) -> None:
    progress = max(0.0, min(1.0, progress))
    if progress >= 1.0:
        return
    reveal_h = rect.height * (1.0 - progress)
    pgui.draw_rect(
        pyray.Rectangle(rect.x - 6, rect.y - 6, rect.width + 12, reveal_h + 12),
        with_alpha(colors.BLACK, int(180 * (1.0 - progress))),
    )
    scan_y = rect.y + rect.height * progress
    pgui.draw_rect(
        pyray.Rectangle(rect.x - 2, scan_y - 2, rect.width + 4, 3),
        with_alpha(accent_color, int(50 + (1.0 - progress) * 80)),
    )
    glitch = _rare_flicker(time_s, rect.x + rect.y, threshold=0.93)
    if glitch > 0.0:
        for index in range(3):
            band_w = rect.width * (0.18 + index * 0.12)
            band_x = rect.x + 12 + index * rect.width * 0.19
            band_y = rect.y + 10 + index * 16 + (math.sin(time_s * 22.0 + index) * 2)
            pgui.draw_rect(
                pyray.Rectangle(band_x, band_y, band_w, 2),
                with_alpha(accent_color, int(18 + glitch * 48)),
            )


def draw_scene_scan_intro(width: int, height: int, progress: float, *, accent_color=LIVE_CYAN, time_s: float | None = None) -> None:
    time_s = _ui_time(time_s)
    progress = max(0.0, min(1.0, progress))
    if progress >= 1.0:
        return

    veil_h = height * (1.0 - progress)
    pgui.draw_rect(
        pyray.Rectangle(0, 0, width, veil_h),
        with_alpha(colors.BLACK, int(220 * (1.0 - progress) + 20)),
    )
    scan_y = veil_h
    glow_alpha = int(36 + (1.0 - progress) * 54)
    pgui.draw_rect(
        pyray.Rectangle(0, scan_y - 2, width, 4),
        with_alpha(accent_color, glow_alpha),
    )
    pgui.draw_rect(
        pyray.Rectangle(0, scan_y + 4, width, 1),
        with_alpha(colors.WHITE, int(12 + (1.0 - progress) * 20)),
    )

    for index in range(4):
        band_y = scan_y - 32 - index * 22 + math.sin(time_s * 8.0 + index) * 2
        if band_y < 0:
            continue
        pgui.draw_rect(
            pyray.Rectangle(width * (0.08 + index * 0.12), band_y, width * (0.18 + index * 0.06), 2),
            with_alpha(accent_color if index % 2 == 0 else LIVE_PINK, int(8 + (1.0 - progress) * 26)),
        )


def draw_title_glitch_pass(center_x: int, y: int, width: int, progress: float, *, accent_color=LIVE_PINK, time_s: float | None = None) -> None:
    time_s = _ui_time(time_s)
    progress = max(0.0, min(1.0, progress))
    if progress >= 1.0:
        return

    intensity = 1.0 - progress
    for index in range(5):
        band_w = width * (0.28 + (index % 3) * 0.16)
        offset = math.sin(time_s * (10.0 + index * 1.6) + index * 2.3) * (10 + intensity * 26)
        band_x = center_x - band_w / 2 + offset
        band_y = y - 18 + index * 12
        pyray.draw_rectangle_rec(
            pyray.Rectangle(band_x, band_y, band_w, 3),
            with_alpha(accent_color if index % 2 == 0 else LIVE_CYAN, int(14 + intensity * 58)),
        )


def draw_button(rect, text: str, focused: bool = False, *, time_s: float | None = None) -> None:
    time_s = _ui_time(time_s)
    mouse = pyray.get_mouse_position()
    hovered = pyray.check_collision_point_rec(mouse, rect)
    pulse = 0.5 + 0.5 * math.sin(time_s * 4.8 + rect.x * 0.01)
    flicker = _rare_flicker(time_s, rect.x + rect.y)
    hover_t, focus_t = _smooth_button_state(rect, text, hovered, focused, time_s)
    active_t = max(hover_t * 0.72, focus_t)
    outer_glow = LIVE_CYAN if focused else LIVE_PINK if hovered else PANEL_ACCENT
    scale = 1.0 + (UI_STYLE.motion.hover_scale - 1.0) * hover_t + (UI_STYLE.motion.focus_scale - 1.0) * focus_t
    draw_rect = _scaled_rect(rect, scale)
    base_fill = with_alpha((5, 10, 22, 255), 210)
    hover_fill = with_alpha((12, 24, 38, 255), 224)
    focus_fill = with_alpha((12, 30, 46, 255), 232)
    fill_color = _blend_color(_blend_color(base_fill, hover_fill, hover_t), focus_fill, focus_t)
    border_color = _blend_color(with_alpha(GLASS_EDGE, 68), with_alpha(LIVE_CYAN, 150), active_t)

    _draw_soft_rect_glow(
        draw_rect,
        outer_glow,
        spread=12 + int(active_t * 8),
        alpha=UI_STYLE.motion.glow_idle + int(active_t * UI_STYLE.motion.glow_focus) + int(pulse * 3) + int(flicker * 4),
        layers=3,
    )
    if focused:
        _draw_soft_rect_glow(
            pyray.Rectangle(draw_rect.x + 6, draw_rect.y + 6, draw_rect.width - 12, draw_rect.height - 12),
            LIVE_CYAN,
            spread=8,
            alpha=6 + int(pulse * 4),
            layers=2,
        )
    pgui.draw_rect(draw_rect, fill_color)
    pgui.draw_rect(draw_rect, border_color, 1)
    _draw_notch_marks(draw_rect, LIVE_PINK if hover_t > 0.2 else PANEL_ACCENT, alpha=48 + int(active_t * 42))
    _draw_corner_brackets(
        draw_rect,
        LIVE_CYAN if focus_t > 0.2 else LIVE_PINK if hover_t > 0.2 else PANEL_ACCENT,
        alpha=62 + int(active_t * 72),
        length=15,
    )
    if focus_t > 0.08:
        pgui.draw_rect(
            pyray.Rectangle(draw_rect.x + 8, draw_rect.y + 8, 3, max(0, draw_rect.height - 16)),
            with_alpha(LIVE_CYAN, int(80 + focus_t * 100)),
        )
    pgui.draw_rect(
        pyray.Rectangle(draw_rect.x + 2, draw_rect.y + 2, max(0, draw_rect.width - 4), max(0, draw_rect.height * 0.24)),
        with_alpha(LIVE_CYAN, 4 + int(active_t * 5) + int(flicker * 4)),
    )
    pgui.draw_rect(
        pyray.Rectangle(draw_rect.x + 18, draw_rect.y + draw_rect.height - 6, max(0, draw_rect.width - 36), 2),
        with_alpha(LIVE_CYAN if focus_t > 0.2 else PANEL_ACCENT, 28 + int(active_t * 70) + int(pulse * 6)),
    )
    _draw_scanline_overlay(draw_rect, alpha=2, spacing=8, time_s=time_s)
    _draw_signal_ticks(draw_rect, LIVE_CYAN if focus_t > 0.2 else PANEL_ACCENT, alpha=24 + int(active_t * 30), time_s=time_s)

    font_size = max(16, min(UI_STYLE.typography.button, int(draw_rect.height * 0.42)))
    tw = pgui.measure_text(text, font_size)
    tx = int(draw_rect.x + (draw_rect.width - tw) / 2)
    ty = int(draw_rect.y + (draw_rect.height - font_size) / 2)
    text_color = _blend_color(with_alpha(colors.WHITE, 228), with_alpha(LIVE_CYAN, 248), focus_t)
    if focused or hovered:
        _draw_soft_rect_glow(
            pyray.Rectangle(tx - 6, ty - 4, tw + 12, font_size + 8),
            LIVE_CYAN if focused else outer_glow,
            spread=10 if focused else 7,
            alpha=12 if focused else 8,
            layers=2,
        )
    if hover_t > 0.1 and focus_t < 0.4:
        pgui.draw_text(text, tx + 1, ty, font_size, with_alpha(LIVE_PINK, int(52 * hover_t)))
    pgui.draw_text(text, tx, ty, font_size, text_color)


def draw_panel(rect, title: str | None = None, *, time_s: float | None = None) -> None:
    time_s = _ui_time(time_s)
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.2 + rect.x * 0.01)
    flicker = _rare_flicker(time_s, rect.width + rect.height, threshold=0.992)
    pgui.draw_rect(
        pyray.Rectangle(rect.x - 16, rect.y - 16, rect.width + 32, rect.height + 32),
        with_alpha(PANEL_ACCENT, 6 + int(pulse * 6)),
    )
    pgui.draw_rect(rect, with_alpha((3, 7, 18, 255), 238))
    pgui.draw_rect(rect, with_alpha(GLASS_EDGE, 104), 1)
    _draw_notch_marks(rect, LIVE_PINK, alpha=54 + int(flicker * 22))
    _draw_corner_brackets(rect, LIVE_CYAN, alpha=86 + int(pulse * 18), length=28)

    inner = pyray.Rectangle(rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20)
    pgui.draw_rect(inner, with_alpha((4, 9, 22, 255), 218))
    _draw_scanline_overlay(inner, alpha=3, spacing=8, time_s=time_s)
    _draw_grid_overlay(inner, alpha=3, cell=34)
    pgui.draw_rect(
        pyray.Rectangle(inner.x, inner.y, inner.width, max(0, inner.height * 0.18)),
        with_alpha(LIVE_CYAN, 7),
    )
    pgui.draw_rect(
        pyray.Rectangle(inner.x + 18, inner.y + inner.height - 18, max(0, inner.width - 36), 2),
        with_alpha(LIVE_CYAN, 34 + int(pulse * 10)),
    )
    _draw_signal_ticks(inner, LIVE_CYAN, alpha=32, time_s=time_s)
    corner_len = 26
    pgui.draw_rect(pyray.Rectangle(rect.x + rect.width - corner_len - 8, rect.y + 8, corner_len, 2), with_alpha(LIVE_CYAN, 72 + int(pulse * 20)))
    pgui.draw_rect(pyray.Rectangle(rect.x + rect.width - 10, rect.y + 8, 2, corner_len), with_alpha(LIVE_CYAN, 72 + int(pulse * 20)))
    pgui.draw_rect(pyray.Rectangle(rect.x + 8, rect.y + rect.height - 10, corner_len, 2), with_alpha(LIVE_PINK, 72 + int(flicker * 28)))
    pgui.draw_rect(pyray.Rectangle(rect.x + 8, rect.y + rect.height - corner_len - 8, 2, corner_len), with_alpha(LIVE_PINK, 72 + int(flicker * 28)))

    if title:
        title_y = int(rect.y + 12)
        draw_text_centered(title, int(rect.x + rect.width / 2), title_y, 22, LIVE_CYAN)


def draw_scene_header(rect, eyebrow: str, title: str, subtitle: str, *, title_size: int = 42) -> None:
    center_x = int(rect.x + rect.width / 2)
    draw_text_centered(eyebrow, center_x, int(rect.y + 22), 18, PANEL_ACCENT)
    draw_shadowed_text_centered(title, center_x, int(rect.y + 50), title_size, colors.WHITE)
    draw_text_centered(subtitle, center_x, int(rect.y + 96), 16, TEXT_DIM)


def draw_scene_footer(rect, text: str = "ENTER OR CLICK") -> None:
    if PRESENTATION_MODE:
        return
    center_x = int(rect.x + rect.width / 2)
    draw_text_centered(text, center_x, int(rect.y + rect.height - 28), 14, TEXT_DIM)


def draw_presentation_bars(width: int, height: int, *, alpha: int = 190) -> None:
    if not PRESENTATION_MODE:
        return
    bar_h = max(26, int(height * 0.05))
    pgui.draw_rect(pyray.Rectangle(0, 0, width, bar_h), with_alpha(colors.BLACK, alpha))
    pgui.draw_rect(pyray.Rectangle(0, height - bar_h, width, bar_h), with_alpha(colors.BLACK, alpha))
    pgui.draw_rect(pyray.Rectangle(0, bar_h - 2, width, 2), with_alpha(LIVE_CYAN, 28))
    pgui.draw_rect(pyray.Rectangle(0, height - bar_h, width, 2), with_alpha(LIVE_PINK, 24))


def draw_glass_card(rect, accent_color=LIVE_CYAN, *, glow_alpha: int = 18, fill_alpha: int = 160, time_s: float | None = None) -> None:
    time_s = _ui_time(time_s)
    pulse = 0.5 + 0.5 * math.sin(time_s * 3.0 + rect.x * 0.012)
    flicker = _rare_flicker(time_s, rect.x * 0.5 + rect.y * 0.7, threshold=0.991)
    _draw_soft_rect_glow(
        rect,
        accent_color,
        spread=28,
        alpha=max(10, int(glow_alpha * 1.2) + int(pulse * 8) + int(flicker * 10)),
        layers=4,
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x - 6, rect.y - 6, rect.width + 12, rect.height + 12),
        with_alpha(accent_color, int(glow_alpha * 0.9) + int(pulse * 8)),
    )
    pgui.draw_rect(rect, with_alpha(PANEL_INNER, min(242, fill_alpha + 20)))
    _draw_scanline_overlay(rect, alpha=3, spacing=8, time_s=time_s)
    _draw_grid_overlay(rect, alpha=2, cell=34)
    pgui.draw_rect(rect, with_alpha(GLASS_EDGE, 96), 1)
    _draw_notch_marks(rect, accent_color, alpha=46 + int(flicker * 22))
    _draw_corner_brackets(rect, accent_color, alpha=72 + int(pulse * 18), length=22)
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 3, rect.y + 3, max(0, rect.width - 6), max(0, rect.height * 0.26)),
        with_alpha(colors.WHITE, 8),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 12, rect.y + 12, 3, max(0, rect.height - 24)),
        with_alpha(accent_color, 110),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 34, rect.y + 12, 22, 2),
        with_alpha(accent_color, 82 + int(flicker * 24)),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 12, rect.y + 12, 2, 18),
        with_alpha(accent_color, 82 + int(flicker * 24)),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 10, rect.y + rect.height - 12, rect.width - 20, 2),
        with_alpha(accent_color, 32),
    )
    _draw_signal_ticks(rect, accent_color, alpha=28, time_s=time_s)


def draw_mission_frame(rect, accent_color=LIVE_PINK, *, support_color=LIVE_CYAN, glow_alpha: int = 16, fill_alpha: int = 150) -> None:
    _draw_soft_rect_glow(rect, accent_color, spread=16, alpha=glow_alpha, layers=3)
    pgui.draw_rect(rect, with_alpha(PANEL_INNER, fill_alpha))
    pgui.draw_rect(rect, with_alpha(accent_color, 96), 1)

    top_bar = pyray.Rectangle(rect.x + 16, rect.y + 14, max(0, rect.width - 32), 2)
    pgui.draw_rect(top_bar, with_alpha(accent_color, 118))
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 28, rect.y + 20, max(0, rect.width * 0.28), 2),
        with_alpha(support_color, 92),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 68, rect.y + 20, 40, 2),
        with_alpha(accent_color, 82),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 14, rect.y + 16, 2, max(0, rect.height - 32)),
        with_alpha(accent_color, 90),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 16, rect.y + 16, 2, 18),
        with_alpha(support_color, 80),
    )

    corner = 14
    pgui.draw_rect(
        pyray.Rectangle(rect.x - 2, rect.y + 10, 2, corner),
        with_alpha(accent_color, 70),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 10, rect.y - 2, corner, 2),
        with_alpha(accent_color, 70),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - corner - 10, rect.y - 2, corner, 2),
        with_alpha(support_color, 64),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width, rect.y + 10, 2, corner),
        with_alpha(support_color, 64),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 8, rect.y + rect.height, corner, 2),
        with_alpha(accent_color, 58),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - corner - 8, rect.y + rect.height, corner, 2),
        with_alpha(accent_color, 40),
    )


def draw_dashboard_rail(center_x: int, y: int, width: int, *, label: str | None = None, accent_color=LIVE_PINK, support_color=LIVE_CYAN, time_s: float = 0.0) -> None:
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.2)
    rail = pyray.Rectangle(center_x - width // 2, y, width, 18)
    _draw_soft_rect_glow(rail, accent_color, spread=14, alpha=int(10 + pulse * 6), layers=3)
    pgui.draw_rect(rail, with_alpha((22, 10, 34, 255), 144))
    pgui.draw_rect(rail, with_alpha(accent_color, 88), 1)

    left_wing = pyray.Rectangle(rail.x - 22, rail.y + 4, 18, 10)
    right_wing = pyray.Rectangle(rail.x + rail.width + 4, rail.y + 4, 18, 10)
    pgui.draw_rect(left_wing, with_alpha(accent_color, 74))
    pgui.draw_rect(right_wing, with_alpha(support_color, 68))
    pgui.draw_rect(pyray.Rectangle(rail.x + 14, rail.y + 7, max(0, rail.width * 0.22), 2), with_alpha(support_color, 118))
    pgui.draw_rect(
        pyray.Rectangle(rail.x + rail.width - 14 - max(0, rail.width * 0.22), rail.y + 7, max(0, rail.width * 0.22), 2),
        with_alpha(accent_color, 92),
    )
    scan_x = int(rail.x + 18 + (math.sin(time_s * 1.4) * 0.5 + 0.5) * max(1, rail.width - 52))
    pgui.draw_rect(
        pyray.Rectangle(scan_x, rail.y + 4, 18, 10),
        with_alpha(colors.WHITE, int(10 + pulse * 12)),
    )

    if label:
        draw_text_centered(label, center_x, y - 1, 14, with_alpha(colors.WHITE, 220))


def _draw_soft_rect_glow(rect, color, *, spread: int = 16, alpha: int = 18, layers: int = 3) -> None:
    for index in range(layers, 0, -1):
        pad = spread * 1.35 * index / layers
        layer_alpha = max(1, int(alpha * 1.45 * index / (layers + 1)))
        pgui.draw_rect(
            pyray.Rectangle(rect.x - pad, rect.y - pad, rect.width + pad * 2, rect.height + pad * 2),
            with_alpha(color, layer_alpha),
        )


def _draw_soft_circle_glow(x: int, y: int, radius: float, color, *, alpha: int = 20, layers: int = 3) -> None:
    for index in range(layers, 0, -1):
        layer_radius = radius + index * 11
        layer_alpha = max(1, int(alpha * 1.4 * index / (layers + 1)))
        pyray.draw_circle(x, y, layer_radius, with_alpha(color, layer_alpha))


def _draw_deep_background_base(width: int, height: int, time_s: float, *, top_color, bottom_color) -> None:
    pyray.draw_rectangle_rec(pyray.Rectangle(0, 0, width, height), with_alpha(bottom_color, 255))

    top_band_h = max(1, int(height * 0.62))
    mid_band_h = max(1, int(height * 0.22))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, width, top_band_h),
        with_alpha(top_color, 232),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, width, height),
        with_alpha((2, 3, 8, 255), 36),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.24), width, mid_band_h),
        with_alpha((6, 8, 18, 255), 92),
    )

    fog_pulse = 0.5 + 0.5 * math.sin(time_s * 0.7)
    pyray.draw_circle(int(width * 0.22), int(height * 0.18), int(height * 0.34), with_alpha(LIVE_CYAN, 4))
    pyray.draw_circle(int(width * 0.66), int(height * 0.22), int(height * 0.30), with_alpha(LIVE_PINK, 3))
    pyray.draw_circle(int(width * 0.48), int(height * 0.30), int(height * 0.42), with_alpha(colors.WHITE, 2))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.10), width, int(height * 0.58)),
        with_alpha((10, 12, 20, 255), int(12 + fog_pulse * 7)),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.28), width, int(height * 0.32)),
        with_alpha((18, 20, 28, 255), int(10 + fog_pulse * 8)),
    )

    # Very light deterministic noise to stop flat color banding and push the background backward.
    x_step = max(20, width // 36)
    y_step = max(18, height // 28)
    for y in range(0, height, y_step):
        for x in range(0, width, x_step):
            noise = ((x * 17 + y * 31) % 11)
            if noise < 8:
                continue
            alpha = 3 if noise < 10 else 5
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, y, max(2, x_step // 4), max(2, y_step // 5)),
                with_alpha(colors.WHITE, alpha),
            )

    # Top vignette to make the upper half fall deeper into black.
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, width, int(height * 0.22)),
        with_alpha(colors.BLACK, 62),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, int(width * 0.08), height),
        with_alpha(colors.BLACK, 34),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.92), 0, int(width * 0.08), height),
        with_alpha(colors.BLACK, 34),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.72), width, int(height * 0.28)),
        with_alpha(colors.BLACK, 28),
    )


def _draw_background_motion_layer(width: int, height: int, time_s: float) -> None:
    # Slow light streaks.
    for index in range(6):
        x = int(width * (0.08 + index * 0.14) + math.sin(time_s * (0.25 + index * 0.03) + index) * 16)
        streak_h = int(height * (0.34 + (index % 3) * 0.08))
        y = int(height * 0.10 + math.cos(time_s * (0.18 + index * 0.02) + index) * 12)
        color = LIVE_CYAN if index % 2 == 0 else LIVE_PINK
        pyray.draw_rectangle_rec(
            pyray.Rectangle(x, y, 2, streak_h),
            with_alpha(color, 8),
        )

    for index in range(4):
        y = int(height * (0.18 + index * 0.16) + math.sin(time_s * (0.22 + index * 0.04) + index * 1.7) * 10)
        x = int(width * 0.06)
        w = int(width * (0.44 - index * 0.06))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(x, y, w, 1),
            with_alpha(colors.WHITE, 5),
        )

    # Sparse digital-rain style drifting particles.
    for index in range(16):
        drift_x = int((index * 79 + time_s * (14 + index % 5) * 6) % (width + 80)) - 40
        drift_y = int((index * 47 + time_s * (18 + index % 7) * 7) % (height + 100)) - 50
        cell_h = 4 + index % 3
        color = LIVE_CYAN if index % 3 else LIVE_PINK
        pyray.draw_rectangle_rec(
            pyray.Rectangle(drift_x, drift_y, 1, cell_h),
            with_alpha(color, 16),
        )


def _draw_dot_matrix_text(text: str, x: int, y: int, cell: int, color, glow_color=None) -> int:
    cursor_x = x
    glow = glow_color or color
    for char in text.upper():
        glyph = DOT_MATRIX_GLYPHS.get(char, DOT_MATRIX_GLYPHS[" "])
        for row_index, row in enumerate(glyph):
            for col_index, value in enumerate(row):
                if value != "1":
                    continue
                px = cursor_x + col_index * cell
                py = y + row_index * cell
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(px - 1, py - 1, cell + 2, cell + 2),
                    with_alpha(glow, 40),
                )
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(px, py, cell, cell),
                    color,
                )
        cursor_x += cell * 6
    return cursor_x - x


def draw_pacman_title_sign(center_x: int, y: int, scale: float = 1.0, time_s: float = 0.0) -> None:
    theme_name = _current_theme_name()
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.6)
    frame_w = int(430 * scale)
    frame_h = int(132 * scale)
    frame_x = int(center_x - frame_w / 2)
    frame = pyray.Rectangle(frame_x, y, frame_w, frame_h)
    inner = pyray.Rectangle(frame.x + 10, frame.y + 10, frame.width - 20, frame.height - 20)
    light_bar = pyray.Rectangle(inner.x + 12, inner.y + 12, inner.width - 24, int(18 * scale))
    side_box = pyray.Rectangle(frame.x + frame.width - int(58 * scale), frame.y + int(14 * scale), int(34 * scale), int(30 * scale))

    glow_color = LIVE_PINK
    frame_fill = (36, 18, 60, 255)
    inner_fill = (18, 18, 46, 255)
    side_color = LIVE_CYAN
    module_label = "07"

    if theme_name == "Amber Rain":
        glow_color = LIVE_GOLD
        frame_fill = (54, 28, 12, 255)
        inner_fill = (28, 16, 10, 255)
        side_color = LIVE_GOLD
        module_label = "AR"
    elif theme_name == "Ice Circuit":
        glow_color = LIVE_CYAN
        frame_fill = (18, 34, 62, 255)
        inner_fill = (12, 20, 40, 255)
        side_color = colors.WHITE
        module_label = "IC"
    elif theme_name == "Velvet Alley":
        glow_color = LIVE_PINK
        frame_fill = (48, 12, 40, 255)
        inner_fill = (22, 10, 28, 255)
        side_color = LIVE_PINK
        module_label = "VA"

    _draw_soft_rect_glow(
        frame,
        glow_color,
        spread=26,
        alpha=int(24 + pulse * 16),
        layers=4,
    )
    pgui.draw_rect(frame, with_alpha(frame_fill, 222))
    pgui.draw_rect(frame, with_alpha(glow_color, 170), 2)
    pgui.draw_rect(inner, with_alpha(inner_fill, 228))
    pgui.draw_rect(light_bar, with_alpha(colors.WHITE, 12))
    pgui.draw_rect(
        pyray.Rectangle(frame.x - int(14 * scale), frame.y + int(18 * scale), int(12 * scale), int(82 * scale)),
        with_alpha(side_color, 64),
    )
    pgui.draw_rect(side_box, with_alpha(side_color, 12))
    pgui.draw_rect(side_box, with_alpha(side_color, 90), 1)
    draw_text_centered(module_label, int(side_box.x + side_box.width / 2), int(side_box.y + 5), max(9, int(12 * scale)), with_alpha(colors.WHITE, 190))

    if theme_name == "Amber Rain":
        awning = pyray.Rectangle(frame.x + 18, frame.y + frame.height - int(20 * scale), frame.width - 88, int(12 * scale))
        pgui.draw_rect(awning, with_alpha(LIVE_GOLD, 84))
    elif theme_name == "Ice Circuit":
        for index in range(7):
            vx = frame.x + 26 + index * int(46 * scale)
            pgui.draw_rect(
                pyray.Rectangle(vx, frame.y + 20, 2, frame.height - 38),
                with_alpha(colors.WHITE, 26),
            )
    elif theme_name == "Velvet Alley":
        pgui.draw_circle(int(frame.x + 34), int(frame.y + 34), int(16 * scale), with_alpha(LIVE_PINK, 40))
        pgui.draw_circle(int(frame.x + frame.width - 106), int(frame.y + 102), int(14 * scale), with_alpha(LIVE_GOLD, 30))

    logo_cell = max(5, int(8 * scale))
    logo_text = "PAC-MAN"
    logo_width = len(logo_text) * logo_cell * 6 - logo_cell
    logo_x = int(center_x - logo_width / 2 - 8 * scale)
    logo_y = int(frame.y + 44 * scale)
    _draw_soft_rect_glow(
        pyray.Rectangle(logo_x - 10, logo_y - 8, logo_width + 20, logo_cell * 7 + 10),
        LIVE_PINK,
        spread=14,
        alpha=12,
        layers=3,
    )
    _draw_dot_matrix_text(logo_text, logo_x, logo_y, logo_cell, colors.WHITE, LIVE_PINK)

    pac_radius = int(13 * scale)
    pac_x = int(center_x + 10 * scale)
    pac_y = int(frame.y + 74 * scale)
    _draw_soft_circle_glow(pac_x, pac_y, pac_radius + 6, LIVE_CYAN, alpha=14, layers=3)
    pgui.draw_circle(pac_x, pac_y, pac_radius, with_alpha((255, 220, 80, 255), 220))
    pgui.draw_rect(
        pyray.Rectangle(pac_x + 2, pac_y - 8, 12, 16),
        with_alpha((18, 18, 46, 255), 255),
    )
    for dot_index in range(3):
        dot_x = pac_x + 28 + dot_index * 12
        _draw_soft_circle_glow(dot_x, pac_y, 2, LIVE_CYAN, alpha=10, layers=2)
        pgui.draw_circle(dot_x, pac_y, 3 + dot_index % 2, with_alpha(LIVE_CYAN, 180 - dot_index * 28))


def draw_street_terminal(rect, title: str, value: str, accent_color, *, subline: str | None = None) -> None:
    draw_glass_card(rect, accent_color=accent_color, glow_alpha=16, fill_alpha=170)
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 10, rect.y + 10, int(rect.width * 0.42), int(rect.height - 20)),
        with_alpha((8, 12, 28, 255), 120),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 14, rect.y + 16, 4, int(rect.height - 32)),
        with_alpha(accent_color, 170),
    )
    theme_name = _current_theme_name()
    if theme_name == "Amber Rain":
        pgui.draw_rect(
            pyray.Rectangle(rect.x + rect.width - 62, rect.y + 14, 42, 10),
            with_alpha(LIVE_GOLD, 60),
        )
    elif theme_name == "Ice Circuit":
        for index in range(4):
            pgui.draw_rect(
                pyray.Rectangle(rect.x + rect.width - 22 - index * 8, rect.y + 14, 2, rect.height - 28),
                with_alpha(colors.WHITE, 22),
            )
    elif theme_name == "Velvet Alley":
        pgui.draw_circle(int(rect.x + rect.width - 30), int(rect.y + 26), 10, with_alpha(LIVE_PINK, 32))
    draw_text_centered(title, int(rect.x + rect.width / 2), int(rect.y + 12), 14, TEXT_DIM)
    draw_text_centered(value, int(rect.x + rect.width / 2), int(rect.y + 36), 20, colors.WHITE)
    if subline:
        draw_text_centered(subline, int(rect.x + rect.width / 2), int(rect.y + 58), 12, accent_color)


def draw_arcade_background(width: int, height: int, time_s: float = 0.0) -> None:
    _draw_deep_background_base(width, height, time_s, top_color=(10, 8, 22, 255), bottom_color=(2, 3, 10, 255))
    _draw_background_motion_layer(width, height, time_s)
    horizon = int(height * 0.56)

    # Neon haze layers
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, width, horizon),
        with_alpha(LIVE_PINK, 18),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.12), width, int(height * 0.46)),
        with_alpha(LIVE_CYAN, 14),
    )

    # Distant skyline
    building_x = -20
    index = 0
    while building_x < width + 40:
        b_width = 46 + (index % 5) * 18
        b_height = 140 + (index % 7) * 28
        top = horizon - b_height
        color = with_alpha((26, 18, 52, 255), 255)
        pyray.draw_rectangle_rec(pyray.Rectangle(building_x, top, b_width, b_height), color)
        neon = LIVE_CYAN if index % 2 == 0 else LIVE_PINK
        _draw_soft_rect_glow(
            pyray.Rectangle(building_x + b_width - 6, top + 10, 3, max(16, b_height - 20)),
            neon,
            spread=8,
            alpha=12,
            layers=3,
        )
        pyray.draw_rectangle_rec(
            pyray.Rectangle(building_x + b_width - 6, top + 10, 3, max(16, b_height - 20)),
            with_alpha(neon, 100),
        )
        for wy in range(top + 16, top + b_height - 12, 18):
            for wx in range(building_x + 8, building_x + b_width - 12, 14):
                if (wx + wy + index) % 3 == 0:
                    continue
                window_color = LIVE_CYAN if (wx + wy) % 2 == 0 else LIVE_PINK
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(wx, wy, 4, 6),
                    with_alpha(window_color, 90),
                )
        building_x += b_width - 8
        index += 1

    # Large neon sign blocks
    sign_y = int(height * 0.18)
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.0)
    sign_alpha = int(90 + pulse * 70)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.12), sign_y, 170, 44),
        with_alpha((34, 20, 72, 255), 210),
    )
    sign_rect_left = pyray.Rectangle(int(width * 0.12), sign_y, 170, 44)
    _draw_soft_rect_glow(sign_rect_left, LIVE_PINK, spread=12, alpha=18, layers=3)
    pyray.draw_rectangle_lines_ex(sign_rect_left, 2, with_alpha(LIVE_PINK, sign_alpha))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.68), sign_y + 26, 120, 38),
        with_alpha((16, 14, 38, 255), 210),
    )
    sign_rect_right = pyray.Rectangle(int(width * 0.68), sign_y + 26, 120, 38)
    _draw_soft_rect_glow(sign_rect_right, LIVE_CYAN, spread=12, alpha=18, layers=3)
    pyray.draw_rectangle_lines_ex(sign_rect_right, 2, with_alpha(LIVE_CYAN, sign_alpha))

    # Rain streaks
    for index in range(48):
        x = (index * 37 + int(time_s * 120)) % (width + 80) - 40
        y = (index * 29 + int(time_s * 210)) % (height + 120) - 60
        streak_color = with_alpha(LIVE_CYAN if index % 2 == 0 else LIVE_PINK, 42)
        pyray.draw_rectangle_rec(pyray.Rectangle(x, y, 2, 16), streak_color)

    # Side light rails
    left_rail = pyray.Rectangle(22, 22, 8, max(0, height - 44))
    right_rail = pyray.Rectangle(width - 30, 22, 8, max(0, height - 44))
    pyray.draw_rectangle_rec(left_rail, with_alpha(LIVE_CYAN, 90))
    pyray.draw_rectangle_rec(right_rail, with_alpha(LIVE_PINK, 90))

    for y in range(34, height - 34, 28):
        pyray.draw_rectangle_rec(pyray.Rectangle(25, y, 4, 10), LIVE_CYAN)
        pyray.draw_rectangle_rec(pyray.Rectangle(width - 29, y, 4, 10), LIVE_PINK)

    _draw_theme_background_overlays(width, height, time_s, live_mode=False)


def draw_cinematic_menu_background(width: int, height: int, time_s: float = 0.0) -> None:
    _draw_deep_background_base(width, height, time_s, top_color=(10, 8, 22, 255), bottom_color=(4, 6, 16, 255))
    _draw_background_motion_layer(width, height, time_s)
    _draw_skyline_layers(width, height, time_s, live_mode=False)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.40), width, int(height * 0.60)),
        with_alpha(STREET_BLUE, 196),
    )

    flicker = 0.5 + 0.5 * math.sin(time_s * 7.4)

    pyray.draw_circle(int(width * 0.28), int(height * 0.26), 220, with_alpha(LIVE_CYAN, 7))
    pyray.draw_circle(int(width * 0.36), int(height * 0.22), 160, with_alpha(LIVE_PINK, 5))
    pyray.draw_circle(int(width * 0.76), int(height * 0.24), 140, with_alpha(LIVE_CYAN, 4))
    pyray.draw_circle(int(width * 0.82), int(height * 0.18), 190, with_alpha(LIVE_PINK, 4))

    left_mass = pyray.Rectangle(int(width * 0.10), int(height * 0.20), int(width * 0.34), int(height * 0.18))
    pyray.draw_rectangle_rec(left_mass, with_alpha((18, 18, 34, 255), 36))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(left_mass.x + 30, left_mass.y + 30, left_mass.width - 60, 20),
        with_alpha(colors.WHITE, 3),
    )

    street_top = int(height * 0.69)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, street_top, width, height - street_top),
        with_alpha((8, 14, 30, 255), 235),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, street_top - 14, int(width * 0.80), 14),
        with_alpha(LIVE_CYAN, 18),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, street_top - 4, int(width * 0.80), 2),
        with_alpha(colors.WHITE, 24),
    )
    for index in range(10):
        ry = street_top + 20 + index * 20
        alpha = max(8, 34 - index * 3)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(int(width * 0.05), ry, int(width * 0.72), 2),
            with_alpha(colors.WHITE, alpha),
    )
    for index in range(18):
        rx = int(width * 0.09) + index * 46
        reflection_height = 34 + (index % 5) * 22
        reflection_color = LIVE_PINK if index % 2 else LIVE_CYAN
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rx, street_top + 8, 4, reflection_height),
            with_alpha(reflection_color, 26),
        )
    for index in range(6):
        stripe_x = int(width * 0.56) + index * 54
        stripe_y = street_top + 56 + index * 14
        stripe_w = 72 - index * 6
        pyray.draw_rectangle_rec(
            pyray.Rectangle(stripe_x, stripe_y, stripe_w, 10),
            with_alpha(colors.WHITE, 34),
        )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, street_top - 36, width, 28),
        with_alpha(LIVE_CYAN, 6),
    )

    # Distant neon venue signs and fog pockets to push the rainy street mood.
    venue_specs = (
        (int(width * 0.58), int(height * 0.26), 118, 32, LIVE_PINK, "NOVA"),
        (int(width * 0.71), int(height * 0.31), 136, 36, LIVE_CYAN, "DISTRICT"),
    )
    for sign_x, sign_y, sign_w, sign_h, sign_color, label in venue_specs:
        sign_rect = pyray.Rectangle(sign_x, sign_y, sign_w, sign_h)
        _draw_soft_rect_glow(sign_rect, sign_color, spread=18, alpha=int(16 + flicker * 8), layers=3)
        pyray.draw_rectangle_rec(sign_rect, with_alpha((18, 12, 30, 255), 170))
        pyray.draw_rectangle_lines_ex(sign_rect, 1, with_alpha(sign_color, 108 + int(flicker * 18)))
        draw_text_centered(label, int(sign_rect.x + sign_rect.width / 2), int(sign_rect.y + 7), 18, with_alpha(colors.WHITE, 224))

    fog_banks = (
        (int(width * 0.68), int(height * 0.34), 120, LIVE_PINK),
        (int(width * 0.74), int(height * 0.52), 150, LIVE_CYAN),
        (int(width * 0.88), int(height * 0.44), 96, colors.WHITE),
    )
    for fog_x, fog_y, fog_r, fog_color in fog_banks:
        _draw_soft_circle_glow(fog_x, fog_y, fog_r, fog_color, alpha=5, layers=4)

    road_end = int(width * 0.83)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(road_end, int(height * 0.40), width - road_end, int(height * 0.60)),
        with_alpha((10, 12, 24, 255), 180),
    )
    for index in range(8):
        rail_y = int(height * 0.47) + index * 22
        pyray.draw_rectangle_rec(
            pyray.Rectangle(road_end + 18, rail_y, width - road_end - 30, 2),
            with_alpha(LIVE_CYAN, 20 + index * 3),
        )

    for index in range(54):
        x = (index * 41 + int(time_s * 140)) % (width + 120) - 60
        y = (index * 33 + int(time_s * 260)) % (height + 140) - 70
        streak_height = 14 + (index % 4) * 6
        streak_color = LIVE_CYAN if index % 3 else LIVE_PINK
        pyray.draw_rectangle_rec(
            pyray.Rectangle(x, y, 2, streak_height),
            with_alpha(streak_color, 34),
        )

    # Tiny drifting light motes keep the menu scene subtly alive.
    for index in range(12):
        drift_x = int(width * (0.10 + (index * 0.07) % 0.78) + math.sin(time_s * (0.6 + index * 0.08) + index) * 12)
        drift_y = int(height * (0.16 + (index * 0.05) % 0.48) + math.cos(time_s * (0.8 + index * 0.06) + index * 0.7) * 10)
        mote_color = LIVE_PINK if index % 2 else LIVE_CYAN
        _draw_soft_circle_glow(drift_x, drift_y, 2 + index % 2, mote_color, alpha=6, layers=2)
        pyray.draw_circle(drift_x, drift_y, 2, with_alpha(mote_color, 72))

    pole_specs = (
        (int(width * 0.55), int(height * 0.18), int(height * 0.72)),
        (int(width * 0.63), int(height * 0.14), int(height * 0.68)),
        (int(width * 0.73), int(height * 0.20), int(height * 0.74)),
    )
    for pole_x, pole_y, pole_h in pole_specs:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(pole_x, pole_y, 5, pole_h),
            with_alpha((18, 18, 24, 255), 255),
        )
        pyray.draw_circle(pole_x + 2, pole_y + 8, 8, with_alpha(LIVE_GOLD, 110))

    cable_sets = (
        (0.56, 0.10, 0.98, 0.12),
        (0.52, 0.14, 0.97, 0.18),
        (0.58, 0.16, 1.00, 0.22),
    )
    for x1r, y1r, x2r, y2r in cable_sets:
        x1 = int(width * x1r)
        y1 = int(height * y1r)
        x2 = int(width * x2r)
        y2 = int(height * y2r)
        span = max(1, x2 - x1)
        for step in range(0, span, 8):
            x = x1 + step
            ratio = step / span
            y = int(y1 + (y2 - y1) * ratio + math.sin(ratio * math.pi) * 10)
            pyray.draw_rectangle_rec(pyray.Rectangle(x, y, 8, 2), with_alpha((14, 14, 18, 255), 255))

    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.84), int(height * 0.52), int(width * 0.16), int(height * 0.48)),
        with_alpha((10, 10, 20, 255), 96),
    )

    pyray.draw_rectangle_rec(
        pyray.Rectangle(width - 24, 0, 6, height),
        with_alpha(LIVE_PINK, 85),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(width - 36, 0, 2, height),
        with_alpha(colors.WHITE, 18),
    )

    _draw_theme_background_overlays(width, height, time_s, live_mode=False)


def draw_live_game_background(width: int, height: int, time_s: float) -> None:
    _draw_deep_background_base(width, height, time_s, top_color=(8, 8, 18, 255), bottom_color=(2, 3, 10, 255))
    _draw_background_motion_layer(width, height, time_s)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.56), width, int(height * 0.44)),
        with_alpha(STREET_BLUE, 188),
    )

    haze_specs = (
        (int(width * 0.16), int(height * 0.22), 170, LIVE_CYAN, 7),
        (int(width * 0.32), int(height * 0.18), 136, LIVE_PINK, 6),
        (int(width * 0.78), int(height * 0.26), 150, LIVE_CYAN, 5),
        (int(width * 0.64), int(height * 0.34), 110, LIVE_PINK, 4),
    )
    for cx, cy, radius, color, alpha in haze_specs:
        pyray.draw_circle(cx, cy, radius, with_alpha(color, alpha))
    _draw_skyline_layers(width, height, time_s, live_mode=True)

    for index in range(10):
        y = int((index * 54 + time_s * 40) % (height + 40)) - 40
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, y, width, 2),
            with_alpha(colors.WHITE, 8),
        )

    street_top = int(height * 0.68)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, street_top, width, height - street_top),
        with_alpha((6, 10, 22, 255), 236),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, street_top - 12, width, 2),
        with_alpha(LIVE_CYAN, 22),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, street_top - 2, width, 1),
        with_alpha(colors.WHITE, 18),
    )
    for index in range(11):
        ry = street_top + 22 + index * 22
        pyray.draw_rectangle_rec(
            pyray.Rectangle(int(width * 0.04), ry, int(width * 0.74), 2),
            with_alpha(colors.WHITE, max(6, 20 - index)),
        )
    for index in range(18):
        rx = int(width * 0.07) + index * max(38, width // 28)
        glow_h = 30 + (index % 5) * 20
        glow_w = 2 if index % 3 else 3
        glow_color = LIVE_CYAN if index % 2 == 0 else LIVE_PINK
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rx, street_top + 8, glow_w, glow_h),
            with_alpha(glow_color, 20 if index % 3 else 28),
        )
    for index in range(5):
        sx = int(width * 0.58) + index * 44
        sy = street_top + 58 + index * 15
        pyray.draw_rectangle_rec(
            pyray.Rectangle(sx, sy, 62 - index * 5, 8),
            with_alpha(colors.WHITE, 22),
        )
    for index in range(12):
        rx = int(width * 0.06) + index * max(48, width // 22)
        r_height = 44 + (index % 4) * 18
        r_color = LIVE_PINK if index % 3 == 0 else LIVE_CYAN
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rx, street_top + 6, 3, r_height),
            with_alpha(r_color, 10),
        )

    _draw_theme_background_overlays(width, height, time_s, live_mode=True)


def draw_live_board_backdrop(rect, time_s: float) -> None:
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.4)
    flicker = 0.5 + 0.5 * math.sin(time_s * 9.5 + rect.x * 0.01)
    glow_alpha = int(12 + pulse * 14)
    outer = pyray.Rectangle(rect.x - 22, rect.y - 20, rect.width + 44, rect.height + 40)
    inner = pyray.Rectangle(rect.x - 8, rect.y - 8, rect.width + 16, rect.height + 16)
    stage = pyray.Rectangle(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4)
    pedestal = pyray.Rectangle(rect.x - 12, rect.y + rect.height + 10, rect.width + 24, 38)
    shadow = pyray.Rectangle(rect.x - 26, rect.y - 18, rect.width + 52, rect.height + 84)

    pyray.draw_rectangle_rec(shadow, with_alpha(colors.BLACK, 62))
    pyray.draw_rectangle_rec(outer, with_alpha(LIVE_CYAN, int(8 + flicker * 4)))
    pyray.draw_rectangle_rec(inner, with_alpha(LIVE_PINK, int(7 + flicker * 4)))
    pyray.draw_rectangle_rec(stage, with_alpha((4, 6, 18, 255), 255))
    pyray.draw_rectangle_rec(pedestal, with_alpha((8, 10, 20, 255), 210))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(pedestal.x + 18, pedestal.y + 8, pedestal.width - 36, 2),
        with_alpha(LIVE_PINK, 18 + glow_alpha // 2),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 10, rect.y + rect.height + 8, rect.width + 20, 26),
        with_alpha(LIVE_CYAN, 8),
    )
    pyray.draw_rectangle_lines_ex(stage, 1, with_alpha(GLASS_EDGE, 44))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 10, rect.y - 4, rect.width - 20, 2),
        with_alpha(LIVE_CYAN, 56 + glow_alpha + int(flicker * 12)),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 16, rect.y + rect.height + 4, rect.width - 32, 2),
        with_alpha(LIVE_PINK, 38 + glow_alpha + int(flicker * 10)),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 28, rect.y + rect.height + 16, rect.width - 56, 10),
        with_alpha(colors.WHITE, 4),
    )
    # Very subtle under-grid so the playfield has structure without looking technical.
    grid_spacing_x = max(28, int(rect.width / 12))
    grid_spacing_y = max(28, int(rect.height / 10))
    for gx in range(int(rect.x + 24), int(rect.x + rect.width - 24), grid_spacing_x):
        pyray.draw_rectangle_rec(
            pyray.Rectangle(gx, rect.y + 18, 1, rect.height - 36),
            with_alpha(LIVE_CYAN, 5),
        )
    for gy in range(int(rect.y + 18), int(rect.y + rect.height - 18), grid_spacing_y):
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x + 18, gy, rect.width - 36, 1),
            with_alpha(colors.WHITE, 4),
        )

    # Soft route-light pulses moving through the board stage.
    for index in range(3):
        ratio = (math.sin(time_s * (0.8 + index * 0.17) + index * 1.6) * 0.5 + 0.5)
        lane_y = int(rect.y + rect.height * (0.22 + index * 0.24))
        lane_x = int(rect.x + 20 + ratio * max(1, rect.width - 110))
        lane_w = 84
        pyray.draw_rectangle_rec(
            pyray.Rectangle(lane_x, lane_y, lane_w, 3),
            with_alpha(LIVE_CYAN if index % 2 == 0 else LIVE_PINK, 14 + int(pulse * 10)),
        )
        pyray.draw_rectangle_rec(
            pyray.Rectangle(lane_x + 12, lane_y + 4, lane_w - 24, 1),
            with_alpha(colors.WHITE, 8),
        )

    corner_radius = 20
    corners = (
        (rect.x + 8, rect.y + 8, LIVE_CYAN),
        (rect.x + rect.width - 8, rect.y + 8, LIVE_PINK),
        (rect.x + 8, rect.y + rect.height - 8, LIVE_PINK),
        (rect.x + rect.width - 8, rect.y + rect.height - 8, LIVE_GOLD),
    )
    for cx, cy, color in corners:
        pyray.draw_circle(int(cx), int(cy), corner_radius, with_alpha(color, 16))
        pyray.draw_circle(int(cx), int(cy), 6, with_alpha(color, 104))

    theme_name = _current_theme_name()
    if theme_name == "Amber Rain":
        for index in range(5):
            ry = rect.y + 20 + index * 26
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x + 18, ry, rect.width - 36, 2),
                with_alpha(LIVE_GOLD, 18 + index * 4),
            )
    elif theme_name == "Ice Circuit":
        for index in range(8):
            x = rect.x + 16 + index * max(24, rect.width // 9)
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, rect.y + 16, 2, rect.height - 32),
                with_alpha(colors.WHITE, 16),
            )
    elif theme_name == "Velvet Alley":
        for index in range(4):
            glow_x = rect.x + 32 + index * max(60, rect.width // 5)
            pyray.draw_circle(int(glow_x), int(rect.y + rect.height - 24), 18 + index * 4, with_alpha(LIVE_PINK, 18))


def draw_live_panel_accent(rect, time_s: float) -> None:
    pulse = 0.5 + 0.5 * math.sin(time_s * 3.0)
    flicker = 0.5 + 0.5 * math.sin(time_s * 8.0 + rect.x * 0.02)
    alpha = int(14 + pulse * 12)
    bar_height = 3
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 18, rect.y + 16, rect.width - 36, bar_height),
        with_alpha(LIVE_CYAN, alpha + int(flicker * 12)),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 18, rect.y + 24, int((rect.width - 36) * 0.44), 1),
        with_alpha(LIVE_PINK, 56 + int(flicker * 8)),
    )
    scan_x = int(rect.x + 24 + (math.sin(time_s * 1.8) * 0.5 + 0.5) * max(1, rect.width - 72))
    pgui.draw_rect(
        pyray.Rectangle(scan_x, rect.y + 13, 24, 7),
        with_alpha(colors.WHITE, int(16 + pulse * 18)),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 32, rect.y + 16, 14, 2),
        with_alpha(LIVE_CYAN, 52),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 18, rect.y + 16, 2, 14),
        with_alpha(LIVE_CYAN, 52),
    )


def _current_theme_name() -> str:
    for theme_name, preset in THEME_PRESETS.items():
        if preset["PANEL_ACCENT"] == PANEL_ACCENT:
            return theme_name
    return "Neon District"


def _draw_skyline_layers(width: int, height: int, time_s: float, *, live_mode: bool) -> None:
    far_base = int(height * (0.38 if live_mode else 0.34))
    mid_base = int(height * (0.48 if live_mode else 0.44))
    near_base = int(height * (0.58 if live_mode else 0.54))

    far_specs = (
        (0.08, 0.10, 0.22),
        (0.20, 0.08, 0.28),
        (0.33, 0.11, 0.18),
        (0.70, 0.07, 0.24),
        (0.81, 0.09, 0.30),
    )
    mid_specs = (
        (0.12, 0.12, 0.26),
        (0.28, 0.14, 0.22),
        (0.58, 0.10, 0.20),
        (0.74, 0.12, 0.24),
        (0.88, 0.08, 0.18),
    )
    near_specs = (
        (0.16, 0.07, 0.32),
        (0.63, 0.06, 0.34),
        (0.72, 0.05, 0.30),
    )

    def draw_layer(specs, base_y: int, alpha_scale: float, drift: float, window_alpha: int) -> None:
        for index, (xr, wr, hr) in enumerate(specs):
            parallax = math.sin(time_s * drift + index * 0.9) * (4 + index % 3)
            bx = int(width * xr + parallax)
            bw = int(width * wr)
            bh = int(height * hr)
            top = base_y - bh
            body = pyray.Rectangle(bx, top, bw, bh)
            pyray.draw_rectangle_rec(body, with_alpha((10, 12, 24, 255), int(150 * alpha_scale)))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(bx + 6, top + 18, max(10, bw - 12), max(18, bh - 28)),
                with_alpha((14, 16, 34, 255), int(72 * alpha_scale)),
            )
            edge_color = LIVE_CYAN if index % 2 == 0 else LIVE_PINK
            pyray.draw_rectangle_rec(
                pyray.Rectangle(bx + bw - 4, top + 12, 2, max(18, bh - 18)),
                with_alpha(edge_color, int(26 * alpha_scale)),
            )
            for wy in range(top + 16, top + bh - 10, 16):
                for wx in range(bx + 8, bx + bw - 10, 14):
                    blink = 0.5 + 0.5 * math.sin(time_s * (1.4 + (wx % 5) * 0.07) + wy * 0.03 + wx * 0.02)
                    if blink < 0.45:
                        continue
                    win_color = LIVE_CYAN if (wx + wy + index) % 2 == 0 else LIVE_PINK
                    alpha = int(window_alpha * blink * alpha_scale)
                    pyray.draw_rectangle_rec(
                        pyray.Rectangle(wx, wy, 4, 6),
                        with_alpha(win_color, alpha),
                    )
            # subtle glow bleed around closer buildings
            if alpha_scale >= 0.9:
                _draw_soft_rect_glow(body, edge_color, spread=10, alpha=5, layers=2)

    draw_layer(far_specs, far_base, 0.55, 0.12, 42)
    draw_layer(mid_specs, mid_base, 0.78, 0.18, 58)
    draw_layer(near_specs, near_base, 1.0, 0.25, 72)


def _draw_theme_background_overlays(width: int, height: int, time_s: float, *, live_mode: bool) -> None:
    theme_name = _current_theme_name()

    if theme_name == "Amber Rain":
        lane_y = int(height * (0.74 if not live_mode else 0.68))
        for index in range(7):
            x = int(width * 0.06) + index * max(56, width // 12)
            puddle_w = 64 + (index % 3) * 18
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, lane_y + index * 8, puddle_w, 8),
                with_alpha(LIVE_GOLD, 18 + index * 4),
            )
        for index in range(10):
            x = int(width * 0.58) + index * 18
            y = int(height * 0.22) + index * 12
            pyray.draw_circle(x, y, 3 + index % 3, with_alpha(LIVE_GOLD, 22))

    elif theme_name == "Ice Circuit":
        for index in range(14):
            x = int(width * 0.08) + index * max(34, width // 18)
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, 0, 1, height),
                with_alpha(colors.WHITE, 14 if index % 2 else 20),
            )
        for index in range(5):
            y = int(height * 0.18) + index * 42
            pyray.draw_rectangle_rec(
                pyray.Rectangle(int(width * 0.62), y, int(width * 0.24), 10),
                with_alpha(LIVE_CYAN, 16 + index * 4),
            )

    elif theme_name == "Velvet Alley":
        for index in range(6):
            cx = int(width * 0.16) + index * max(70, width // 9)
            cy = int(height * 0.28) + (index % 2) * 36
            pyray.draw_circle(cx, cy, 28 + index * 3, with_alpha(LIVE_PINK, 12))
        for index in range(8):
            x = int(width * 0.54) + index * 20
            y = int(height * 0.46) + index * 10
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, y, 34, 3),
                with_alpha(LIVE_GOLD, 18 + index * 3),
            )


def draw_text_centered(text: str, center_x: int, y: int, font_size: int, color) -> None:
    pgui.draw_text_centered(text, center_x, y, font_size, color)


def draw_shadowed_text_centered(
    text: str,
    center_x: int,
    y: int,
    font_size: int,
    color,
    shadow_color=colors.BLACK,
    shadow_offset: int = 2,
) -> None:
    pgui.draw_text_centered(text, center_x + shadow_offset, y + shadow_offset, font_size, shadow_color)
    pgui.draw_text_centered(text, center_x, y, font_size, color)


def draw_cinematic_title_stack(center_x: int, y: int, title: str, subtitle: str, kicker: str, time_s: float = 0.0, *, variant: str = "Standard") -> None:
    pulse = 0.5 + 0.5 * math.sin(time_s * 1.7)
    title_size = 82
    glow_w = max(360, pgui.measure_text(title, title_size) + 72)

    line_color = LIVE_CYAN
    subtitle_color = with_alpha(LIVE_PINK, 220)
    kicker_color = with_alpha(TEXT_DIM, 142)

    if variant == "Broadcast":
        for index in range(4):
            pyray.draw_rectangle_rec(
                pyray.Rectangle(center_x - glow_w // 2 - 8, y + 18 + index * 24, glow_w + 16, 3),
                with_alpha(LIVE_CYAN, 12 + index * 4),
            )
        subtitle_color = with_alpha(LIVE_GOLD, 220)
    elif variant == "Splitline":
        line_color = LIVE_GOLD
        subtitle_color = with_alpha(LIVE_CYAN, 230)
        kicker_color = with_alpha(LIVE_GOLD, 150)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(center_x + glow_w // 2 - 20, y + 8, 12, 110),
            with_alpha(LIVE_GOLD, 34),
        )
    elif variant == "Executive":
        line_color = colors.WHITE
        subtitle_color = with_alpha(LIVE_CYAN, 230)
        kicker_color = with_alpha(colors.WHITE, 132)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(center_x - glow_w // 2 - 16, y - 10, glow_w + 32, 126),
            with_alpha(colors.WHITE, 8),
        )
        pyray.draw_rectangle_lines_ex(
            pyray.Rectangle(center_x - glow_w // 2 - 12, y - 6, glow_w + 24, 118),
            1,
            with_alpha(colors.WHITE, 48),
        )

    _draw_soft_circle_glow(center_x - 96, y + 28, 84, LIVE_CYAN, alpha=10, layers=3)
    _draw_soft_circle_glow(center_x + 62, y + 14, 56, LIVE_PINK, alpha=8, layers=3)
    _draw_soft_rect_glow(
        pyray.Rectangle(center_x - glow_w // 2, y + 92, glow_w, 8),
        line_color,
        spread=10,
        alpha=8,
        layers=2,
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(center_x - glow_w // 2, y + 94, glow_w, 1),
        with_alpha(line_color, 60),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(center_x - glow_w // 2 + 28, y + 97, glow_w - 56, 1),
        with_alpha(line_color, int(18 + pulse * 10)),
    )
    _draw_soft_rect_glow(
        pyray.Rectangle(center_x - glow_w // 2 + 26, y - 8, glow_w - 52, title_size + 16),
        LIVE_CYAN if variant != "Executive" else colors.WHITE,
        spread=12,
        alpha=8,
        layers=2,
    )
    draw_shadowed_text_centered(title, center_x, y, title_size, colors.WHITE)
    draw_text_centered(subtitle, center_x, y + 106, 20, subtitle_color)
    draw_text_centered(kicker, center_x, y + 134, 13, kicker_color)
