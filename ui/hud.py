from __future__ import annotations

import math

import pyray
from raylib import colors

from entities.ghost import Ghost
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK, TEXT_DIM, draw_glass_card


def _card_height(line_count: int, line_height: int) -> int:
    return 40 + max(1, line_count) * line_height + 14


def _draw_card(title: str, lines: list[tuple[str, object]], rect, font_size: int, line_height: int, accent_color) -> None:
    draw_glass_card(rect, accent_color=accent_color, glow_alpha=16, fill_alpha=150)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 18, rect.y + 30, max(48, rect.width * 0.24), 2),
        accent_color,
    )
    pyray.draw_text(title, int(rect.x + 22), int(rect.y + 12), max(15, font_size - 3), TEXT_DIM)

    content_y = int(rect.y + 38)
    for text, color in lines:
        label_color = TEXT_DIM if color == colors.WHITE else color
        if ":" in text:
            label, value = text.split(":", 1)
            pyray.draw_text(f"{label}:", int(rect.x + 22), content_y, font_size, label_color)
            label_width = pyray.measure_text(f"{label}:", font_size)
            pyray.draw_text(value.strip(), int(rect.x + 22 + label_width + 8), content_y, font_size, color)
        else:
            pyray.draw_text(text, int(rect.x + 22), content_y, font_size, color)
        content_y += line_height


def draw_game_hud(
    ctx,
    seeds_left: int,
    cherry_status: tuple[bool, int] | None = None,
    ghost_release_status: tuple[int, int] | None = None,
    ghost_return_status: tuple[int, int] | None = None,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    font_size: int,
    line_height: int,
    columns: int,
) -> None:
    rage_active = bool(getattr(ctx.pacman, "rage", False))
    difficulty_color = (
        colors.GREEN if ctx.difficulty == "Easy"
        else colors.RED if ctx.difficulty == "Hard"
        else colors.YELLOW
    )
    ghost_color = colors.SKYBLUE if ctx.ghost_mode == "scatter" else colors.RED

    cherry_text = None
    cherry_color = colors.WHITE
    if cherry_status is not None:
        cherry_ready, cherry_value = cherry_status
        if cherry_ready:
            cherry_text = "Cherry: READY"
            if cherry_value > 1:
                cherry_text = f"Cherry: READY x{cherry_value}"
            cherry_color = colors.GOLD

    core_lines = [
        (f"Score: {ctx.score}", colors.WHITE),
        (f"High score: {ctx.high_score}", colors.WHITE),
        (f"Lives: {ctx.lives}", colors.WHITE),
        (f"Level: {ctx.current_level}", colors.SKYBLUE),
    ]

    field_lines = [(f"Seeds: {seeds_left}", colors.WHITE)]
    if ctx.game_mode != "Arcade":
        field_lines.append((f"Mode: {ctx.mode_label().upper()}", difficulty_color))
    map_trait = ctx.current_map_trait()
    field_lines.append((f"District: {map_trait.title}", map_trait.accent))
    if getattr(ctx, "pressure_stage", 0) > 0 or ctx.ghost_mode != "chase":
        field_lines.append((f"Ghosts: {ctx.ghost_mode.upper()}", ghost_color))

    bonus_lines: list[tuple[str, object]] = []
    directive = ctx.current_run_directive()
    directive_line = f"{directive.title}: {ctx.directive_progress_text()}"
    bonus_lines.append((directive_line, directive.accent))

    if cherry_text is not None:
        bonus_lines.append((cherry_text, cherry_color))

    if ghost_release_status is not None:
        pending_ghosts, total_ghosts = ghost_release_status
        release_text = f"Deploying: {pending_ghosts}/{total_ghosts}"
        bonus_lines.insert(0, (release_text, colors.LIGHTGRAY))

    if ghost_return_status is not None:
        returning_ghosts, total_ghosts = ghost_return_status
        return_text = f"Returning: {returning_ghosts}/{total_ghosts}"
        bonus_lines.insert(0, (return_text, colors.WHITE))

    if rage_active:
        bonus_lines.append(("Rage: ON", colors.YELLOW))
        bonus_lines.append((f"Combo: x{ctx.ghost_combo + 1}", colors.GOLD))

        rage_timer = getattr(ctx.pacman, "rage_timer", 0)
        if 0 < rage_timer <= Ghost.FRIGHTENED_BLINK_TICKS:
            bonus_lines.append(("Rage ending soon!", colors.ORANGE))

    sections = [("RUN STATUS", core_lines, LIVE_CYAN), ("FIELD STATUS", field_lines, LIVE_PINK)]
    if bonus_lines:
        sections.append(("LIVE BONUS", bonus_lines, LIVE_GOLD))

    theme_name = getattr(ctx, "theme_name", lambda: "Neon District")()
    if theme_name == "Amber Rain":
        sections = [
            ("RUN STATUS", core_lines, LIVE_GOLD),
            ("FIELD STATUS", field_lines, LIVE_PINK),
        ] + ([("LIVE BONUS", bonus_lines, LIVE_CYAN)] if bonus_lines else [])
    elif theme_name == "Ice Circuit":
        sections = [
            ("RUN STATUS", core_lines, LIVE_CYAN),
            ("FIELD STATUS", field_lines, colors.SKYBLUE),
        ] + ([("LIVE BONUS", bonus_lines, LIVE_GOLD)] if bonus_lines else [])
    elif theme_name == "Velvet Alley":
        sections = [
            ("RUN STATUS", core_lines, LIVE_PINK),
            ("FIELD STATUS", field_lines, LIVE_GOLD),
        ] + ([("LIVE BONUS", bonus_lines, LIVE_CYAN)] if bonus_lines else [])

    gap = 14
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
