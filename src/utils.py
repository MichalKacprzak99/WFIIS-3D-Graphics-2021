from typing import Union

import pygame
from OpenGL.GL import *


def drawText(x: int, y: int, text: str, font_name: str, font_size: int, color: Union[tuple, pygame.Color]):
    font = pygame.font.SysFont(font_name, font_size)
    textSurface = font.render(text, True, color).convert_alpha()
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)
