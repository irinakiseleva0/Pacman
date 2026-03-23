from __future__ import annotations

import math

import pyray
from raylib import colors

from entities.ghost import Ghost


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
    rage_text = "ON" if getattr(ctx.pacman, "rage", False) else "OFF"
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
        else:
            cherry_text = f"Cherry: {cherry_value}"
            cherry_color = colors.GRAY

    lines = [
        (f"Score: {ctx.score}", colors.WHITE),
        (f"Lives: {ctx.lives}", colors.WHITE),
        (f"Level: {ctx.current_level}", colors.SKYBLUE),
        (f"Rage: {rage_text}", colors.YELLOW if rage_text == "ON" else colors.GRAY),
        (f"Seeds left: {seeds_left}", colors.WHITE),
        (f"Ghosts: {ctx.ghost_mode.upper()}", ghost_color),
        (f"Mode: {ctx.difficulty.upper()}", difficulty_color),
        (f"High score: {ctx.high_score}", colors.WHITE),
    ]

    if cherry_text is not None:
        lines.insert(5, (cherry_text, cherry_color))
        lines.insert(6, (f"Cherry score: {ctx.effective_cherry_score()}", colors.GOLD))

    if ghost_release_status is not None:
        pending_ghosts, total_ghosts = ghost_release_status
        release_text = f"Ghosts deploying: {pending_ghosts}/{total_ghosts}"
        lines.insert(5, (release_text, colors.LIGHTGRAY))

    if ghost_return_status is not None:
        returning_ghosts, total_ghosts = ghost_return_status
        return_text = f"Ghosts returning: {returning_ghosts}/{total_ghosts}"
        lines.insert(5, (return_text, colors.WHITE))

    if rage_text == "ON":
        next_combo_score = ctx.next_ghost_combo_score()
        combo_label = f"Ghost combo: x{ctx.ghost_combo + 1} ({next_combo_score})"
        lines.insert(5, (combo_label, colors.GOLD))
        lines.insert(6, (f"Large seed: {ctx.effective_large_seed_score()}", colors.MAGENTA))

        rage_timer = getattr(ctx.pacman, "rage_timer", 0)
        if 0 < rage_timer <= Ghost.FRIGHTENED_BLINK_TICKS:
            lines.insert(7, ("Rage ending soon!", colors.ORANGE))

    title = "RUN STATUS"
    title_size = font_size + 6
    title_width = pyray.measure_text(title, title_size)
    title_x = int(x + (width - title_width) / 2)
    pyray.draw_text(title, title_x, y, title_size, colors.YELLOW)

    content_y = y + title_size + 14
    column_count = max(1, columns)
    column_width = max(1, width // column_count)
    rows_per_column = max(1, math.ceil(len(lines) / column_count))

    for index, (text, color) in enumerate(lines):
        column = min(column_count - 1, index // rows_per_column)
        row = index % rows_per_column
        draw_x = x + column * column_width
        draw_y = content_y + row * line_height
        if draw_y + font_size > y + height:
            break
        pyray.draw_text(text, draw_x, draw_y, font_size, color)
