import math
from pathlib import Path
from typing import Optional, Union

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from src.config import load_configuration
from src.square import Square
from src.utils import drawText


class Animation:
    def __init__(self, animation_config: Optional[Union[Path, str]] = None):
        # Constants
        self.configuration = load_configuration(animation_config)
        pygame.mixer.init()
        self.collision_sound = pygame.mixer.Sound(Path(__file__).parent / "resources/clack.wav")

        # Scene
        self.floor = Square(**self.configuration["floor"])
        self.wall = Square(**self.configuration["wall"])

        # Blocks
        self.inside_block = Square(**self.configuration["inside_block"])
        self.outside_block = Square(**self.configuration["outside_block"])

        # Simulation control flags
        self.simulation_ended = False
        self.start_simulation = False

        self.collisions_number = 0

    def start_animation(self):
        self._init_pygame()
        self._init_openGL()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start_simulation = True
                        self.set_up_blocks()
                    if event.key == K_r:
                        self.reset_scene()

            if self.start_simulation and not self.simulation_ended:
                self.move_blocks()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.draw_scene()

            pygame.display.flip()
            pygame.time.wait(self.configuration.get("fps"))

    def set_up_blocks(self):
        self.outside_block.mass = 1
        self.outside_block.vel = 1 / self.configuration.get("fps")

    def draw_scene(self):
        drawText(0, 550, f"Number of collisions: {self.collisions_number}", "arial", 32, Color('black'))

        self.floor.draw()
        self.wall.draw()
        self.inside_block.draw()
        self.outside_block.draw()

    def move_blocks(self):
        for _ in range(self.configuration.get("fps")):
            if self.outside_block.x + self.outside_block.width > self.inside_block.x:

                vel1 = ((self.outside_block.mass - self.inside_block.mass) / (
                        self.outside_block.mass + self.inside_block.mass)) * self.outside_block.vel + (
                               (2 * self.inside_block.mass) / (
                               self.outside_block.mass + self.inside_block.mass)) * self.inside_block.vel

                vel2 = ((self.inside_block.mass - self.outside_block.mass) / (
                        self.outside_block.mass + self.inside_block.mass)) * self.inside_block.vel + (
                               (2 * self.outside_block.mass) / (
                               self.outside_block.mass + self.inside_block.mass)) * self.outside_block.vel

                self.outside_block.vel = vel1
                self.inside_block.vel = vel2
                self.collisions_number += 1
                self.collision_sound.play()

            elif self.inside_block.x + self.inside_block.width > 750:

                self.inside_block.vel = -self.inside_block.vel
                self.collisions_number += 1
                self.collision_sound.play()

            self.outside_block.x += self.outside_block.vel
            self.inside_block.x += self.inside_block.vel

        blocks_ratio = int(math.log10(self.outside_block.mass / self.inside_block.mass))
        power = blocks_ratio - 1 if blocks_ratio >= 2 else 0
        needed_collisions_number = int(float(str(math.pi)[:blocks_ratio+1]) * 10 ** power)
        if needed_collisions_number == self.collisions_number:
            self.simulation_ended = True

    def reset_scene(self):
        self.collisions_number = 0
        self.simulation_ended = False
        self.start_simulation = False
        self.inside_block = Square(**self.configuration["inside_block"])
        self.outside_block = Square(**self.configuration["outside_block"])

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption('3D Graphics Project')
        pygame.display.set_mode((list(self.configuration["window"].values())), pygame.OPENGL | pygame.DOUBLEBUF)

    def _init_openGL(self):
        glClearColor(*Color('white'))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        width, height = self.configuration["window"].values()
        gluOrtho2D(0, width, 0, height)
