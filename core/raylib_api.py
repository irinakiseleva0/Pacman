from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pygame


@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Rectangle:
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0


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


BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (230, 41, 55, 255)
GREEN = (0, 228, 48, 255)
BLUE = (0, 121, 241, 255)
YELLOW = (253, 249, 0, 255)
MAGENTA = (255, 0, 255, 255)
RAYWHITE = (245, 245, 245, 255)
GRAY = (130, 130, 130, 255)
DARKGRAY = (80, 80, 80, 255)

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
_logical_w = 800
_logical_h = 600
_scale = 1.0
_offset_x = 0
_offset_y = 0
_logical_surface: pygame.Surface | None = None
_target_stack: list[pygame.Surface] = []
_clock = pygame.time.Clock()
_fps = 60
_last_dt = 1.0 / 60.0
_start_time = time.monotonic()
_quit_requested = False
_pressed_keys: set[int] = set()
_pressed_mouse: set[int] = set()
_key_queue: list[int] = []
_char_queue: list[int] = []
_events_pumped = False
_dirty_rects: list[pygame.Rect] = []


def _as_path(path: str | bytes) -> str:
    return path.decode("utf-8") if isinstance(path, bytes) else str(path)


def _target() -> pygame.Surface:
    if _target_stack:
        return _target_stack[-1]
    if _logical_surface is None:
        raise RuntimeError("pygame display is not initialized")
    return _logical_surface


def _mark_dirty(rect: pygame.Rect | None = None) -> None:
    if _target_stack:
        return
    if _logical_surface is None:
        return
    _dirty_rects.append(_logical_surface.get_rect() if rect is None else pygame.Rect(rect))


def _scale_dirty_rect(rect: pygame.Rect) -> pygame.Rect:
    left = _offset_x + int(rect.left * _scale)
    top = _offset_y + int(rect.top * _scale)
    right = _offset_x + int(rect.right * _scale)
    bottom = _offset_y + int(rect.bottom * _scale)
    return pygame.Rect(left, top, max(1, right - left), max(1, bottom - top))


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
        if len(color) >= 3:
            return int(color[0]), int(color[1]), int(color[2]), 255
    return WHITE


def _rect(rect) -> pygame.Rect:
    if isinstance(rect, Rectangle) or all(hasattr(rect, attr) for attr in ("x", "y", "width", "height")):
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


def update_scale(real_w: int, real_h: int) -> None:
    global _screen, _scale, _offset_x, _offset_y, _logical_surface
    real_w = max(1, int(real_w))
    real_h = max(1, int(real_h))
    _screen = pygame.display.get_surface()
    _scale = min(real_w / _logical_w, real_h / _logical_h)
    scaled_w = max(1, int(_logical_w * _scale))
    scaled_h = max(1, int(_logical_h * _scale))
    _offset_x = (real_w - scaled_w) // 2
    _offset_y = (real_h - scaled_h) // 2
    if _logical_surface is None or _logical_surface.get_size() != (_logical_w, _logical_h):
        _logical_surface = pygame.Surface((_logical_w, _logical_h), pygame.SRCALPHA)
        if pygame.display.get_surface() is not None:
            _logical_surface = _logical_surface.convert_alpha()


def _pump_events() -> None:
    global _quit_requested, _events_pumped
    if _events_pumped:
        return
    _pressed_keys.clear()
    _pressed_mouse.clear()
    _key_queue.clear()
    _char_queue.clear()
    for event in pygame.event.get((pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
        if event.type == pygame.QUIT:
            _quit_requested = True
        elif event.type == pygame.KEYDOWN:
            _pressed_keys.add(event.key)
            _key_queue.append(event.key)
            if event.unicode:
                _char_queue.append(ord(event.unicode))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            _pressed_mouse.add(event.button - 1)
    _events_pumped = True


def create_camera_2d():
    return Camera2D()


def init_window(width: int, height: int, title) -> None:
    global _screen, _logical_w, _logical_h, _quit_requested, _events_pumped, _dirty_rects
    pygame.init()
    _logical_w = int(width)
    _logical_h = int(height)
    _screen = pygame.display.set_mode((int(width), int(height)), pygame.RESIZABLE)
    pygame.display.set_caption(str(title))
    update_scale(int(width), int(height))
    _quit_requested = False
    _events_pumped = False
    _dirty_rects = []


def close_window() -> None:
    pygame.quit()


def window_should_close() -> bool:
    _pump_events()
    return _quit_requested


def set_window_size(width: int, height: int) -> None:
    global _screen
    _screen = pygame.display.set_mode((int(width), int(height)), pygame.RESIZABLE)
    update_scale(int(width), int(height))


def begin_drawing() -> None:
    return None


def end_drawing() -> None:
    global _last_dt, _events_pumped, _dirty_rects
    if _screen is None or _logical_surface is None:
        raise RuntimeError("pygame display is not initialized")
    real_w, real_h = _screen.get_size()
    scaled_w = max(1, int(_logical_w * _scale))
    scaled_h = max(1, int(_logical_h * _scale))
    if (real_w, real_h) != pygame.display.get_surface().get_size():
        update_scale(real_w, real_h)
    scaled = pygame.transform.scale(_logical_surface, (scaled_w, scaled_h))
    _screen.fill((0, 0, 0))
    _screen.blit(scaled, (_offset_x, _offset_y))
    if _dirty_rects:
        rects = [
            _scale_dirty_rect(clipped)
            for rect in _dirty_rects
            if (clipped := rect.clip(_logical_surface.get_rect())).width > 0 and clipped.height > 0
        ]
        pygame.display.update(rects)
    else:
        pygame.display.flip()
    _dirty_rects = []
    _last_dt = _clock.tick(_fps) / 1000.0
    _events_pumped = False


def clear_background(color) -> None:
    _target().fill(_color(color))
    _mark_dirty()


def _draw_alpha_shape(draw_func, color, *args, **kwargs) -> None:
    rgba = _color(color)
    if rgba[3] >= 255:
        draw_func(_target(), rgba, *args, **kwargs)
        _mark_dirty()
        return
    layer = pygame.Surface(_target().get_size(), pygame.SRCALPHA)
    draw_func(layer, rgba, *args, **kwargs)
    _target().blit(layer, (0, 0))
    _mark_dirty()


def draw_rectangle(x: int, y: int, width: int, height: int, color) -> None:
    draw_rectangle_rec(Rectangle(x, y, width, height), color)


def draw_rectangle_rec(rect, color) -> None:
    target = _rect(rect)
    rgba = _color(color)
    if rgba[3] >= 255:
        pygame.draw.rect(_target(), rgba, target)
        _mark_dirty(target)
        return
    layer = pygame.Surface((max(1, target.width), max(1, target.height)), pygame.SRCALPHA)
    pygame.draw.rect(layer, rgba, layer.get_rect())
    _target().blit(layer, target.topleft)
    _mark_dirty(target)


def draw_rectangle_lines(x: int, y: int, width: int, height: int, color) -> None:
    draw_rectangle_lines_ex(Rectangle(x, y, width, height), 1, color)


def draw_rectangle_lines_ex(rect, line_thick, color) -> None:
    target = _rect(rect)
    width = max(1, int(line_thick))
    rgba = _color(color)
    if rgba[3] >= 255:
        pygame.draw.rect(_target(), rgba, target, width)
        _mark_dirty(target.inflate(width * 2, width * 2))
        return
    layer = pygame.Surface((max(1, target.width), max(1, target.height)), pygame.SRCALPHA)
    pygame.draw.rect(layer, rgba, layer.get_rect(), width)
    _target().blit(layer, target.topleft)
    _mark_dirty(target.inflate(width * 2, width * 2))


def draw_circle(center_x: int, center_y: int, radius: int, color) -> None:
    center = int(center_x), int(center_y)
    radius_i = max(0, int(radius))
    rgba = _color(color)
    if rgba[3] >= 255:
        pygame.draw.circle(_target(), rgba, center, radius_i)
        _mark_dirty(pygame.Rect(center[0] - radius_i, center[1] - radius_i, radius_i * 2, radius_i * 2))
        return
    pad = 1
    size = max(1, radius_i * 2 + pad * 2)
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    local_center = radius_i + pad, radius_i + pad
    pygame.draw.circle(layer, rgba, local_center, radius_i)
    _target().blit(layer, (center[0] - local_center[0], center[1] - local_center[1]))
    _mark_dirty(pygame.Rect(center[0] - radius_i - pad, center[1] - radius_i - pad, radius_i * 2 + pad * 2, radius_i * 2 + pad * 2))


def draw_circle_lines(center_x: int, center_y: int, radius: int, color) -> None:
    center = int(center_x), int(center_y)
    radius_i = max(0, int(radius))
    rgba = _color(color)
    if rgba[3] >= 255:
        pygame.draw.circle(_target(), rgba, center, radius_i, 1)
        _mark_dirty(pygame.Rect(center[0] - radius_i - 1, center[1] - radius_i - 1, radius_i * 2 + 2, radius_i * 2 + 2))
        return
    pad = 2
    size = max(1, radius_i * 2 + pad * 2)
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    local_center = radius_i + pad, radius_i + pad
    pygame.draw.circle(layer, rgba, local_center, radius_i, 1)
    _target().blit(layer, (center[0] - local_center[0], center[1] - local_center[1]))
    _mark_dirty(pygame.Rect(center[0] - radius_i - pad, center[1] - radius_i - pad, radius_i * 2 + pad * 2, radius_i * 2 + pad * 2))


def draw_line(start_pos_x: int, start_pos_y: int, end_pos_x: int, end_pos_y: int, color) -> None:
    start = int(start_pos_x), int(start_pos_y)
    end = int(end_pos_x), int(end_pos_y)
    rgba = _color(color)
    if rgba[3] >= 255:
        pygame.draw.line(_target(), rgba, start, end, 1)
        _mark_dirty(pygame.Rect(min(start[0], end[0]) - 1, min(start[1], end[1]) - 1, abs(end[0] - start[0]) + 2, abs(end[1] - start[1]) + 2))
        return
    pad = 2
    left = min(start[0], end[0]) - pad
    top = min(start[1], end[1]) - pad
    right = max(start[0], end[0]) + pad
    bottom = max(start[1], end[1]) + pad
    layer = pygame.Surface((max(1, right - left), max(1, bottom - top)), pygame.SRCALPHA)
    pygame.draw.line(layer, rgba, (start[0] - left, start[1] - top), (end[0] - left, end[1] - top), 1)
    _target().blit(layer, (left, top))
    _mark_dirty(pygame.Rect(left, top, max(1, right - left), max(1, bottom - top)))


def draw_text(text, x: int, y: int, font_size: int, color) -> None:
    font = pygame.font.Font(None, max(1, int(font_size)))
    surface = font.render(str(text), True, _color(color))
    _target().blit(surface, (int(x), int(y)))
    _mark_dirty(pygame.Rect(int(x), int(y), surface.get_width(), surface.get_height()))


def measure_text(text, font_size: int) -> int:
    font = pygame.font.Font(None, max(1, int(font_size)))
    return int(font.size(str(text))[0])


def load_font_ex(path: str, size: int) -> Font:
    resolved = _as_path(path)
    return Font(resolved if Path(resolved).exists() else None, int(size))


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
    _mark_dirty(pygame.Rect(int(x), int(y), surface.get_width(), surface.get_height()))


def measure_text_ex(font, text: str, size: float, _spacing: float) -> tuple[float, float]:
    return tuple(float(v) for v in _pygame_font(font, size).size(str(text)))


def set_target_fps(fps: int) -> None:
    global _fps
    _fps = max(1, int(fps))


def get_frame_time() -> float:
    return float(_last_dt)


def get_fps() -> float:
    return float(_clock.get_fps())


def get_time() -> float:
    return time.monotonic() - _start_time


def is_key_pressed(key: int) -> bool:
    _pump_events()
    return int(key) in _pressed_keys


def was_key_pressed(key: int) -> bool:
    return is_key_pressed(key)


def is_key_down(key: int) -> bool:
    try:
        keys = pygame.key.get_pressed()
    except pygame.error:
        return False
    return 0 <= int(key) < len(keys) and bool(keys[int(key)])


def get_key_pressed() -> int:
    _pump_events()
    return _key_queue.pop(0) if _key_queue else 0


def get_pressed_key_events() -> set[int]:
    _pump_events()
    return set(_pressed_keys)


def get_pressed_keys():
    try:
        return pygame.key.get_pressed()
    except pygame.error:
        return ()


def get_char_pressed() -> int:
    _pump_events()
    return _char_queue.pop(0) if _char_queue else 0


def begin_mode_2d(_camera) -> None:
    return None


def end_mode_2d() -> None:
    return None


def load_render_texture(width: int, height: int) -> RenderTexture:
    surface = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
    if pygame.display.get_surface() is not None:
        surface = surface.convert_alpha()
    return RenderTexture(surface)


def unload_render_texture(_rt) -> None:
    return None


def begin_texture_mode(rt: RenderTexture) -> None:
    _target_stack.append(rt.surface)


def end_texture_mode() -> None:
    if _target_stack:
        _target_stack.pop()


def load_texture(path) -> pygame.Surface:
    return pygame.image.load(_as_path(path)).convert_alpha()


def unload_texture(_texture) -> None:
    return None


def set_texture_filter_bilinear(_texture) -> None:
    return None


def draw_texture_ex(texture, position, rotation=0.0, scale=1.0, tint=WHITE) -> None:
    surface = texture.surface if hasattr(texture, "surface") else texture
    if scale != 1.0:
        width = max(1, int(surface.get_width() * float(scale)))
        height = max(1, int(surface.get_height() * float(scale)))
        surface = pygame.transform.scale(surface, (width, height))
    if rotation:
        surface = pygame.transform.rotate(surface, -float(rotation))
    if _color(tint)[3] < 255:
        surface = surface.copy()
        surface.set_alpha(_color(tint)[3])
    pos = tuple(int(v) for v in _vec2(position))
    _target().blit(surface, pos)
    _mark_dirty(pygame.Rect(pos[0], pos[1], surface.get_width(), surface.get_height()))


def draw_texture_rec(texture, source, position, tint=WHITE) -> None:
    surface = texture.surface if hasattr(texture, "surface") else texture
    src = _rect(source)
    if src.height < 0:
        src.height = abs(src.height)
        subsurface = pygame.transform.flip(surface.subsurface(src).copy(), False, True)
    else:
        subsurface = surface.subsurface(src).copy()
    if _color(tint)[3] < 255:
        subsurface.set_alpha(_color(tint)[3])
    pos = tuple(int(v) for v in _vec2(position))
    _target().blit(subsurface, pos)
    _mark_dirty(pygame.Rect(pos[0], pos[1], subsurface.get_width(), subsurface.get_height()))


def draw_texture_pro(texture, source, dest, origin=None, rotation=0.0, tint=WHITE) -> None:
    surface = texture.surface if hasattr(texture, "surface") else texture
    src = _rect(source)
    flip_x = src.width < 0
    flip_y = src.height < 0
    src.width = abs(src.width)
    src.height = abs(src.height)
    frame = surface.subsurface(src).copy()
    if flip_x or flip_y:
        frame = pygame.transform.flip(frame, flip_x, flip_y)

    dst = _rect(dest)
    if frame.get_size() != (max(1, dst.width), max(1, dst.height)):
        frame = pygame.transform.scale(frame, (max(1, dst.width), max(1, dst.height)))
    if rotation:
        frame = pygame.transform.rotate(frame, -float(rotation))
    rgba = _color(tint)
    if rgba != WHITE:
        frame = frame.copy()
        frame.fill(rgba, special_flags=pygame.BLEND_RGBA_MULT)

    ox, oy = _vec2(origin or (0, 0))
    pos = int(dst.x - ox), int(dst.y - oy)
    _target().blit(frame, pos)
    _mark_dirty(pygame.Rect(pos[0], pos[1], frame.get_width(), frame.get_height()))


def fade(color, alpha: float):
    r, g, b, a = _color(color)
    return r, g, b, int(a * max(0.0, min(1.0, float(alpha))))


def check_collision_point_rec(point, rect) -> bool:
    return _rect(rect).collidepoint(tuple(int(v) for v in _vec2(point)))


def get_mouse_position():
    real_x, real_y = pygame.mouse.get_pos()
    if _scale <= 0:
        return {"x": 0.0, "y": 0.0}
    logical_x = (real_x - _offset_x) / _scale
    logical_y = (real_y - _offset_y) / _scale
    return {"x": float(logical_x), "y": float(logical_y)}


def is_mouse_button_pressed(button: int) -> bool:
    _pump_events()
    return int(button) in _pressed_mouse


def is_mouse_button_down(button: int) -> bool:
    buttons = pygame.mouse.get_pressed(5)
    return 0 <= int(button) < len(buttons) and bool(buttons[int(button)])
