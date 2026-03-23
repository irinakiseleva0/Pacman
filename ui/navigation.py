from __future__ import annotations

import pyray


class ButtonNavigator:
    def __init__(self, item_count: int, initial_index: int = 0) -> None:
        self.item_count = item_count
        self.focus_index = initial_index

    def reset(self, index: int = 0) -> None:
        self.focus_index = index

    def move_vertical(self) -> bool:
        if pyray.is_key_pressed(pyray.KEY_UP) or pyray.is_key_pressed(pyray.KEY_W):
            self.focus_index = (self.focus_index - 1) % self.item_count
            return True
        if pyray.is_key_pressed(pyray.KEY_DOWN) or pyray.is_key_pressed(pyray.KEY_S):
            self.focus_index = (self.focus_index + 1) % self.item_count
            return True
        return False

    def move_horizontal_within(self, group_size: int) -> bool:
        if group_size <= 0:
            return False
        if pyray.is_key_pressed(pyray.KEY_LEFT) or pyray.is_key_pressed(pyray.KEY_A):
            if self.focus_index < group_size:
                self.focus_index = (self.focus_index - 1) % group_size
                return True
        if pyray.is_key_pressed(pyray.KEY_RIGHT) or pyray.is_key_pressed(pyray.KEY_D):
            if self.focus_index < group_size:
                self.focus_index = (self.focus_index + 1) % group_size
                return True
        return False

    def confirm_pressed(self) -> bool:
        return (
            pyray.is_key_pressed(pyray.KEY_ENTER)
            or pyray.is_key_pressed(pyray.KEY_KP_ENTER)
            or pyray.is_key_pressed(pyray.KEY_SPACE)
        )
