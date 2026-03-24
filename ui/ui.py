from __future__ import annotations

import math

import pyray
from raylib import colors

from utils.visual_effects import with_alpha


BG_TOP = (34, 20, 72, 255)
BG_BOTTOM = (8, 7, 20, 255)
PANEL_OUTER = (28, 18, 58, 235)
PANEL_INNER = (16, 14, 38, 220)
PANEL_ACCENT = (102, 232, 255, 255)
TEXT_DIM = (214, 220, 255, 255)
BUTTON_IDLE = (52, 36, 98, 255)
BUTTON_ACTIVE = (88, 62, 154, 255)
BUTTON_HOVER = (114, 86, 188, 255)
LIVE_CYAN = (112, 242, 255, 255)
LIVE_PINK = (255, 86, 212, 255)
LIVE_GOLD = (255, 208, 92, 255)
PANEL_PINK = (255, 86, 212, 255)
NOIR_BLUE = (6, 8, 26, 255)
STREET_BLUE = (14, 20, 48, 255)
GLASS_EDGE = (186, 236, 255, 255)
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
    global PANEL_ACCENT, LIVE_CYAN, LIVE_PINK, LIVE_GOLD, BG_TOP, NOIR_BLUE, STREET_BLUE
    preset = THEME_PRESETS.get(theme_name, THEME_PRESETS["Neon District"])
    PANEL_ACCENT = preset["PANEL_ACCENT"]
    LIVE_CYAN = preset["LIVE_CYAN"]
    LIVE_PINK = preset["LIVE_PINK"]
    LIVE_GOLD = preset["LIVE_GOLD"]
    BG_TOP = preset["BG_TOP"]
    NOIR_BLUE = preset["NOIR_BLUE"]
    STREET_BLUE = preset["STREET_BLUE"]


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


def draw_button(rect, text: str, focused: bool = False) -> None:
    mouse = pyray.get_mouse_position()
    hovered = pyray.check_collision_point_rec(mouse, rect)
    outer_glow = LIVE_CYAN if focused else LIVE_PINK if hovered else PANEL_ACCENT
    fill_color = (
        with_alpha((34, 28, 70, 255), 182) if hovered
        else with_alpha((28, 24, 60, 255), 196) if focused
        else with_alpha((20, 20, 44, 255), 168)
    )
    border_color = with_alpha(LIVE_CYAN, 160) if focused else with_alpha(GLASS_EDGE, 92)

    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 10, rect.y - 10, rect.width + 20, rect.height + 20),
        with_alpha(outer_glow, 24 if hovered or focused else 12),
    )
    pyray.draw_rectangle_rec(rect, fill_color)
    pyray.draw_rectangle_lines_ex(rect, 1, border_color)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 2, rect.y + 2, max(0, rect.width - 4), max(0, rect.height * 0.34)),
        with_alpha(colors.WHITE, 12),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 16, rect.y + rect.height - 5, max(0, rect.width - 32), 1),
        with_alpha(LIVE_CYAN if focused else PANEL_ACCENT, 110 if hovered or focused else 38),
    )

    font_size = max(18, min(26, int(rect.height * 0.42)))
    tw = pyray.measure_text(text, font_size)
    tx = int(rect.x + (rect.width - tw) / 2)
    ty = int(rect.y + (rect.height - font_size) / 2)
    text_color = with_alpha(LIVE_CYAN, 240) if focused else with_alpha(colors.WHITE, 230)
    pyray.draw_text(text, tx, ty, font_size, text_color)


def draw_panel(rect, title: str | None = None) -> None:
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 16, rect.y - 16, rect.width + 32, rect.height + 32),
        with_alpha(PANEL_ACCENT, 16),
    )
    pyray.draw_rectangle_rec(rect, with_alpha((18, 18, 42, 255), 226))
    pyray.draw_rectangle_lines_ex(rect, 1, with_alpha(GLASS_EDGE, 88))

    inner = pyray.Rectangle(rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20)
    pyray.draw_rectangle_rec(inner, with_alpha((16, 14, 34, 255), 210))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(inner.x, inner.y, inner.width, max(0, inner.height * 0.22)),
        with_alpha(colors.WHITE, 8),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(inner.x + 18, inner.y + inner.height - 18, max(0, inner.width - 36), 1),
        with_alpha(LIVE_CYAN, 38),
    )
    corner_len = 26
    pyray.draw_rectangle_rec(pyray.Rectangle(rect.x + rect.width - corner_len - 8, rect.y + 8, corner_len, 2), with_alpha(LIVE_CYAN, 72))
    pyray.draw_rectangle_rec(pyray.Rectangle(rect.x + rect.width - 10, rect.y + 8, 2, corner_len), with_alpha(LIVE_CYAN, 72))
    pyray.draw_rectangle_rec(pyray.Rectangle(rect.x + 8, rect.y + rect.height - 10, corner_len, 2), with_alpha(LIVE_PINK, 72))
    pyray.draw_rectangle_rec(pyray.Rectangle(rect.x + 8, rect.y + rect.height - corner_len - 8, 2, corner_len), with_alpha(LIVE_PINK, 72))

    if title:
        title_y = int(rect.y + 12)
        draw_text_centered(title, int(rect.x + rect.width / 2), title_y, 22, LIVE_CYAN)


def draw_scene_header(rect, eyebrow: str, title: str, subtitle: str, *, title_size: int = 42) -> None:
    center_x = int(rect.x + rect.width / 2)
    draw_text_centered(eyebrow, center_x, int(rect.y + 22), 18, PANEL_ACCENT)
    draw_shadowed_text_centered(title, center_x, int(rect.y + 50), title_size, colors.WHITE)
    draw_text_centered(subtitle, center_x, int(rect.y + 96), 16, TEXT_DIM)


def draw_scene_footer(rect, text: str = "ENTER OR CLICK") -> None:
    center_x = int(rect.x + rect.width / 2)
    draw_text_centered(text, center_x, int(rect.y + rect.height - 28), 14, TEXT_DIM)


def draw_glass_card(rect, accent_color=LIVE_CYAN, *, glow_alpha: int = 18, fill_alpha: int = 160) -> None:
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 6, rect.y - 6, rect.width + 12, rect.height + 12),
        with_alpha(accent_color, glow_alpha),
    )
    pyray.draw_rectangle_rec(rect, with_alpha(PANEL_INNER, fill_alpha))
    pyray.draw_rectangle_lines_ex(rect, 1, with_alpha(GLASS_EDGE, 90))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 3, rect.y + 3, max(0, rect.width - 6), max(0, rect.height * 0.35)),
        with_alpha(colors.WHITE, 14),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 12, rect.y + 12, 3, max(0, rect.height - 24)),
        with_alpha(accent_color, 110),
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

    pyray.draw_rectangle_rec(
        pyray.Rectangle(frame.x - 16, frame.y - 16, frame.width + 32, frame.height + 32),
        with_alpha(glow_color, int(20 + pulse * 18)),
    )
    pyray.draw_rectangle_rec(frame, with_alpha(frame_fill, 222))
    pyray.draw_rectangle_lines_ex(frame, 2, with_alpha(glow_color, 170))
    pyray.draw_rectangle_rec(inner, with_alpha(inner_fill, 228))
    pyray.draw_rectangle_rec(light_bar, with_alpha(colors.WHITE, 12))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(frame.x - int(14 * scale), frame.y + int(18 * scale), int(12 * scale), int(82 * scale)),
        with_alpha(side_color, 64),
    )
    pyray.draw_rectangle_rec(side_box, with_alpha(side_color, 12))
    pyray.draw_rectangle_lines_ex(side_box, 1, with_alpha(side_color, 90))
    draw_text_centered(module_label, int(side_box.x + side_box.width / 2), int(side_box.y + 5), max(9, int(12 * scale)), with_alpha(colors.WHITE, 190))

    if theme_name == "Amber Rain":
        awning = pyray.Rectangle(frame.x + 18, frame.y + frame.height - int(20 * scale), frame.width - 88, int(12 * scale))
        pyray.draw_rectangle_rec(awning, with_alpha(LIVE_GOLD, 84))
    elif theme_name == "Ice Circuit":
        for index in range(7):
            vx = frame.x + 26 + index * int(46 * scale)
            pyray.draw_rectangle_rec(
                pyray.Rectangle(vx, frame.y + 20, 2, frame.height - 38),
                with_alpha(colors.WHITE, 26),
            )
    elif theme_name == "Velvet Alley":
        pyray.draw_circle(int(frame.x + 34), int(frame.y + 34), int(16 * scale), with_alpha(LIVE_PINK, 40))
        pyray.draw_circle(int(frame.x + frame.width - 106), int(frame.y + 102), int(14 * scale), with_alpha(LIVE_GOLD, 30))

    logo_cell = max(5, int(8 * scale))
    logo_text = "PAC-MAN"
    logo_width = len(logo_text) * logo_cell * 6 - logo_cell
    logo_x = int(center_x - logo_width / 2 - 8 * scale)
    logo_y = int(frame.y + 44 * scale)
    _draw_dot_matrix_text(logo_text, logo_x, logo_y, logo_cell, colors.WHITE, LIVE_PINK)

    pac_radius = int(13 * scale)
    pac_x = int(center_x + 10 * scale)
    pac_y = int(frame.y + 74 * scale)
    pyray.draw_circle(pac_x, pac_y, pac_radius + 14, with_alpha(LIVE_CYAN, 12))
    pyray.draw_circle(pac_x, pac_y, pac_radius, with_alpha((255, 220, 80, 255), 220))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(pac_x + 2, pac_y - 8, 12, 16),
        with_alpha((18, 18, 46, 255), 255),
    )
    for dot_index in range(3):
        dot_x = pac_x + 28 + dot_index * 12
        pyray.draw_circle(dot_x, pac_y, 3 + dot_index % 2, with_alpha(LIVE_CYAN, 180 - dot_index * 28))


def draw_street_terminal(rect, title: str, value: str, accent_color, *, subline: str | None = None) -> None:
    draw_glass_card(rect, accent_color=accent_color, glow_alpha=16, fill_alpha=170)
    pyl = int(rect.y + rect.height * 0.56)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 10, rect.y + 10, int(rect.width * 0.42), int(rect.height - 20)),
        with_alpha((8, 12, 28, 255), 120),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 14, rect.y + 16, 4, int(rect.height - 32)),
        with_alpha(accent_color, 170),
    )
    theme_name = _current_theme_name()
    if theme_name == "Amber Rain":
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x + rect.width - 62, rect.y + 14, 42, 10),
            with_alpha(LIVE_GOLD, 60),
        )
    elif theme_name == "Ice Circuit":
        for index in range(4):
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x + rect.width - 22 - index * 8, rect.y + 14, 2, rect.height - 28),
                with_alpha(colors.WHITE, 22),
            )
    elif theme_name == "Velvet Alley":
        pyray.draw_circle(int(rect.x + rect.width - 30), int(rect.y + 26), 10, with_alpha(LIVE_PINK, 32))
    draw_text_centered(title, int(rect.x + rect.width / 2), int(rect.y + 12), 14, TEXT_DIM)
    draw_text_centered(value, int(rect.x + rect.width / 2), int(rect.y + 36), 20, colors.WHITE)
    if subline:
        draw_text_centered(subline, int(rect.x + rect.width / 2), int(rect.y + 58), 12, accent_color)


def draw_arcade_background(width: int, height: int, time_s: float = 0.0) -> None:
    pyray.draw_rectangle_rec(pyray.Rectangle(0, 0, width, height), BG_BOTTOM)
    sky = pyray.Rectangle(0, 0, width, height)
    pyray.draw_rectangle_rec(sky, with_alpha(BG_TOP, 180))
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
    pyray.draw_rectangle_lines_ex(
        pyray.Rectangle(int(width * 0.12), sign_y, 170, 44),
        2,
        with_alpha(LIVE_PINK, sign_alpha),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.68), sign_y + 26, 120, 38),
        with_alpha((16, 14, 38, 255), 210),
    )
    pyray.draw_rectangle_lines_ex(
        pyray.Rectangle(int(width * 0.68), sign_y + 26, 120, 38),
        2,
        with_alpha(LIVE_CYAN, sign_alpha),
    )

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
    pyray.draw_rectangle_rec(pyray.Rectangle(0, 0, width, height), NOIR_BLUE)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, width, int(height * 0.66)),
        with_alpha((40, 32, 90, 255), 150),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.38), width, int(height * 0.62)),
        with_alpha(STREET_BLUE, 210),
    )

    pulse = 0.5 + 0.5 * math.sin(time_s * 1.8)
    cyan_alpha = int(34 + pulse * 38)
    pink_alpha = int(28 + pulse * 34)

    pyray.draw_circle(int(width * 0.22), int(height * 0.24), 180, with_alpha(LIVE_CYAN, 8))
    pyray.draw_circle(int(width * 0.34), int(height * 0.18), 150, with_alpha(LIVE_PINK, 7))

    horizon = int(height * 0.56)
    building_x = int(width * 0.52)
    index = 0
    while building_x < width + 60:
        b_width = 56 + (index % 4) * 24
        b_height = 170 + (index % 5) * 42
        top = horizon - b_height
        pyray.draw_rectangle_rec(
            pyray.Rectangle(building_x, top, b_width, b_height),
            with_alpha((16, 16, 34, 255), 248),
        )
        if index % 2 == 0:
            pyray.draw_rectangle_rec(
                pyray.Rectangle(building_x + 6, top + 18, 4, max(22, b_height - 36)),
                with_alpha(LIVE_CYAN, 72),
            )
        for wy in range(top + 24, top + b_height - 12, 18):
            for wx in range(building_x + 12, building_x + b_width - 12, 16):
                if (wx + wy + index) % 4 == 0:
                    continue
                window_color = LIVE_PINK if (wx + index) % 2 else LIVE_CYAN
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(wx, wy, 5, 7),
                    with_alpha(window_color, 68),
                )
        building_x += b_width - 8
        index += 1

    left_block = pyray.Rectangle(int(width * 0.12), int(height * 0.20), int(width * 0.30), int(height * 0.16))
    pyray.draw_rectangle_rec(left_block, with_alpha((32, 28, 74, 255), 44))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(left_block.x + 22, left_block.y + 26, left_block.width - 44, 24),
        with_alpha(colors.WHITE, 4),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.16), int(height * 0.45), int(width * 0.07), int(height * 0.15)),
        with_alpha((18, 18, 38, 255), 118),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.24), int(height * 0.40), int(width * 0.06), int(height * 0.20)),
        with_alpha((16, 16, 34, 255), 128),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(int(width * 0.31), int(height * 0.42), int(width * 0.04), int(height * 0.14)),
        with_alpha((14, 14, 30, 255), 110),
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
    pyray.draw_rectangle_rec(pyray.Rectangle(0, 0, width, height), BG_BOTTOM)

    band_specs = (
        (LIVE_CYAN, 0.22, 120, 90),
        (LIVE_PINK, 0.16, 210, 120),
        (LIVE_GOLD, 0.12, 310, 150),
    )
    for color, speed, band_width, alpha in band_specs:
        x = (math.sin(time_s * speed * 0.1) * 0.5 + 0.5) * max(1, width - band_width)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(int(x), 0, band_width, height),
            with_alpha(color, alpha),
        )

    for index in range(10):
        y = int((index * 54 + time_s * 40) % (height + 40)) - 40
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, y, width, 2),
            with_alpha(colors.WHITE, 12),
        )

    _draw_theme_background_overlays(width, height, time_s, live_mode=True)


def draw_live_board_backdrop(rect, time_s: float) -> None:
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.4)
    glow_alpha = int(38 + pulse * 42)

    pyray.draw_rectangle_rec(rect, (2, 2, 8, 255))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 10, rect.y - 10, rect.width + 20, rect.height + 20),
        with_alpha(LIVE_CYAN, glow_alpha),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10),
        with_alpha(LIVE_PINK, 26),
    )
    pyray.draw_rectangle_rec(rect, (4, 4, 12, 255))

    corner_radius = 28
    corners = (
        (rect.x + 8, rect.y + 8, LIVE_CYAN),
        (rect.x + rect.width - 8, rect.y + 8, LIVE_PINK),
        (rect.x + 8, rect.y + rect.height - 8, LIVE_PINK),
        (rect.x + rect.width - 8, rect.y + rect.height - 8, LIVE_GOLD),
    )
    for cx, cy, color in corners:
        pyray.draw_circle(int(cx), int(cy), corner_radius, with_alpha(color, 28))
        pyray.draw_circle(int(cx), int(cy), 8, with_alpha(color, 120))

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
    alpha = int(30 + pulse * 32)
    bar_height = 8
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 14, rect.y + 14, rect.width - 28, bar_height),
        with_alpha(LIVE_GOLD, alpha),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 14, rect.y + 28, int((rect.width - 28) * 0.68), 3),
        with_alpha(LIVE_CYAN, 80),
    )


def _current_theme_name() -> str:
    for theme_name, preset in THEME_PRESETS.items():
        if preset["PANEL_ACCENT"] == PANEL_ACCENT:
            return theme_name
    return "Neon District"


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
    text_width = pyray.measure_text(text, font_size)
    x = int(center_x - text_width / 2)
    pyray.draw_text(text, x, y, font_size, color)


def draw_shadowed_text_centered(
    text: str,
    center_x: int,
    y: int,
    font_size: int,
    color,
    shadow_color=colors.BLACK,
    shadow_offset: int = 2,
) -> None:
    draw_text_centered(text, center_x + shadow_offset, y + shadow_offset, font_size, shadow_color)
    draw_text_centered(text, center_x, y, font_size, color)


def draw_cinematic_title_stack(center_x: int, y: int, title: str, subtitle: str, kicker: str, time_s: float = 0.0) -> None:
    pulse = 0.5 + 0.5 * math.sin(time_s * 1.7)
    title_size = 68
    glow_w = max(280, pyray.measure_text(title, title_size) + 56)

    pyray.draw_circle(center_x - 76, y + 20, 68, with_alpha(LIVE_CYAN, 5))
    pyray.draw_circle(center_x + 48, y + 10, 58, with_alpha(LIVE_PINK, 4))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(center_x - glow_w // 2, y + 76, glow_w, 1),
        with_alpha(LIVE_CYAN, 68),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(center_x - glow_w // 2 + 28, y + 79, glow_w - 56, 1),
        with_alpha(LIVE_CYAN, int(26 + pulse * 14)),
    )

    draw_shadowed_text_centered(title, center_x, y, title_size, colors.WHITE)
    draw_text_centered(subtitle, center_x, y + 86, 18, with_alpha(LIVE_PINK, 220))
    draw_text_centered(kicker, center_x, y + 112, 13, with_alpha(TEXT_DIM, 142))
