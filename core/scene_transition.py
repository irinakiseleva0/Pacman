from __future__ import annotations

from enum import Enum, auto

import core.raylib_api as pyray


class TransitionState(Enum):
    IDLE = auto()
    FADE_OUT = auto()
    FADE_IN = auto()


class SceneTransition:
    DURATION = 0.25

    def __init__(self) -> None:
        self.state = TransitionState.IDLE
        self._progress = 0.0
        self._pending_scene = None
        self._on_switch = None

    def start(self, new_scene, on_switch_callback) -> None:
        """Start a transition to new_scene."""
        if self.state != TransitionState.IDLE:
            return
        self._pending_scene = new_scene
        self._on_switch = on_switch_callback
        self.state = TransitionState.FADE_OUT
        self._progress = 0.0

    def update(self, dt: float) -> None:
        if self.state == TransitionState.IDLE:
            return
        self._progress += max(0.0, float(dt)) / self.DURATION
        if self._progress < 1.0:
            return

        self._progress = 0.0
        if self.state == TransitionState.FADE_OUT:
            if self._on_switch:
                self._on_switch(self._pending_scene)
            self.state = TransitionState.FADE_IN
            return

        self.state = TransitionState.IDLE
        self._pending_scene = None
        self._on_switch = None

    def draw_overlay(self) -> None:
        if self.state == TransitionState.IDLE:
            return
        if self.state == TransitionState.FADE_OUT:
            alpha = int(self._progress * 255)
        else:
            alpha = int((1.0 - self._progress) * 255)
        surface = pyray.get_drawing_surface()
        width, height = surface.get_size()
        pyray.draw_rectangle(0, 0, width, height, (5, 8, 20, alpha))

    @property
    def is_busy(self) -> bool:
        return self.state != TransitionState.IDLE


TRANSITION = SceneTransition()
