from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from entities.ghost import Ghost
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK, TEXT_DIM, draw_glass_card
from utils.visual_effects import with_alpha


def _card_height(line_count: int, line_height: int) -> int:
    return 28 + max(1, line_count) * line_height + 18


def _draw_card(title: str, lines: list[tuple[str, object]], rect, font_size: int, line_height: int, accent_color) -> None:
    draw_glass_card(rect, accent_color=accent_color, glow_alpha=10, fill_alpha=132)
    pyray.draw_text(title, int(rect.x + 18), int(rect.y + 8), max(12, font_size - 10), TEXT_DIM)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 18, rect.y + 24, max(42, rect.width * 0.18), 2),
        with_alpha(accent_color, 152),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + rect.width - 28, rect.y + 12, 10, 2),
        with_alpha(accent_color, 72),
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
            pyray.draw_text(f"{label}:", int(rect.x + 22), content_y + 1, label_size, label_color)
            label_width = pyray.measure_text(f"{label}:", label_size)
            pyray.draw_text(value.strip(), int(rect.x + 22 + label_width + 10), content_y - 1, value_size, color)
        else:
            draw_size = max(14, font_size + 2)
            pyray.draw_text(text, int(rect.x + 22), content_y, draw_size, color)
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
    hud_pack = getattr(ctx, "hud_pack_name", lambda: "Standard")()
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
        (f"Lives: {ctx.lives}", colors.WHITE),
        (f"Level: {ctx.current_level}", colors.SKYBLUE),
    ]
    if ctx.game_mode == "Time Attack":
        seconds_left = max(0, math.ceil(ctx.time_attack_seconds))
        timer_color = colors.ORANGE if ctx.time_attack_warning_active() else LIVE_GOLD
        core_lines.insert(1, (f"Time: {seconds_left}", timer_color))
    elif ctx.high_score > 0:
        core_lines.append((f"Best: {ctx.high_score}", TEXT_DIM))

    map_trait = ctx.current_map_trait()
    field_lines = [(f"Seeds: {seeds_left}", colors.WHITE)]
    field_lines.append((map_trait.title, map_trait.accent))
    if ctx.game_mode == "Endless":
        tier = ctx.endless_tier()
        field_lines.append((f"Tier: {tier.title}", tier.accent))
    elif ctx.game_mode == "Time Attack":
        field_lines.append(("Clock pressure live", colors.ORANGE))
    elif ctx.game_mode != "Arcade":
        field_lines.append((ctx.mode_label().upper(), difficulty_color))
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
        if ctx.power_chain_level > 1:
            bonus_lines.append((f"Chain: {ctx.power_chain_level}", colors.WHITE))

        rage_timer = getattr(ctx.pacman, "rage_timer", 0)
        if 0 < rage_timer <= Ghost.FRIGHTENED_BLINK_TICKS:
            bonus_lines.append(("Rage ending soon!", colors.ORANGE))
    elif ctx.power_chain_window > 0:
        bonus_lines.append((f"Chain window: {ctx.power_chain_window}", colors.GOLD))

    if ctx.route_chain_active():
        bonus_lines.append((f"Route: x{ctx.route_chain_count}", ctx.effect_palette()["dot"]))

    sections = [("RUN", core_lines, LIVE_CYAN), ("DISTRICT", field_lines, LIVE_PINK)]
    if bonus_lines:
        sections.append(("LIVE SIGNAL", bonus_lines, LIVE_GOLD))

    if hud_pack == "Relay Grid":
        sections = [("ROUTE FEED", core_lines, LIVE_CYAN), ("DISTRICT FEED", field_lines, LIVE_GOLD)] + ([("LIVE SIGNAL", bonus_lines, LIVE_PINK)] if bonus_lines else [])
    elif hud_pack == "Hunter Scope":
        sections = [("HUNTER SCOPE", core_lines, LIVE_PINK), ("THREAT READOUT", field_lines, colors.RED)] + ([("TACTICAL SIGNAL", bonus_lines, LIVE_GOLD)] if bonus_lines else [])
    elif hud_pack == "Chrome Vector":
        sections = [("VECTOR RUN", core_lines, colors.WHITE), ("FIELD VECTOR", field_lines, LIVE_CYAN)] + ([("LIVE SIGNAL", bonus_lines, LIVE_GOLD)] if bonus_lines else [])

    theme_name = getattr(ctx, "theme_name", lambda: "Neon District")()
    if theme_name == "Amber Rain":
        sections = [
            ("RUN", core_lines, LIVE_GOLD),
            ("DISTRICT", field_lines, LIVE_PINK),
        ] + ([("LIVE SIGNAL", bonus_lines, LIVE_CYAN)] if bonus_lines else [])
    elif theme_name == "Ice Circuit":
        sections = [
            ("RUN", core_lines, LIVE_CYAN),
            ("DISTRICT", field_lines, colors.SKYBLUE),
        ] + ([("LIVE SIGNAL", bonus_lines, LIVE_GOLD)] if bonus_lines else [])
    elif theme_name == "Velvet Alley":
        sections = [
            ("RUN", core_lines, LIVE_PINK),
            ("DISTRICT", field_lines, LIVE_GOLD),
        ] + ([("LIVE SIGNAL", bonus_lines, LIVE_CYAN)] if bonus_lines else [])

    gap = 10
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
