from dataclasses import field, dataclass
from typing import Tuple

from OpenGL.GL import *


@dataclass
class Square:
    x: int
    y: int
    height: int
    width: int
    color: Tuple[int]
    mass: int = field(default=1)
    vel: int = field(default=0)

    def draw(self):
        glColor3f(*self.color)
        glRectd(self.x, self.y, self.x + self.width, self.y + self.height)
