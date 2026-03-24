from __future__ import annotations

import raylib as rl
from raylib import colors


def _b(s):
    """Convert Python str to UTF-8 bytes for raylib C-API calls."""
    return s.encode("utf-8") if isinstance(s, str) else s


# -------------------------
# Lightweight python types
# -------------------------
class Vector2:
    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)


class Rectangle:
    __slots__ = ("x", "y", "width", "height")

    def __init__(self, x=0.0, y=0.0, width=0.0, height=0.0):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)


def _is_cdata(obj) -> bool:
    # CFFI cdata usually has a nice repr like "<cdata 'Vector2' ...>"
    # This is a pragmatic check that works well in practice.
    return type(obj).__module__.startswith("_cffi_backend")


def _as_vec2(v):
    # Our Vector2
    if isinstance(v, Vector2):
        return {"x": v.x, "y": v.y}

    # tuple/list
    if isinstance(v, (tuple, list)) and len(v) == 2:
        return {"x": float(v[0]), "y": float(v[1])}

    # raylib cdata Vector2 OR any object with x/y (including cdata)
    if hasattr(v, "x") and hasattr(v, "y"):
        return {"x": float(v.x), "y": float(v.y)}

    return v


def _as_rect(r):
    # Our Rectangle
    if isinstance(r, Rectangle):
        return {"x": r.x, "y": r.y, "width": r.width, "height": r.height}

    # tuple/list
    if isinstance(r, (tuple, list)) and len(r) == 4:
        return {"x": float(r[0]), "y": float(r[1]), "width": float(r[2]), "height": float(r[3])}

    # raylib cdata Rectangle OR any object with x/y/width/height
    if all(hasattr(r, k) for k in ("x", "y", "width", "height")):
        return {"x": float(r.x), "y": float(r.y), "width": float(r.width), "height": float(r.height)}

    return r


# -------------------------
# Window & timing
# -------------------------
def init_window(width: int, height: int, title):
    rl.InitWindow(width, height, _b(title))


set_target_fps = rl.SetTargetFPS
get_frame_time = rl.GetFrameTime

window_should_close = rl.WindowShouldClose
close_window = rl.CloseWindow


# -------------------------
# Audio
# -------------------------
init_audio_device = rl.InitAudioDevice
close_audio_device = rl.CloseAudioDevice
is_audio_device_ready = rl.IsAudioDeviceReady


def load_sound(path):
    return rl.LoadSound(_b(path))


unload_sound = rl.UnloadSound
play_sound = rl.PlaySound
stop_sound = rl.StopSound
set_sound_volume = rl.SetSoundVolume
is_sound_playing = rl.IsSoundPlaying


def load_music_stream(path):
    return rl.LoadMusicStream(_b(path))


unload_music_stream = rl.UnloadMusicStream
play_music_stream = rl.PlayMusicStream
stop_music_stream = rl.StopMusicStream
update_music_stream = rl.UpdateMusicStream
set_music_volume = rl.SetMusicVolume
is_music_stream_playing = rl.IsMusicStreamPlaying


# -------------------------
# Drawing
# -------------------------
begin_drawing = rl.BeginDrawing
end_drawing = rl.EndDrawing
clear_background = rl.ClearBackground


def draw_text(text, x: int, y: int, font_size: int, color):
    rl.DrawText(_b(text), int(x), int(y), int(font_size), color)


def measure_text(text, font_size: int) -> int:
    return int(rl.MeasureText(_b(text), int(font_size)))


def draw_texture_ex(texture, position, rotation=0.0, scale=1.0, tint=colors.WHITE):
    rl.DrawTextureEx(texture, _as_vec2(position),
                     float(rotation), float(scale), tint)


def draw_rectangle_rec(rect, color):
    rl.DrawRectangleRec(_as_rect(rect), color)


def draw_rectangle_lines_ex(rect, line_thick, color):
    rl.DrawRectangleLinesEx(_as_rect(rect), float(line_thick), color)


def draw_circle(center_x: int, center_y: int, radius: int, color):
    rl.DrawCircle(int(center_x), int(center_y), int(radius), color)


# -------------------------
# Collision
# -------------------------
def check_collision_point_rec(point, rect) -> bool:
    return bool(rl.CheckCollisionPointRec(_as_vec2(point), _as_rect(rect)))


# -------------------------
# Mouse
# -------------------------
def get_mouse_position():
    # Convert raylib cdata -> dict so it works everywhere
    p = rl.GetMousePosition()
    return _as_vec2(p)


is_mouse_button_pressed = rl.IsMouseButtonPressed


# -------------------------
# Textures
# -------------------------
def load_texture(path):
    return rl.LoadTexture(_b(path))


unload_texture = rl.UnloadTexture


# -------------------------
# Input
# -------------------------
is_key_pressed = rl.IsKeyPressed

KEY_W = rl.KEY_W
KEY_A = rl.KEY_A
KEY_S = rl.KEY_S
KEY_D = rl.KEY_D
KEY_P = rl.KEY_P
KEY_UP = rl.KEY_UP
KEY_DOWN = rl.KEY_DOWN
KEY_LEFT = rl.KEY_LEFT
KEY_RIGHT = rl.KEY_RIGHT
KEY_ESCAPE = rl.KEY_ESCAPE


# -------------------------
# Colors re-export
# -------------------------
WHITE = colors.WHITE
BLACK = colors.BLACK
YELLOW = colors.YELLOW
GRAY = colors.GRAY
DARKGRAY = colors.DARKGRAY
