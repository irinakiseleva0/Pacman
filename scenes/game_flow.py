from __future__ import annotations

import math
from typing import TYPE_CHECKING

import core.raylib_api as pyray
from core import colors

from core.scene_ids import EXIT_SCENE, MENU_SCENE, PAUSE_SCENE, RESULT_SCENE
from entities.pacman import State
from maps.class_map import Map
from ui import gamepad
from ui.hud import update_floating_texts
from ui.mobile_controls import handle_mobile_controls
from ui.ui import button_clicked
from utils.effects import trigger_glitch

if TYPE_CHECKING:
    from scenes.game_scene import GameScene


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
    scene.tutorial_stage_timer = 0.0
    scene.tutorial_wow_timer = 0.0
    scene.failure_reason = ""
    scene.near_miss_timer = 0.0
    scene.near_miss_cooldown = 0.0
    scene.danger_chain_count = 0
    scene.danger_chain_timer = 0.0
    scene.overtime_banner_timer = 0.0
    scene.overtime_announced = False
    visual.freeze_frames = 0
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
    if scene.ctx.replay_recorder is not None and scene.ctx.last_result == "":
        scene.ctx.replay_recorder.start(
            seed=scene.ctx.current_level_seed(),
            mode=scene.ctx.game_mode,
            map_name=map_path,
        )
    run.should_resume_game = False
    scene.transition = _transition(scene, "ready", scene.ctx.cfg.legacy_frames_to_seconds(scene.ctx.cfg.ready_duration_ticks))


def update(scene: "GameScene", dt: float) -> None:
    visual = scene.ctx.visual
    runtime = scene.ctx.runtime
    game_map = runtime.game_map
    if game_map is None:
        return

    if visual.freeze_frames > 0:
        visual.freeze_frames -= 1
        return

    mobile_action = _input_system(scene)
    if mobile_action == "handled":
        return

    effective_dt = _feedback_system(scene, dt)
    _timer_system(scene, dt, effective_dt)

    game_map.frame()
    _tutorial_system(scene, mobile_action)

    if _transition_system(scene, effective_dt):
        return

    if _time_attack_system(scene, effective_dt):
        return

    scene.ctx.run_stats.level_elapsed_seconds += effective_dt
    _gameplay_step_system(scene, game_map, effective_dt)
    if scene.ctx.replay_recorder is not None:
        scene.ctx.replay_recorder.record_tick(scene.ctx)
    _effects_update_system(scene)

    if _combat_or_collision_system(scene, game_map):
        return


def _input_system(scene: "GameScene") -> str | None:
    if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed():
        scene.request_switch(MENU_SCENE)
        return "handled"

    if pyray.is_key_pressed(pyray.KEY_P) or gamepad.pause_pressed():
        scene.request_switch(PAUSE_SCENE)
        return "handled"

    if scene.btn_pause is not None and button_clicked(scene.btn_pause):
        scene.request_switch(PAUSE_SCENE)
        return "handled"
    if scene.btn_menu is not None and button_clicked(scene.btn_menu):
        scene.ctx.reset_run_state()
        scene.request_switch(MENU_SCENE)
        return "handled"
    if scene.btn_end_run is not None and button_clicked(scene.btn_end_run):
        scene.failure_reason = "abort"
        scene.ctx.last_result = "abandon"
        scene.request_switch(RESULT_SCENE)
        return "handled"
    if scene.btn_exit is not None and button_clicked(scene.btn_exit):
        scene.request_switch(EXIT_SCENE)
        return "handled"

    mobile_action = handle_mobile_controls(scene.ctx)
    if mobile_action == "pause":
        scene.request_switch(PAUSE_SCENE)
        return "handled"
    return mobile_action


def _feedback_system(scene: "GameScene", dt: float) -> float:
    visual = scene.ctx.visual
    effective_dt = dt
    if visual.action_hitstop > 0:
        visual.action_hitstop = max(0.0, visual.action_hitstop - dt)
        return 0.0
    if visual.action_slowdown > 0:
        visual.action_slowdown = max(0.0, visual.action_slowdown - dt)
        effective_dt *= visual.action_slow_scale
        if visual.action_slowdown == 0:
            visual.action_slow_scale = 1.0
    return effective_dt


def _timer_system(scene: "GameScene", dt: float, effective_dt: float) -> None:
    visual = scene.ctx.visual
    scene.visual_time += effective_dt
    visual.visual_time = scene.visual_time
    if effective_dt > 0:
        scene.ctx.tick_power_chain_window()
        scene.ctx.tick_route_chain_window()
        scene.ctx.tick_district_windows()
    scene.near_miss_timer = max(0.0, scene.near_miss_timer - dt)
    scene.near_miss_cooldown = max(0.0, scene.near_miss_cooldown - dt)
    scene.danger_chain_timer = max(0.0, scene.danger_chain_timer - dt)
    if scene.danger_chain_timer == 0.0:
        scene.danger_chain_count = 0
    scene.overtime_banner_timer = max(0.0, scene.overtime_banner_timer - dt)
    scene.tutorial_wow_timer = max(0.0, scene.tutorial_wow_timer - dt)
    if scene.tutorial_stage > 0:
        scene.tutorial_stage_timer += dt


def _tutorial_system(scene: "GameScene", mobile_action: str | None) -> None:
    update_tutorial_state(scene, mobile_action)


def _transition_system(scene: "GameScene", effective_dt: float) -> bool:
    if scene.transition is None:
        return False
    scene.transition.ticks -= effective_dt
    if scene.transition.ticks <= 0:
        finish_transition(scene)
    return True


def _time_attack_system(scene: "GameScene", effective_dt: float) -> bool:
    run = scene.ctx.run
    runtime = scene.ctx.runtime
    visual = scene.ctx.visual
    if run.game_mode != "Time Attack":
        return False

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
        return True
    return False


def _gameplay_step_system(scene: "GameScene", game_map, effective_dt: float) -> None:
    run = scene.ctx.run
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


def _effects_update_system(scene: "GameScene") -> None:
    visual = scene.ctx.visual
    frame_dt = pyray.get_frame_time()
    visual.particles.update(frame_dt)
    visual.light_bursts.update(frame_dt)
    visual.screen_shake.update(frame_dt)
    visual.floating_text.update(frame_dt)
    visual.screen_flash.update(frame_dt)
    update_floating_texts(frame_dt)


def _combat_or_collision_system(scene: "GameScene", game_map) -> bool:
    run = scene.ctx.run
    runtime = scene.ctx.runtime

    if run.score > run.high_score:
        run.high_score = run.score

    pacman = runtime.pacman
    if pacman is not None and scene.transition is None:
        check_near_miss(scene)
    if pacman is not None and pacman.state == State.NONE and scene.transition is None:
        start_death_transition(scene)
        return True

    if game_map.remaining_seeds() == 0 and not getattr(game_map, "boss_alive", lambda: False)() and scene.transition is None:
        start_level_complete_transition(scene)
        return True
    return False


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
    trigger_glitch(1.5)
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
        if scene.ctx.replay_recorder is not None:
            scene.ctx.replay_recorder.stop()
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
        if scene.ctx.replay_recorder is not None:
            scene.ctx.replay_recorder.stop()
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
    scene.ctx.play_sfx("level_clear")
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
    scene.near_miss_timer = 0.5
    scene.near_miss_cooldown = 1.35
    scene.ctx.run_stats.near_misses += 1
    scene.ctx.check_achievements(save=False)
    scene.ctx.trigger_screen_flash(palette["ghost"], 0.12 if risk_turn else 0.09, 0.11 if risk_turn else 0.09)
    scene.ctx.trigger_screen_shake(3.6 if risk_turn else 2.6, 0.14 if risk_turn else 0.11)
    scene.ctx.trigger_action_juice(
        hitstop=0.04 if risk_turn else 0.028,
        slow_scale=0.56 if risk_turn else 0.68,
        slow_duration=0.085 if risk_turn else 0.07,
    )
    scene.ctx.visual.light_bursts.add_grid_burst(
        pacman.x,
        pacman.y,
        palette["ghost"],
        28 if risk_turn else 24,
        1.45 if risk_turn else 1.15,
        0.18 if risk_turn else 0.14,
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
        scene.ctx.run_stats.risk_bonus_score += bonus
        scene.ctx.visual.floating_text.add_text(
            f"THREAD +{bonus}",
            pacman.x * 16 - 22,
            pacman.y * 16 - 38,
            colors.GOLD,
            0.72,
            12,
        )
    _advance_danger_chain(scene, risk_turn)


def _advance_danger_chain(scene: "GameScene", risk_turn: bool) -> None:
    if scene.danger_chain_timer > 0:
        scene.danger_chain_count += 1
    else:
        scene.danger_chain_count = 1

    scene.danger_chain_timer = 3.4
    _handle_district_risk_window(scene, risk_turn)
    if scene.danger_chain_count < 2:
        return

    bonus = scene.ctx.danger_chain_bonus_value(scene.danger_chain_count, risk_turn=risk_turn)
    scene.ctx.run.score += bonus
    scene.ctx.run_stats.risk_bonus_score += bonus
    palette = scene.ctx.effect_palette()
    pacman = scene.ctx.runtime.pacman
    if pacman is None:
        return

    accent = colors.GOLD if risk_turn else palette["ghost"]
    label = f"NERVE x{scene.danger_chain_count} +{bonus}"
    scene.ctx.visual.floating_text.add_text(
        label,
        pacman.x * 16 - 28,
        pacman.y * 16 - 56,
        accent,
        0.86 if risk_turn else 0.78,
        12,
    )
    scene.ctx.trigger_screen_flash(accent, 0.06 if risk_turn else 0.045, 0.06)
    scene.ctx.trigger_screen_shake(2.8 + scene.danger_chain_count * 0.35, 0.1 if risk_turn else 0.08)


def _handle_district_risk_window(scene: "GameScene", risk_turn: bool) -> None:
    ctx = scene.ctx
    pacman = ctx.runtime.pacman
    game_map = ctx.runtime.game_map
    if pacman is None or game_map is None:
        return

    map_number = ctx.current_map_number()
    palette = ctx.effect_palette()
    if map_number == 1:
        ctx.route_chain_window = max(ctx.route_chain_window, ctx.route_chain_grace_ticks() + 12)
        bonus = ctx.map_transit_escape_bonus()
        if bonus > 0:
            ctx.run.score += bonus
            ctx.run_stats.route_bonus_score += bonus
            ctx.visual.floating_text.add_text(
                f"OPEN LANE +{bonus}",
                pacman.x * 16 - 26,
                pacman.y * 16 - 70,
                palette["dot"],
                0.78,
                12,
            )
    elif map_number == 2:
        game_map.nudge_pending_ghosts(1 + int(risk_turn))
        bonus = ctx.map_pressure_bait_bonus()
        if bonus > 0:
            ctx.run.score += bonus
            ctx.run_stats.risk_bonus_score += bonus
            ctx.visual.floating_text.add_text(
                f"BAIT PAID +{bonus}",
                pacman.x * 16 - 26,
                pacman.y * 16 - 70,
                palette["ghost"],
                0.82,
                12,
            )
    elif map_number == 3:
        ctx.arm_hunt_window()
        ctx.visual.floating_text.add_text(
            "HUNT WINDOW",
            pacman.x * 16 - 24,
            pacman.y * 16 - 70,
            palette["power"],
            0.84,
            12,
        )
    elif map_number == 4:
        ctx.arm_market_window()
        ctx.visual.floating_text.add_text(
            "MARKET WINDOW",
            pacman.x * 16 - 28,
            pacman.y * 16 - 70,
            palette["respawn"][0],
            0.84,
            12,
        )
    elif map_number == 5 and (ctx.pressure_stage >= 1 or game_map.remaining_pickups() <= 18):
        bonus = ctx.map_survival_bank_bonus(scene.danger_chain_count)
        if bonus > 0:
            ctx.run.score += bonus
            ctx.run_stats.risk_bonus_score += bonus
            game_map.nudge_pending_ghosts(1)
            ctx.visual.floating_text.add_text(
                f"PANIC BANK +{bonus}",
                pacman.x * 16 - 28,
                pacman.y * 16 - 70,
                palette["ghost"],
                0.84,
                12,
            )


def tutorial_active(scene: "GameScene") -> bool:
    return scene.ctx.tutorial_enabled() and not scene.ctx.tutorial_seen()


def movement_pressed(scene: "GameScene") -> bool:
    return any(
        pyray.is_key_pressed(key)
        for key in (pyray.KEY_W, pyray.KEY_A, pyray.KEY_S, pyray.KEY_D, pyray.KEY_UP, pyray.KEY_DOWN, pyray.KEY_LEFT, pyray.KEY_RIGHT)
    ) or gamepad.movement_direction() is not None


def advance_tutorial(scene: "GameScene", next_stage: int, *, complete: bool = False) -> None:
    scene.tutorial_stage = next_stage
    scene.tutorial_stage_timer = 0.0
    if next_stage == 0 and complete:
        scene.ctx.mark_tutorial_seen()


def update_tutorial_state(scene: "GameScene", mobile_action: str | None) -> None:
    if scene.tutorial_stage <= 0:
        return

    if scene.transition is not None and scene.transition.kind == "death":
        scene.tutorial_stage = 1
        scene.tutorial_stage_timer = 0.0
        return

    if scene.tutorial_stage == 1 and (movement_pressed(scene) or mobile_action in {"up", "left", "right", "down"}):
        advance_tutorial(scene, 2)
        return

    if scene.tutorial_stage == 2 and scene.ctx.run_stats.dots_eaten >= 4:
        advance_tutorial(scene, 3)
        return

    if scene.tutorial_stage == 3 and (scene.ctx.route_chain_active() or scene.ctx.route_chain_count >= 5):
        advance_tutorial(scene, 4)
        return

    if scene.tutorial_stage == 4 and scene.ctx.run_stats.power_seeds_eaten > 0:
        scene.tutorial_wow_timer = 1.5
        pacman = scene.ctx.runtime.pacman
        if pacman is not None:
            scene.ctx.visual.floating_text.add_text(
                "CHASE FLIPPED",
                pacman.x * 16 - 30,
                pacman.y * 16 - 54,
                colors.GOLD,
                1.1,
                14,
            )
        scene.ctx.trigger_screen_flash(colors.GOLD, 0.16, 0.14)
        scene.ctx.trigger_screen_shake(3.8, 0.16)
        advance_tutorial(scene, 5)
        return

    if scene.tutorial_stage == 5 and (
        scene.ctx.run_stats.ghosts_eaten > 0
        or scene.tutorial_stage_timer >= 2.4
    ):
        advance_tutorial(scene, 6)
        return

    if scene.tutorial_stage == 6 and (
        scene.ctx.run_stats.near_misses > 0
        or scene.tutorial_stage_timer >= 5.0
    ):
        advance_tutorial(scene, 7)
        return

    if scene.tutorial_stage == 7 and (navigator_confirm_like() or scene.tutorial_stage_timer >= 3.2):
        advance_tutorial(scene, 0, complete=True)


def tutorial_card_content(scene: "GameScene") -> tuple[str, str, str, object]:
    route_count = scene.ctx.route_chain_count
    stage = scene.tutorial_stage
    if stage == 1:
        return (
            "MOVE OUT",
            "Move with WASD, arrows, or the stick",
            "First goal: start the route and feel the lane flow",
            colors.SKYBLUE,
        )
    if stage == 2:
        dots_left = max(0, 4 - scene.ctx.run_stats.dots_eaten)
        return (
            "SWEEP THE LANE",
            "Eat a short line of dots without stopping",
            f"Clean movement builds tempo. {dots_left} more dots to go",
            colors.SKYBLUE,
        )
    if stage == 3:
        return (
            "ROUTE CHAIN",
            "Keep sweeping dots to arm your route bonus",
            f"Route chain grows your score and opens shortcut play. Chain {route_count}",
            scene.ctx.effect_palette()["dot"],
        )
    if stage == 4:
        return (
            "FLIP THE CHASE",
            "Grab a power seed now",
            "This is your first spike: ghosts turn edible and the board tempo changes",
            scene.ctx.effect_palette()["power_flash"],
        )
    if stage == 5:
        detail = "Eat a ghost now, or just feel how the board changes under rage"
        if scene.ctx.run_stats.ghosts_eaten > 0:
            detail = "Perfect. Hunt windows convert into big score very quickly"
        return (
            "WOW MOMENT",
            "Rage flips the district from panic into pressure control",
            detail,
            colors.GOLD,
        )
    if stage == 6:
        detail = "Near misses and thread turns feed risk bonuses when you cut it close"
        if scene.ctx.run_stats.near_misses > 0:
            detail = "That pulse was a near miss. Risk is strongest when it stays controlled"
        return (
            "RISK PLAY",
            "You do not score only by surviving",
            detail,
            colors.ORANGE,
        )
    return (
        "TRAINING COMPLETE",
        "Tempo, flips, and controlled risk are your core loop",
        "Route for tempo, power-seeds for swings, risk for bursts. Press confirm to lock it in",
        colors.GOLD,
    )


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
