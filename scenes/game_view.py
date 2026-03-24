from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from entities.ghost import Ghost
from ui.hud import draw_game_hud
from ui.mobile_controls import draw_mobile_controls
from ui.ui import (
    LIVE_CYAN,
    PANEL_ACCENT,
    TEXT_DIM,
    draw_glass_card,
    draw_live_board_backdrop,
    draw_live_game_background,
    draw_live_panel_accent,
    draw_panel,
    draw_presentation_bars,
    draw_shadowed_text_centered,
    draw_text_centered,
)
from utils.visual_effects import with_alpha


def draw_scene(game_scene) -> None:
    game_map = game_scene.ctx.game_map
    if game_map is None:
        return
    cfg = game_scene.ctx.cfg

    shake_x, shake_y = game_scene.ctx.screen_shake.get_offset()
    board_rect = pyray.Rectangle(cfg.board_offset_x, cfg.board_offset_y, cfg.board_width, cfg.board_height)

    draw_live_game_background(cfg.window_width, cfg.window_height, game_scene.visual_time)
    draw_live_board_backdrop(board_rect, game_scene.visual_time)
    draw_pressure_overlay(game_scene, board_rect)

    game_map.draw()

    effect_scale = cfg.tile_size / 16
    game_scene.ctx.particles.draw(cfg.board_offset_x + shake_x, cfg.board_offset_y + shake_y, effect_scale)
    game_scene.ctx.floating_text.draw(cfg.board_offset_x + shake_x, cfg.board_offset_y + shake_y, effect_scale)

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

    game_scene.ctx.screen_flash.draw()
    draw_presentation_bars(cfg.window_width, cfg.window_height)


def draw_hud(game_scene) -> None:
    game_map = game_scene.ctx.game_map
    if game_map is None:
        return

    cfg = game_scene.ctx.cfg
    hud_rect = pyray.Rectangle(cfg.hud_x, cfg.hud_y, cfg.hud_width, cfg.hud_height)
    draw_live_panel_accent(hud_rect, game_scene.visual_time)
    draw_panel(hud_rect)

    if cfg.hud_mode == "side":
        pyray.draw_rectangle_rec(
            pyray.Rectangle(cfg.hud_x - 4, 0, 2, cfg.window_height),
            with_alpha(PANEL_ACCENT, 110),
        )
        pyray.draw_rectangle_rec(
            pyray.Rectangle(cfg.hud_x - 12, 0, 1, cfg.window_height),
            with_alpha(game_scene.ctx.effect_palette()["ghost"], 44),
        )
    else:
        pyray.draw_rectangle_rec(
            pyray.Rectangle(0, cfg.hud_y - 3, cfg.window_width, 3),
            PANEL_ACCENT,
        )

    hud_x = cfg.hud_x + 18
    hud_y = 42 if cfg.hud_mode == "side" else cfg.hud_y + 42
    hud_width = cfg.hud_width - 36
    hud_columns = cfg.hud_columns

    if cfg.layout_name == "mobile":
        controls_width = min(220, max(180, cfg.hud_width // 2))
        hud_width = max(150, cfg.hud_width - controls_width - 28)
        hud_columns = 1

    draw_game_hud(
        game_scene.ctx,
        game_map.remaining_seeds(),
        game_map.cherry_status(),
        game_map.ghost_release_status(),
        game_map.ghost_return_status(),
        x=hud_x,
        y=hud_y,
        width=hud_width,
        height=cfg.hud_height - 56,
        font_size=cfg.hud_font_size,
        line_height=cfg.hud_line_height,
        columns=hud_columns,
    )

    draw_mobile_controls(game_scene.ctx)


def draw_live_feedback(game_scene) -> None:
    game_map = game_scene.ctx.game_map
    if game_map is None:
        return

    palette = game_scene.ctx.effect_palette()
    pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 4.2)
    center_x = game_scene.ctx.cfg.window_width // 2
    top_y = 24

    pressure_stage = getattr(game_scene.ctx, "pressure_stage", 0)
    rage_active = bool(getattr(game_scene.ctx.pacman, "rage", False))

    if pressure_stage > 0:
        widths = {1: 220, 2: 250, 3: 278}
        labels = {
            1: ("PRESSURE RISING", "ghost routes tightening"),
            2: ("DANGER WINDOW", "late-board pressure live"),
            3: ("OVERRUN", "district at peak threat"),
        }
        accent = palette["ghost"]
        if game_scene.ctx.elite_pressure_active():
            labels[3] = ("ELITE PRESSURE", "scatter windows collapsing")
            widths[3] = 300
        width = widths.get(pressure_stage, 278)
        headline, detail = labels.get(pressure_stage, labels[3])
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

    if rage_active:
        rage_timer = getattr(game_scene.ctx.pacman, "rage_timer", 0)
        accent = palette["power_flash"]
        width = 248
        panel = pyray.Rectangle(center_x - width // 2, top_y + (66 if pressure_stage > 0 else 0), width, 54)
        draw_glass_card(panel, accent_color=accent, glow_alpha=int(16 + pulse * 14), fill_alpha=162)
        draw_text_centered("RAGE ACTIVE", center_x, int(panel.y + 10), 16, colors.WHITE)
        combo_text = f"combo x{game_scene.ctx.ghost_combo + 1}" if game_scene.ctx.ghost_combo > 0 else "ghosts vulnerable"
        if 0 < rage_timer <= 45:
            combo_text = "window collapsing"
        draw_text_centered(combo_text.upper(), center_x, int(panel.y + 30), 12, colors.GOLD)
    elif game_scene.ctx.power_chain_window > 0:
        accent = palette["power_flash"]
        width = 248
        panel = pyray.Rectangle(center_x - width // 2, top_y + (66 if pressure_stage > 0 else 0), width, 54)
        draw_glass_card(panel, accent_color=accent, glow_alpha=int(12 + pulse * 10), fill_alpha=150)
        draw_text_centered(f"CHAIN WINDOW {game_scene.ctx.power_chain_level}", center_x, int(panel.y + 10), 16, colors.WHITE)
        draw_text_centered(f"next seed keeps combo  {game_scene.ctx.power_chain_window}", center_x, int(panel.y + 30), 12, colors.GOLD)

    if game_scene.ctx.route_chain_active():
        route_width = 236
        top_offset = 66 if pressure_stage > 0 else 0
        if rage_active or game_scene.ctx.power_chain_window > 0:
            top_offset += 66
        panel = pyray.Rectangle(center_x - route_width // 2, top_y + top_offset, route_width, 46)
        draw_glass_card(panel, accent_color=palette["dot"], glow_alpha=int(10 + pulse * 10), fill_alpha=142)
        draw_text_centered(f"ROUTE CHAIN {game_scene.ctx.route_chain_count}", center_x, int(panel.y + 10), 15, colors.WHITE)
        draw_text_centered(f"keep sweeping dots  {game_scene.ctx.route_chain_window}", center_x, int(panel.y + 27), 11, palette["power"])

    if game_scene.near_miss_timer > 0:
        alert_pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 9.0)
        width = 212
        top_offset = 66 if pressure_stage > 0 else 0
        if rage_active or game_scene.ctx.power_chain_window > 0:
            top_offset += 66
        panel = pyray.Rectangle(center_x - width // 2, top_y + top_offset, width, 46)
        draw_glass_card(panel, accent_color=colors.WHITE, glow_alpha=int(10 + alert_pulse * 12), fill_alpha=146)
        draw_text_centered("NEAR MISS", center_x, int(panel.y + 10), 15, colors.WHITE)
        draw_text_centered("ghost almost clipped your line", center_x, int(panel.y + 27), 11, palette["ghost"])

    release_status = game_map.ghost_release_status()
    if release_status is not None and not rage_active:
        pending, total = release_status
        width = 188
        panel = pyray.Rectangle(24, 24, width, 46)
        draw_glass_card(panel, accent_color=PANEL_ACCENT, glow_alpha=10, fill_alpha=138)
        draw_text_centered("DEPLOYING", int(panel.x + panel.width / 2), int(panel.y + 10), 14, colors.WHITE)
        draw_text_centered(f"{pending}/{total} GHOSTS", int(panel.x + panel.width / 2), int(panel.y + 28), 12, TEXT_DIM)


def draw_pressure_overlay(game_scene, board_rect) -> None:
    pressure_stage = getattr(game_scene.ctx, "pressure_stage", 0)
    if pressure_stage <= 0 or game_scene.transition is not None:
        return

    pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * (4.5 + pressure_stage * 1.2))
    base_color = game_scene.ctx.effect_palette()["ghost"]
    if pressure_stage >= 3:
        base_color = colors.RED

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
    if game_scene.ctx.game_mode == "Arcade":
        chapter = game_scene.ctx.arcade_campaign_chapter()
        detail = f"{chapter.title}  |  {chapter.subtitle}" if chapter is not None else f"{map_trait.title}  |  {directive.title}"
        accent = chapter.accent if chapter is not None else map_trait.accent
    elif game_scene.ctx.game_mode == "Endless":
        tier = game_scene.ctx.endless_tier()
        detail = f"{tier.title}  |  {map_trait.title}"
        accent = tier.accent
    elif game_scene.ctx.game_mode == "Time Attack":
        seconds_left = max(0, math.ceil(game_scene.ctx.time_attack_seconds))
        detail = f"T-{seconds_left:02d}  |  {directive.title}"
        accent = colors.ORANGE
    else:
        detail = f"{map_trait.title}  |  {directive.title}"
        accent = map_trait.accent
    draw_transition_card(game_scene, "READY", detail, accent, width=430)


def draw_death_overlay(game_scene) -> None:
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
            "DISTRICT CONTROL LOST",
            game_scene.ctx.effect_palette()["death_flash"],
            width=380,
        )
    else:
        draw_transition_card(
            game_scene,
            "LIFE LOST",
            "SIGNAL RESTORE IN PROGRESS",
            game_scene.ctx.effect_palette()["death_flash"],
            width=380,
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
            detail = "NEXT SURVIVAL WAVE COMING UP"
        elif game_scene.ctx.game_mode == "Time Attack":
            detail = "BANKING TIME FOR THE NEXT BOARD"
        else:
            detail = "SYNCING NEXT REPORT"

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
