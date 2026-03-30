from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


APP_NAME = "Cyberpunk Pac-Man"
LEGACY_SAVE_DIR = Path("data") / "saves"
LEGACY_PROFILE_FILE = LEGACY_SAVE_DIR / "profile.json"
LEGACY_SCORE_FILE = LEGACY_SAVE_DIR / "scores.json"


def _user_data_root() -> Path:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata)
        return Path.home() / "AppData" / "Roaming"

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home)
    return Path.home() / ".local" / "share"


SAVE_DIR = _user_data_root() / APP_NAME / "saves"
PROFILE_FILE = SAVE_DIR / "profile.json"
SCORE_FILE = SAVE_DIR / "scores.json"


def ensure_save_dir() -> Path:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    return SAVE_DIR


def migrate_legacy_file(target_file: Path, legacy_file: Path) -> None:
    if target_file.exists() or not legacy_file.exists():
        return

    ensure_save_dir()
    try:
        target_file.write_text(legacy_file.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        return


def atomic_write_json(target_file: Path, payload: object) -> None:
    ensure_save_dir()
    fd, temp_path = tempfile.mkstemp(prefix=f"{target_file.stem}-", suffix=".tmp", dir=str(target_file.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        Path(temp_path).replace(target_file)
    except Exception:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except OSError:
            pass
        raise
