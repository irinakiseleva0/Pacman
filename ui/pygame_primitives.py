from __future__ import annotations

import pygame

import core.raylib_api as pyray


def color_rgba(color) -> tuple[int, int, int, int]:
    if isinstance(color, pygame.Color):
        return color.r, color.g, color.b, color.a
    if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
        return int(color.r), int(color.g), int(color.b), int(getattr(color, "a", 255))
    if isinstance(color, (tuple, list)):
        if len(color) >= 4:
            return int(color[0]), int(color[1]), int(color[2]), int(color[3])
        return int(color[0]), int(color[1]), int(color[2]), 255
    return 255, 255, 255, 255


def rect_tuple(rect) -> tuple[int, int, int, int]:
    return int(rect.x), int(rect.y), int(rect.width), int(rect.height)


def draw_rect(rect, color, width: int = 0) -> None:
    surface = pyray.get_drawing_surface()
    rgba = color_rgba(color)
    target = pygame.Rect(*rect_tuple(rect))
    if rgba[3] < 255:
        layer = pygame.Surface((max(1, target.width), max(1, target.height)), pygame.SRCALPHA)
        pygame.draw.rect(layer, rgba, layer.get_rect(), int(width))
        surface.blit(layer, target.topleft)
        return
    pygame.draw.rect(surface, rgba, target, int(width))


def draw_line(start, end, color, width: int = 1) -> None:
    surface = pyray.get_drawing_surface()
    rgba = color_rgba(color)
    start_pos = int(start[0]), int(start[1])
    end_pos = int(end[0]), int(end[1])
    if rgba[3] < 255:
        line_width = max(1, int(width))
        pad = line_width + 1
        left = min(start_pos[0], end_pos[0]) - pad
        top = min(start_pos[1], end_pos[1]) - pad
        right = max(start_pos[0], end_pos[0]) + pad
        bottom = max(start_pos[1], end_pos[1]) + pad
        layer = pygame.Surface((max(1, right - left), max(1, bottom - top)), pygame.SRCALPHA)
        local_start = start_pos[0] - left, start_pos[1] - top
        local_end = end_pos[0] - left, end_pos[1] - top
        pygame.draw.line(layer, rgba, local_start, local_end, line_width)
        surface.blit(layer, (left, top))
        return
    pygame.draw.line(surface, rgba, start_pos, end_pos, max(1, int(width)))


def draw_circle(x: float, y: float, radius: float, color, width: int = 0) -> None:
    surface = pyray.get_drawing_surface()
    rgba = color_rgba(color)
    center = int(x), int(y)
    if rgba[3] < 255:
        radius_i = max(0, int(radius))
        line_width = max(0, int(width))
        pad = line_width + 1
        size = max(1, radius_i * 2 + pad * 2)
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        local_center = radius_i + pad, radius_i + pad
        pygame.draw.circle(layer, rgba, local_center, radius_i, line_width)
        surface.blit(layer, (center[0] - local_center[0], center[1] - local_center[1]))
        return
    pygame.draw.circle(surface, rgba, center, max(0, int(radius)), int(width))


def font(size: int) -> pygame.font.Font:
    return pygame.font.Font(None, max(1, int(size)))


def measure_text(text: str, size: int) -> int:
    return font(size).size(str(text))[0]


def draw_text(text: str, x: float, y: float, size: int, color) -> None:
    rendered = font(size).render(str(text), True, color_rgba(color))
    pyray.get_drawing_surface().blit(rendered, (int(x), int(y)))


def draw_text_centered(text: str, center_x: float, y: float, size: int, color) -> None:
    width = measure_text(text, size)
    draw_text(text, int(center_x - width / 2), y, size, color)
