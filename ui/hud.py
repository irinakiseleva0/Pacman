from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from core.gameplay_view_models import GameplayHudModel
from ui import pygame_primitives as pgui
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK, TEXT_DIM, draw_glass_card
from utils.effects import FloatingText
from utils.visual_effects import with_alpha


_floating_texts: list[FloatingText] = []


def spawn_floating_text(text: str, pos, color, lifetime: float = 1.0) -> None:
    _floating_texts.append(FloatingText(text, pos, color, lifetime))


def update_floating_texts(dt: float) -> None:
    _floating_texts[:] = [text for text in _floating_texts if text.update(dt)]


def draw_floating_texts() -> None:
    for text in _floating_texts:
        font_size = 22 if "x" in text.text else 20
        width = pgui.measure_text(text.text, font_size)
        x = int(text.pos.x - width / 2)
        y = int(text.pos.y)
        pgui.draw_text(text.text, x + 1, y + 1, font_size, with_alpha(colors.BLACK, 150 * text.alpha))
        pgui.draw_text(text.text, x, y, font_size, text.color)


def draw_ability_slots(ctx, *, x: int, y: int, width: int, time_s: float = 0.0) -> None:
    pacman = getattr(ctx.runtime, "pacman", None)
    abilities = list(getattr(pacman, "abilities", []) or [])[:3]
    if not abilities:
        return

    slot_size = 42
    gap = 10
    total_width = len(abilities) * slot_size + max(0, len(abilities) - 1) * gap
    start_x = int(x + max(0, width - total_width) / 2)
    for index, ability in enumerate(abilities):
        sx = start_x + index * (slot_size + gap)
        sy = y
        cx = sx + slot_size // 2
        cy = sy + slot_size // 2
        unlocked = bool(getattr(ability, "unlocked", True))
        active = ability.is_active()
        ready = ability.is_ready()
        progress = ability.cooldown_progress()
        accent = LIVE_CYAN if ability.name == "Dash" else LIVE_GOLD if ability.name == "Shield" else LIVE_PINK
        fill_alpha = 150 if ready else 88
        if not unlocked:
            fill_alpha = 52
            accent = TEXT_DIM

        rect = pyray.Rectangle(sx, sy, slot_size, slot_size)
        pgui.draw_rect(rect, with_alpha(colors.BLACK, 96))
        pgui.draw_rect(rect, with_alpha(accent, 150 if ready or active else 78), 1)
        pgui.draw_circle(cx, cy, 17, with_alpha(accent, 18 if ready else 9))
        pgui.draw_circle(cx, cy, 13, with_alpha(accent, fill_alpha))

        if active:
            pulse = 0.5 + 0.5 * math.sin(time_s * 12.0)
            pgui.draw_circle(cx, cy, 20 + int(pulse * 2), with_alpha(colors.WHITE, 170), 1)
        elif progress > 0:
            remaining_height = int(slot_size * progress)
            pgui.draw_rect(
                pyray.Rectangle(sx, sy + slot_size - remaining_height, slot_size, remaining_height),
                with_alpha(colors.BLACK, 126),
            )
            pgui.draw_circle(cx, cy, 20, with_alpha(accent, 68), 1)

        icon = getattr(ability, "icon", "?")
        key = getattr(ability, "key_label", "")
        icon_size = 18
        icon_w = pgui.measure_text(icon, icon_size)
        pgui.draw_text(icon, int(cx - icon_w / 2), int(sy + 10), icon_size, colors.WHITE if unlocked else TEXT_DIM)
        key_size = 10
        key_w = pgui.measure_text(key, key_size)
        pgui.draw_text(key, int(cx - key_w / 2), int(sy + slot_size - 13), key_size, with_alpha(colors.WHITE, 185))


def _card_height(line_count: int, line_height: int) -> int:
    return 28 + max(1, line_count) * line_height + 18


def _draw_card(title: str, lines: list[tuple[str, object]], rect, font_size: int, line_height: int, accent_color) -> None:
    draw_glass_card(rect, accent_color=accent_color, glow_alpha=18, fill_alpha=150)
    pgui.draw_rect(
        pyray.Rectangle(rect.x - 7, rect.y - 7, rect.width + 14, rect.height + 14),
        with_alpha(accent_color, 9),
    )
    title_size = max(12, font_size - 10)
    pgui.draw_text(title.upper(), int(rect.x + 18), int(rect.y + 8), title_size, with_alpha(TEXT_DIM, 216))
    pgui.draw_rect(
        pyray.Rectangle(rect.x + 18, rect.y + 25, max(42, rect.width * 0.26), 2),
        with_alpha(accent_color, 152),
    )
    pgui.draw_rect(
        pyray.Rectangle(rect.x + rect.width - 54, rect.y + 13, 34, 2),
        with_alpha(LIVE_CYAN if accent_color != LIVE_CYAN else LIVE_PINK, 70),
    )
    pgui.draw_rect(
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
            label_width = pgui.measure_text(f"{label}:", label_size)
            value_text = value.strip()
            value_width = pgui.measure_text(value_text, value_size)
            value_accent = LIVE_GOLD if key in {"score", "best"} else LIVE_CYAN if key in {"time", "seeds"} else accent_color
            pgui.draw_rect(
                pyray.Rectangle(rect.x + 18 + label_width + 4, content_y - 5, value_width + 12, value_size + 8),
                with_alpha(value_accent, 8 if key not in {"score", "time", "lives", "level"} else 15),
            )
            pgui.draw_text(f"{label}:", int(rect.x + 22), content_y + 1, label_size, label_color)
            pgui.draw_text(value_text, int(rect.x + 22 + label_width + 10), content_y - 1, value_size, color)
        else:
            draw_size = max(14, font_size + 2)
            pgui.draw_text(text, int(rect.x + 22), content_y, draw_size, color)
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
