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


def create_camera_2d():
    camera = rl.ffi.new("Camera2D *")
    camera.offset.x = 0.0
    camera.offset.y = 0.0
    camera.target.x = 0.0
    camera.target.y = 0.0
    camera.rotation = 0.0
    camera.zoom = 1.0
    return camera


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
get_time = rl.GetTime

window_should_close = rl.WindowShouldClose
close_window = rl.CloseWindow


def set_window_size(width: int, height: int):
    rl.SetWindowSize(int(width), int(height))


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
begin_mode_2d = rl.BeginMode2D
end_mode_2d = rl.EndMode2D
load_render_texture = rl.LoadRenderTexture
unload_render_texture = rl.UnloadRenderTexture
begin_texture_mode = rl.BeginTextureMode
end_texture_mode = rl.EndTextureMode
unload_shader = rl.UnloadShader
set_shader_value = rl.SetShaderValue
begin_shader_mode = rl.BeginShaderMode
end_shader_mode = rl.EndShaderMode


def load_shader(vs_path, fs_path):
    return rl.LoadShader(_b(vs_path) if vs_path else rl.ffi.NULL, _b(fs_path) if fs_path else rl.ffi.NULL)


def get_shader_location(shader, name: str) -> int:
    return int(rl.GetShaderLocation(shader, _b(name)))


def draw_text(text, x: int, y: int, font_size: int, color):
    rl.DrawText(_b(text), int(x), int(y), int(font_size), color)


def measure_text(text, font_size: int) -> int:
    return int(rl.MeasureText(_b(text), int(font_size)))


def draw_texture_ex(texture, position, rotation=0.0, scale=1.0, tint=colors.WHITE):
    rl.DrawTextureEx(texture, _as_vec2(position),
                     float(rotation), float(scale), tint)


def draw_texture_rec(texture, source, position, tint=colors.WHITE):
    rl.DrawTextureRec(texture, _as_rect(source), _as_vec2(position), tint)


def draw_rectangle_rec(rect, color):
    rl.DrawRectangleRec(_as_rect(rect), color)


def draw_rectangle_lines_ex(rect, line_thick, color):
    rl.DrawRectangleLinesEx(_as_rect(rect), float(line_thick), color)


def draw_circle(center_x: int, center_y: int, radius: int, color):
    rl.DrawCircle(int(center_x), int(center_y), int(radius), color)


def draw_circle_lines(center_x: int, center_y: int, radius: int, color):
    rl.DrawCircleLines(int(center_x), int(center_y), float(radius), color)


def fade(color, alpha: float):
    return rl.Fade(color, float(alpha))


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
is_mouse_button_down = rl.IsMouseButtonDown


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
is_key_down = rl.IsKeyDown
is_gamepad_available = rl.IsGamepadAvailable
is_gamepad_button_pressed = rl.IsGamepadButtonPressed
is_gamepad_button_down = rl.IsGamepadButtonDown
get_gamepad_axis_movement = rl.GetGamepadAxisMovement
get_char_pressed = rl.GetCharPressed

KEY_W = rl.KEY_W
KEY_A = rl.KEY_A
KEY_S = rl.KEY_S
KEY_D = rl.KEY_D
KEY_Q = rl.KEY_Q
KEY_E = rl.KEY_E
KEY_R = rl.KEY_R
KEY_P = rl.KEY_P
KEY_UP = rl.KEY_UP
KEY_DOWN = rl.KEY_DOWN
KEY_LEFT = rl.KEY_LEFT
KEY_RIGHT = rl.KEY_RIGHT
KEY_ESCAPE = rl.KEY_ESCAPE
KEY_F10 = rl.KEY_F10
KEY_ENTER = rl.KEY_ENTER
KEY_KP_ENTER = rl.KEY_KP_ENTER
KEY_SPACE = rl.KEY_SPACE
KEY_BACKSPACE = rl.KEY_BACKSPACE

GAMEPAD_AXIS_LEFT_X = rl.GAMEPAD_AXIS_LEFT_X
GAMEPAD_AXIS_LEFT_Y = rl.GAMEPAD_AXIS_LEFT_Y
GAMEPAD_BUTTON_LEFT_FACE_UP = rl.GAMEPAD_BUTTON_LEFT_FACE_UP
GAMEPAD_BUTTON_LEFT_FACE_RIGHT = rl.GAMEPAD_BUTTON_LEFT_FACE_RIGHT
GAMEPAD_BUTTON_LEFT_FACE_DOWN = rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN
GAMEPAD_BUTTON_LEFT_FACE_LEFT = rl.GAMEPAD_BUTTON_LEFT_FACE_LEFT
GAMEPAD_BUTTON_RIGHT_FACE_DOWN = rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN
GAMEPAD_BUTTON_RIGHT_FACE_RIGHT = rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT
GAMEPAD_BUTTON_MIDDLE_LEFT = rl.GAMEPAD_BUTTON_MIDDLE_LEFT
GAMEPAD_BUTTON_MIDDLE = rl.GAMEPAD_BUTTON_MIDDLE
GAMEPAD_BUTTON_MIDDLE_RIGHT = rl.GAMEPAD_BUTTON_MIDDLE_RIGHT


# -------------------------
# Colors re-export
# -------------------------
WHITE = colors.WHITE
BLACK = colors.BLACK
YELLOW = colors.YELLOW
GRAY = colors.GRAY
DARKGRAY = colors.DARKGRAY


def load_font_ex(path: str, size: int):
    return rl.LoadFontEx(_b(path), int(size), rl.ffi.NULL, 0)

def unload_font(font) -> None:
    rl.UnloadFont(font)

def draw_text_ex(font, text: str, x: float, y: float, size: float, spacing: float, color) -> None:
    pos = rl.ffi.new("Vector2 *", [float(x), float(y)])
    rl.DrawTextEx(font, _b(text), pos[0], float(size), float(spacing), color)

def measure_text_ex(font, text: str, size: float, spacing: float) -> tuple[float, float]:
    vec = rl.MeasureTextEx(font, _b(text), float(size), float(spacing))
    return float(vec.x), float(vec.y)

def set_texture_filter_bilinear(texture) -> None:
    rl.SetTextureFilter(texture, rl.TEXTURE_FILTER_BILINEAR)

def load_font_ex(path: str, size: int):
    return rl.LoadFontEx(_b(path), int(size), rl.ffi.NULL, 0)

def unload_font(font) -> None:
    rl.UnloadFont(font)

def draw_text_ex(font, text: str, x: float, y: float, size: float, spacing: float, color) -> None:
    pos = rl.ffi.new("Vector2 *", [float(x), float(y)])
    rl.DrawTextEx(font, _b(text), pos[0], float(size), float(spacing), color)

def measure_text_ex(font, text: str, size: float, spacing: float) -> tuple[float, float]:
    vec = rl.MeasureTextEx(font, _b(text), float(size), float(spacing))
    return float(vec.x), float(vec.y)

def set_texture_filter_bilinear(texture) -> None:
    rl.SetTextureFilter(texture, rl.TEXTURE_FILTER_BILINEAR)