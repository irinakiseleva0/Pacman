from __future__ import annotations

from dataclasses import dataclass, field

from core.state import RunStats
from utils.profile_storage import PROFILE_FILE, load_profile, save_profile


@dataclass
class ProfileService:
    profile: dict = field(default_factory=load_profile)

    @property
    def profile_file(self):
        return PROFILE_FILE

    def save(self) -> None:
        save_profile(self.profile)

    def settings(self) -> dict:
        return self.profile.setdefault("settings", {})


@dataclass
class SettingsService:
    profile_service: ProfileService

    def get_string(self, key: str, default: str) -> str:
        return str(self.profile_service.settings().get(key, default))

    def set_string(self, key: str, value: str, *, save: bool = True) -> None:
        self.profile_service.settings()[key] = value
        if save:
            self.profile_service.save()

    def get_bool(self, key: str, default: bool) -> bool:
        return bool(self.profile_service.settings().get(key, 1 if default else 0))

    def set_bool(self, key: str, value: bool, *, save: bool = True) -> None:
        self.profile_service.settings()[key] = 1 if value else 0
        if save:
            self.profile_service.save()


@dataclass
class ProgressionService:
    run_stats: RunStats = field(default_factory=RunStats)
    pre_run_unlock_snapshot: dict = field(default_factory=dict)
    last_unlock_lines: tuple[str, str, str] = field(default_factory=lambda: ("", "", ""))
    last_unlocks_are_new: bool = False

    def reset_run_tracking(self) -> None:
        self.run_stats = RunStats()
        self.pre_run_unlock_snapshot = {}
        self.last_unlock_lines = ("", "", "")
        self.last_unlocks_are_new = False
