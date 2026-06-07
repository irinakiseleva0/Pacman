from __future__ import annotations

import math
from dataclasses import dataclass

from core import colors

from core.core_loop import current_core_loop_focus
from entities.ghost import Ghost
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK


@dataclass(frozen=True)
class HudSection:
    title: str
    lines: tuple[tuple[str, object], ...]
    accent: object


@dataclass(frozen=True)
class GameplayHudModel:
    sections: tuple[HudSection, ...]


@dataclass(frozen=True)
class FeedbackCard:
    headline: str
    detail: str
    accent: object
    width: int


@dataclass(frozen=True)
class LiveFeedbackModel:
    pressure_card: FeedbackCard | None = None
    rage_card: FeedbackCard | None = None
    route_card: FeedbackCard | None = None
    near_miss_card: FeedbackCard | None = None


def build_hud_model(ctx, game_map) -> GameplayHudModel:
    run = ctx.run
    runtime = ctx.runtime
    seeds_left = game_map.remaining_seeds()
    cherry_status = game_map.cherry_status()
    ghost_release_status = game_map.ghost_release_status()
    ghost_return_status = game_map.ghost_return_status()
    rage_active = bool(getattr(runtime.pacman, "rage", False))
    hud_pack = getattr(ctx, "hud_pack_name", lambda: "Standard")()
    difficulty_color = (
        colors.GREEN if run.difficulty == "Easy"
        else colors.RED if run.difficulty == "Hard"
        else colors.YELLOW
    )
    ghost_color = colors.SKYBLUE if run.ghost_mode == "scatter" else colors.RED

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
        (f"Score: {run.score}", colors.WHITE),
        (f"Lives: {run.lives}", colors.WHITE),
        (f"Level: {run.current_level}", colors.SKYBLUE),
    ]
    if run.game_mode == "Time Attack":
        seconds_left = max(0, math.ceil(run.time_attack_seconds))
        timer_color = colors.ORANGE if ctx.time_attack_warning_active() else LIVE_GOLD
        core_lines.insert(1, (f"Time: {seconds_left}", timer_color))
    elif run.high_score > 0:
        core_lines.append((f"Best: {run.high_score}", colors.WHITE))

    map_trait = ctx.current_map_trait()
    field_lines = [(f"Seeds: {seeds_left}", colors.WHITE), (map_trait.title, map_trait.accent)]
    if run.game_mode == "Endless":
        tier = ctx.endless_tier()
        field_lines.append((f"Tier: {tier.title}", tier.accent))
    elif run.game_mode == "Time Attack":
        field_lines.append(("Clock pressure live", colors.ORANGE))
    elif run.game_mode != "Arcade":
        field_lines.append((ctx.mode_label().upper(), difficulty_color))
    if run.pressure_stage > 0 or run.ghost_mode != "chase":
        field_lines.append((f"Ghosts: {run.ghost_mode.upper()}", ghost_color))

    bonus_lines: list[tuple[str, object]] = []

    if cherry_text is not None:
        bonus_lines.append((cherry_text, cherry_color))
    if ghost_release_status is not None:
        pending_ghosts, total_ghosts = ghost_release_status
        bonus_lines.insert(0, (f"Deploying: {pending_ghosts}/{total_ghosts}", colors.LIGHTGRAY))
    if ghost_return_status is not None:
        returning_ghosts, total_ghosts = ghost_return_status
        bonus_lines.insert(0, (f"Returning: {returning_ghosts}/{total_ghosts}", colors.WHITE))

    if rage_active:
        bonus_lines.append(("Rage: ON", colors.YELLOW))
        bonus_lines.append((f"Combo: x{run.ghost_combo + 1}", colors.GOLD))
        if run.power_chain_level > 1:
            bonus_lines.append((f"Chain: {run.power_chain_level}", colors.WHITE))
        rage_timer = getattr(runtime.pacman, "rage_timer", 0)
        if 0 < rage_timer <= Ghost.FRIGHTENED_BLINK_TICKS:
            bonus_lines.append(("Rage ending soon!", colors.ORANGE))
    elif run.power_chain_window > 0:
        bonus_lines.append((f"Chain window: {run.power_chain_window}", colors.GOLD))

    if ctx.route_chain_active():
        bonus_lines.append((f"Route: x{run.route_chain_count}", ctx.effect_palette()["dot"]))
    if ctx.hunt_window_active():
        bonus_lines.append(("Hunt window live", ctx.effect_palette()["power"]))
    if ctx.market_window_active():
        bonus_lines.append(("Jackpot route live", ctx.effect_palette()["cherry"][1]))

    loop_focus = current_core_loop_focus(ctx, game_map)
    signal_lines = [(loop_focus.detail.upper(), loop_focus.accent), *bonus_lines]

    sections = [
        HudSection("RUN", tuple(core_lines), LIVE_CYAN),
        HudSection("DISTRICT", tuple(field_lines), LIVE_PINK),
    ]
    if signal_lines:
        sections.append(HudSection(loop_focus.phase, tuple(signal_lines), loop_focus.accent))

    if hud_pack == "Relay Grid":
        sections = [
            HudSection("ROUTE FEED", tuple(core_lines), LIVE_CYAN),
            HudSection("DISTRICT FEED", tuple(field_lines), LIVE_GOLD),
        ] + ([HudSection(loop_focus.phase, tuple(signal_lines), LIVE_PINK)] if signal_lines else [])
    elif hud_pack == "Hunter Scope":
        sections = [
            HudSection("HUNTER SCOPE", tuple(core_lines), LIVE_PINK),
            HudSection("THREAT READOUT", tuple(field_lines), colors.RED),
        ] + ([HudSection(loop_focus.phase, tuple(signal_lines), LIVE_GOLD)] if signal_lines else [])
    elif hud_pack == "Chrome Vector":
        sections = [
            HudSection("VECTOR RUN", tuple(core_lines), colors.WHITE),
            HudSection("FIELD VECTOR", tuple(field_lines), LIVE_CYAN),
        ] + ([HudSection(loop_focus.phase, tuple(signal_lines), LIVE_GOLD)] if signal_lines else [])

    theme_name = getattr(ctx, "theme_name", lambda: "Neon District")()
    if theme_name == "Amber Rain":
        sections = [
            HudSection("RUN", tuple(core_lines), LIVE_GOLD),
            HudSection("DISTRICT", tuple(field_lines), LIVE_PINK),
        ] + ([HudSection(loop_focus.phase, tuple(signal_lines), LIVE_CYAN)] if signal_lines else [])
    elif theme_name == "Ice Circuit":
        sections = [
            HudSection("RUN", tuple(core_lines), LIVE_CYAN),
            HudSection("DISTRICT", tuple(field_lines), colors.SKYBLUE),
        ] + ([HudSection(loop_focus.phase, tuple(signal_lines), LIVE_GOLD)] if signal_lines else [])
    elif theme_name == "Velvet Alley":
        sections = [
            HudSection("RUN", tuple(core_lines), LIVE_PINK),
            HudSection("DISTRICT", tuple(field_lines), LIVE_GOLD),
        ] + ([HudSection(loop_focus.phase, tuple(signal_lines), LIVE_CYAN)] if signal_lines else [])

    return GameplayHudModel(tuple(sections))


def build_live_feedback_model(scene) -> LiveFeedbackModel:
    run = scene.ctx.run
    runtime = scene.ctx.runtime
    palette = scene.ctx.effect_palette()
    pressure_stage = run.pressure_stage
    rage_active = bool(getattr(runtime.pacman, "rage", False))

    pressure_card = None
    if pressure_stage > 0:
        widths = {1: 220, 2: 250, 3: 278}
        labels = {
            1: ("PRESSURE RISING", "ghost routes tightening"),
            2: ("DANGER WINDOW", "late-board pressure live"),
            3: ("OVERRUN", "district at peak threat"),
        }
        accent = palette["ghost"]
        if scene.ctx.elite_pressure_active():
            labels[3] = ("ELITE PRESSURE", "scatter windows collapsing")
            widths[3] = 300
        headline, detail = labels.get(pressure_stage, labels[3])
        pressure_card = FeedbackCard(headline, detail, accent, widths.get(pressure_stage, 278))

    rage_card = None
    if rage_active:
        rage_timer = getattr(runtime.pacman, "rage_timer", 0)
        combo_text = f"combo x{run.ghost_combo + 1}" if run.ghost_combo > 0 else "ghosts vulnerable"
        if 0 < rage_timer <= 45:
            combo_text = "window collapsing"
        rage_card = FeedbackCard("RAGE ACTIVE", combo_text.upper(), palette["power_flash"], 248)
    elif run.power_chain_window > 0:
        rage_card = FeedbackCard(
            f"CHAIN WINDOW {run.power_chain_level}",
            f"next seed keeps combo  {run.power_chain_window}",
            palette["power_flash"],
            248,
        )

    route_card = None
    if scene.ctx.route_chain_active():
        route_card = FeedbackCard(
            f"ROUTE CHAIN {run.route_chain_count}",
            f"keep sweeping dots  {run.route_chain_window}",
            palette["dot"],
            236,
        )

    near_miss_card = None
    if scene.near_miss_timer > 0:
        chain_count = getattr(scene, "danger_chain_count", 0)
        if chain_count >= 2:
            detail = f"nerve chain x{chain_count}  |  keep threading pressure"
            headline = f"NERVE CHAIN {chain_count}"
            width = 252
        else:
            detail = "ghost almost clipped your line"
            headline = "NEAR MISS"
            width = 212
        near_miss_card = FeedbackCard(
            headline,
            detail,
            colors.WHITE,
            width,
        )

    return LiveFeedbackModel(
        pressure_card=pressure_card,
        rage_card=rage_card,
        route_card=route_card,
        near_miss_card=near_miss_card,
    )
