from __future__ import annotations

import pyray
from raylib import colors


def draw_game_hud(ctx, seeds_left: int) -> None:
    rage_text = "ON" if getattr(ctx.pacman, "rage", False) else "OFF"
    difficulty_color = (
        colors.GREEN if ctx.difficulty == "Easy"
        else colors.RED if ctx.difficulty == "Hard"
        else colors.YELLOW
    )
    ghost_color = colors.SKYBLUE if ctx.ghost_mode == "scatter" else colors.RED

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

    x = 10
    y = 10
    line_height = 24
    for text, color in lines:
        pyray.draw_text(text, x, y, 20, color)
        y += line_height
