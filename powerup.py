import pygame as pg


class Powerup:
    def __init__(self, x=50, y=50, typ=0):
        self.xpos = x
        self.ypos = y
        self.type = typ
        self.rect = pg.Rect(x, y, 8, 8)
        
    def draw(self, camx, camy):
        return_rect = self.rect.copy()
        return_rect.x = self.rect.x - camx
        return_rect.y = self.rect.y - camy
        return return_rect
