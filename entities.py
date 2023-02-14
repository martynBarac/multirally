import entity
from networkvar import NetworkVar
from constant import *


class HitMarker(entity.Entity):
    """Displays a hit circle for the client"""
    def __init__(self, x, y):
        entity.Entity.__init__(self)
        self.class_id = 3
        self.netxpos = NetworkVar(self, x, 0)
        self.netypos = NetworkVar(self, y, 1)
        self.frames = 0

    def update(self, world):
        self.frames += 1
        if self.frames > 32:
            self.destroy(world)


class CHitMarker(entity.CEntity):
    def __init__(self):
        entity.CEntity.__init__(self)
        self.netxpos = NetworkVar(self, 0, 0)
        self.netypos = NetworkVar(self, 0, 1)

    def draw(self, pg, screen, cam):
        pg.draw.circle(screen, (200, 200, 0), (self.netxpos.var-cam[0], self.netypos.var-cam[1]), 1)


class DebugTarget(entity.Entity):
    def __init__(self, x, y):
        entity.Entity.__init__(self)
        self.shootable = True
        self.class_id = 4
        self.w = 4
        self.netxpos = NetworkVar(self, x, 0)
        self.netypos = NetworkVar(self, y, 1)
        self.count = 0
        self.velocity = 10

    def get_collision_bounds(self):
        return [(self.netxpos.var-self.w, self.netypos.var-self.w),
                (self.netxpos.var+self.w, self.netypos.var-self.w),
                (self.netxpos.var-self.w, self.netypos.var+self.w),
                (self.netxpos.var+self.w, self.netypos.var+self.w)]

    def update(self, world):
        self.netypos.set(self.netypos.var + self.velocity*world.dt, True)
        self.count += world.dt
        if self.count > 3:
            self.velocity = -self.velocity
            self.count = 0

    def get_shot(self, damage):
        print("HIT")
        return


class CDebugTarget(entity.CEntity):
    def __init__(self):
        entity.CEntity.__init__(self)
        self.netxpos = NetworkVar(self, 0, 0, True)
        self.netypos = NetworkVar(self, 0, 1, True)

    def draw(self, pg, screen, cam):
        pg.draw.circle(screen, (0, 200, 0), (self.netxpos.var-cam[0], self.netypos.var-cam[1]), 8)


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