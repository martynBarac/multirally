import entity
import math
from constant import *
from networkvar import NetworkVar

UPARROW = '1'
LEFTARROW = '2'
RIGHTARROW = '3'
DOWNARROW = '4'


class Player(entity.Entity):
    def __init__(self, x, y, angle, name):
        entity.Entity.__init__(self)
        self.class_id = 1

        self.name = NetworkVar(self, name, 0)
        self.netxpos = NetworkVar(self, x, 1)
        self.netypos = NetworkVar(self, y, 2)
        self.xpos = x
        self.ypos = y
        self.w = 16
        self.h = 16
        self.xvel = 0
        self.yvel = 0

        self.xacc = 0
        self.yacc = 0

        self.angle = angle

        self.health = 100
        self.topSpeed = 0.7
        self.engine_power = 0.01
        self.colour = (255, 255, 255)
        self.image = "sprites/car.png"

    def update(self, world, actions):
        # world variables
        dt = world.dt
        lvl0 = world.walls


        # Do actions
        throttle = 0
        if actions[UPARROW]:
            throttle = self.engine_power
        if actions[DOWNARROW]:
            throttle = -self.engine_power/2
        if actions[LEFTARROW]:
            self.angle += 0.1
        if actions[RIGHTARROW]:
            self.angle -= 0.1

        maxfric = 0.005

        self.angle = self.angle % (2 * math.pi)
        self.angle = round(self.angle, 10)

        speed = math.sqrt(self.xvel**2 + self.yvel**2)
        direction = math.atan2(self.yvel, self.xvel)

        fric = speed*0.00001
        centripmax = 0.001
        centripForce = -math.sin(self.angle+direction) * centripmax
        # print("dir:", math.degrees(direction))
        # print("ang:", math.degrees(self.angle))

        if self.yvel < 0:
            fcx = centripForce * math.sin(self.angle)
            fcy = -centripForce * math.cos(self.angle)
        else:
            fcx = centripForce * math.sin(self.angle)
            fcy = -centripForce * math.cos(self.angle)

        self.xacc = - fric*math.cos(self.angle) + throttle*math.cos(self.angle) + fcx
        self.yacc = fric*math.sin(self.angle) - throttle*math.sin(self.angle) - fcy

        self.xvel += self.xacc*dt
        self.yvel += self.yacc*dt

        self.xvel = round(self.xvel, 6)
        self.yvel = round(self.yvel, 6)

        self.xpos += self.xvel*dt
        self.ypos += self.yvel*dt

        self.xpos = round(self.xpos, 10)
        self.ypos = round(self.ypos, 10)

        # self.xpos = self.xpos%150000
        # self.ypos = self.ypos%150000

        # COLLISION
        walls = self.check_wall_col(lvl0, False, self.xpos, self.ypos)
        
        if walls: # Check if it hit anything
            for col in walls: # Loop through every wall it hit
                # Right side of block
                if self.xvel < 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos - self.xvel*dt, self.ypos):
                        self.xpos = col[0] + 32
                        self.xvel = 0
                # Left side of block
                elif self.xvel > 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos - self.xvel*dt, self.ypos):
                        self.xpos = col[0] - self.w
                        self.xvel = 0
                # Bottom side of block
                if self.yvel < 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos, self.ypos - self.yvel*dt):
                        self.ypos = col[1] + 32
                        self.yvel = 0
                # Top side of block
                elif self.yvel > 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos, self.ypos - self.yvel*dt):
                        self.ypos = col[1] - self.h
                        self.yvel = 0

        self.netxpos.set(self.xpos, True)
        self.netypos.set(self.ypos, True)
        return self.prepare_data_table()

    def rect_col(self, rect1, rect2):
        # not to the right and not to the left
        if not rect1[0] >= rect2[0] + rect2[2] and not rect1[0] + rect1[2] <= rect2[0]:
            # not below and not above
            if not rect1[1] >= rect2[1] + rect2[3] and not rect1[1] + rect1[3] <= rect2[1]:
                return True
        return False
    
    def check_wall_col(self, lvl0, wall=False, x=False, y=False):
        # If wall is set it will only check collisions with that specific wall, otherwise it checks all walls
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


class CPlayer(entity.Entity):

    def __init__(self):
        entity.Entity.__init__(self)
        self.name = NetworkVar(self, "", 0)
        self.netxpos = NetworkVar(self, 0, 1, True)
        self.netypos = NetworkVar(self, 0, 2, True)

    def update(self, data_table):
        self.apply_data_table(data_table)

    def draw(self, pg, screen):
        rectangle = pg.Rect(self.netxpos.var, self.netypos.var, 16, 16)
        pg.draw.rect(screen, (0, 150, 0), rectangle)
        return rectangle
