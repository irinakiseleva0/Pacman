from __future__ import annotations

import math

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import GAME_SCENE
from ui.ui import (
    LIVE_CYAN,
    LIVE_GOLD,
    LIVE_PINK,
    PANEL_ACCENT,
    TEXT_DIM,
    draw_arcade_background,
    draw_cinematic_menu_background,
    draw_glass_card,
    draw_panel,
    draw_scene_footer,
    draw_text_centered,
)
from utils.visual_effects import with_alpha

TYPE_SPEED = 30.0

CHARACTER_NAMES = {
    "GHOST_01": "Blinky Corp. Security",
    "SYSTEM_AI": "SYSTEM_AI",
    "PAC": "Hacker unit",
}

CHARACTER_ACCENTS = {
    "GHOST_01": LIVE_PINK,
    "SYSTEM_AI": LIVE_CYAN,
    "PAC": LIVE_GOLD,
}


class DialogueScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.entries: list[dict[str, str | int]] = []
        self.index = 0
        self.visible_chars = 0.0
        self.panel = None

    def enter_tree(self) -> None:
        self.entries = self.ctx.consume_pending_dialogue()
        self.index = 0
        self.visible_chars = 0.0
        self._layout()
        if not self.entries:
            self._finish()

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        if not self.entries:
            return

        if pyray.is_key_pressed(pyray.KEY_ESCAPE):
            self.ctx.play_sfx("ui_back")
            self._finish()
            return

        text = self._current_text()
        text_done = self.visible_chars >= len(text)
        if pyray.is_key_pressed(pyray.KEY_SPACE):
            if text_done:
                self._advance()
            else:
                self.visible_chars = float(len(text))
            return

        self.visible_chars = min(float(len(text)), self.visible_chars + TYPE_SPEED * dt)

    def draw(self) -> None:
        cfg = self.ctx.cfg
        if cfg.layout_name == "desktop":
            draw_cinematic_menu_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        else:
            draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)

        if self.panel is None:
            self._layout()
        panel = self.panel
        draw_panel(panel, "INTERCEPTED SIGNAL", time_s=self.ctx.visual_time)

        if not self.entries:
            return

        entry = self.entries[self.index]
        character = str(entry["character"])
        accent = CHARACTER_ACCENTS.get(character, PANEL_ACCENT)
        display_name = CHARACTER_NAMES.get(character, character)

        draw_text_centered("INTERCEPTED SIGNAL", int(panel.x + panel.width / 2), int(panel.y + 24), 16, PANEL_ACCENT)
        draw_text_centered(display_name, int(panel.x + panel.width / 2), int(panel.y + 56), 30, accent)

        portrait_rect = self._portrait_rect(panel)
        text_rect = self._text_rect(panel, portrait_rect)
        self._draw_portrait(portrait_rect, str(entry["portrait"]), accent)

        draw_glass_card(text_rect, accent_color=accent, glow_alpha=14, fill_alpha=176, time_s=self.ctx.visual_time)
        self._draw_dialogue_text(text_rect, self._current_text()[: int(self.visible_chars)])

        progress = f"{self.index + 1}/{len(self.entries)}"
        pyray.draw_text(progress, int(text_rect.x + text_rect.width - 48), int(text_rect.y + text_rect.height - 30), 16, TEXT_DIM)
        prompt = "SPACE"
        if self.visible_chars >= len(self._current_text()):
            prompt = "SPACE TO CONTINUE"
        draw_text_centered(prompt, int(panel.x + panel.width / 2), int(panel.y + panel.height - 38), 14, TEXT_DIM)
        draw_scene_footer(panel)

    def _layout(self) -> None:
        cfg = self.ctx.cfg
        panel_width = min(1040, cfg.window_width - 80) if cfg.layout_name == "desktop" else min(560, cfg.window_width - 28)
        panel_height = min(560, cfg.window_height - 80)
        panel_x = cfg.window_width // 2 - panel_width // 2
        panel_y = max(36, cfg.window_height // 2 - panel_height // 2)
        self.panel = pyray.Rectangle(panel_x, panel_y, panel_width, panel_height)

    def _portrait_rect(self, panel):
        if panel.width < 720:
            size = min(132, int(panel.width * 0.34))
            return pyray.Rectangle(panel.x + 24, panel.y + 104, size, size)
        return pyray.Rectangle(panel.x + 34, panel.y + 112, 220, 260)

    def _text_rect(self, panel, portrait_rect):
        if panel.width < 720:
            x = portrait_rect.x + portrait_rect.width + 16
            return pyray.Rectangle(x, panel.y + 104, panel.x + panel.width - x - 24, 250)
        x = portrait_rect.x + portrait_rect.width + 28
        return pyray.Rectangle(x, panel.y + 112, panel.x + panel.width - x - 34, 260)

    def _current_text(self) -> str:
        return str(self.entries[self.index]["text"])

    def _advance(self) -> None:
        if self.index + 1 >= len(self.entries):
            self.ctx.play_sfx("ui_confirm")
            self._finish()
            return
        self.ctx.play_sfx("ui_confirm")
        self.index += 1
        self.visible_chars = 0.0

    def _finish(self) -> None:
        self.ctx.next_level()
        self.request_switch(GAME_SCENE)

    def _draw_dialogue_text(self, rect, text: str) -> None:
        font_size = 22 if rect.width >= 420 else 18
        line_height = font_size + 10
        max_width = int(rect.width - 44)
        y = int(rect.y + 34)
        for line in _wrap_text(text, font_size, max_width):
            pyray.draw_text(line, int(rect.x + 22), y, font_size, colors.WHITE)
            y += line_height

    def _draw_portrait(self, rect, portrait: str, accent) -> None:
        draw_glass_card(rect, accent_color=accent, glow_alpha=18, fill_alpha=156, time_s=self.ctx.visual_time)
        cx = int(rect.x + rect.width / 2)
        cy = int(rect.y + rect.height / 2)
        pulse = 0.5 + 0.5 * math.sin(self.ctx.visual_time * 3.2)

        if portrait == "ghost_red":
            body_w = int(rect.width * 0.56)
            body_h = int(rect.height * 0.46)
            body = pyray.Rectangle(cx - body_w // 2, cy - body_h // 2, body_w, body_h)
            pyray.draw_rectangle_rec(body, with_alpha(LIVE_PINK, 210))
            pyray.draw_circle(cx - body_w // 2, int(body.y), body_w // 2, with_alpha(LIVE_PINK, 210))
            pyray.draw_circle(cx + body_w // 2, int(body.y), body_w // 2, with_alpha(LIVE_PINK, 210))
            for offset in (-34, 34):
                pyray.draw_circle(cx + offset, cy - 18, 16, colors.WHITE)
                pyray.draw_circle(cx + offset + 5, cy - 18, 7, colors.BLACK)
            for index in range(4):
                x = int(body.x + index * body_w / 3)
                pyray.draw_circle(x, int(body.y + body.height), 16, with_alpha(LIVE_PINK, 210))
        elif portrait == "pac_hacker":
            pyray.draw_circle(cx, cy, int(rect.width * 0.24), with_alpha(LIVE_GOLD, 220))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(cx + 6, cy - 24, int(rect.width * 0.22), 48),
                with_alpha((8, 12, 24, 255), 255),
            )
            pyray.draw_rectangle_rec(
                pyray.Rectangle(cx - 58, cy - 48, 116, 14),
                with_alpha(LIVE_CYAN, int(90 + pulse * 90)),
            )
        else:
            pyray.draw_circle(cx, cy, int(rect.width * 0.22), with_alpha(LIVE_CYAN, 72))
            pyray.draw_circle_lines(cx, cy, int(rect.width * 0.28), with_alpha(LIVE_CYAN, 180))
            pyray.draw_rectangle_rec(
                pyray.Rectangle(cx - 54, cy - 10, 108, 20),
                with_alpha(LIVE_CYAN, int(90 + pulse * 80)),
            )
            pyray.draw_rectangle_rec(
                pyray.Rectangle(cx - 8, cy - 62, 16, 124),
                with_alpha(LIVE_GOLD, 92),
            )


def _wrap_text(text: str, font_size: int, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if pyray.measure_text(candidate, font_size) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines
