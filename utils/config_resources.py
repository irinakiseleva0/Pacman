from __future__ import annotations

import json
from importlib import resources


CONFIG_PACKAGE = "data.config"


def load_config_json(filename: str) -> object | None:
    try:
        raw = resources.files(CONFIG_PACKAGE).joinpath(filename).read_text(encoding="utf-8")
        return json.loads(raw)
    except (FileNotFoundError, ModuleNotFoundError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
