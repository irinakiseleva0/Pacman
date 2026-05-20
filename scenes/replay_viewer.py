from __future__ import annotations

import core.raylib_api as pyray
from raylib import colors

from core.scene import Scene
from core.scene_ids import MENU_SCENE, RESULT_SCENE
from ui import gamepad
from ui.ui import (
    LIVE_CYAN,
    LIVE_GOLD,
    LIVE_PINK,
    PANEL_ACCENT,
    TEXT_DIM,
    button_clicked,
    centered_rect,
    draw_arcade_background,
    draw_button,
    draw_glass_card,
    draw_panel,
    draw_scene_footer,
    draw_text_centered,
)
from utils.replay import ReplayPlayer
from utils.visual_effects import with_alpha


class ReplayViewerScene(Scene):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.player: ReplayPlayer | None = None
        self.panel = None
        self.btn_back = None
        self.play_accumulator = 0.0
        self.return_scene = RESULT_SCENE

    def enter_tree(self) -> None:
        cfg = self.ctx.cfg
        path = self.ctx.selected_replay_path
        self.player = ReplayPlayer(path) if path else None
        self.ctx.replay_player = self.player
        self.play_accumulator = 0.0
        self.return_scene = RESULT_SCENE if path and self.ctx.last_result else MENU_SCENE
        panel_width = min(980, cfg.window_width - 80)
        panel_height = min(760, cfg.window_height - 80)
        self.panel = pyray.Rectangle(
            cfg.window_width // 2 - panel_width // 2,
            max(36, cfg.window_height // 2 - panel_height // 2),
            panel_width,
            panel_height,
        )
        self.btn_back = centered_rect(cfg.window_width // 2, int(self.panel.y + self.panel.height - 74), 240, 52)

    def update(self, dt: float) -> None:
        self.ctx.visual_time += dt
        if pyray.is_key_pressed(pyray.KEY_ESCAPE) or gamepad.back_pressed() or button_clicked(self.btn_back):
            self.ctx.play_sfx("ui_back")
            self.request_switch(self.return_scene)
            return
        if self.player is None:
            return
        self.play_accumulator += dt
        while self.play_accumulator >= 1 / 60:
            self.player.seek_next()
            self.play_accumulator -= 1 / 60

    def draw(self) -> None:
        cfg = self.ctx.cfg
        draw_arcade_background(cfg.window_width, cfg.window_height, self.ctx.visual_time)
        if self.panel is None:
            self.enter_tree()
        panel = self.panel
        draw_panel(panel, "REPLAY VIEWER", time_s=self.ctx.visual_time)
        draw_text_centered("REPLAY VIEWER", int(panel.x + panel.width / 2), int(panel.y + 24), 18, PANEL_ACCENT)

        if self.player is None:
            draw_text_centered("NO REPLAY SELECTED", int(panel.x + panel.width / 2), int(panel.y + 180), 28, LIVE_PINK)
            draw_button(self.btn_back, "BACK", focused=True, time_s=self.ctx.visual_time)
            return

        meta = self.player.metadata
        draw_text_centered(
            f"SCORE {int(meta.get('score', 0))}  |  SEED {int(meta.get('seed', 0)):06d}",
            int(panel.x + panel.width / 2),
            int(panel.y + 58),
            16,
            LIVE_GOLD,
        )
        board = pyray.Rectangle(panel.x + 54, panel.y + 98, panel.width - 108, panel.height - 210)
        draw_glass_card(board, accent_color=LIVE_CYAN, glow_alpha=12, fill_alpha=150, time_s=self.ctx.visual_time)
        self._draw_playback_board(board)

        progress = 0.0
        if self.player.total_frames > 0:
            progress = min(1.0, self.player.frame / self.player.total_frames)
        bar = pyray.Rectangle(board.x + 24, board.y + board.height + 22, board.width - 48, 10)
        pyray.draw_rectangle_rec(bar, with_alpha(TEXT_DIM, 90))
        pyray.draw_rectangle_rec(pyray.Rectangle(bar.x, bar.y, bar.width * progress, bar.height), LIVE_CYAN)
        draw_text_centered(f"FRAME {self.player.frame}/{self.player.total_frames}", int(panel.x + panel.width / 2), int(bar.y + 18), 13, TEXT_DIM)
        draw_button(self.btn_back, "BACK", focused=True, time_s=self.ctx.visual_time)
        draw_scene_footer(panel)

    def _draw_playback_board(self, rect) -> None:
        if self.player is None:
            return
        state = self.player.state
        ghosts = state.get("ghost_positions", [])
        pac = state.get("pacman_pos", {})
        max_x = max([int(pac.get("x", 1))] + [int(ghost.get("x", 1)) for ghost in ghosts] + [1])
        max_y = max([int(pac.get("y", 1))] + [int(ghost.get("y", 1)) for ghost in ghosts] + [1])
        cell = max(12, min(int((rect.width - 48) / max(1, max_x + 1)), int((rect.height - 48) / max(1, max_y + 1))))
        origin_x = int(rect.x + rect.width / 2 - (max_x + 1) * cell / 2)
        origin_y = int(rect.y + rect.height / 2 - (max_y + 1) * cell / 2)
        for x in range(max_x + 1):
            for y in range(max_y + 1):
                if (x + y) % 2 == 0:
                    pyray.draw_circle(origin_x + x * cell + cell // 2, origin_y + y * cell + cell // 2, 1, with_alpha(LIVE_CYAN, 54))
        for ghost in ghosts:
            gx = origin_x + int(ghost.get("x", 0)) * cell + cell // 2
            gy = origin_y + int(ghost.get("y", 0)) * cell + cell // 2
            pyray.draw_circle(gx, gy, max(5, cell // 3), with_alpha(LIVE_PINK, 220))
            pyray.draw_circle(gx - 3, gy - 2, 2, colors.WHITE)
            pyray.draw_circle(gx + 3, gy - 2, 2, colors.WHITE)
        if pac:
            px = origin_x + int(pac.get("x", 0)) * cell + cell // 2
            py = origin_y + int(pac.get("y", 0)) * cell + cell // 2
            pyray.draw_circle(px, py, max(6, cell // 3), LIVE_GOLD)
