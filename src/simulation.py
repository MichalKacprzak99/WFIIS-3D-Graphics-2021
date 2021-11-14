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
from src.utils.utils import calculate_velocity
from src.utils.drawing_utils import draw_text

# COLORS
COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)


class Simulation:
    def __init__(self, simulation_config: Optional[Union[Path, str]] = None):
        # Configuration
        self.configuration = load_configuration(simulation_config)

        # Initialize
        self._init_pygame()
        self._init_openGL()

        # Initialize camera values
        width, height = self.configuration["window"].values()
        self.camera_left = 0
        self.camera_right = width
        self.camera_bottom = 0
        self.camera_top = height

        # Constants
        self.collision_sound = pygame.mixer.Sound(Path(__file__).parent / "resources/clack.wav")

        # Scene
        self.floor = Square(**self.configuration["floor"])
        self.wall = Square(**self.configuration["wall"])

        # Blocks
        self.inside_block = Square(**self.configuration["inside_block"])
        self.outside_block = Square(**self.configuration["outside_block"])

        # Menu
        self.outside_block_weight_select = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            **self.configuration.get("outside_block_weigh_selector"))

        # Simulation control flags
        self.simulation_ended = False
        self.simulation_started = False

        self.collisions_number = 0

    def start_simulation(self):
        clock = pygame.time.Clock()
        width, height = self.configuration["window"].values()
        gluPerspective(45, (1.0 * (width / height)), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

        while True:

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    simulation_start_conditions = all([event.key == pygame.K_SPACE,
                                                       not self.simulation_started,
                                                       self.outside_block_weight_select.valid_option])
                    if simulation_start_conditions:
                        self.simulation_started = True

                        # Starts outside block movement
                        self.outside_block.vel = 1 / self.configuration.get("fps")
                    if event.key == K_r:
                        self.reset_simulation()
                self.mouse_scroll(event)
            selected_option = self.outside_block_weight_select.update(event_list)
            if selected_option >= 0:
                self.outside_block.mass = int(self.outside_block_weight_select.main)
                self.outside_block.set_size(self.outside_block_weight_select.active_option)

            if self.simulation_started and not self.simulation_ended:
                self.move_blocks()

            self.draw()

            pygame.display.flip()

            clock.tick(self.configuration.get("fps"))

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glClearColor(*Color('white'))

        self._draw_gui()
        self._draw_scene()

    def _draw_scene(self):
        gluOrtho2D(self.camera_left, self.camera_right, self.camera_bottom, self.camera_top)
        self.floor.draw()
        self.wall.draw()
        self.inside_block.draw()
        self.outside_block.draw()

    def _draw_gui(self):
        self.outside_block_weight_select.draw()
        draw_text(text=f"Number of collisions: {self.collisions_number}", **self.configuration.get("collision_text"))
        draw_text(**self.configuration.get("instruction_text"))

    def move_blocks(self):
        """Handles blocks movement and detects collisions

        Number of collision increase when:
            - two block collide
            - inside block collides with wall
        """
        # Additional loop for better calculation
        for _ in range(self.configuration.get("fps")):

            # Check if blocks collide
            if self.outside_block.x + self.outside_block.width > self.inside_block.x:

                # Calculate new velocity for blocks
                outside_block_vel = calculate_velocity(self.outside_block, self.inside_block)
                inside_block_vel = calculate_velocity(self.inside_block, self.outside_block)

                self.outside_block.vel = outside_block_vel
                self.inside_block.vel = inside_block_vel

                self.collisions_number += 1
                self.collision_sound.play()

            # Check if block collide with wall
            elif self.inside_block.x + self.inside_block.width > self.wall.x:
                self.inside_block.vel = -self.inside_block.vel
                self.collisions_number += 1
                self.collision_sound.play()

            self.outside_block.x += self.outside_block.vel
            self.inside_block.x += self.inside_block.vel

        # Stop simulation if collisions number reached
        blocks_ratio = int(math.log10(self.outside_block.mass / self.inside_block.mass))
        needed_collisions_number = int(float(str(math.pi)[:blocks_ratio + 1]) * 10 ** (blocks_ratio / 2))
        if needed_collisions_number == self.collisions_number:
            if self.outside_block.vel < 0 and abs(
                    self.outside_block.x - self.inside_block.x) > 10 * self.inside_block.width:
                self.simulation_ended = True

    def reset_simulation(self):
        """Resets simulation when R key pressed"""
        self.collisions_number = 0

        self.simulation_ended = False
        self.simulation_started = False

        self.outside_block_weight_select.reset()

        # Reset blocks position
        self.inside_block = Square(**self.configuration["inside_block"])
        self.outside_block = Square(**self.configuration["outside_block"])

    def mouse_scroll(self, event: pygame.event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:  # wheel rolled up
            self.camera_left += 50
            self.camera_right -= 50
            self.camera_bottom += 50
            self.camera_top -= 50

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:  # wheel rolled down
            self.camera_bottom -= 50
            self.camera_top += 50
            self.camera_left -= 50
            self.camera_right += 50
            self.floor.x -= 50
            self.floor.width += 50

    def _init_pygame(self):
        """Initializes Pygame"""
        pygame.init()
        pygame.display.set_caption(self.configuration.get("title"))
        pygame.display.set_mode((list(self.configuration["window"].values())), pygame.OPENGL | pygame.DOUBLEBUF)

    def _init_openGL(self):
        """Initializes OpenGl"""
        width, height = self.configuration["window"].values()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glMatrixMode(GL_MODELVIEW)
