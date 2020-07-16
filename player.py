import pygame as pg
from level import *
from math import *

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
        self.w = 16
        self.h = 16
        self.xvel = 0
        self.yvel = 0
        self.xacc = 0
        self.yacc = 0
        self.health = 100
        self.topSpeed = 1
        self.colour = (255, 255, 255)

    def update(self, actions, dt):
        # Do actions
        if actions[UPARROW]:
            self.yvel = -self.topSpeed
        if actions[DOWNARROW]:
            self.yvel = self.topSpeed
        if actions[LEFTARROW]:
            self.xvel = -self.topSpeed
        if actions[RIGHTARROW]:
            self.xvel = self.topSpeed

        if self.xvel > 0:
            self.xacc = -0.01
        elif self.xvel < 0:
            self.xacc = 0.01
        else:
            self.xacc = 0

        if self.yvel > 0:
            self.yacc = -0.01
        elif self.yvel < 0:
            self.yacc = 0.01
        else:
            self.yacc = 0

        self.xvel += self.xacc*dt
        self.yvel += self.yacc*dt

        self.xvel = round(self.xvel, 3)
        self.yvel = round(self.yvel, 3)

        if 0.2 > self.xvel > -0.2:
            self.xvel = 0
        if 0.2 > self.yvel > -0.2:
            self.yvel = 0

        self.xpos += self.xvel*dt
        self.ypos += self.yvel*dt
        
        #COLLISION
        if self.check_col():
            mag = sqrt(self.xvel**2 + self.yvel**2)
            dirx = self.xvel / mag
            diry = self.yvel / mag
            while self.check_col():
                self.xpos -= dirx
                self.ypos -= diry
    
    def check_col(self):
        for wall in lvl0:
            if not self.xpos > wall[0] + 64 and not self.xpos + self.w < wall[0]:
                if not self.ypos > wall[1] + 64 and not self.ypos + self.w < wall[1]:
                    return wall
        return False
    def draw(self):
        rectangle = pg.Rect(self.xpos, self.ypos, 16, 16)
        return rectangle
