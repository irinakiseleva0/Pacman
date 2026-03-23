from __future__ import annotations

import pyray
from raylib import colors


def draw_game_hud(ctx, seeds_left: int, cherry_status: tuple[bool, int] | None = None) -> None:
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

    if rage_text == "ON":
        next_combo_score = ctx.next_ghost_combo_score()
        combo_label = f"Ghost combo: x{ctx.ghost_combo + 1} ({next_combo_score})"
        lines.insert(5, (combo_label, colors.GOLD))

    x = 10
    y = 10
    line_height = 24
    for text, color in lines:
        pyray.draw_text(text, x, y, 20, color)
        y += line_height
