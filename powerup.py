import entity
from networkvar import NetworkVar
from constant import *

class Powerup(entity.Entity):
    def __init__(self, x=50, y=50, typ=0):
        entity.Entity.__init__(self)
        self.class_id = 2
        self.netxpos = NetworkVar(self, x, 1)
        self.netypos = NetworkVar(self, y, 2)
        self.type = NetworkVar(self, typ, 0)
        self.w = 8
        self.h = 8

    def check_col(self, world):
        for player in world.player_table:
            if player.xpos < self.netxpos.var + self.w and player.xpos + player.w > self.netxpos.var:
                if player.ypos < self.netypos.var + self.h and player.ypos + player.h > self.netypos.var:
                    # There is a collision

                    # Give powerup
                    if self.type.var == POWERUP_HEALTH:
                        player.health = max(player.health + POWERUP_HEALTH_AMT, 200)

                    # Destroy self
                    self.destroy(world)

    def update(self, world):
        self.check_col(world)
        return None


class CPowerup(entity.CEntity):
    def __init__(self):
        entity.CEntity.__init__(self)
        self.netxpos = NetworkVar(self, 0, 1)
        self.netypos = NetworkVar(self, 0, 2)
        self.type = NetworkVar(self, 0, 0)
        self.check_type = True
        self.image = None
        self.actor = False

    def draw(self, pg, screen, cam):
        if self.check_type:
            if self.type.var == POWERUP_HEALTH:
                self.image = pg.image.load('sprites/health.png').convert()

            self.check_type = False
        rect = [self.netxpos.var-cam[0], self.netypos.var-cam[1], 8, 8]
        screen.blit(self.image, rect)
        #pg.draw.rect(screen, (200, 200, 0), rect)
        return rect


class PowerupSpawner(entity.Entity):
    def __init__(self):
        entity.Entity.__init__(self)
        self.xpos = 0
        self.ypos = 0
        self.count = 0
        self.powerup = None

    def update(self, world):
        if self.powerup is None:
            self.count += world.dt
            if self.count > 10:
                self.powerup = Powerup(self.xpos, self.ypos)
                world.spawn_entity(self.powerup)
                self.count = 0


