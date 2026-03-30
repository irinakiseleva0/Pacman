from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from core.gameplay_view_models import build_live_feedback_model
from ui.ui import (
    LIVE_CYAN,
    LIVE_PINK,
    TEXT_DIM,
    draw_glass_card,
    draw_shadowed_text_centered,
    draw_text_centered,
    _draw_glitch_reveal,
)
from utils.visual_effects import with_alpha


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
        panel = pyray.Rectangle(center_x - width // 2, top_y, width, 54)
        draw_glass_card(panel, accent_color=accent, glow_alpha=int(22 + pulse * 22), fill_alpha=150)
        draw_text_centered(feedback.pressure_card.headline, center_x, int(panel.y + 10), 16, colors.WHITE)
        draw_text_centered(feedback.pressure_card.detail.upper(), center_x, int(panel.y + 30), 12, accent)

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
        glow_alpha = int(24 + pulse * 18) if rage_active else int(16 + pulse * 12)
        draw_glass_card(panel, accent_color=accent, glow_alpha=glow_alpha, fill_alpha=fill_alpha)
        draw_text_centered(feedback.rage_card.headline, center_x, int(panel.y + 10), 16, colors.WHITE)
        draw_text_centered(feedback.rage_card.detail.upper(), center_x, int(panel.y + 30), 12, colors.GOLD)

    if feedback.route_card is not None:
        route_width = feedback.route_card.width
        top_offset = 66 if pressure_stage > 0 else 0
        if feedback.rage_card is not None:
            top_offset += 66
        panel = pyray.Rectangle(center_x - route_width // 2, top_y + top_offset, route_width, 46)
        draw_glass_card(panel, accent_color=feedback.route_card.accent, glow_alpha=int(16 + pulse * 12), fill_alpha=142)
        draw_text_centered(feedback.route_card.headline, center_x, int(panel.y + 10), 15, colors.WHITE)
        draw_text_centered(feedback.route_card.detail, center_x, int(panel.y + 27), 11, palette["power"])

    if feedback.near_miss_card is not None:
        alert_pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 9.0)
        width = feedback.near_miss_card.width
        top_offset = 66 if pressure_stage > 0 else 0
        if feedback.rage_card is not None:
            top_offset += 66
        panel = pyray.Rectangle(center_x - width // 2, top_y + top_offset, width, 46)
        draw_glass_card(panel, accent_color=feedback.near_miss_card.accent, glow_alpha=int(18 + alert_pulse * 16), fill_alpha=146)
        draw_text_centered(feedback.near_miss_card.headline, center_x, int(panel.y + 10), 15, colors.WHITE)
        draw_text_centered(feedback.near_miss_card.detail, center_x, int(panel.y + 27), 11, palette["ghost"])

    if getattr(game_scene, "overtime_banner_timer", 0.0) > 0:
        overtime_alpha = min(1.0, game_scene.overtime_banner_timer / 1.35)
        panel = pyray.Rectangle(center_x - 158, top_y + 12, 316, 52)
        draw_glass_card(panel, accent_color=colors.ORANGE, glow_alpha=int(14 + overtime_alpha * 16), fill_alpha=156)
        draw_text_centered("OVERTIME", center_x, int(panel.y + 9), 16, colors.WHITE)
        draw_text_centered("CLOCK DANGER  |  NO SAFE RESET", center_x, int(panel.y + 28), 12, colors.ORANGE)


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
    reveal_progress = _transition_reveal_progress(game_scene)
    _draw_glitch_reveal(rect, reveal_progress, accent_color=accent_color, time_s=game_scene.visual_time)


def _transition_reveal_progress(game_scene) -> float:
    transition = game_scene.transition
    if transition is None:
        return 1.0

    cfg = game_scene.ctx.cfg
    if transition.kind == "ready":
        total = cfg.legacy_frames_to_seconds(cfg.ready_duration_ticks)
    elif transition.kind == "death":
        total = cfg.legacy_frames_to_seconds(
            cfg.game_over_pause_ticks if transition.result == "lose" else cfg.death_pause_ticks
        )
    elif transition.kind == "level_complete":
        total = cfg.legacy_frames_to_seconds(cfg.level_clear_pause_ticks)
    else:
        total = 0.35

    total = max(0.18, total)
    elapsed = max(0.0, total - transition.ticks)
    return min(1.0, elapsed / 0.26)


def draw_ready_overlay(game_scene) -> None:
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
    cfg = game_scene.ctx.cfg
    pulse = 0.5 + 0.5 * math.sin(game_scene.visual_time * 10.0)
    flash_color = game_scene.ctx.effect_palette()["death_flash"]
    distortion_alpha = int(18 + pulse * 24)
    for index in range(8):
        y = int((cfg.window_height / 8) * index + math.sin(game_scene.visual_time * (7.5 + index)) * 4)
        x_offset = math.sin(game_scene.visual_time * (11.0 + index * 0.7)) * (6 + index)
        pyray.draw_rectangle_rec(
            pyray.Rectangle(x_offset, y, cfg.window_width, 6),
            with_alpha(flash_color if index % 2 == 0 else LIVE_PINK, max(6, distortion_alpha - index * 2)),
        )
    pyray.draw_rectangle_rec(
        pyray.Rectangle(0, 0, cfg.window_width, cfg.window_height),
        with_alpha(colors.WHITE, int(6 + pulse * 12)),
    )
    killer_map = {
        "Blinky": "BLINKY CUT THE ROUTE",
        "Pinky": "PINKY HELD THE FRONT",
        "Inky": "INKY SLIPPED THE FLANK",
        "Clyde": "CLYDE FLIPPED THE READ",
    }
    killer_line = killer_map.get(game_scene.ctx.run.last_killer_name, "DISTRICT CONTROL LOST")
    if game_scene.failure_reason == "timeout":
        draw_transition_card(game_scene, "TIME OUT", "CLOCK DRAINED  |  RUN FORCE-CLOSED", colors.ORANGE, width=380)
    elif game_scene.transition is not None and game_scene.transition.result == "lose":
        draw_transition_card(game_scene, "GAME OVER", killer_line, game_scene.ctx.effect_palette()["death_flash"], width=380)
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
