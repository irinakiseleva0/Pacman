from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pygame
from raylib import colors


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


@dataclass
class RenderTexture:
    surface: pygame.Surface

    @property
    def texture(self) -> pygame.Surface:
        return self.surface


@dataclass
class Font:
    path: str | None
    base_size: int
    texture: Any = None


class Camera2D:
    def __init__(self) -> None:
        self.offset = Vector2()
        self.target = Vector2()
        self.rotation = 0.0
        self.zoom = 1.0

    def __getitem__(self, index: int):
        if index != 0:
            raise IndexError(index)
        return self


class _FFI:
    NULL = None

    @staticmethod
    def new(_ctype: str, init=None):
        return init


class _RL:
    ffi = _FFI()
    TEXTURE_FILTER_BILINEAR = 0

    @staticmethod
    def SetTextureFilter(_texture, _filter) -> None:
        return None


rl = _RL()

WHITE = colors.WHITE
BLACK = colors.BLACK
YELLOW = colors.YELLOW
GRAY = colors.GRAY
DARKGRAY = colors.DARKGRAY

KEY_W = pygame.K_w
KEY_A = pygame.K_a
KEY_S = pygame.K_s
KEY_D = pygame.K_d
KEY_Q = pygame.K_q
KEY_E = pygame.K_e
KEY_R = pygame.K_r
KEY_P = pygame.K_p
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_ESCAPE = pygame.K_ESCAPE
KEY_F10 = pygame.K_F10
KEY_ENTER = pygame.K_RETURN
KEY_KP_ENTER = pygame.K_KP_ENTER
KEY_SPACE = pygame.K_SPACE
KEY_BACKSPACE = pygame.K_BACKSPACE

_screen: pygame.Surface | None = None
_target_stack: list[pygame.Surface] = []
_clock = pygame.time.Clock()
_fps = 60
_last_dt = 1.0 / 60.0
_start_time = time.monotonic()
_quit_requested = False
_pressed_keys: set[int] = set()
_pressed_mouse: set[int] = set()
_char_queue: list[int] = []
_events_pumped = False


def _as_path(path: str | bytes) -> str:
    return path.decode("utf-8") if isinstance(path, bytes) else path


def _target() -> pygame.Surface:
    if _target_stack:
        return _target_stack[-1]
    if _screen is None:
        raise RuntimeError("pygame display is not initialized")
    return _screen


def get_drawing_surface() -> pygame.Surface:
    return _target()


def _color(color) -> tuple[int, int, int, int]:
    if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
        return (
            int(color.r),
            int(color.g),
            int(color.b),
            int(getattr(color, "a", 255)),
        )
    if isinstance(color, pygame.Color):
        return color.r, color.g, color.b, color.a
    if isinstance(color, (tuple, list)):
        if len(color) >= 4:
            return int(color[0]), int(color[1]), int(color[2]), int(color[3])
        return int(color[0]), int(color[1]), int(color[2]), 255
    return 255, 255, 255, 255


def _rect(rect) -> pygame.Rect:
    if isinstance(rect, Rectangle):
        return pygame.Rect(int(rect.x), int(rect.y), int(rect.width), int(rect.height))
    if all(hasattr(rect, attr) for attr in ("x", "y", "width", "height")):
        return pygame.Rect(int(rect.x), int(rect.y), int(rect.width), int(rect.height))
    return pygame.Rect(rect)


def _vec2(pos) -> tuple[float, float]:
    if isinstance(pos, Vector2):
        return pos.x, pos.y
    if isinstance(pos, dict):
        return float(pos["x"]), float(pos["y"])
    if hasattr(pos, "x") and hasattr(pos, "y"):
        return float(pos.x), float(pos.y)
    return float(pos[0]), float(pos[1])


def _pump_events() -> None:
    global _quit_requested, _events_pumped
    if _events_pumped:
        return
    _pressed_keys.clear()
    _pressed_mouse.clear()
    _char_queue.clear()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _quit_requested = True
        elif event.type == pygame.KEYDOWN:
            _pressed_keys.add(event.key)
            if event.unicode:
                _char_queue.append(ord(event.unicode))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            _pressed_mouse.add(event.button - 1)
    _events_pumped = True


def create_camera_2d():
    return Camera2D()


def init_window(width: int, height: int, title) -> None:
    global _screen, _quit_requested
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    _screen = pygame.display.set_mode((int(width), int(height)))
    pygame.display.set_caption(str(title))
    _quit_requested = False


def set_target_fps(fps: int) -> None:
    global _fps
    _fps = max(1, int(fps))


def get_frame_time() -> float:
    return float(_last_dt)


def get_time() -> float:
    return time.monotonic() - _start_time


def window_should_close() -> bool:
    _pump_events()
    return _quit_requested


def close_window() -> None:
    pygame.quit()


def set_window_size(width: int, height: int) -> None:
    global _screen
    _screen = pygame.display.set_mode((int(width), int(height)))


def begin_drawing() -> None:
    return None


def end_drawing() -> None:
    global _last_dt, _events_pumped
    pygame.display.flip()
    _last_dt = _clock.tick(_fps) / 1000.0
    _events_pumped = False


def clear_background(color) -> None:
    _target().fill(_color(color))


def begin_mode_2d(_camera) -> None:
    return None


def end_mode_2d() -> None:
    return None


def load_render_texture(width: int, height: int) -> RenderTexture:
    return RenderTexture(pygame.Surface((int(width), int(height)), pygame.SRCALPHA).convert_alpha())


def unload_render_texture(_rt) -> None:
    return None


def begin_texture_mode(rt: RenderTexture) -> None:
    _target_stack.append(rt.surface)


def end_texture_mode() -> None:
    if _target_stack:
        _target_stack.pop()


def draw_text(text, x: int, y: int, font_size: int, color) -> None:
    font = pygame.font.Font(None, max(1, int(font_size)))
    surface = font.render(str(text), True, _color(color))
    _target().blit(surface, (int(x), int(y)))


def measure_text(text, font_size: int) -> int:
    font = pygame.font.Font(None, max(1, int(font_size)))
    return int(font.size(str(text))[0])


def load_font_ex(path: str, size: int) -> Font:
    return Font(path if Path(path).exists() else None, int(size))


def unload_font(_font) -> None:
    return None


def _pygame_font(font: Font | None, size: float):
    font_size = max(1, int(size))
    if font is not None and font.path:
        try:
            return pygame.font.Font(font.path, font_size)
        except Exception:
            pass
    return pygame.font.Font(None, font_size)


def draw_text_ex(font, text: str, x: float, y: float, size: float, _spacing: float, color) -> None:
    surface = _pygame_font(font, size).render(str(text), True, _color(color))
    _target().blit(surface, (int(x), int(y)))


def measure_text_ex(font, text: str, size: float, _spacing: float) -> tuple[float, float]:
    return tuple(float(v) for v in _pygame_font(font, size).size(str(text)))


def set_texture_filter_bilinear(_texture) -> None:
    return None


def load_texture(path) -> pygame.Surface:
    surface = pygame.image.load(_as_path(path)).convert_alpha()
    return surface


def unload_texture(_texture) -> None:
    return None


def draw_texture_ex(texture, position, rotation=0.0, scale=1.0, tint=colors.WHITE) -> None:
    surface = texture.surface if hasattr(texture, "surface") else texture
    if scale != 1.0:
        w = max(1, int(surface.get_width() * float(scale)))
        h = max(1, int(surface.get_height() * float(scale)))
        surface = pygame.transform.smoothscale(surface, (w, h))
    if rotation:
        surface = pygame.transform.rotate(surface, -float(rotation))
    if _color(tint)[3] < 255:
        surface = surface.copy()
        surface.set_alpha(_color(tint)[3])
    _target().blit(surface, tuple(int(v) for v in _vec2(position)))


def draw_texture_rec(texture, source, position, tint=colors.WHITE) -> None:
    surface = texture.surface if hasattr(texture, "surface") else texture
    src = _rect(source)
    if src.height < 0:
        src.height = abs(src.height)
        subsurface = pygame.transform.flip(surface.subsurface(src).copy(), False, True)
    else:
        subsurface = surface.subsurface(src).copy()
    if _color(tint)[3] < 255:
        subsurface.set_alpha(_color(tint)[3])
    _target().blit(subsurface, tuple(int(v) for v in _vec2(position)))


def _draw_alpha_shape(draw_func, color, *args, **kwargs) -> None:
    rgba = _color(color)
    if rgba[3] >= 255:
        draw_func(_target(), rgba, *args, **kwargs)
        return
    layer = pygame.Surface(_target().get_size(), pygame.SRCALPHA)
    draw_func(layer, rgba, *args, **kwargs)
    _target().blit(layer, (0, 0))


def draw_rectangle_rec(rect, color) -> None:
    _draw_alpha_shape(pygame.draw.rect, color, _rect(rect))


def draw_rectangle_lines_ex(rect, line_thick, color) -> None:
    _draw_alpha_shape(pygame.draw.rect, color, _rect(rect), max(1, int(line_thick)))


def draw_circle(center_x: int, center_y: int, radius: int, color) -> None:
    _draw_alpha_shape(
        pygame.draw.circle,
        color,
        (int(center_x), int(center_y)),
        max(0, int(radius)),
    )


def draw_circle_lines(center_x: int, center_y: int, radius: int, color) -> None:
    _draw_alpha_shape(
        pygame.draw.circle,
        color,
        (int(center_x), int(center_y)),
        max(0, int(radius)),
        1,
    )


def fade(color, alpha: float):
    r, g, b, a = _color(color)
    return r, g, b, int(a * max(0.0, min(1.0, float(alpha))))


def check_collision_point_rec(point, rect) -> bool:
    return _rect(rect).collidepoint(tuple(int(v) for v in _vec2(point)))


def get_mouse_position():
    x, y = pygame.mouse.get_pos()
    return {"x": float(x), "y": float(y)}


def is_mouse_button_pressed(button: int) -> bool:
    _pump_events()
    return int(button) in _pressed_mouse


def is_mouse_button_down(button: int) -> bool:
    buttons = pygame.mouse.get_pressed(5)
    return 0 <= int(button) < len(buttons) and bool(buttons[int(button)])


def is_key_pressed(key: int) -> bool:
    _pump_events()
    return int(key) in _pressed_keys


def was_key_pressed(key: int) -> bool:
    _pump_events()
    return int(key) in _pressed_keys


def get_pressed_key_events() -> set[int]:
    _pump_events()
    return set(_pressed_keys)


def get_pressed_keys():
    return pygame.key.get_pressed()


def is_key_down(key: int) -> bool:
    keys = pygame.key.get_pressed()
    return 0 <= int(key) < len(keys) and bool(keys[int(key)])


def get_char_pressed() -> int:
    _pump_events()
    return _char_queue.pop(0) if _char_queue else 0

