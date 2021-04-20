import entity
from networkvar import NetworkVar
from constant import *


class LaserWall(entity.Entity):
    """A laser wall the instantly kills your car!
    Static object needs level editor implementation along with powerup
    """
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        pass

    def check_col(self, world):
        for player in world.player_table:
            if player.xpos < self.x + self.w and player.xpos + player.w > self.x:
                if player.ypos < self.y + self.h and player.ypos + player.h > self.y:
                    # There is a collision, respawn the car
                    spawnx, spawny = world.level["spawn"][0]
                    player.xpos = spawnx
                    player.ypos = spawny

    def update(self, world):
        self.check_col(world)
        return None


class CLaserWall(entity.Entity):

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, pg, screen, cam):
        rect = [self.x - cam[0], self.y - cam[1], self.w, self.h]
        pg.draw.rect(screen, (200, 0, 0), rect)
        return rect


"""
Any extra entities should go in this file!!

         Q
          )
         (
    _+_   |
0-<('-')>-0
    | |
    V V

jim has a balloon

_________________

    +      z         .
.     .   z  .   +  .
    D       z    .
    .    .Z  .     .   +
        ___
    ___(-00)___
    ===:::::===
       '''''
       00 00

sick swagger

_________________


      _____
_____//___||_____
|0====| = | ===||= ==-- - -  -
  (@)==--- --(@)====--- -
WWWWWWWWWWWWWWWWWW

_________________


"""