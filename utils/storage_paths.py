from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


APP_NAME = "Cyberpunk Pac-Man"
LEGACY_SAVE_DIR = Path("data") / "saves"
LEGACY_PROFILE_FILE = LEGACY_SAVE_DIR / "profile.json"
LEGACY_SCORE_FILE = LEGACY_SAVE_DIR / "scores.json"
LEGACY_DAILY_SCORE_FILE = LEGACY_SAVE_DIR / "daily_scores.json"


def browser_storage_enabled() -> bool:
    return sys.platform == "emscripten"


def _user_data_root() -> Path:
    if browser_storage_enabled():
        return Path("/tmp")

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
DAILY_SCORE_FILE = SAVE_DIR / "daily_scores.json"


def _storage_key(target_file: Path) -> str:
    return f"cyberpunk-pacman:{Path(target_file).name}"


def _local_storage():
    try:
        from js import localStorage  # type: ignore
    except Exception:
        return None
    return localStorage


def read_json(target_file: Path) -> object | None:
    if browser_storage_enabled():
        storage = _local_storage()
        if storage is None:
            return None
        try:
            raw = storage.getItem(_storage_key(target_file))
        except Exception:
            return None
        if not raw:
            return None
        try:
            return json.loads(str(raw))
        except (TypeError, ValueError, json.JSONDecodeError):
            return None

    try:
        with Path(target_file).open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def ensure_save_dir(directory: Path | None = None) -> Path:
    target_dir = SAVE_DIR if directory is None else Path(directory)
    if browser_storage_enabled():
        return target_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def migrate_legacy_file(target_file: Path, legacy_file: Path) -> None:
    if browser_storage_enabled():
        return
    if target_file.exists() or not legacy_file.exists():
        return

    ensure_save_dir(target_file.parent)
    try:
        target_file.write_text(legacy_file.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        return


def atomic_write_json(target_file: Path, payload: object) -> None:
    if browser_storage_enabled():
        storage = _local_storage()
        if storage is None:
            return
        storage.setItem(_storage_key(target_file), json.dumps(payload, ensure_ascii=False))
        return

    ensure_save_dir(target_file.parent)
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
