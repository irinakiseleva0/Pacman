from __future__ import annotations

from pathlib import Path

import pygame


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
        "pellet_eat": "assets/sfx/pellet_eat.ogg",
        "power_eat": "assets/sfx/power_eat.ogg",
        "ghost_eat": "assets/sfx/ghost_eat.ogg",
        "death": "assets/sfx/death.ogg",
        "level_clear": "assets/sfx/level_clear.ogg",
        "dot": "assets/sfx/pellet_eat.ogg",
        "power": "assets/sfx/power_eat.ogg",
        "ghost": "assets/sfx/ghost_eat.ogg",
        "win": "assets/sfx/level_clear.ogg",
        "lose": "assets/sfx/death.ogg",
        "cherry": "assets/sfx/pellet_eat.ogg",
        "ui_confirm": "assets/sfx/pellet_eat.ogg",
        "ui_back": "assets/sfx/death.ogg",
        "start_run": "assets/sfx/power_eat.ogg",
    }

    def __init__(self) -> None:
        self.ready = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.music_streams: dict[str, str] = {}
        self.current_scene_music: str | None = None
        self._sfx_paths_loaded: dict[str, pygame.mixer.Sound] = {}
        self._music_volume = 0.45
        self._sfx_volume = 0.75

    def initialize(self) -> None:
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.ready = True
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

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.sounds.clear()
        self._sfx_paths_loaded.clear()
        self.music_streams.clear()
        self.current_scene_music = None
        self.ready = False

    def sync_settings(self, ctx) -> None:
        if not self.ready:
            return

        self._music_volume = _clamp_volume(getattr(ctx.cfg, "music_volume", 0.45), 0.45) if ctx.music_enabled() else 0.0
        self._sfx_volume = _clamp_volume(getattr(ctx.cfg, "sfx_volume", 0.75), 0.75) if ctx.sfx_enabled() else 0.0

        try:
            pygame.mixer.music.set_volume(self._music_volume)
        except Exception:
            pass
        for sound in self._sfx_paths_loaded.values():
            try:
                sound.set_volume(self._sfx_volume)
            except Exception:
                pass

    def set_scene_music(self, scene_key: str, ctx) -> None:
        self.play_music(scene_key, ctx)

    def play_music(self, name: str, ctx=None) -> None:
        if not self.ready:
            return
        if name == self.current_scene_music and pygame.mixer.music.get_busy():
            return

        self.current_scene_music = name
        if ctx is not None:
            self.sync_settings(ctx)
            if not ctx.music_enabled():
                self.stop_music()
                return

        music = self.music_streams.get(name)
        if music is None:
            return
        try:
            pygame.mixer.music.load(music)
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def stop_music(self) -> None:
        if not self.ready:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def update(self, ctx) -> None:
        if not self.ready:
            return
        self.sync_settings(ctx)
        if not ctx.music_enabled():
            self.stop_music()
            return
        if self.current_scene_music is None:
            return
        if not pygame.mixer.music.get_busy():
            self.play_music(self.current_scene_music, ctx)

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
            sound.set_volume(self._sfx_volume)
            sound.play()
        except Exception:
            pass

    def _load_shared_sound(self, path: str) -> pygame.mixer.Sound | None:
        if path not in self._sfx_paths_loaded:
            sound = self._safe_load_sound(path)
            if sound is not None:
                self._sfx_paths_loaded[path] = sound
        return self._sfx_paths_loaded.get(path)

    def _safe_load_sound(self, path: str) -> pygame.mixer.Sound | None:
        if not Path(path).exists():
            return None
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    def _safe_load_music(self, path: str) -> str | None:
        if not Path(path).exists():
            return None
        return path
