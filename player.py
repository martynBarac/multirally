import pygame as pg
from level import *
from math import *
from constant import *

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
        self.topSpeed = 0.7
        self.colour = (255, 255, 255)

    def update(self, actions, dt, powerups):
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
        walls = self.check_wall_col(False, self.xpos, self.ypos)
        
        if walls: #Check if it hit anything
            for col in walls: #Loop through every wall it hit
                #Right side of block
                if self.xvel < 0:
                    if self.check_wall_col(col) and not self.check_wall_col(col, self.xpos - self.xvel*dt, self.ypos):
                        self.xpos = col[0] + 32
                        self.xvel = 0
                #Left side of block
                elif self.xvel > 0:
                    if self.check_wall_col(col) and not self.check_wall_col(col, self.xpos - self.xvel*dt, self.ypos):
                        self.xpos = col[0] - self.w
                        self.xvel = 0
                #Bottom side of block
                if self.yvel < 0:
                    if self.check_wall_col(col) and not self.check_wall_col(col, self.xpos, self.ypos - self.yvel*dt):
                        self.ypos = col[1] + 32
                        self.yvel = 0
                #Top side of block
                elif self.yvel > 0:
                    if self.check_wall_col(col) and not self.check_wall_col(col, self.xpos, self.ypos - self.yvel*dt):
                        self.ypos = col[1] - self.h
                        self.yvel = 0
       
        #POWERUP COLLISION
        return self.powerup_col(powerups)
   
    def powerup_col(self, powerups):
        for i in range(len(powerups)):
            if self.rect_col([self.xpos, self.ypos, self.w, self.h], powerups[i].rect):
                if powerups[i].type == POWERUP_HEALTH:
                    self.health += POWERUP_HEALTH_AMT
                powerups.pop(i)
        return powerups
                
    def rect_col(self, rect1, rect2):
        if not rect1[0] >= rect2[0] + rect2[2] and not rect1[0] + rect1[2] <= rect2[0]: # not to the right and not to the left
            if not rect1[1] >= rect2[1] + rect2[3] and not rect1[1] + rect1[3] <= rect2[1]: # not below and not above
                return True
        return False
    
    def check_wall_col(self, wall=False, x=False, y=False):
        #If wall is set it will only check collisions with that specific wall, otherwise it checks all walls
        if x == False:
            x = self.xpos
        if y == False:
            y = self.ypos
        walls = []
        if wall:
            if self.rect_col([x, y, self.w, self.h], [wall[0], wall[1], 32, 32]):
                return True
            return False
        else:
            for wall in lvl0:
                if self.rect_col([x, y, self.w, self.h], [wall[0], wall[1], 32, 32]):
                    walls.append(wall)
        if walls:
            return walls
        return False
        
    def draw(self):
        rectangle = pg.Rect(self.xpos, self.ypos, 16, 16)
        return rectangle
