from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ability:
    name: str
    cooldown: float
    duration: float
    icon: str = "?"
    key_label: str = ""
    cooldown_remaining: float = 0.0
    active_remaining: float = 0.0
    unlocked: bool = True

    def activate(self, pacman) -> bool:
        if not self.unlocked or not self.is_ready():
            return False

        self.cooldown_remaining = self.cooldown
        self.active_remaining = self.duration
        self.on_activate(pacman)
        return True

    def update(self, pacman, dt: float) -> None:
        was_active = self.is_active()
        self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
        self.active_remaining = max(0.0, self.active_remaining - dt)
        if was_active and not self.is_active():
            self.on_expire(pacman)
        if self.is_active():
            self.on_update(pacman, dt)

    def is_ready(self) -> bool:
        return self.unlocked and self.cooldown_remaining <= 0.0 and self.active_remaining <= 0.0

    def is_active(self) -> bool:
        return self.active_remaining > 0.0

    def cooldown_progress(self) -> float:
        if not self.unlocked:
            return 1.0
        if self.cooldown <= 0:
            return 0.0
        return max(0.0, min(1.0, self.cooldown_remaining / self.cooldown))

    def on_activate(self, pacman) -> None:
        return None

    def on_update(self, pacman, dt: float) -> None:
        return None

    def on_expire(self, pacman) -> None:
        return None


class DashAbility(Ability):
    def __init__(self, *, unlocked: bool = True) -> None:
        super().__init__("Dash", 8.0, 0.5, icon="D", key_label="Q", unlocked=unlocked)

    def on_activate(self, pacman) -> None:
        pacman.ability_speed_multiplier = max(pacman.ability_speed_multiplier, 3.0)

    def on_update(self, pacman, dt: float) -> None:
        pacman.ability_speed_multiplier = max(pacman.ability_speed_multiplier, 3.0)

    def on_expire(self, pacman) -> None:
        pacman.refresh_ability_modifiers()


class ShieldAbility(Ability):
    def __init__(self, *, unlocked: bool = True) -> None:
        super().__init__("Shield", 15.0, 2.0, icon="S", key_label="E", unlocked=unlocked)

    def on_activate(self, pacman) -> None:
        pacman.ability_invulnerable = True

    def on_update(self, pacman, dt: float) -> None:
        pacman.ability_invulnerable = True

    def on_expire(self, pacman) -> None:
        pacman.refresh_ability_modifiers()


class SlowAbility(Ability):
    def __init__(self, *, unlocked: bool = True) -> None:
        super().__init__("Slow", 20.0, 3.0, icon="L", key_label="R", unlocked=unlocked)

    def on_activate(self, pacman) -> None:
        pacman.ability_slow_ghosts = True

    def on_update(self, pacman, dt: float) -> None:
        pacman.ability_slow_ghosts = True

    def on_expire(self, pacman) -> None:
        pacman.refresh_ability_modifiers()


def default_abilities(unlocks: dict[str, bool] | None = None) -> list[Ability]:
    unlocks = unlocks or {}
    return [
        DashAbility(unlocked=bool(unlocks.get("Dash", False))),
        ShieldAbility(unlocked=bool(unlocks.get("Shield", False))),
        SlowAbility(unlocked=bool(unlocks.get("Slow", False))),
    ]
