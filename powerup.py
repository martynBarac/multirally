import entity
from networkvar import NetworkVar
from constant import *

class Powerup(entity.Entity):
    def __init__(self, x=50, y=50, typ=0):
        entity.Entity.__init__(self)
        self.class_id = 2
        self.xpos = NetworkVar(self, x, 1)
        self.ypos = NetworkVar(self, y, 2)
        self.type = NetworkVar(self, typ, 0)
        self.w = 8
        self.h = 8

    def check_col(self, world):
        for player in world.player_table:
            if player.xpos < self.xpos.var + self.w and player.xpos + player.w > self.xpos.var:
                if player.ypos < self.ypos.var + self.h and player.ypos + player.h > self.ypos.var:
                    # There is a collision

                    # Give powerup
                    if self.type.var == POWERUP_HEALTH:
                        player.health = max(player.health + POWERUP_HEALTH_AMT, 200)

                    # Destroy self
                    self.destroy(world)

    def update(self, world):
        self.check_col(world)
        return self.prepare_data_table()


class CPowerup(entity.Entity):
    def __init__(self):
        entity.Entity.__init__(self)
        self.xpos = NetworkVar(self, 0, 1, True)
        self.ypos = NetworkVar(self, 0, 2, True)
        self.type = NetworkVar(self, 0, 0)

    def draw(self, pg, screen):
        rect = [self.xpos.var, self.ypos.var, 8, 8]
        pg.draw.rect(screen, (200, 200, 0), rect)
        return rect


