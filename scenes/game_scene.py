from __future__ import annotations

from dataclasses import dataclass

from core.scene import Scene
from scenes import game_flow, game_view


@dataclass
class SceneTransition:
    kind: str
    ticks: float
    result: str = ""


class GameScene(Scene):
    TOTAL_LEVELS = 3

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.logic_accumulator = 0.0
        self.transition: SceneTransition | None = None
        self.visual_time = 0.0
        self.tutorial_stage = 0
        self.failure_reason = ""
        self.near_miss_timer = 0.0
        self.near_miss_cooldown = 0.0
        self.overtime_banner_timer = 0.0
        self.overtime_announced = False
        self.btn_pause = None
        self.btn_menu = None
        self.btn_end_run = None
        self.btn_exit = None

    def _tutorial_step_total(self) -> int:
        return 4

    def _tutorial_progress_index(self) -> int:
        if self.tutorial_stage <= 0:
            return self._tutorial_step_total()
        return min(self._tutorial_step_total(), self.tutorial_stage)

    def enter_tree(self) -> None:
        game_flow.enter_tree(self)

    def update(self, dt: float) -> None:
        game_flow.update(self, dt)

    def start_death_transition(self) -> None:
        game_flow.start_death_transition(self)

    def start_timeout_transition(self) -> None:
        game_flow.start_timeout_transition(self)

    def finish_transition(self) -> None:
        game_flow.finish_transition(self)

    def start_level_complete_transition(self) -> None:
        game_flow.start_level_complete_transition(self)

    def _check_near_miss(self) -> None:
        game_flow.check_near_miss(self)

    def draw(self) -> None:
        game_view.draw_scene(self)

    def draw_hud(self) -> None:
        game_view.draw_hud(self)

    def draw_live_feedback(self) -> None:
        game_view.draw_live_feedback(self)

    def _draw_pressure_overlay(self, board_rect) -> None:
        game_view.draw_pressure_overlay(self, board_rect)

    def _draw_transition_card(self, headline: str, detail: str, accent_color, *, width: int = 360) -> None:
        game_view.draw_transition_card(self, headline, detail, accent_color, width=width)

    def draw_ready_overlay(self) -> None:
        game_view.draw_ready_overlay(self)

    def draw_death_overlay(self) -> None:
        game_view.draw_death_overlay(self)

    def draw_level_complete_overlay(self) -> None:
        game_view.draw_level_complete_overlay(self)

    def _tutorial_active(self) -> bool:
        return game_flow.tutorial_active(self)

    def _movement_pressed(self) -> bool:
        return game_flow.movement_pressed(self)

    def _advance_tutorial(self, next_stage: int) -> None:
        game_flow.advance_tutorial(self, next_stage)

    def _update_tutorial_state(self, mobile_action: str | None) -> None:
        game_flow.update_tutorial_state(self, mobile_action)

    def navigator_confirm_like(self) -> bool:
        return game_flow.navigator_confirm_like()

    def draw_tutorial_overlay(self) -> None:
        game_view.draw_tutorial_overlay(self)
