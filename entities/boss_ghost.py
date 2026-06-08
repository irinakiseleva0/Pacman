from __future__ import annotations

import math

import core.raylib_api as pyray
from core import colors

from entities.ghost import Ghost
from ui.ui import LIVE_CYAN, LIVE_GOLD, LIVE_PINK
from utils.visual_effects import with_alpha


class BossGhost(Ghost):
    MAX_HP = 3
    HIT_SCORE = 700
    DEFEAT_SCORE = 3000
    SKIN_REWARD = "Intruder Husk"

    def __init__(self, ctx, *, split_clone: bool = False) -> None:
        super().__init__(ctx)
        self.color = colors.VIOLET if not split_clone else colors.SKYBLUE
        self.max_hp = 1 if split_clone else self.MAX_HP
        self.hp = self.max_hp
        self.split_clone = split_clone
        self.split_spawned = split_clone
        self.defeated = False
        self.berserk_extra_tick = False
        self.scatter_target = (self.ctx.cfg.map_width // 2, self.ctx.cfg.map_height // 2)

    @property
    def phase(self) -> str:
        if self.split_clone:
            return "split"
        if self.hp <= 1:
            return "berserk"
        if self.hp <= 2:
            return "split"
        return "chase"

    def occupied_tiles(self) -> set[tuple[int, int]]:
        return {
            (self.x, self.y),
            (self.x + 1, self.y),
            (self.x, self.y + 1),
            (self.x + 1, self.y + 1),
        }

    def overlaps(self, actor) -> bool:
        return (getattr(actor, "x", None), getattr(actor, "y", None)) in self.occupied_tiles()

    def hit_score(self) -> int:
        return self.DEFEAT_SCORE if self.hp <= 1 and not self.split_clone else self.HIT_SCORE

    def on_eaten(self, game_map=None) -> int:
        score = self.hit_score()
        self.hp -= 1
        self.respawn_lock_ticks = 10
        self.returning_home = False

        if self.hp <= 0:
            self.defeated = True
            self._unlock_skin()
            return score

        if self.phase == "split":
            self._spawn_split_echo(game_map)
        return score

    def _spawn_split_echo(self, game_map) -> None:
        if self.split_spawned or game_map is None:
            return

        self.split_spawned = True
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            x = self.x + dx
            y = self.y + dy
            if not self._can_occupy(game_map, x, y):
                continue
            clone = BossGhost(self.ctx, split_clone=True)
            clone.set_spawn(x, y)
            clone.last_dx = -dx // max(1, abs(dx)) if dx else 0
            clone.last_dy = -dy // max(1, abs(dy)) if dy else 0
            game_map.add_actor(clone)
            self.ctx.visual.floating_text.add_text("SIGNAL SPLIT", x * 16 - 22, y * 16 - 26, LIVE_CYAN, 0.8, 12)
            return

    def _can_occupy(self, game_map, x: int, y: int) -> bool:
        for px, py in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
            cell = game_map.get_cell(px, py)
            if cell is None or cell.is_blocking(self):
                return False
        return True

    def _valid_moves(self, game_map) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            if self._can_occupy(game_map, self.x + dx, self.y + dy):
                moves.append((dx, dy))
        return moves

    def _unlock_skin(self) -> None:
        profile = getattr(self.ctx, "profile", None)
        if not isinstance(profile, dict) or self.split_clone:
            return
        skins = profile.setdefault("unlocked_skins", {})
        if int(skins.get(self.SKIN_REWARD, 0)) == 0:
            skins[self.SKIN_REWARD] = 1
            save_profile = getattr(self.ctx, "save_profile", None)
            if callable(save_profile):
                save_profile()

    def _update_mode(self) -> None:
        if self.phase == "berserk":
            self.mode = "chase"
            return
        super()._update_mode()

    def personality_score_adjustment(self, dx: int, dy: int, new_x: int, new_y: int, pacman) -> float:
        if self.phase == "berserk":
            return -0.8
        if self.phase == "split":
            return -0.25 if (new_x + new_y) % 2 == 0 else 0.25
        return -0.35

    def process(self) -> None:
        if self.defeated:
            return

        super().process()
        if self.phase == "berserk" and not self.defeated:
            self.berserk_extra_tick = not self.berserk_extra_tick
            if self.berserk_extra_tick:
                super().process()

    def draw(self) -> None:
        if self.defeated:
            return

        cfg = self.ctx.cfg
        tile = cfg.tile_size
        time_s = getattr(self.ctx, "visual_time", 0.0)
        px = cfg.board_offset_x + self.x * tile + tile
        py = cfg.board_offset_y + self.y * tile + tile
        phase = self.phase
        base = colors.RED if phase == "berserk" else LIVE_PINK if phase == "split" else colors.VIOLET
        if self.split_clone:
            base = LIVE_CYAN
        pulse = 0.5 + 0.5 * math.sin(time_s * (10.0 if phase == "berserk" else 5.5))
        radius = max(12, tile - 3)
        aura = radius + 12 + int(pulse * 8)

        pyray.draw_circle(px, py, aura + 16, with_alpha(base, 18))
        pyray.draw_circle(px, py, aura + 7, with_alpha(LIVE_GOLD if phase == "berserk" else base, 28))
        pyray.draw_circle(px, py, radius, with_alpha(base, 232))
        pyray.draw_circle(px, py - tile // 4, max(7, tile // 3), with_alpha(colors.WHITE, 28))

        eye_y = py - tile // 5
        eye_dx = tile // 3
        for eye_x in (px - eye_dx, px + eye_dx):
            pyray.draw_circle(eye_x, eye_y, max(4, tile // 5), colors.WHITE)
            pyray.draw_circle(eye_x, eye_y, max(2, tile // 11), colors.BLACK)

        hp_width = tile * 2
        hp_ratio = max(0.0, self.hp / max(1, self.max_hp))
        bar_x = px - hp_width // 2
        bar_y = py - tile - 12
        pyray.draw_rectangle_rec(pyray.Rectangle(bar_x, bar_y, hp_width, 4), with_alpha(colors.BLACK, 170))
        pyray.draw_rectangle_rec(pyray.Rectangle(bar_x, bar_y, hp_width * hp_ratio, 4), with_alpha(LIVE_GOLD, 230))
        pyray.draw_text("INTRUDER", int(px - tile), int(py + tile - 4), max(9, tile // 3), with_alpha(colors.WHITE, 180))
