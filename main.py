from __future__ import annotations

import asyncio
import sys

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


BLOOM_INTENSITY    = 0.45
SCANLINE_STRENGTH  = 0.04
VIGNETTE_STRENGTH  = 0.0


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

        self.glitch_shader = None
        self.glitch_time_loc = -1
        self.glitch_intensity_loc = -1

        self.bloom_shader = None
        self.bloom_resolution_loc = -1
        self.bloom_intensity_loc = -1
        self.bloom_target = None 

        self.scanlines_shader = None
        self.scanlines_time_loc = -1
        self.scanlines_scan_loc = -1
        self.scanlines_vig_loc = -1

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
        self.bloom_target  = pyray.load_render_texture(cfg.window_width, cfg.window_height)

        self._load_glitch_shader()
        self._load_bloom_shader()
        self._load_scanlines_shader()
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

        self._apply_bloom()

        pyray.begin_drawing()
        pyray.clear_background(pyray.BLACK)
        self._draw_final()
        self.notifications.draw(cfg.window_width, cfg.window_height)
        pyray.end_drawing()
        return True

    def _shutdown(self) -> None:
        for shader in [self.glitch_shader, self.bloom_shader, self.scanlines_shader]:
            if shader is not None:
                pyray.unload_shader(shader)
        for rt in [self.scene_target, self.bloom_target]:
            if rt is not None:
                pyray.unload_render_texture(rt)
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

    def _load_glitch_shader(self) -> None:
        try:
            self.glitch_shader = pyray.load_shader(None, "assets/shaders/glitch.fs")
            self.glitch_time_loc = pyray.get_shader_location(self.glitch_shader, "time")
            self.glitch_intensity_loc = pyray.get_shader_location(self.glitch_shader, "intensity")
        except Exception as exc:
            print(f"[Shader] Glitch unavailable: {exc}")
            self.glitch_shader = None

    def _load_bloom_shader(self) -> None:
        try:
            self.bloom_shader = pyray.load_shader(None, "assets/shaders/bloom.fs")
            self.bloom_resolution_loc = pyray.get_shader_location(self.bloom_shader, "resolution")
            self.bloom_intensity_loc  = pyray.get_shader_location(self.bloom_shader, "intensity")
        except Exception as exc:
            print(f"[Shader] Bloom unavailable: {exc}")
            self.bloom_shader = None

    def _load_scanlines_shader(self) -> None:
        try:
            self.scanlines_shader = pyray.load_shader(None, "assets/shaders/scanlines.fs")
            self.scanlines_time_loc = pyray.get_shader_location(self.scanlines_shader, "time")
            self.scanlines_scan_loc = pyray.get_shader_location(self.scanlines_shader, "scanline_strength")
            self.scanlines_vig_loc  = pyray.get_shader_location(self.scanlines_shader, "vignette_strength")
        except Exception as exc:
            print(f"[Shader] Scanlines unavailable: {exc}")
            self.scanlines_shader = None


    def _apply_bloom(self) -> None:
        """Проход bloom: scene_target → bloom_target."""
        if self.bloom_target is None:
            return

        cfg = self.ctx.cfg
        source = pyray.Rectangle(0, 0, cfg.window_width, -cfg.window_height)
        pos = pyray.Vector2(0, 0)

        pyray.begin_texture_mode(self.bloom_target)
        pyray.clear_background(pyray.BLACK)

        if self.bloom_shader is not None:
            res = pyray.rl.ffi.new("float[2]", [float(cfg.window_width), float(cfg.window_height)])
            intensity = pyray.rl.ffi.new("float *", BLOOM_INTENSITY)
            pyray.set_shader_value(self.bloom_shader, self.bloom_resolution_loc, res, pyray.rl.SHADER_UNIFORM_VEC2)
            pyray.set_shader_value(self.bloom_shader, self.bloom_intensity_loc, intensity, pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.begin_shader_mode(self.bloom_shader)

        pyray.draw_texture_rec(self.scene_target.texture, source, pos, pyray.WHITE)

        if self.bloom_shader is not None:
            pyray.end_shader_mode()

        pyray.end_texture_mode()

    def _draw_final(self) -> None:
        cfg = self.ctx.cfg
        src_texture = self.bloom_target if self.bloom_target is not None else self.scene_target
        if src_texture is None:
            return

        source = pyray.Rectangle(0, 0, cfg.window_width, -cfg.window_height)
        pos = pyray.Vector2(0, 0)

        use_glitch = self.glitch_shader is not None and glitch_effect.is_active()
        use_scan   = self.scanlines_shader is not None and not use_glitch

        if use_glitch:
            time_val = pyray.rl.ffi.new("float *", float(self.ctx.visual_time))
            inten_val = pyray.rl.ffi.new("float *", float(glitch_effect.intensity))
            pyray.set_shader_value(self.glitch_shader, self.glitch_time_loc, time_val, pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.set_shader_value(self.glitch_shader, self.glitch_intensity_loc, inten_val, pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.begin_shader_mode(self.glitch_shader)
        elif use_scan:
            time_val = pyray.rl.ffi.new("float *", float(self.ctx.visual_time))
            scan_val = pyray.rl.ffi.new("float *", SCANLINE_STRENGTH)
            vig_val  = pyray.rl.ffi.new("float *", VIGNETTE_STRENGTH)
            pyray.set_shader_value(self.scanlines_shader, self.scanlines_time_loc, time_val, pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.set_shader_value(self.scanlines_shader, self.scanlines_scan_loc, scan_val, pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.set_shader_value(self.scanlines_shader, self.scanlines_vig_loc,  vig_val,  pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.begin_shader_mode(self.scanlines_shader)

        pyray.draw_texture_rec(src_texture.texture, source, pos, pyray.WHITE)

        if use_glitch or use_scan:
            pyray.end_shader_mode()


def main() -> None:
    game = Game()
    if sys.platform == "emscripten":
        asyncio.get_event_loop().create_task(game.run_async())
        return
    game.run()


if __name__ == "__main__":
    main()
