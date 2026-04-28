from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.gameplay_view_models import GameplayHudModel
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK, TEXT_DIM, draw_glass_card
from utils.visual_effects import with_alpha


def _card_height(line_count: int, line_height: int) -> int:
    return 28 + max(1, line_count) * line_height + 18


def _draw_card(title: str, lines: list[tuple[str, object]], rect, font_size: int, line_height: int, accent_color) -> None:
    draw_glass_card(rect, accent_color=accent_color, glow_alpha=18, fill_alpha=150)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 7, rect.y - 7, rect.width + 14, rect.height + 14),
        with_alpha(accent_color, 9),
    )
    title_size = max(12, font_size - 10)
    pyray.draw_text(title.upper(), int(rect.x + 18), int(rect.y + 8), title_size, with_alpha(TEXT_DIM, 216))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 18, rect.y + 25, max(42, rect.width * 0.26), 2),
        with_alpha(accent_color, 152),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + rect.width - 54, rect.y + 13, 34, 2),
        with_alpha(LIVE_CYAN if accent_color != LIVE_CYAN else LIVE_PINK, 70),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + rect.width - 20, rect.y + 13, 2, 14),
        with_alpha(accent_color, 82),
    )

    content_y = int(rect.y + 38)
    for text, color in lines:
        label_color = TEXT_DIM if color == colors.WHITE else color
        if ":" in text:
            label, value = text.split(":", 1)
            key = label.lower()
            label_size = max(12, font_size - 9)
            value_boost = 1
            if key in {"score", "time", "lives", "level"}:
                value_boost = 5
            elif key in {"best", "seeds"}:
                value_boost = 2
            value_size = max(16, font_size + value_boost)
            label_width = pyray.measure_text(f"{label}:", label_size)
            value_text = value.strip()
            value_width = pyray.measure_text(value_text, value_size)
            value_accent = LIVE_GOLD if key in {"score", "best"} else LIVE_CYAN if key in {"time", "seeds"} else accent_color
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x + 18 + label_width + 4, content_y - 5, value_width + 12, value_size + 8),
                with_alpha(value_accent, 8 if key not in {"score", "time", "lives", "level"} else 15),
            )
            pyray.draw_text(f"{label}:", int(rect.x + 22), content_y + 1, label_size, label_color)
            pyray.draw_text(value_text, int(rect.x + 22 + label_width + 10), content_y - 1, value_size, color)
        else:
            draw_size = max(14, font_size + 2)
            pyray.draw_text(text, int(rect.x + 22), content_y, draw_size, color)
        content_y += line_height


def draw_game_hud(
    model: GameplayHudModel,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    font_size: int,
    line_height: int,
    columns: int,
) -> None:
    gap = 10
    sections = [(section.title, list(section.lines), section.accent) for section in model.sections]
    if max(1, columns) > 1 and len(sections) >= 2:
        top_width = max(1, int((width - gap) / 2))
        first_height = _card_height(len(sections[0][1]), line_height)
        second_height = _card_height(len(sections[1][1]), line_height)
        top_height = max(first_height, second_height)

        first_rect = pyray.Rectangle(x, y, top_width, top_height)
        second_rect = pyray.Rectangle(x + top_width + gap, y, width - top_width - gap, top_height)
        _draw_card(sections[0][0], sections[0][1], first_rect, font_size, line_height, sections[0][2])
        _draw_card(sections[1][0], sections[1][1], second_rect, font_size, line_height, sections[1][2])

        if len(sections) > 2:
            third_height = _card_height(len(sections[2][1]), line_height)
            third_rect = pyray.Rectangle(x, y + top_height + gap, width, min(third_height, height - top_height - gap))
            _draw_card(sections[2][0], sections[2][1], third_rect, font_size, line_height, sections[2][2])
        return

    current_y = y
    for title, lines, accent in sections:
        card_height = _card_height(len(lines), line_height)
        if current_y + card_height > y + height:
            card_height = max(80, int(y + height - current_y))
        rect = pyray.Rectangle(x, current_y, width, card_height)
        _draw_card(title, lines, rect, font_size, line_height, accent)
        current_y += card_height + gap
        if current_y >= y + height:
            break
