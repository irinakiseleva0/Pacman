from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.gameplay_view_models import build_hud_model
from ui.hud import draw_ability_slots, draw_game_hud
from ui.mobile_controls import draw_mobile_controls
from ui.ui import (
    LIVE_CYAN,
    LIVE_GOLD,
    LIVE_PINK,
    PANEL_ACCENT,
    TEXT_DIM,
    draw_button,
    draw_glass_card,
    draw_live_panel_accent,
    draw_panel,
    draw_text_centered,
)
from utils.visual_effects import with_alpha


def draw_hud(game_scene) -> None:
    runtime = game_scene.ctx.runtime
    run = game_scene.ctx.run
    game_map = runtime.game_map
    if game_map is None:
        return

    game_scene.btn_pause = None
    game_scene.btn_menu = None
    game_scene.btn_end_run = None
    game_scene.btn_exit = None

    cfg = game_scene.ctx.cfg
    compact_height = 300
    if cfg.layout_name == "mobile":
        compact_height = cfg.hud_height
    elif run.game_mode == "Time Attack":
        compact_height = 320
    elif getattr(runtime.pacman, "rage", False) or run.power_chain_window > 0:
        compact_height = 314

    panel_height = min(cfg.hud_height, compact_height)
    ambient_rect = pyray.Rectangle(cfg.hud_x, cfg.hud_y, cfg.hud_width, panel_height)
    hud_rect = pyray.Rectangle(cfg.hud_x + 16, cfg.hud_y + 14, cfg.hud_width - 24, panel_height - 28)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(ambient_rect.x - 20, ambient_rect.y - 16, ambient_rect.width + 32, ambient_rect.height + 28),
        with_alpha(colors.BLACK, 54),
    )
    draw_live_panel_accent(hud_rect, game_scene.visual_time)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(ambient_rect.x - 10, ambient_rect.y, 2, ambient_rect.height),
        with_alpha(PANEL_ACCENT, 38),
    )
    draw_panel(hud_rect)

    if cfg.hud_mode == "side":
        pyray.draw_rectangle_rec(
            pyray.Rectangle(cfg.hud_x - 2, hud_rect.y - 10, 2, hud_rect.height + 20),
            with_alpha(PANEL_ACCENT, 56),
        )
        pyray.draw_rectangle_rec(
            pyray.Rectangle(cfg.hud_x - 10, hud_rect.y - 10, 1, hud_rect.height + 20),
            with_alpha(game_scene.ctx.effect_palette()["ghost"], 24),
        )
    else:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, cfg.hud_y - 3, cfg.window_width, 3),
            PANEL_ACCENT,
        )

    hud_x = int(hud_rect.x + 14)
    hud_y = int(hud_rect.y + 36) if cfg.hud_mode == "side" else int(hud_rect.y + 38)
    hud_width = int(hud_rect.width - 28)
    hud_columns = cfg.hud_columns

    if cfg.layout_name == "mobile":
        controls_width = min(220, max(180, cfg.hud_width // 2))
        hud_width = max(150, cfg.hud_width - controls_width - 28)
        hud_columns = 1

    hud_model = build_hud_model(game_scene.ctx, game_map)
    draw_game_hud(
        hud_model,
        x=hud_x,
        y=hud_y,
        width=hud_width,
        height=max(120, int(hud_rect.height - (hud_y - hud_rect.y) - 18)),
        font_size=max(18, cfg.hud_font_size - 3),
        line_height=max(24, cfg.hud_line_height - 6),
        columns=hud_columns,
    )

    _draw_control_dock(game_scene, hud_rect)
    draw_mobile_controls(game_scene.ctx)


def _draw_control_dock(game_scene, hud_rect) -> None:
    cfg = game_scene.ctx.cfg
    dock_h = 172
    dock_y = int(cfg.window_height - dock_h - 34)
    if dock_h < 104:
        return

    dock_rect = pyray.Rectangle(hud_rect.x, dock_y, hud_rect.width, dock_h)
    center_x = int(dock_rect.x + dock_rect.width / 2)

    draw_glass_card(dock_rect, accent_color=LIVE_PINK, glow_alpha=12, fill_alpha=138, time_s=game_scene.visual_time)
    draw_text_centered("CONTROL", center_x, int(dock_rect.y + 8), 15, LIVE_CYAN)
    draw_text_centered("P = PAUSE  |  ESC = MENU", center_x, int(dock_rect.y + 24), 11, TEXT_DIM)
    draw_ability_slots(
        game_scene.ctx,
        x=int(dock_rect.x + 10),
        y=int(dock_rect.y + 40),
        width=int(dock_rect.width - 20),
        time_s=game_scene.visual_time,
    )

    gap_x = 10
    gap_y = 8
    inner_x = int(dock_rect.x + 10)
    inner_w = int(dock_rect.width - 20)
    btn_w = int((inner_w - gap_x) / 2)
    btn_h = 34
    left_x = inner_x
    right_x = inner_x + btn_w + gap_x
    row1_y = int(dock_rect.y + 86)
    row2_y = row1_y + btn_h + gap_y

    game_scene.btn_pause = pyray.Rectangle(left_x, row1_y, btn_w, btn_h)
    game_scene.btn_menu = pyray.Rectangle(right_x, row1_y, btn_w, btn_h)
    game_scene.btn_end_run = pyray.Rectangle(left_x, row2_y, btn_w, btn_h)
    game_scene.btn_exit = pyray.Rectangle(right_x, row2_y, btn_w, btn_h)

    draw_button(game_scene.btn_pause, "PAUSE", time_s=game_scene.visual_time)
    draw_button(game_scene.btn_menu, "MENU", time_s=game_scene.visual_time)
    draw_button(game_scene.btn_end_run, "END RUN", time_s=game_scene.visual_time)
    draw_button(game_scene.btn_exit, "EXIT", time_s=game_scene.visual_time)

    draw_text_centered("END RUN = report  |  EXIT = close game", center_x, int(dock_rect.y + dock_rect.height - 12), 10, LIVE_GOLD)
