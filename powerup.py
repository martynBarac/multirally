import entity
from networkvar import NetworkVar
from constant import *

class Powerup(entity.Entity):
    def __init__(self, x=50, y=50, typ=0):
        entity.Entity.__init__(self)
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
                    #self.destroy(world)

    def update(self, world):
        self.check_col(world)
        return self.prepare_data_table()


    #def draw(self, camx, camy):
    #    return_rect = self.rect.copy()
    #    return_rect.x = self.rect.x - camx
    #    return_rect.y = self.rect.y - camy
    #    return return_rect
