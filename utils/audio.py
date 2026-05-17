from __future__ import annotations

from pathlib import Path
from typing import Any

import core.raylib_api as pyray


def _clamp_volume(value: object, default: float) -> float:
    try:
        volume = float(value)
    except (TypeError, ValueError):
        volume = default
    return max(0.0, min(1.0, volume))


class AudioManager:
    MUSIC_FILES = {
        "menu": "assets/audio/music/menu_loop.ogg",
        "game": "assets/audio/music/game_loop.ogg",
        "result": "assets/audio/music/result_loop.ogg",
        "pause": "assets/audio/music/pause_loop.ogg",
        "options": "assets/audio/music/options_loop.ogg",
    }

    SFX_FILES = {
        "pellet_eat": "assets/sfx/pellet_eat.wav",
        "power_eat": "assets/sfx/power_eat.wav",
        "ghost_eat": "assets/sfx/ghost_eat.wav",
        "death": "assets/sfx/death.wav",
        "level_clear": "assets/sfx/level_clear.wav",
        "dot": "assets/sfx/pellet_eat.wav",
        "power": "assets/sfx/power_eat.wav",
        "ghost": "assets/sfx/ghost_eat.wav",
        "win": "assets/sfx/level_clear.wav",
        "lose": "assets/sfx/death.wav",
        "cherry": "assets/sfx/pellet_eat.wav",
        "ui_confirm": "assets/sfx/pellet_eat.wav",
        "ui_back": "assets/sfx/death.wav",
        "start_run": "assets/sfx/power_eat.wav",
    }

    def __init__(self) -> None:
        self.ready = False
        self.sounds: dict[str, Any] = {}
        self.music_streams: dict[str, Any] = {}
        self.current_scene_music: str | None = None
        self._sfx_paths_loaded: dict[str, Any] = {}

    def initialize(self) -> None:
        try:
            pyray.init_audio_device()
            self.ready = bool(pyray.is_audio_device_ready())
        except Exception:
            self.ready = False

        if not self.ready:
            return

        for name, path in self.SFX_FILES.items():
            sound = self._load_shared_sound(path)
            if sound is not None:
                self.sounds[name] = sound

        for name, path in self.MUSIC_FILES.items():
            music = self._safe_load_music(path)
            if music is not None:
                self.music_streams[name] = music

    def shutdown(self) -> None:
        if not self.ready:
            return

        for sound in self._sfx_paths_loaded.values():
            try:
                pyray.unload_sound(sound)
            except Exception:
                pass
        self.sounds.clear()
        self._sfx_paths_loaded.clear()

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

        music_volume = _clamp_volume(getattr(ctx.cfg, "music_volume", 0.45), 0.45) if ctx.music_enabled() else 0.0
        sfx_volume = _clamp_volume(getattr(ctx.cfg, "sfx_volume", 0.75), 0.75) if ctx.sfx_enabled() else 0.0

        for music in self.music_streams.values():
            try:
                pyray.set_music_volume(music, music_volume)
            except Exception:
                pass
        for sound in self._sfx_paths_loaded.values():
            try:
                pyray.set_sound_volume(sound, sfx_volume)
            except Exception:
                pass

    def set_scene_music(self, scene_key: str, ctx) -> None:
        self.play_music(scene_key, ctx)

    def play_music(self, name: str, ctx=None) -> None:
        if not self.ready:
            return
        if name == self.current_scene_music:
            return

        self.stop_music()
        self.current_scene_music = name
        if ctx is not None:
            self.sync_settings(ctx)
            if not ctx.music_enabled():
                return

        music = self.music_streams.get(name)
        if music is None:
            return
        try:
            pyray.play_music_stream(music)
        except Exception:
            pass

    def stop_music(self) -> None:
        if not self.ready:
            return
        for music in self.music_streams.values():
            try:
                pyray.stop_music_stream(music)
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

    def play_sfx(self, name: str, ctx=None) -> None:
        if not self.ready:
            return
        if ctx is not None and not ctx.sfx_enabled():
            return
        if ctx is not None:
            self.sync_settings(ctx)

        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            pyray.play_sound(sound)
        except Exception:
            pass

    def _load_shared_sound(self, path: str):
        if path not in self._sfx_paths_loaded:
            sound = self._safe_load_sound(path)
            if sound is not None:
                self._sfx_paths_loaded[path] = sound
        return self._sfx_paths_loaded.get(path)

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
