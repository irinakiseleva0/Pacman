from __future__ import annotations

from dataclasses import dataclass

import core.raylib_api as pyray
from core import colors

from ui import pygame_primitives as pgui
from ui.style import UI_STYLE
from ui.ui import (
    LIVE_CYAN,
    LIVE_GOLD,
    PANEL_ACCENT,
    TEXT_DIM,
    button_clicked,
    draw_button,
    draw_glass_card,
    draw_panel,
    draw_shadowed_text_centered,
    draw_text_centered,
)
from utils.visual_effects import with_alpha


@dataclass(frozen=True)
class Button:
    rect: object
    text: str
    focused: bool = False

    def draw(self, *, time_s: float | None = None) -> None:
        draw_button(self.rect, self.text, focused=self.focused, time_s=time_s)

    def clicked(self) -> bool:
        return button_clicked(self.rect)


@dataclass(frozen=True)
class Panel:
    rect: object
    title: str | None = None

    def draw(self, *, time_s: float | None = None) -> None:
        draw_panel(self.rect, self.title, time_s=time_s)


@dataclass(frozen=True)
class Label:
    text: str
    x: int
    y: int
    size: int = UI_STYLE.typography.body
    color: object = TEXT_DIM
    centered: bool = False

    def draw(self) -> None:
        if self.centered:
            draw_text_centered(self.text, self.x, self.y, self.size, self.color)
            return
        pgui.draw_text(self.text, self.x, self.y, self.size, self.color)


@dataclass(frozen=True)
class ScreenTitle:
    rect: object
    eyebrow: str
    title: str
    subtitle: str = ""
    accent: object = PANEL_ACCENT
    title_size: int = UI_STYLE.typography.screen_title

    def draw(self) -> None:
        center_x = int(self.rect.x + self.rect.width / 2)
        draw_text_centered(self.eyebrow.upper(), center_x, int(self.rect.y + 20), UI_STYLE.typography.section, self.accent)
        draw_shadowed_text_centered(self.title.upper(), center_x, int(self.rect.y + 50), self.title_size, colors.WHITE)
        if self.subtitle:
            draw_text_centered(self.subtitle.upper(), center_x, int(self.rect.y + 104), UI_STYLE.typography.body, TEXT_DIM)


@dataclass(frozen=True)
class StatusBadge:
    rect: object
    label: str
    value: str
    accent: object = LIVE_CYAN

    def draw(self, *, time_s: float | None = None) -> None:
        draw_glass_card(self.rect, accent_color=self.accent, glow_alpha=8, fill_alpha=132, time_s=time_s)
        center_x = int(self.rect.x + self.rect.width / 2)
        draw_text_centered(self.label.upper(), center_x, int(self.rect.y + 7), UI_STYLE.typography.small, TEXT_DIM)
        draw_text_centered(self.value.upper(), center_x, int(self.rect.y + 25), UI_STYLE.typography.body, colors.WHITE)


@dataclass(frozen=True)
class ProgressBar:
    rect: object
    value: float
    accent: object = LIVE_GOLD
    track_alpha: int = 80

    def draw(self) -> None:
        clamped = max(0.0, min(1.0, self.value))
        pgui.draw_rect(self.rect, with_alpha(colors.BLACK, self.track_alpha))
        pgui.draw_rect(self.rect, with_alpha(PANEL_ACCENT, 80), 1)
        fill_width = max(0, int((self.rect.width - 4) * clamped))
        pgui.draw_rect(
            pyray.Rectangle(self.rect.x + 2, self.rect.y + 2, fill_width, max(0, self.rect.height - 4)),
            with_alpha(self.accent, 188),
        )


def draw_button_component(rect, text: str, *, focused: bool = False, time_s: float | None = None) -> None:
    Button(rect, text, focused).draw(time_s=time_s)
