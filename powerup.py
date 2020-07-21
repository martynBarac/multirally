import pygame as pg

class Powerup:
    def __init__(self, x=50, y=50, typ=0):
        self.xpos = x
        self.ypos = y
        self.type = typ
        self.rect = pg.Rect(x, y, 8, 8)
        
    def draw(self):
        return self.rect
