from __future__ import annotations

import core.raylib_api as pyray
import ui.ui as ui_theme

from assets.assets import Assets
from core.context import GameContext
from core.scene_ids import EXIT_SCENE, MENU_SCENE
from scenes.registry import SCENE_MUSIC, build_scene_table
from ui.layout import DEFAULT_LAYOUT
from utils.audio import AudioManager
from utils.effects import glitch_effect, set_camera, update_camera_shake, update_glitch


class Game:
    def __init__(self) -> None:
        self.ctx = GameContext()
        self.ctx.apply_layout(DEFAULT_LAYOUT)
        self.audio = AudioManager()
        self.ctx.audio_manager = self.audio

        self.current_scene_index = MENU_SCENE
        self.scenes = build_scene_table(self.ctx)
        self.scene_target = None
        self.glitch_shader = None
        self.glitch_time_loc = -1
        self.glitch_intensity_loc = -1

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    def run(self) -> None:
        cfg = self.ctx.cfg

        pyray.init_window(cfg.window_width, cfg.window_height, "Pacman")
        pyray.set_target_fps(cfg.fps)
        self.ctx.camera = pyray.create_camera_2d()
        set_camera(self.ctx.camera)
        self.ctx.screen_flash.set_size(cfg.window_width, cfg.window_height)
        self.scene_target = pyray.load_render_texture(cfg.window_width, cfg.window_height)
        self._load_glitch_shader()
        self.audio.initialize()

        self.current_scene_index = MENU_SCENE
        self.current_scene.enter_tree()
        self._sync_scene_audio()

        try:
            while not pyray.window_should_close():
                dt = pyray.get_frame_time()
                ui_theme.set_visual_theme(self.ctx.theme_name())
                if pyray.is_key_pressed(pyray.KEY_F10):
                    self.ctx.set_capture_mode_enabled(not self.ctx.capture_mode_enabled())

                self.current_scene.update(dt)
                self.audio.update(self.ctx)

                nxt = self.current_scene.consume_switch_request()
                if nxt is not None:
                    if nxt == EXIT_SCENE:
                        break
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
                self._draw_scene_target()
                pyray.end_drawing()

        finally:
            if self.glitch_shader is not None:
                pyray.unload_shader(self.glitch_shader)
            if self.scene_target is not None:
                pyray.unload_render_texture(self.scene_target)
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
            print(f"[Shader] Glitch shader unavailable: {exc}")
            self.glitch_shader = None

    def _draw_scene_target(self) -> None:
        if self.scene_target is None:
            return

        cfg = self.ctx.cfg
        source = pyray.Rectangle(0, 0, cfg.window_width, -cfg.window_height)
        target_pos = pyray.Vector2(0, 0)
        use_shader = self.glitch_shader is not None and glitch_effect.is_active()
        if use_shader:
            time_value = pyray.rl.ffi.new("float *", float(self.ctx.visual_time))
            intensity_value = pyray.rl.ffi.new("float *", float(glitch_effect.intensity))
            pyray.set_shader_value(self.glitch_shader, self.glitch_time_loc, time_value, pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.set_shader_value(self.glitch_shader, self.glitch_intensity_loc, intensity_value, pyray.rl.SHADER_UNIFORM_FLOAT)
            pyray.begin_shader_mode(self.glitch_shader)

        pyray.draw_texture_rec(self.scene_target.texture, source, target_pos, pyray.WHITE)

        if use_shader:
            pyray.end_shader_mode()


def main() -> None:
    Game().run()



if __name__ == "__main__":
    main()
