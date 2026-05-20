from __future__ import annotations

import core.raylib_api as pyray

from scenes.game_view_background import (
    draw_live_board_backdrop,
    draw_live_game_background,
    draw_pressure_overlay,
)
from scenes.game_view_hud import draw_hud
from scenes.game_view_overlays import (
    draw_death_overlay,
    draw_level_complete_overlay,
    draw_live_feedback,
    draw_ready_overlay,
    draw_tutorial_overlay,
)
from ui.hud import draw_floating_texts
from ui.ui import draw_presentation_bars


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

    draw_floating_texts()
    visual.screen_flash.draw()
    draw_presentation_bars(cfg.window_width, cfg.window_height)
