from pathlib import Path
from typing import Optional, Union

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from src.config import load_configuration
from src.square import Square


class Animation:
    def __init__(self, animation_config: Optional[Union[Path, str]] = None):
        self.configuration = load_configuration(animation_config)
        self.left_block = Square(100, 100, 200, 200, (1.0, 0, 0))
        self.right_block = Square(400, 100, 200, 200, (1.0, 0, 0))

    def start_animation(self):

        self._init_pygame()
        self._init_openGL()

        self.draw_scene()
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return

    def draw_scene(self):
        glClearColor(255, 255, 255, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.left_block.draw()
        self.right_block.draw()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption('3D Graphics Project')
        w, h = self.configuration.window_width, self.configuration.window_height
        pygame.display.set_mode((w, h), pygame.OPENGL | pygame.DOUBLEBUF)

    def _init_openGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        w, h = self.configuration.window_width, self.configuration.window_height
        gluOrtho2D(0, w, 0, h)
