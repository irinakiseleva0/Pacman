from __future__ import annotations

from dataclasses import dataclass

from core import colors


@dataclass(frozen=True)
class CoreLoopFocus:
    phase: str
    detail: str
    accent: object


def current_core_loop_focus(ctx, game_map) -> CoreLoopFocus:
    pacman = ctx.runtime.pacman
    run = ctx.run
    cherry_status = game_map.cherry_status()
    cherry_ready = bool(cherry_status and cherry_status[0])

    if pacman is not None and getattr(pacman, "rage", False):
        combo = max(1, run.ghost_combo + 1)
        return CoreLoopFocus("CHASE", f"ghosts vulnerable  |  combo x{combo}", colors.GOLD)

    if pacman is not None:
        closest_ghost = _closest_danger_distance(game_map, pacman)
        if closest_ghost is not None and closest_ghost <= 2:
            danger_text = "ghost on your line" if closest_ghost <= 1 else "ghost closing the lane"
            return CoreLoopFocus("AVOID", danger_text, ctx.effect_palette()["ghost"])

    if cherry_ready or game_map.remaining_seeds() <= 2:
        if cherry_ready and game_map.remaining_seeds() <= 2:
            return CoreLoopFocus("EAT", "cherry live  |  power seeds still matter", colors.ORANGE)
        if cherry_ready:
            return CoreLoopFocus("EAT", "bonus route open  |  cherry ready", colors.GOLD)
        return CoreLoopFocus("EAT", "late board  |  finish the clean sweep", ctx.effect_palette()["dot"])

    if ctx.route_chain_active():
        return CoreLoopFocus("MOVE", f"hold the line  |  route x{run.route_chain_count}", ctx.effect_palette()["dot"])

    return CoreLoopFocus("MOVE", "clear lanes  |  stay ahead of pressure", colors.SKYBLUE)


def _closest_danger_distance(game_map, pacman) -> int | None:
    closest = None
    for actor in getattr(game_map, "dynamic_actors", []):
        if getattr(actor, "kind", None) != "ghost":
            continue
        if getattr(actor, "is_harmless", lambda: False)():
            continue
        distance = abs(actor.x - pacman.x) + abs(actor.y - pacman.y)
        if closest is None or distance < closest:
            closest = distance
    return closest
