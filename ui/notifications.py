from __future__ import annotations

from dataclasses import dataclass

import core.raylib_api as pyray
from raylib import colors

from ui.ui import LIVE_CYAN, LIVE_GOLD, TEXT_DIM, draw_glass_card
from utils.visual_effects import with_alpha


@dataclass
class Notification:
    title: str
    detail: str
    age: float = 0.0
    duration: float = 3.0


class NotificationManager:
    def __init__(self) -> None:
        self.items: list[Notification] = []

    def push(self, title: str, detail: str, duration: float = 3.0) -> None:
        self.items.append(Notification(title, detail, duration=duration))
        self.items = self.items[-4:]

    def update(self, dt: float) -> None:
        for item in self.items:
            item.age += dt
        self.items = [item for item in self.items if item.age < item.duration]

    def draw(self, width: int, height: int) -> None:
        card_w = min(380, max(280, width - 28))
        card_h = 84
        margin = 18
        y = height - margin - card_h
        for item in reversed(self.items):
            progress = min(1.0, item.age / 0.28)
            if item.duration - item.age < 0.35:
                progress = min(progress, max(0.0, (item.duration - item.age) / 0.35))
            ease = 1.0 - (1.0 - progress) * (1.0 - progress)
            x = width - margin - card_w + int((1.0 - ease) * (card_w + margin))
            rect = pyray.Rectangle(x, y, card_w, card_h)
            draw_glass_card(rect, accent_color=LIVE_GOLD, glow_alpha=18, fill_alpha=190)
            pyray.draw_rectangle_rec(
                pyray.Rectangle(rect.x + 12, rect.y + 14, 4, rect.height - 28),
                with_alpha(LIVE_CYAN, 210),
            )
            pyray.draw_text("ACHIEVEMENT UNLOCKED", int(rect.x + 28), int(rect.y + 14), 13, LIVE_GOLD)
            pyray.draw_text(item.title, int(rect.x + 28), int(rect.y + 34), 20, colors.WHITE)
            pyray.draw_text(item.detail[:42], int(rect.x + 28), int(rect.y + 60), 13, TEXT_DIM)
            y -= card_h + 10
