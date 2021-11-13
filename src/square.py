from OpenGL.GL import *


class Square:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.vel = 0
        self.color = color
        self.exponent = 1
        self.mass = 10 ** self.exponent

    def draw(self):
        glColor3f(*self.color)
        glRectd(self.x, self.y, self.x + self.width, self.y + self.height)
