import math
from pathlib import Path
from typing import Optional, Union

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from src.config import load_configuration
from src.square import Square
from src.ui_elements import DropDown
from src.utils import draw_text


class Animation:
    def __init__(self, animation_config: Optional[Union[Path, str]] = None):
        # Constants
        self.configuration = load_configuration(animation_config)

        # Initialize
        self._init_pygame()
        self._init_openGL()

        self.collision_sound = pygame.mixer.Sound(Path(__file__).parent / "resources/clack.wav")

        # Scene
        self.floor = Square(**self.configuration["floor"])
        self.wall = Square(**self.configuration["wall"])

        # Menu
        COLOR_INACTIVE = (100, 80, 255)
        COLOR_ACTIVE = (100, 200, 255)
        COLOR_LIST_INACTIVE = (255, 100, 100)
        COLOR_LIST_ACTIVE = (255, 150, 150)

        self.outside_block_weight_select = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            300, 50, 300, 50,
            None, 30,
            "Select outside block weight", ["1", "100", "10000", "1000000"])

        # Blocks
        self.inside_block = Square(**self.configuration["inside_block"])
        self.outside_block = Square(**self.configuration["outside_block"])

        # Simulation control flags
        self.simulation_ended = False
        self.start_simulation = False

        self.collisions_number = 0

    def start_animation(self):
        clock = pygame.time.Clock()

        while True:
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.start_simulation:
                        self.start_simulation = True
                        self.set_up_blocks()
                    if event.key == K_r:
                        self.reset_scene()

            selected_option = self.outside_block_weight_select.update(event_list)
            if selected_option >= 0:
                self.outside_block_weight_select.main = self.outside_block_weight_select.options[selected_option]
                self.outside_block.mass = int(self.outside_block_weight_select.main)

            if self.start_simulation and not self.simulation_ended:
                self.move_blocks()

            self.draw()

            pygame.display.flip()

            clock.tick(self.configuration.get("fps"))

    def set_up_blocks(self):
        self.outside_block.vel = 1 / self.configuration.get("fps")

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glClearColor(*Color('white'))

        self._draw_gui()
        self._draw_scene()

    def _draw_scene(self):
        width, height = self.configuration["window"].values()
        gluOrtho2D(0, width, 0, height)
        self.floor.draw()
        self.wall.draw()
        self.inside_block.draw()
        self.outside_block.draw()

    def _draw_gui(self):
        self.outside_block_weight_select.draw()
        draw_text(0, 550, f"Number of collisions: {self.collisions_number}", "arial", 32, Color('black'))

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
        needed_collisions_number = int(float(str(math.pi)[:blocks_ratio + 1]) * 10 ** (blocks_ratio / 2))
        if needed_collisions_number == self.collisions_number:
            self.simulation_ended = True

    def reset_scene(self):
        self.collisions_number = 0
        self.simulation_ended = False
        self.start_simulation = False
        self.inside_block = Square(**self.configuration["inside_block"])
        self.outside_block = Square(**self.configuration["outside_block"])
        self.outside_block_weight_select.reset()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption('3D Graphics Project')
        pygame.display.set_mode((list(self.configuration["window"].values())), pygame.OPENGL | pygame.DOUBLEBUF)

    def _init_openGL(self):
        width, height = self.configuration["window"].values()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
