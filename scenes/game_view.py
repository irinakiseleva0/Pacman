from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from core.gameplay_view_models import build_hud_model, build_live_feedback_model
from entities.ghost import Ghost
from ui.hud import draw_game_hud
from ui.mobile_controls import draw_mobile_controls
from ui.ui import (
    LIVE_CYAN,
    LIVE_PINK,
    PANEL_ACCENT,
    TEXT_DIM,
    draw_glass_card,
    draw_live_board_backdrop as ui_draw_live_board_backdrop,
    draw_live_game_background as ui_draw_live_game_background,
    draw_live_panel_accent,
    draw_panel,
    draw_presentation_bars,
    draw_shadowed_text_centered,
    draw_text_centered,
)
from utils.visual_effects import with_alpha


def draw_scene(game_scene) -> None:
    runtime = game_scene.ctx.runtime
    visual = game_scene.ctx.visual
    game_map = runtime.game_map
    if game_map is None:
        return
    cfg = game_scene.ctx.cfg

    shake_x, shake_y = visual.screen_shake.get_offset()
    board_rect = pyray.Rectangle(cfg.board_offset_x, cfg.board_offset_y, cfg.board_width, cfg.board_height)

    draw_live_game_background(game_scene, cfg.window_width, cfg.window_height, game_scene.visual_time)
    draw_live_board_backdrop(game_scene, board_rect, game_scene.visual_time)
    draw_pressure_overlay(game_scene, board_rect)

    game_map.draw()

    effect_scale = cfg.tile_size / 16
    visual.light_bursts.draw(cfg.board_offset_x + shake_x, cfg.board_offset_y + shake_y, effect_scale)
    visual.particles.draw(cfg.board_offset_x + shake_x, cfg.board_offset_y + shake_y, effect_scale)
    visual.floating_text.draw(cfg.board_offset_x + shake_x, cfg.board_offset_y + shake_y, effect_scale)

    if not game_scene.ctx.capture_mode_enabled():
        draw_hud(game_scene)

    if game_scene.transition is None and not game_scene.ctx.capture_mode_enabled():
        draw_live_feedback(game_scene)

    if game_scene.transition is not None and game_scene.transition.kind == "ready":
        draw_ready_overlay(game_scene)
    elif game_scene.transition is not None and game_scene.transition.kind == "death":
        draw_death_overlay(game_scene)
    elif game_scene.transition is not None and game_scene.transition.kind == "level_complete":
        draw_level_complete_overlay(game_scene)

    if game_scene.tutorial_stage > 0 and not game_scene.ctx.capture_mode_enabled():
        draw_tutorial_overlay(game_scene)

    visual.screen_flash.draw()
    draw_presentation_bars(cfg.window_width, cfg.window_height)


def draw_live_game_background(game_scene, width: int, height: int, time_s: float) -> None:
    ui_draw_live_game_background(width, height, time_s)
    map_number = game_scene.ctx.current_map_number()
    trait = game_scene.ctx.current_map_trait()
    pulse = 0.5 + 0.5 * math.sin(time_s * 2.1)

    if map_number == 1:
        # Transit Grid: longer speed streaks and route lanes.
        for index in range(6):
            y = int(height * 0.18) + index * 54
            pyray.draw_rectangle_rec(
                pyray.Rectangle(int(width * 0.58), y, int(width * 0.26), 3),
                with_alpha(trait.accent, int(10 + pulse * 12)),
            )
    elif map_number == 2:
        # Pressure Lanes: narrowing red tension columns.
        for index in range(4):
            x = int(width * (0.10 + index * 0.18))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, 0, 18, height),
                with_alpha(trait.accent, 8 + index * 2),
            )
    elif map_number == 3:
        # Black Channel: darker flank scene with cold side haze.
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, 0, width, height),
            with_alpha((10, 6, 24, 255), 24),
        )
        for index in range(3):
            cx = int(width * (0.18 + index * 0.28))
            pyray.draw_circle(cx, int(height * 0.34), 120 + index * 24, with_alpha(trait.accent, 6))
    elif map_number == 4:
        # Market Loop: warmer bonus scene with side beacons around teleport play.
        for index in range(5):
            x = int(width * 0.12) + index * 96
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, int(height * 0.16), 26, int(height * 0.30)),
                with_alpha(trait.accent, 9 + index * 2),
            )
    elif map_number == 5:
        # Credit Spiral: collapse scene with magenta overrun bands.
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

    if map_number == 1:
        for index in range(4):
            x = rect.x + 42 + index * max(56, int(rect.width / 5))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(x, rect.y - 12, 2, rect.height + 24),
                with_alpha(trait.accent, int(14 + pulse * 10)),
            )
    elif map_number == 2:
        for index in range(3):
            y = rect.y + 28 + index * max(64, int(rect.height / 4))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x - 16, y, rect.width + 32, 3),
                with_alpha(trait.accent, int(14 + pulse * 14)),
            )
    elif map_number == 3:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x - 18, rect.y - 18, rect.width + 36, rect.height + 36),
            with_alpha((12, 8, 28, 255), 16),
        )
    elif map_number == 4:
        # Telegraph teleport risk with side exit halos.
        for cx in (rect.x + 18, rect.x + rect.width - 18):
            pyray.draw_circle(int(cx), int(rect.y + rect.height * 0.43), 26, with_alpha(trait.accent, int(16 + pulse * 12)))
            pyray.draw_circle(int(cx), int(rect.y + rect.height * 0.57), 26, with_alpha(trait.accent, int(16 + pulse * 12)))
    elif map_number == 5:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(rect.x - 10, rect.y + rect.height - 44, rect.width + 20, 30),
            with_alpha(trait.accent, int(14 + pulse * 12)),
        )


def draw_hud(game_scene) -> None:
    runtime = game_scene.ctx.runtime
    run = game_scene.ctx.run
    game_map = runtime.game_map
    if game_map is None:
        return

    cfg = game_scene.ctx.cfg
    compact_height = 408
    if cfg.layout_name == "mobile":
        compact_height = cfg.hud_height
    elif run.game_mode == "Time Attack":
        compact_height = 430
    elif getattr(runtime.pacman, "rage", False) or run.power_chain_window > 0:
        compact_height = 438

    panel_height = min(cfg.hud_height, compact_height)
    ambient_rect = pyray.Rectangle(cfg.hud_x, cfg.hud_y, cfg.hud_width, panel_height)
    hud_rect = pyray.Rectangle(cfg.hud_x + 16, cfg.hud_y + 14, cfg.hud_width - 24, panel_height - 28)
    draw_live_panel_accent(hud_rect, game_scene.visual_time)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(ambient_rect.x - 10, ambient_rect.y, 2, ambient_rect.height),
        with_alpha(PANEL_ACCENT, 38),
    )
    draw_panel(hud_rect)
    _draw_hud_terminal_backdrop(game_scene, hud_rect)

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

    draw_mobile_controls(game_scene.ctx)


def _draw_hud_terminal_backdrop(game_scene, hud_rect) -> None:
    lower_zone = pyray.Rectangle(
        hud_rect.x + 14,
        hud_rect.y + hud_rect.height * 0.56,
        hud_rect.width - 28,
        hud_rect.height * 0.32,
    )
    if lower_zone.height <= 0:
        return

    pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 2.4)
    accent = game_scene.ctx.effect_palette()["ghost"]

    pyray.draw_rectangle_rec(
        lower_zone,
        with_alpha((10, 14, 28, 255), 108),
    )
    pyray.draw_rectangle_lines_ex(
        lower_zone,
        1,
        with_alpha(PANEL_ACCENT, 24),
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(lower_zone.x, lower_zone.y, lower_zone.width, max(0, lower_zone.height * 0.24)),
        with_alpha(colors.WHITE, 5),
    )

    line_count = 6
    line_gap = lower_zone.height / (line_count + 1)
    for index in range(line_count):
        y = lower_zone.y + (index + 1) * line_gap
        width = lower_zone.width * (0.82 - index * 0.08)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(lower_zone.x + 16, y, width, 1),
            with_alpha(PANEL_ACCENT, 20 if index < 2 else 14),
        )

    for index in range(4):
        x = lower_zone.x + lower_zone.width * (0.58 + index * 0.09)
        height = 24 + index * 10
        y = lower_zone.y + lower_zone.height - height - 18
        pyray.draw_rectangle_rec(
            pyray.Rectangle(x, y, 10 + index * 2, height),
            with_alpha(accent if index % 2 else PANEL_ACCENT, int(18 + pulse * 16)),
        )

    pyray.draw_rectangle_rec(
        pyray.Rectangle(lower_zone.x + 12, lower_zone.y + lower_zone.height - 18, lower_zone.width - 24, 1),
        with_alpha(LIVE_PINK, 20),
    )


def draw_live_feedback(game_scene) -> None:
    game_map = game_scene.ctx.runtime.game_map
    if game_map is None:
        return

    feedback = build_live_feedback_model(game_scene)
    palette = game_scene.ctx.effect_palette()
    pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 4.2)
    center_x = game_scene.ctx.cfg.window_width // 2
    top_y = 24

    pressure_stage = game_scene.ctx.run.pressure_stage
    rage_active = bool(getattr(game_scene.ctx.runtime.pacman, "rage", False))

    if feedback.pressure_card is not None:
        accent = feedback.pressure_card.accent
        width = feedback.pressure_card.width
        headline = feedback.pressure_card.headline
        detail = feedback.pressure_card.detail
        panel = pyray.Rectangle(center_x - width // 2, top_y, width, 54)
        draw_glass_card(panel, accent_color=accent, glow_alpha=int(12 + pulse * 16), fill_alpha=150)
        draw_text_centered(headline, center_x, int(panel.y + 10), 16, colors.WHITE)
        draw_text_centered(detail.upper(), center_x, int(panel.y + 30), 12, accent)

        if pressure_stage >= 2:
            edge_alpha = int(12 + pulse * 18)
            danger_color = colors.RED if pressure_stage >= 3 else accent
            pyray.draw_rectangle_rec(
                pyray.Rectangle(0, 0, game_scene.ctx.cfg.window_width, 8),
                with_alpha(danger_color, edge_alpha),
            )
            pyray.draw_rectangle_rec(
                pyray.Rectangle(0, game_scene.ctx.cfg.window_height - 8, game_scene.ctx.cfg.window_width, 8),
                with_alpha(danger_color, int(edge_alpha * 0.7)),
            )
            if pressure_stage >= 3:
                side_alpha = int(16 + pulse * 22)
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(0, 0, 12, game_scene.ctx.cfg.window_height),
                    with_alpha(danger_color, side_alpha),
                )
                pyray.draw_rectangle_rec(
                    pyray.Rectangle(game_scene.ctx.cfg.window_width - 12, 0, 12, game_scene.ctx.cfg.window_height),
                    with_alpha(danger_color, side_alpha),
                )

    if feedback.rage_card is not None:
        accent = feedback.rage_card.accent
        width = feedback.rage_card.width
        panel = pyray.Rectangle(center_x - width // 2, top_y + (66 if pressure_stage > 0 else 0), width, 54)
        fill_alpha = 162 if rage_active else 150
        glow_alpha = int(16 + pulse * 14) if rage_active else int(12 + pulse * 10)
        draw_glass_card(panel, accent_color=accent, glow_alpha=glow_alpha, fill_alpha=fill_alpha)
        draw_text_centered(feedback.rage_card.headline, center_x, int(panel.y + 10), 16, colors.WHITE)
        draw_text_centered(feedback.rage_card.detail.upper(), center_x, int(panel.y + 30), 12, colors.GOLD)

    if feedback.route_card is not None:
        route_width = feedback.route_card.width
        top_offset = 66 if pressure_stage > 0 else 0
        if feedback.rage_card is not None:
            top_offset += 66
        panel = pyray.Rectangle(center_x - route_width // 2, top_y + top_offset, route_width, 46)
        draw_glass_card(panel, accent_color=feedback.route_card.accent, glow_alpha=int(10 + pulse * 10), fill_alpha=142)
        draw_text_centered(feedback.route_card.headline, center_x, int(panel.y + 10), 15, colors.WHITE)
        draw_text_centered(feedback.route_card.detail, center_x, int(panel.y + 27), 11, palette["power"])

    if feedback.near_miss_card is not None:
        alert_pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 9.0)
        width = feedback.near_miss_card.width
        top_offset = 66 if pressure_stage > 0 else 0
        if feedback.rage_card is not None:
            top_offset += 66
        panel = pyray.Rectangle(center_x - width // 2, top_y + top_offset, width, 46)
        draw_glass_card(panel, accent_color=feedback.near_miss_card.accent, glow_alpha=int(10 + alert_pulse * 12), fill_alpha=146)
        draw_text_centered(feedback.near_miss_card.headline, center_x, int(panel.y + 10), 15, colors.WHITE)
        draw_text_centered(feedback.near_miss_card.detail, center_x, int(panel.y + 27), 11, palette["ghost"])

    if getattr(game_scene, "overtime_banner_timer", 0.0) > 0:
        overtime_alpha = min(1.0, game_scene.overtime_banner_timer / 1.35)
        panel = pyray.Rectangle(center_x - 158, top_y + 12, 316, 52)
        draw_glass_card(panel, accent_color=colors.ORANGE, glow_alpha=int(14 + overtime_alpha * 16), fill_alpha=156)
        draw_text_centered("OVERTIME", center_x, int(panel.y + 9), 16, colors.WHITE)
        draw_text_centered("CLOCK DANGER  |  NO SAFE RESET", center_x, int(panel.y + 28), 12, colors.ORANGE)


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
    shift_alpha = int((8 + pressure_stage * 6) * scarcity + pulse * 8)

    pyray.draw_rectangle_rec(
        board_rect,
        with_alpha(base_color, shift_alpha),
    )

    glow_pad = 18 + pressure_stage * 6
    glow_alpha = int(16 + pressure_stage * 8 + pulse * 18)
    inner_alpha = int(8 + pressure_stage * 5 + pulse * 10)

    pyray.draw_rectangle_rec(
        pyray.Rectangle(
            board_rect.x - glow_pad,
            board_rect.y - glow_pad,
            board_rect.width + glow_pad * 2,
            board_rect.height + glow_pad * 2,
        ),
        with_alpha(base_color, glow_alpha),
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

    if game_scene.ctx.elite_pressure_active():
        scan_x = int(board_rect.x + (math.sin(game_scene.visual_time * 1.7) * 0.5 + 0.5) * max(1, board_rect.width - 36))
        pyray.draw_rectangle_rec(
            pyray.Rectangle(scan_x, board_rect.y - 8, 20, board_rect.height + 16),
            with_alpha(base_color, int(18 + pulse * 20)),
        )


def draw_transition_card(game_scene, headline: str, detail: str, accent_color, *, width: int = 360) -> None:
    cfg = game_scene.ctx.cfg
    center_x = cfg.window_width // 2
    center_y = cfg.window_height // 2
    pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 4.0)
    card_h = 122 if detail else 92
    rect = pyray.Rectangle(center_x - width // 2, center_y - card_h // 2 - 8, width, card_h)
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x - 18, rect.y - 18, rect.width + 36, rect.height + 36),
        with_alpha(accent_color, int(18 + pulse * 18)),
    )
    draw_glass_card(rect, accent_color=accent_color, glow_alpha=20, fill_alpha=186)

    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 22, rect.y + 18, max(80, rect.width * 0.28), 2),
        accent_color,
    )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(rect.x + 22, rect.y + rect.height - 20, max(120, rect.width * 0.42), 2),
        with_alpha(accent_color, 96),
    )
    draw_shadowed_text_centered(headline, center_x, int(rect.y + 24), 30, accent_color)
    if detail:
        draw_text_centered(detail, center_x, int(rect.y + 66), 15, colors.WHITE)


def draw_ready_overlay(game_scene) -> None:
    directive = game_scene.ctx.current_run_directive()
    map_trait = game_scene.ctx.current_map_trait()
    scene_tag = game_scene.ctx.current_map_scene_tag()
    scene_brief = game_scene.ctx.current_map_scene_brief().upper()
    if game_scene.ctx.game_mode == "Arcade":
        chapter = game_scene.ctx.arcade_campaign_chapter()
        detail = f"{chapter.title}  |  {scene_tag}  |  {scene_brief}" if chapter is not None else f"{map_trait.title}  |  {scene_tag}  |  {scene_brief}"
        accent = chapter.accent if chapter is not None else map_trait.accent
    elif game_scene.ctx.game_mode == "Endless":
        tier = game_scene.ctx.endless_tier()
        detail = f"{tier.title}  |  {scene_tag}  |  {scene_brief}"
        accent = tier.accent
    elif game_scene.ctx.game_mode == "Time Attack":
        seconds_left = max(0, math.ceil(game_scene.ctx.time_attack_seconds))
        detail = f"T-{seconds_left:02d}  |  {scene_tag}  |  {scene_brief}"
        accent = colors.ORANGE
    else:
        detail = f"{map_trait.title}  |  {scene_tag}  |  {scene_brief}"
        accent = map_trait.accent
    draw_transition_card(game_scene, "DISTRICT LIVE", detail, accent, width=560)


def draw_death_overlay(game_scene) -> None:
    killer_map = {
        "Blinky": "BLINKY CUT THE ROUTE",
        "Pinky": "PINKY HELD THE FRONT",
        "Inky": "INKY SLIPPED THE FLANK",
        "Clyde": "CLYDE FLIPPED THE READ",
    }
    killer_line = killer_map.get(game_scene.ctx.run.last_killer_name, "DISTRICT CONTROL LOST")
    if game_scene.failure_reason == "timeout":
        draw_transition_card(
            game_scene,
            "TIME OUT",
            "CLOCK DRAINED  |  RUN FORCE-CLOSED",
            colors.ORANGE,
            width=380,
        )
    elif game_scene.transition is not None and game_scene.transition.result == "lose":
        draw_transition_card(
            game_scene,
            "GAME OVER",
            killer_line,
            game_scene.ctx.effect_palette()["death_flash"],
            width=380,
        )
    else:
        draw_transition_card(
            game_scene,
            "LIFE LOST",
            f"{killer_line}  |  SIGNAL RESTORE IN PROGRESS",
            game_scene.ctx.effect_palette()["death_flash"],
            width=520,
        )


def draw_level_complete_overlay(game_scene) -> None:
    transition_result = game_scene.transition.result if game_scene.transition is not None else ""
    if transition_result == "game_won":
        headline = "RUN CLEARED"
        headline_color = game_scene.ctx.effect_palette()["win_flash"]
        if game_scene.ctx.game_mode == "Arcade":
            detail = "CAMPAIGN DISTRICTS SECURED"
        elif game_scene.ctx.game_mode == "Time Attack":
            detail = "CLOCK ROUTE LOCKED IN"
        else:
            detail = "FINALIZING RESULTS"
    elif transition_result == "challenge_failed":
        headline = "TRIAL FAILED"
        headline_color = game_scene.ctx.effect_palette()["death_flash"]
        detail = "BOARD CLEARED  |  TARGET MISSED"
    else:
        headline = "LEVEL CLEAR"
        headline_color = game_scene.ctx.effect_palette()["win_flash"]
        if game_scene.ctx.game_mode == "Endless":
            detail = f"{game_scene.ctx.current_map_scene_tag()} SECURED  |  NEXT SURVIVAL WAVE"
        elif game_scene.ctx.game_mode == "Time Attack":
            detail = "DISTRICT CLOCK BANKED  |  NEXT BOARD ARMED"
        else:
            detail = f"{game_scene.ctx.current_map_scene_tag()} SECURED  |  SYNCING NEXT REPORT"

    draw_transition_card(game_scene, headline, detail, headline_color, width=420)


def draw_tutorial_overlay(game_scene) -> None:
    cfg = game_scene.ctx.cfg
    panel_w = min(520, cfg.window_width - 120)
    panel_h = 144
    panel = pyray.Rectangle(cfg.window_width // 2 - panel_w // 2, cfg.window_height - panel_h - 34, panel_w, panel_h)
    draw_glass_card(panel, accent_color=LIVE_CYAN, glow_alpha=14, fill_alpha=164)

    titles = {
        1: ("MOVE OUT", "Move with WASD or Arrow Keys"),
        2: ("CLEAR A LANE", "Eat dots to start the route"),
        3: ("TRIGGER RAGE", "Grab a power seed and flip the chase"),
        4: ("YOU'RE SET", "Start moving to continue"),
    }
    title, body = titles.get(game_scene.tutorial_stage, titles[4])
    step_label = f"STEP {game_scene._tutorial_progress_index()}/{game_scene._tutorial_step_total()}"

    draw_text_centered("FIRST RUN TRAINING", int(panel.x + panel.width / 2), int(panel.y + 14), 16, LIVE_CYAN)
    draw_shadowed_text_centered(title, int(panel.x + panel.width / 2), int(panel.y + 40), 24, colors.WHITE)
    draw_text_centered(body.upper(), int(panel.x + panel.width / 2), int(panel.y + 76), 14, LIVE_CYAN)
    draw_text_centered(step_label, int(panel.x + panel.width / 2), int(panel.y + 100), 12, TEXT_DIM)
    draw_text_centered("START MOVING TO CONTINUE", int(panel.x + panel.width / 2), int(panel.y + 118), 12, colors.WHITE)
