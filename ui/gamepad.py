from __future__ import annotations


def _disabled() -> bool:
    return False


def up_pressed() -> bool:
    return _disabled()


def down_pressed() -> bool:
    return _disabled()


def left_pressed() -> bool:
    return _disabled()


def right_pressed() -> bool:
    return _disabled()


def confirm_pressed() -> bool:
    return _disabled()


def back_pressed() -> bool:
    return _disabled()


def pause_pressed() -> bool:
    return _disabled()


def movement_direction() -> str | None:
    return None
