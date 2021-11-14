from typing import List, Optional

import pygame
from OpenGL.GL import *

from src.utils import draw_texture, surface_to_texture


class DropDown:
    def __init__(self, color_menu, color_option, x: int, y: int, width: int, height: int,
                 font_name: str, font_size: int, main: str, options: List[str], default: Optional[str] = None):

        self._init_pygame()
        self._init_openGL()
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.main = main
        self.default = default if default else main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.valid_option = False

    def draw(self):
        self.surface.fill("white")
        pygame.draw.rect(self.surface, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, True, (0, 0, 0))
        self.surface.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(self.surface, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, True, (0, 0, 0))
                self.surface.blit(msg, msg.get_rect(center=rect.center))

        surface_to_texture(pygame_surface=self.surface, texture_id=self.texture_id)
        draw_texture(texture_id=self.texture_id)

    def update(self, event_list):
        mouse_pos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mouse_pos)

        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mouse_pos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    self.valid_option = True
                    self.main = self.options[self.active_option]
                    return self.active_option
        return -1

    def reset(self):
        self.main = self.default
        self.valid_option = False

    def _init_pygame(self):
        self.surface = pygame.Surface((800, 600))

    def _init_openGL(self):

        self.texture_id = glGenTextures(1)
