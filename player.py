import pygame as pg

UPARROW = 1
LEFTARROW = 2
RIGHTARROW = 3
DOWNARROW = 4


class Player:
    def __init__(self, x, y, name):
        self.name = name
        self.id = -1
        self.xpos = x
        self.ypos = y
        self.health = 100
        self.topSpeed = 1

    def update(self, actions, dt):
        # Do actions
        if actions[UPARROW]:
            self.ypos -= self.topSpeed*dt
        if actions[DOWNARROW]:
            self.ypos += self.topSpeed*dt
        if actions[LEFTARROW]:
            self.xpos -= self.topSpeed*dt
        if actions[RIGHTARROW]:
            self.xpos += self.topSpeed*dt

    def draw(self):
        rectangle = pg.Rect(self.xpos, self.ypos, 16, 16)
        return rectangle
