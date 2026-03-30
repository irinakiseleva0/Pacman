from __future__ import annotations

import math
from typing import TYPE_CHECKING

import core.raylib_api as pyray
from raylib import colors

from core.scene_ids import EXIT_SCENE, MENU_SCENE, PAUSE_SCENE, RESULT_SCENE
from entities.pacman import State
from maps.class_map import Map
from ui import gamepad
from ui.mobile_controls import handle_mobile_controls
from ui.ui import button_clicked

if TYPE_CHECKING:
    from scenes.game_scene import GameScene, SceneTransition


def _transition(scene: "GameScene", kind: str, ticks: float, result: str = ""):
    from scenes.game_scene import SceneTransition

    return SceneTransition(kind, ticks, result)


def enter_tree(scene: "GameScene") -> None:
    visual = scene.ctx.visual
    runtime = scene.ctx.runtime
    run = scene.ctx.run
    scene.logic_accumulator = 0.0
    scene.transition = None
    scene.visual_time = 0.0
    visual.visual_time = 0.0
    scene.tutorial_stage = 1 if tutorial_active(scene) else 0
    scene.failure_reason = ""
    scene.near_miss_timer = 0.0
    scene.near_miss_cooldown = 0.0
    scene.overtime_banner_timer = 0.0
    scene.overtime_announced = False
    visual.action_hitstop = 0.0
    visual.action_slowdown = 0.0
    visual.action_slow_scale = 1.0

    if run.should_resume_game and runtime.game_map is not None:
        run.should_resume_game = False
        return

    scene.ctx.play_transition_effect(scene.ctx.effect_palette()["ready_flash"], 0.2, 0.6)
    scene.ctx.last_result = ""

    map_path = scene.ctx.get_map_path()
    scene.ctx.reset_ghost_mode_cycle()
    runtime.game_map = Map(scene.ctx, path=map_path)
    run.should_resume_game = False
    scene.transition = _transition(scene, "ready", scene.ctx.cfg.legacy_frames_to_seconds(scene.ctx.cfg.ready_duration_ticks))


def update(scene: "GameScene", dt: float) -> None:
    run = scene.ctx.run
    visual = scene.ctx.visual
    runtime = scene.ctx.runtime
    game_map = runtime.game_map
    if game_map is None:
        return

    if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
        scene.request_switch(MENU_SCENE)
        return

    if pyray.is_key_pressed(pyray.KEY_P) or gamepad.pause_pressed():
        scene.request_switch(PAUSE_SCENE)
        return

    if scene.btn_pause is not None and button_clicked(scene.btn_pause):
        scene.request_switch(PAUSE_SCENE)
        return
    if scene.btn_menu is not None and button_clicked(scene.btn_menu):
        scene.ctx.reset_run_state()
        scene.request_switch(MENU_SCENE)
        return
    if scene.btn_end_run is not None and button_clicked(scene.btn_end_run):
        scene.failure_reason = "abort"
        scene.ctx.last_result = "abandon"
        scene.request_switch(RESULT_SCENE)
        return
    if scene.btn_exit is not None and button_clicked(scene.btn_exit):
        scene.request_switch(EXIT_SCENE)
        return

    mobile_action = handle_mobile_controls(scene.ctx)
    if mobile_action == "pause":
        scene.request_switch(PAUSE_SCENE)
        return

    effective_dt = dt
    if visual.action_hitstop > 0:
        visual.action_hitstop = max(0.0, visual.action_hitstop - dt)
        effective_dt = 0.0
    elif visual.action_slowdown > 0:
        visual.action_slowdown = max(0.0, visual.action_slowdown - dt)
        effective_dt *= visual.action_slow_scale
        if visual.action_slowdown == 0:
            visual.action_slow_scale = 1.0

    scene.visual_time += effective_dt
    visual.visual_time = scene.visual_time
    if effective_dt > 0:
        scene.ctx.tick_power_chain_window()
        scene.ctx.tick_route_chain_window()
    scene.near_miss_timer = max(0.0, scene.near_miss_timer - dt)
    scene.near_miss_cooldown = max(0.0, scene.near_miss_cooldown - dt)
    scene.overtime_banner_timer = max(0.0, scene.overtime_banner_timer - dt)

    game_map.frame()

    update_tutorial_state(scene, mobile_action)

    if scene.transition is not None:
        scene.transition.ticks -= effective_dt
        if scene.transition.ticks <= 0:
            finish_transition(scene)
        return

    if run.game_mode == "Time Attack":
        run.time_attack_seconds = max(0.0, run.time_attack_seconds - effective_dt)
        if run.time_attack_seconds <= 10.0 and not scene.overtime_announced:
            scene.overtime_announced = True
            scene.overtime_banner_timer = 1.35
            scene.ctx.trigger_screen_flash(colors.ORANGE, 0.12, 0.12)
            scene.ctx.trigger_screen_shake(2.8, 0.12)
            if runtime.pacman is not None:
                visual.floating_text.add_text(
                    "OVERTIME WINDOW",
                    runtime.pacman.x * 16 - 30,
                    runtime.pacman.y * 16 - 28,
                    colors.ORANGE,
                    0.9,
                    13,
                )
        if run.time_attack_seconds <= 0:
            start_timeout_transition(scene)
            return

    scene.logic_accumulator += effective_dt
    logic_step = scene.ctx.cfg.logic_step_seconds()
    processed_steps = 0
    while scene.logic_accumulator >= logic_step and processed_steps < 4:
        scene.logic_accumulator -= logic_step
        processed_steps += 1
        pressure_changed = scene.ctx.advance_ghost_mode_cycle(
            game_map.remaining_pickups(),
            getattr(game_map, "total_pickups", 0),
        )
        if pressure_changed and run.pressure_stage > 0:
            _handle_pressure_escalation(scene, game_map)
        game_map.process()

    frame_dt = pyray.get_frame_time()
    visual.particles.update(frame_dt)
    visual.light_bursts.update(frame_dt)
    visual.screen_shake.update(frame_dt)
    visual.floating_text.update(frame_dt)
    visual.screen_flash.update(frame_dt)

    if run.score > run.high_score:
        run.high_score = run.score

    pacman = runtime.pacman
    if pacman is not None and scene.transition is None:
        check_near_miss(scene)
    if pacman is not None and pacman.state == State.NONE and scene.transition is None:
        start_death_transition(scene)
        return

    if game_map.remaining_seeds() == 0 and scene.transition is None:
        start_level_complete_transition(scene)


def _handle_pressure_escalation(scene: "GameScene", game_map) -> None:
    run = scene.ctx.run
    visual = scene.ctx.visual
    palette = scene.ctx.effect_palette()
    flash_strength = 0.04 + run.pressure_stage * 0.02
    shake_strength = 1.8 + run.pressure_stage * 0.7
    if scene.ctx.elite_pressure_active():
        flash_strength += 0.04
        shake_strength += 1.2
    scene.ctx.trigger_screen_flash(palette["ghost"], flash_strength, 0.05)
    scene.ctx.trigger_screen_shake(shake_strength, 0.08)
    surge = scene.ctx.map_release_surge_amount()
    if scene.ctx.elite_pressure_active():
        surge += 2
    if surge > 0:
        game_map.nudge_pending_ghosts(surge)
        visual.floating_text.add_text(
            "ELITE SURGE" if scene.ctx.elite_pressure_active() else "SURGE",
            int(scene.ctx.cfg.board_width * 0.48),
            24,
            palette["ghost"],
            0.75,
            12,
        )


def start_death_transition(scene: "GameScene") -> None:
    run = scene.ctx.run
    scene.failure_reason = ""
    scene.ctx.play_sfx("death")
    scene.ctx.play_transition_effect(scene.ctx.effect_palette()["death_flash"], 0.3, 0.2, 8.0, 0.5)

    run.lives -= 1

    if run.lives <= 0:
        scene.transition = _transition(scene, "death", scene.ctx.cfg.legacy_frames_to_seconds(scene.ctx.cfg.game_over_pause_ticks), "lose")
        return

    scene.transition = _transition(scene, "death", scene.ctx.cfg.legacy_frames_to_seconds(scene.ctx.cfg.death_pause_ticks), "reload")


def start_timeout_transition(scene: "GameScene") -> None:
    scene.failure_reason = "timeout"
    scene.ctx.play_sfx("death")
    scene.ctx.reset_ghost_combo()
    scene.ctx.play_transition_effect(colors.ORANGE, 0.34, 0.22, 9.0, 0.45)
    scene.transition = _transition(scene, "death", scene.ctx.cfg.legacy_frames_to_seconds(scene.ctx.cfg.game_over_pause_ticks), "lose")


def finish_transition(scene: "GameScene") -> None:
    if scene.transition is None:
        return

    if scene.transition.kind == "ready":
        scene.ctx.play_transition_effect(scene.ctx.effect_palette()["power_flash"], 0.15, 0.12)
        scene.transition = None
        return

    if scene.transition.kind == "death" and scene.transition.result == "lose":
        scene.ctx.last_result = "lose"
        scene.request_switch(RESULT_SCENE)
        scene.transition = None
        return

    if scene.transition.kind == "death":
        map_path = scene.ctx.get_map_path()
        scene.ctx.reset_ghost_mode_cycle()
        scene.ctx.runtime.game_map = Map(scene.ctx, path=map_path)
        scene.logic_accumulator = 0.0
        scene.transition = _transition(scene, "ready", scene.ctx.cfg.legacy_frames_to_seconds(scene.ctx.cfg.ready_duration_ticks))
        return

    if scene.transition.kind == "level_complete":
        scene.ctx.last_result = scene.transition.result or "level_complete"
        scene.request_switch(RESULT_SCENE)
        scene.transition = None


def start_level_complete_transition(scene: "GameScene") -> None:
    run = scene.ctx.run
    runtime = scene.ctx.runtime
    visual = scene.ctx.visual
    transition_result = "level_complete"
    if run.game_mode == "Challenge":
        transition_result = scene.ctx.challenge_result_on_clear()
    elif scene.ctx.run_won_on_level_clear():
        transition_result = "game_won"
    clear_bonus = scene.ctx.mode_clear_bonus()
    directive_bonus = scene.ctx.directive_clear_bonus()
    if clear_bonus > 0:
        run.score += clear_bonus
        if runtime.game_map is not None and runtime.pacman is not None:
            visual.floating_text.add_text(
                f"CLEAR +{clear_bonus}",
                runtime.pacman.x * 16 - 10,
                runtime.pacman.y * 16 - 26,
                colors.GOLD,
                1.1,
                14,
            )
    if directive_bonus > 0 and runtime.game_map is not None and runtime.pacman is not None:
        run.score += directive_bonus
        directive = scene.ctx.current_run_directive()
        visual.floating_text.add_text(
            f"{directive.title} +{directive_bonus}",
            runtime.pacman.x * 16 - 18,
            runtime.pacman.y * 16 - 44,
            directive.accent,
            1.2,
            14,
        )
    if run.game_mode == "Time Attack" and runtime.game_map is not None and runtime.pacman is not None:
        bonus_seconds = math.ceil(scene.ctx.time_attack_clear_bonus_seconds())
        visual.floating_text.add_text(
            f"+{bonus_seconds}S",
            runtime.pacman.x * 16 + 18,
            runtime.pacman.y * 16 - 62,
            colors.ORANGE,
            1.1,
            14,
        )
    scene.ctx.play_sfx("win")
    scene.ctx.record_level_cleared()
    scene.ctx.reset_ghost_combo()
    scene.ctx.play_transition_effect(scene.ctx.effect_palette()["win_flash"], 0.25, 0.2, 3.0, 0.2)
    if runtime.pacman is not None:
        visual.light_bursts.add_grid_burst(
            runtime.pacman.x,
            runtime.pacman.y,
            scene.ctx.effect_palette()["win_flash"],
            42,
            1.6,
            0.34,
        )
    scene.transition = _transition(
        scene,
        "level_complete",
        scene.ctx.cfg.legacy_frames_to_seconds(scene.ctx.cfg.level_complete_duration_ticks),
        transition_result,
    )


def check_near_miss(scene: "GameScene") -> None:
    if scene.near_miss_cooldown > 0:
        return

    game_map = scene.ctx.runtime.game_map
    pacman = scene.ctx.runtime.pacman
    if game_map is None or pacman is None or getattr(pacman, "rage", False):
        return

    closest_distance = None
    for actor in game_map.dynamic_actors:
        if getattr(actor, "kind", None) != "ghost":
            continue
        if getattr(actor, "is_harmless", lambda: False)():
            continue
        distance = abs(actor.x - pacman.x) + abs(actor.y - pacman.y)
        if closest_distance is None or distance < closest_distance:
            closest_distance = distance

    if closest_distance != 1:
        return

    palette = scene.ctx.effect_palette()
    risk_turn = getattr(pacman, "turn_feedback_timer", 0.0) > 0.03
    scene.near_miss_timer = 0.55
    scene.near_miss_cooldown = 1.1
    scene.ctx.run_stats.near_misses += 1
    scene.ctx.trigger_screen_flash(palette["ghost"], 0.06 if risk_turn else 0.05, 0.07 if risk_turn else 0.06)
    scene.ctx.trigger_screen_shake(2.1 if risk_turn else 1.4, 0.1 if risk_turn else 0.08)
    scene.ctx.trigger_action_juice(
        hitstop=0.022 if risk_turn else 0.014,
        slow_scale=0.66 if risk_turn else 0.78,
        slow_duration=0.06 if risk_turn else 0.045,
    )
    scene.ctx.visual.light_bursts.add_grid_burst(
        pacman.x,
        pacman.y,
        palette["ghost"],
        22 if risk_turn else 18,
        1.05 if risk_turn else 0.85,
        0.14 if risk_turn else 0.11,
    )
    scene.ctx.visual.floating_text.add_text(
        "CLOSE CALL",
        pacman.x * 16 - 18,
        pacman.y * 16 - 20,
        colors.WHITE,
        0.48,
        12,
    )
    if risk_turn:
        scene.ctx.run_stats.thread_turns += 1
        bonus = scene.ctx.risk_turn_bonus_value()
        scene.ctx.run.score += bonus
        scene.ctx.visual.floating_text.add_text(
            f"THREAD +{bonus}",
            pacman.x * 16 - 22,
            pacman.y * 16 - 38,
            colors.GOLD,
            0.72,
            12,
        )


def tutorial_active(scene: "GameScene") -> bool:
    return scene.ctx.tutorial_enabled() and not scene.ctx.tutorial_seen()


def movement_pressed(scene: "GameScene") -> bool:
    return any(
        pyray.is_key_pressed(key)
        for key in (pyray.KEY_W, pyray.KEY_A, pyray.KEY_S, pyray.KEY_D, pyray.KEY_UP, pyray.KEY_DOWN, pyray.KEY_LEFT, pyray.KEY_RIGHT)
    ) or gamepad.movement_direction() is not None


def advance_tutorial(scene: "GameScene", next_stage: int) -> None:
    scene.tutorial_stage = next_stage
    if next_stage == 0:
        scene.ctx.mark_tutorial_seen()


def update_tutorial_state(scene: "GameScene", mobile_action: str | None) -> None:
    if scene.tutorial_stage <= 0:
        return

    if scene.transition is not None and scene.transition.kind == "death":
        advance_tutorial(scene, 0)
        return

    if scene.tutorial_stage == 1 and (movement_pressed(scene) or mobile_action in {"up", "left", "right", "down"}):
        advance_tutorial(scene, 2)
        return

    if scene.tutorial_stage == 2 and scene.ctx.run_stats.dots_eaten > 0:
        advance_tutorial(scene, 3)
        return

    if scene.tutorial_stage == 3 and scene.ctx.run_stats.power_seeds_eaten > 0:
        advance_tutorial(scene, 4)
        return

    if scene.tutorial_stage == 4 and navigator_confirm_like():
        advance_tutorial(scene, 0)


def navigator_confirm_like() -> bool:
    enter_key = getattr(pyray, "KEY_ENTER", 257)
    kp_enter_key = getattr(pyray, "KEY_KP_ENTER", 335)
    space_key = getattr(pyray, "KEY_SPACE", 32)
    return (
        pyray.is_key_pressed(enter_key)
        or pyray.is_key_pressed(kp_enter_key)
        or pyray.is_key_pressed(space_key)
        or gamepad.confirm_pressed()
    )
