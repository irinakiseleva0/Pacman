from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from ui.ui import (
    LIVE_CYAN,
    LIVE_GOLD,
    LIVE_PINK,
    draw_live_board_backdrop as ui_draw_live_board_backdrop,
    draw_live_game_background as ui_draw_live_game_background,
)
from utils.visual_effects import with_alpha


def draw_live_game_background(game_scene, width: int, height: int, time_s: float) -> None:
    ui_draw_live_game_background(width, height, time_s)
    map_number = game_scene.ctx.current_map_number()
    trait = game_scene.ctx.current_map_trait()
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.1)

    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, width, int(height * 0.62)),
        with_alpha(colors.BLACK, 22),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, int(height * 0.62), width, int(height * 0.38)),
        with_alpha(colors.BLACK, 10),
    )

    if map_number == 1:
        for index in range(6):
            y = int(height * 0.18) + index * 54
            pyray.draw_rectangle_rec(
                pyray.Rectangle(int(width * 0.58), y, int(width * 0.26), 3),
                with_alpha(trait.accent, int(10 + pulse * 12)),
            )
    elif map_number == 2:
        for index in range(4):
            x = int(width * (0.10 + index * 0.18))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, 0, 18, height),
                with_alpha(trait.accent, 8 + index * 2),
            )
    elif map_number == 3:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, 0, width, height),
            with_alpha((10, 6, 24, 255), 24),
        )
        for index in range(3):
            cx = int(width * (0.18 + index * 0.28))
            pyray.draw_circle(cx, int(height * 0.34), 120 + index * 24, with_alpha(trait.accent, 6))
    elif map_number == 4:
        for index in range(5):
            x = int(width * 0.12) + index * 96
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, int(height * 0.16), 26, int(height * 0.30)),
                with_alpha(trait.accent, 9 + index * 2),
            )
    elif map_number == 5:
        for index in range(5):
            y = int(height * 0.12) + index * 72
            pyray.draw_rectangle_rec(
                pyray.Rectangle(0, y, width, 10),
                with_alpha(trait.accent, 7 + index * 2),
            )


def draw_live_board_backdrop(game_scene, rect, time_s: float) -> None:
    ui_draw_live_board_backdrop(rect, time_s)
    map_number = game_scene.ctx.current_map_number()
    trait = game_scene.ctx.current_map_trait()
    pulse = 0.5 + 0.5 * math.sin(time_s * 3.2)

    shimmer_x = int(rect.x + 20 + (math.sin(time_s * 1.1) * 0.5 + 0.5) * max(1, rect.width - 60))
    pyray.draw_rectangle_rec(
        pyray.Rectangle(shimmer_x, rect.y - 6, 18, rect.height + 12),
        with_alpha(colors.WHITE, int(4 + pulse * 6)),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 8, rect.y - 8, rect.width + 16, rect.height + 16),
        with_alpha(trait.accent, int(3 + pulse * 4)),
    )

    route_alpha = int(8 + pulse * 8)

    if map_number == 1:
        for index in range(4):
            x = rect.x + 42 + index * max(56, int(rect.width / 5))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, rect.y - 12, 2, rect.height + 24),
                with_alpha(trait.accent, int(14 + pulse * 10)),
            )
        for index in range(2):
            y = int(rect.y + rect.height * (0.28 + index * 0.36))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x + 28, y, rect.width - 56, 2),
                with_alpha(LIVE_CYAN, route_alpha),
            )
    elif map_number == 2:
        for index in range(3):
            y = rect.y + 28 + index * max(64, int(rect.height / 4))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x - 16, y, rect.width + 32, 3),
                with_alpha(trait.accent, int(14 + pulse * 14)),
            )
        for index in range(2):
            x = int(rect.x + rect.width * (0.24 + index * 0.42))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, rect.y + 24, 2, rect.height - 48),
                with_alpha(LIVE_PINK, route_alpha + 4),
            )
    elif map_number == 3:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x - 18, rect.y - 18, rect.width + 36, rect.height + 36),
            with_alpha((12, 8, 28, 255), 16),
        )
        diag_x = int(rect.x + rect.width * (0.18 + (math.sin(time_s * 0.9) * 0.5 + 0.5) * 0.44))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(diag_x, rect.y + 18, 2, rect.height - 36),
            with_alpha(trait.accent, route_alpha + 2),
        )
    elif map_number == 4:
        for cx in (rect.x + 18, rect.x + rect.width - 18):
            pyray.draw_circle(int(cx), int(rect.y + rect.height * 0.43), 26, with_alpha(trait.accent, int(16 + pulse * 12)))
            pyray.draw_circle(int(cx), int(rect.y + rect.height * 0.57), 26, with_alpha(trait.accent, int(16 + pulse * 12)))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x + 24, int(rect.y + rect.height * 0.50), rect.width - 48, 2),
            with_alpha(LIVE_GOLD, route_alpha + 6),
        )
    elif map_number == 5:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x - 10, rect.y + rect.height - 44, rect.width + 20, 30),
            with_alpha(trait.accent, int(14 + pulse * 12)),
        )
        for index in range(3):
            y = int(rect.y + rect.height * (0.22 + index * 0.24))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x + 18, y, rect.width - 36, 2),
                with_alpha(LIVE_PINK, route_alpha + index * 2),
            )


def draw_pressure_overlay(game_scene, board_rect) -> None:
    pressure_stage = getattr(game_scene.ctx, "pressure_stage", 0)
    runtime = game_scene.ctx.runtime
    game_map = runtime.game_map
    if pressure_stage <= 0 or game_scene.transition is not None or game_map is None:
        return

    pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * (4.5 + pressure_stage * 1.2))
    base_color = game_scene.ctx.effect_palette()["ghost"]
    if pressure_stage >= 3:
        base_color = colors.RED

    remaining = max(0, game_map.remaining_pickups())
    total = max(1, getattr(game_map, "total_pickups", 1))
    scarcity = 1.0 - (remaining / total)
    shift_alpha = int((12 + pressure_stage * 8) * scarcity + pulse * 12)
    heat_color = colors.ORANGE if scarcity >= 0.8 else colors.RED if pressure_stage >= 3 else base_color

    pyray.draw_rectangle_rec(board_rect, with_alpha(base_color, shift_alpha))
    if scarcity >= 0.7:
        pyray.draw_rectangle_rec(
            board_rect,
            with_alpha(heat_color, int(6 + scarcity * 18 + pulse * 6)),
        )

    glow_pad = 18 + pressure_stage * 6
    glow_alpha = int(34 + pressure_stage * 14 + pulse * 26 + scarcity * 22)
    inner_alpha = int(10 + pressure_stage * 6 + pulse * 12 + scarcity * 12)

    pyray.draw_rectangle_rec(
        pyray.Rectangle(
            board_rect.x - glow_pad,
            board_rect.y - glow_pad,
            board_rect.width + glow_pad * 2,
            board_rect.height + glow_pad * 2,
        ),
        with_alpha(base_color, glow_alpha),
    )
    if pressure_stage >= 2:
        outer_pad = glow_pad + 14
        pyray.draw_rectangle_rec(
            pyray.Rectangle(
                board_rect.x - outer_pad,
                board_rect.y - outer_pad,
                board_rect.width + outer_pad * 2,
                board_rect.height + outer_pad * 2,
            ),
            with_alpha(base_color, int(glow_alpha * 0.55)),
        )

    line_thickness = 3 if pressure_stage >= 2 else 2
    pyray.draw_rectangle_lines_ex(
        pyray.Rectangle(
            board_rect.x - 6,
            board_rect.y - 6,
            board_rect.width + 12,
            board_rect.height + 12,
        ),
        line_thickness,
        with_alpha(base_color, 80 + glow_alpha // 2),
    )

    if pressure_stage >= 2:
        for index in range(4):
            band_y = board_rect.y + 22 + index * max(42, int(board_rect.height / 5))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(board_rect.x - 10, band_y, board_rect.width + 20, 2),
                with_alpha(base_color, inner_alpha - index * 2),
            )

        floor_reflect_h = max(40, int(board_rect.height * 0.18))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(board_rect.x + 12, board_rect.y + board_rect.height - floor_reflect_h, board_rect.width - 24, floor_reflect_h),
            with_alpha(base_color, int(10 + scarcity * 14 + pulse * 6)),
        )

    if scarcity >= 0.6:
        top_bar_alpha = int(10 + scarcity * 28 + pulse * 8)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(board_rect.x, board_rect.y - 4, board_rect.width, 4),
            with_alpha(heat_color, top_bar_alpha),
        )
        pyray.draw_rectangle_rec(
            pyray.Rectangle(board_rect.x, board_rect.y + board_rect.height, board_rect.width, 4),
            with_alpha(heat_color, max(0, top_bar_alpha - 6)),
        )
        pulse_pad = 10 + int(scarcity * 12)
        pulse_alpha = int(8 + scarcity * 22 + pulse * 12)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(
                board_rect.x - pulse_pad,
                board_rect.y - pulse_pad,
                board_rect.width + pulse_pad * 2,
                board_rect.height + pulse_pad * 2,
            ),
            with_alpha(heat_color, pulse_alpha),
        )

    if game_scene.ctx.elite_pressure_active():
        scan_x = int(board_rect.x + (math.sin(game_scene.visual_time * 1.7) * 0.5 + 0.5) * max(1, board_rect.width - 36))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(scan_x, board_rect.y - 8, 20, board_rect.height + 16),
            with_alpha(base_color, int(18 + pulse * 20)),
        )
