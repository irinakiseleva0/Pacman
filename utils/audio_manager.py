from __future__ import annotations

from pathlib import Path
from typing import Any

import core.raylib_api as pyray


class AudioManager:
    MUSIC_FILES = {
        "menu": "assets/audio/music/menu_loop.ogg",
        "game": "assets/audio/music/game_loop.ogg",
        "result": "assets/audio/music/result_loop.ogg",
        "pause": "assets/audio/music/pause_loop.ogg",
        "options": "assets/audio/music/options_loop.ogg",
    }

    SFX_FILES = {
        "ui_confirm": "assets/audio/sfx/ui_confirm.wav",
        "ui_back": "assets/audio/sfx/ui_back.wav",
        "start_run": "assets/audio/sfx/start_run.wav",
        "dot": "assets/audio/sfx/dot.wav",
        "power": "assets/audio/sfx/power.wav",
        "cherry": "assets/audio/sfx/cherry.wav",
        "ghost": "assets/audio/sfx/ghost.wav",
        "death": "assets/audio/sfx/death.wav",
        "win": "assets/audio/sfx/win.wav",
        "lose": "assets/audio/sfx/lose.wav",
    }

    def __init__(self) -> None:
        self.ready = False
        self.sounds: dict[str, Any] = {}
        self.music_streams: dict[str, Any] = {}
        self.current_scene_music: str | None = None

    def initialize(self) -> None:
        try:
            pyray.init_audio_device()
            self.ready = bool(pyray.is_audio_device_ready())
        except Exception:
            self.ready = False

        if not self.ready:
            return

        for name, path in self.SFX_FILES.items():
            sound = self._safe_load_sound(path)
            if sound is not None:
                self.sounds[name] = sound

        for name, path in self.MUSIC_FILES.items():
            music = self._safe_load_music(path)
            if music is not None:
                self.music_streams[name] = music

    def shutdown(self) -> None:
        if not self.ready:
            return

        for sound in self.sounds.values():
            try:
                pyray.unload_sound(sound)
            except Exception:
                pass
        self.sounds.clear()

        for music in self.music_streams.values():
            try:
                pyray.stop_music_stream(music)
            except Exception:
                pass
            try:
                pyray.unload_music_stream(music)
            except Exception:
                pass
        self.music_streams.clear()

        try:
            pyray.close_audio_device()
        except Exception:
            pass
        self.ready = False

    def sync_settings(self, ctx) -> None:
        if not self.ready:
            return

        music_volume = 0.45 if ctx.music_enabled() else 0.0
        sfx_volume = 0.75 if ctx.sfx_enabled() else 0.0

        for music in self.music_streams.values():
            try:
                pyray.set_music_volume(music, music_volume)
            except Exception:
                pass
        for sound in self.sounds.values():
            try:
                pyray.set_sound_volume(sound, sfx_volume)
            except Exception:
                pass

    def set_scene_music(self, scene_key: str, ctx) -> None:
        if not self.ready:
            return
        if scene_key == self.current_scene_music:
            return

        for music in self.music_streams.values():
            try:
                pyray.stop_music_stream(music)
            except Exception:
                pass

        self.current_scene_music = scene_key
        self.sync_settings(ctx)
        if not ctx.music_enabled():
            return

        music = self.music_streams.get(scene_key)
        if music is None:
            return
        try:
            pyray.play_music_stream(music)
        except Exception:
            pass

    def update(self, ctx) -> None:
        if not self.ready:
            return
        self.sync_settings(ctx)
        if not ctx.music_enabled():
            return
        if self.current_scene_music is None:
            return
        music = self.music_streams.get(self.current_scene_music)
        if music is None:
            return
        try:
            pyray.update_music_stream(music)
            if not pyray.is_music_stream_playing(music):
                pyray.play_music_stream(music)
        except Exception:
            pass

    def play_sfx(self, name: str, ctx) -> None:
        if not self.ready or not ctx.sfx_enabled():
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            pyray.play_sound(sound)
        except Exception:
            pass

    def _safe_load_sound(self, path: str):
        if not Path(path).exists():
            return None
        try:
            return pyray.load_sound(path)
        except Exception:
            return None

    def _safe_load_music(self, path: str):
        if not Path(path).exists():
            return None
        try:
            return pyray.load_music_stream(path)
        except Exception:
            return None
