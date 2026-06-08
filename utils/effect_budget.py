from __future__ import annotations

from enum import IntEnum


class EffectLevel(IntEnum):
    FULL = 3
    REDUCED = 2
    MINIMAL = 1
    NONE = 0


class EffectBudget:
    _HYSTERESIS = 5
    _SAMPLE_FRAMES = 30

    def __init__(self) -> None:
        self._samples: list[float] = []
        self.level = EffectLevel.FULL
        self._last_avg = 60.0

    def tick(self, current_fps: float) -> None:
        if current_fps <= 0:
            return

        self._samples.append(float(current_fps))
        if len(self._samples) > self._SAMPLE_FRAMES:
            self._samples.pop(0)

        avg = sum(self._samples) / len(self._samples)
        self._last_avg = avg

        if avg >= 60 + self._HYSTERESIS:
            self.level = EffectLevel.FULL
        elif avg >= 45 + self._HYSTERESIS:
            self.level = EffectLevel.REDUCED
        elif avg >= 30 + self._HYSTERESIS:
            self.level = EffectLevel.MINIMAL
        elif avg < 30 - self._HYSTERESIS:
            self.level = EffectLevel.NONE

    @property
    def scanlines(self) -> bool:
        return self.level >= EffectLevel.REDUCED

    @property
    def particles(self) -> bool:
        return self.level >= EffectLevel.REDUCED

    @property
    def animated_grid(self) -> bool:
        return self.level >= EffectLevel.FULL

    @property
    def bloom(self) -> bool:
        return self.level >= EffectLevel.MINIMAL


EFFECT_BUDGET = EffectBudget()
