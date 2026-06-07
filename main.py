# /// script
from __future__ import annotations

import asyncio
import math
import random

import pygame

import core.raylib_api as pyray
import ui.ui as ui_theme

from assets.assets import Assets
from core.context import GameContext
from core.scene_ids import EXIT_SCENE, MENU_SCENE
from scenes.registry import SCENE_MUSIC, build_scene_table
from ui.layout import DEFAULT_LAYOUT
from ui.notifications import NotificationManager
from utils.audio import AudioManager
from utils.effects import glitch_effect, set_camera, update_camera_shake, update_glitch
from utils.replay import ReplayRecorder


BLOOM_INTENSITY = 0.18
SCANLINE_ALPHA = 18
VIGNETTE_ALPHA = 76


class Game:
    def __init__(self) -> None:
        self.ctx = GameContext()
        self.ctx.apply_layout(DEFAULT_LAYOUT)
        self.audio = AudioManager()
        self.notifications = NotificationManager()
        self.replay_recorder = ReplayRecorder()
        self.ctx.audio_manager = self.audio
        self.ctx.notification_manager = self.notifications
        self.ctx.replay_recorder = self.replay_recorder

        self.current_scene_index = MENU_SCENE
        self.scenes = build_scene_table(self.ctx)
        self.scene_target = None
        self.scanline_overlay: pygame.Surface | None = None
        self.vignette_overlay: pygame.Surface | None = None
        self.glitch_shader = None
        self.bloom_shader = None
        self.scanlines_shader = None

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    def run(self) -> None:
        self._initialize()
        try:
            while not pyray.window_should_close():
                if not self._tick():
                    break
        finally:
            self._shutdown()

    async def run_async(self) -> None:
        self._initialize()
        try:
            while not pyray.window_should_close():
                if not self._tick():
                    break
                await asyncio.sleep(0)
        finally:
            self._shutdown()

    def _initialize(self) -> None:
        cfg = self.ctx.cfg

        pyray.init_window(cfg.window_width, cfg.window_height, "Pacman")
        pyray.set_target_fps(cfg.fps)
        self.ctx.camera = pyray.create_camera_2d()
        set_camera(self.ctx.camera)
        self.ctx.screen_flash.set_size(cfg.window_width, cfg.window_height)

        self.scene_target = pyray.load_render_texture(cfg.window_width, cfg.window_height)
        self.glitch_shader = self._load_glitch_shader()
        self.bloom_shader = self._load_bloom_shader()
        self.scanlines_shader = self._load_scanlines_shader()
        self._build_post_effect_surfaces()
        self.audio.initialize()
        from utils.font_manager import FontManager
        FontManager.initialize()

        self.current_scene_index = MENU_SCENE
        self.current_scene.enter_tree()
        self._sync_scene_audio()

    def _tick(self) -> bool:
        cfg = self.ctx.cfg
        dt = pyray.get_frame_time()
        ui_theme.set_visual_theme(self.ctx.theme_name())
        if pyray.is_key_pressed(pyray.KEY_F10):
            self.ctx.set_capture_mode_enabled(not self.ctx.capture_mode_enabled())

        self.current_scene.update(dt)
        self.audio.update(self.ctx)
        self.notifications.update(dt)

        nxt = self.current_scene.consume_switch_request()
        if nxt is not None:
            if nxt == EXIT_SCENE:
                return False
            self.switch_scene(nxt)

        update_glitch(dt)

        pyray.begin_texture_mode(self.scene_target)
        pyray.clear_background(pyray.BLACK)
        update_camera_shake(dt)
        pyray.begin_mode_2d(self.ctx.camera[0])
        self.current_scene.draw()
        pyray.end_mode_2d()
        pyray.end_texture_mode()

        pyray.begin_drawing()
        pyray.clear_background(pyray.BLACK)
        self._draw_final()
        self.notifications.draw(cfg.window_width, cfg.window_height)
        pyray.end_drawing()
        return True

    def _shutdown(self) -> None:
        if self.scene_target is not None:
            pyray.unload_render_texture(self.scene_target)
        from utils.font_manager import FontManager
        FontManager.shutdown()
        self.audio.shutdown()
        Assets.unload_all()
        pyray.close_window()

    def switch_scene(self, index: int) -> None:
        if index not in self.scenes:
            raise IndexError(f"Scene index out of range: {index}")
        self.current_scene.exit_tree()
        self.current_scene_index = index
        self.current_scene.enter_tree()
        self._sync_scene_audio()

    def _sync_scene_audio(self) -> None:
        scene_music = SCENE_MUSIC.get(self.current_scene_index, "menu")
        self.audio.set_scene_music(scene_music, self.ctx)

    def _build_post_effect_surfaces(self) -> None:
        cfg = self.ctx.cfg
        size = (cfg.window_width, cfg.window_height)
        self.scanline_overlay = pygame.Surface(size, pygame.SRCALPHA)
        for y in range(0, cfg.window_height, 2):
            pygame.draw.line(self.scanline_overlay, (0, 0, 0, SCANLINE_ALPHA), (0, y), (cfg.window_width, y), 1)

        self.vignette_overlay = pygame.Surface(size, pygame.SRCALPHA)
        cx = cfg.window_width / 2
        cy = cfg.window_height / 2
        max_distance = math.hypot(cx, cy)
        for radius in range(int(max_distance), 0, -18):
            t = 1.0 - radius / max_distance
            alpha = int(VIGNETTE_ALPHA * t * t)
            pygame.draw.circle(self.vignette_overlay, (0, 0, 0, alpha), (int(cx), int(cy)), radius, 18)

    def _draw_final(self) -> None:
        if self.scene_target is None:
            return

        screen = pyray.get_drawing_surface()
        scene = self.scene_target.surface
        if glitch_effect.is_active():
            self._draw_glitch_surface(screen, scene)
        else:
            screen.blit(scene, (0, 0))
        self._apply_bloom(screen, scene)
        if self.scanline_overlay is not None:
            screen.blit(self.scanline_overlay, (0, 0))
        if self.vignette_overlay is not None:
            screen.blit(self.vignette_overlay, (0, 0))

    def _load_glitch_shader(self):
        return None

    def _load_bloom_shader(self):
        return None

    def _load_scanlines_shader(self):
        return None

    def _apply_bloom(self, screen: pygame.Surface, scene: pygame.Surface) -> None:
        width, height = scene.get_size()
        small_size = (max(1, width // 3), max(1, height // 3))
        bloom = pygame.transform.smoothscale(scene, small_size)
        bloom = pygame.transform.smoothscale(bloom, (width, height))
        bloom.set_alpha(int(255 * BLOOM_INTENSITY))
        screen.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _draw_glitch_surface(self, screen: pygame.Surface, scene: pygame.Surface) -> None:
        glitched = scene.copy()
        width, height = scene.get_size()
        amount = max(0.0, min(1.0, float(glitch_effect.intensity)))
        time_s = float(self.ctx.visual_time)
        band_count = max(3, int(8 + amount * 10))
        for index in range(band_count):
            y = random.randrange(0, max(1, height))
            band_h = max(2, int(3 + amount * 12 + (index % 3) * 2))
            jitter = random.randint(-18, 18)
            shift = int((jitter + math.sin(time_s * 35.0 + index * 1.7) * 10) * amount)
            src = pygame.Rect(0, y, width, min(band_h, height - y))
            if src.height <= 0:
                continue
            glitched.blit(scene, (shift, y), src)
            if shift > 0:
                glitched.blit(scene, (shift - width, y), src)
            elif shift < 0:
                glitched.blit(scene, (shift + width, y), src)

        screen.blit(glitched, (0, 0))

        red = scene.copy()
        red.fill((255, 40, 90, int(42 * amount)), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(red, (int(3 * amount), 0), special_flags=pygame.BLEND_RGB_ADD)
        cyan = scene.copy()
        cyan.fill((40, 220, 255, int(36 * amount)), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(cyan, (int(-3 * amount), 0), special_flags=pygame.BLEND_RGB_ADD)


async def main() -> None:
    game = Game()
    await game.run_async()


def cli_main() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
