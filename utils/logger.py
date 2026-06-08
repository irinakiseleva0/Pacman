from __future__ import annotations

import logging
import platform


def setup_logging() -> None:
    level = logging.WARNING if platform.system() == "Emscripten" else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
