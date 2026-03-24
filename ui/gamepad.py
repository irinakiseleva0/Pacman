from __future__ import annotations

import core.raylib_api as pyray

PAD = 0
AXIS_THRESHOLD = 0.55

def _available() -> bool:
    return bool(getattr(pyray, "is_gamepad_available", lambda _pad: False)(PAD))


def _button_pressed(button) -> bool:
    return _available() and bool(pyray.is_gamepad_button_pressed(PAD, button))


def _axis_direction() -> str | None:
    if not _available():
        return None

    x = pyray.get_gamepad_axis_movement(PAD, pyray.GAMEPAD_AXIS_LEFT_X)
    y = pyray.get_gamepad_axis_movement(PAD, pyray.GAMEPAD_AXIS_LEFT_Y)

    if abs(x) < AXIS_THRESHOLD and abs(y) < AXIS_THRESHOLD:
        return None
    if abs(x) > abs(y):
        return "right" if x > 0 else "left"
    return "down" if y > 0 else "up"


def up_pressed() -> bool:
    return _button_pressed(pyray.GAMEPAD_BUTTON_LEFT_FACE_UP)


def down_pressed() -> bool:
    return _button_pressed(pyray.GAMEPAD_BUTTON_LEFT_FACE_DOWN)


def left_pressed() -> bool:
    return _button_pressed(pyray.GAMEPAD_BUTTON_LEFT_FACE_LEFT)


def right_pressed() -> bool:
    return _button_pressed(pyray.GAMEPAD_BUTTON_LEFT_FACE_RIGHT)


def confirm_pressed() -> bool:
    return _button_pressed(pyray.GAMEPAD_BUTTON_RIGHT_FACE_DOWN)


def back_pressed() -> bool:
    return (
        _button_pressed(pyray.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT)
        or _button_pressed(pyray.GAMEPAD_BUTTON_MIDDLE_LEFT)
    )


def pause_pressed() -> bool:
    return (
        _button_pressed(pyray.GAMEPAD_BUTTON_MIDDLE_RIGHT)
        or _button_pressed(pyray.GAMEPAD_BUTTON_MIDDLE)
    )


def movement_direction() -> str | None:
    if up_pressed():
        return "up"
    if down_pressed():
        return "down"
    if left_pressed():
        return "left"
    if right_pressed():
        return "right"
    return _axis_direction()
