from typing import Sequence, Union

import pygame
from OpenGL.GL import *


def draw_text(x: int, y: int, text: str, font_name: str, font_size: int, color: Union[Sequence, pygame.Color, str]):
    font = pygame.font.SysFont(font_name, font_size)

    lines = text.splitlines()

    for i, line in enumerate(lines):
        # screen.blit(sys_font.render(l, 0, hecolor), (x, y + fsize * i))
        textSurface = font.render(line, True, color).convert_alpha()
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        glWindowPos2d(x, y - font_size * i)
        glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)


def surface_to_texture(pygame_surface, texture_id):
    rgb_surface = pygame.image.tostring(pygame_surface, 'RGB')
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    surface_rect = pygame_surface.get_rect()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGB, GL_UNSIGNED_BYTE,
                 rgb_surface)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)


def draw_texture(texture_id):
    glEnable(GL_TEXTURE_2D)
    glColor3fv((1, 1, 1))
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-1, 1)
    glTexCoord2f(0, 1)
    glVertex2f(-1, -1)
    glTexCoord2f(1, 1)
    glVertex2f(1, -1)
    glTexCoord2f(1, 0)
    glVertex2f(1, 1)
    glEnd()

    glDisable(GL_TEXTURE_2D)
