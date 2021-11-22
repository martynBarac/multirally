import entities
import math
import entity
from constant import *
from networkvar import NetworkVar

import pygame as pg # Needs to be imported for image loading

UPARROW = '1'
LEFTARROW = '2'
RIGHTARROW = '3'
DOWNARROW = '4'


class Player(entity.Entity):
    def __init__(self, x, y, angle, name, owner = None):
        entity.Entity.__init__(self)
        self.class_id = 1
        self.owner = owner
        self.shootable = True
        self.name = NetworkVar(self, name, 0)
        self.netxpos = NetworkVar(self, x, 1)
        self.netxpos.quantise = 2
        self.netypos = NetworkVar(self, y, 2)
        self.netypos.quantise = 2
        self.netangle = NetworkVar(self, y, 3)
        self.netangle.quantise = 6
        self.netcolour = NetworkVar(self, (255, 255, 0), 4)
        self.gun_range = 500

        self.xpos = x
        self.ypos = y
        self.w = CAR_SIZE
        self.h = CAR_SIZE

        self.xvel = 0
        self.yvel = 0
        self.netxvel = NetworkVar(self, self.xvel, 5)
        self.netxvel.quantise = 2
        self.netxvel.only_send_to_owner = True
        self.netyvel = NetworkVar(self, self.yvel, 6)
        self.netyvel.quantise = 2
        self.netyvel.only_send_to_owner = True

        self.xacc = 0
        self.yacc = 0
        self.netxacc = NetworkVar(self, 0, 7)
        self.netyacc = NetworkVar(self, 0, 8)
        self.netxacc.quantise = 3
        self.netxacc.only_send_to_owner = True

        self.netyacc.quantise = 3
        self.netyacc.only_send_to_owner = True

        self.angle = angle

        self.health = 100
        self.mass = 10
        self.topSpeed = 10
        self.engine_power = 3.
        self.colour = (255, 255, 255)
        self.image = "sprites/car.png"

    def update(self, world, actions):
        # world variables
        dt = world.dt
        lvl0 = world.level["wall"]


        # Do actions
        throttle = 0
        if actions[UPARROW]:
            throttle = self.engine_power
        if actions[DOWNARROW]:
            throttle = -self.engine_power/2
        if actions[LEFTARROW]:
            self.angle += 0.2*dt
        if actions[RIGHTARROW]:
            self.angle -= 0.2*dt
        if actions[SHOOT_BUTTON]:
            if not world.client_world:
                #fastforward = world.rewind_to_snapshot_number(0)  # Rewind to the past
                hitscan_endpoint = (self.xpos+math.cos(self.angle)*self.gun_range, self.ypos-math.sin(self.angle)*self.gun_range)
                hitscan_startpoint = (self.xpos, self.ypos)
                hit_point = None
                for _id in world.entdict:
                    _entity = world.entdict[_id]
                    if _entity is None:
                        continue
                    if _entity.shootable and _entity != self:
                        colpoints = _entity.get_collision_bounds()
                        for i in range(len(colpoints)):
                            colpoint1 = colpoints[i-1]
                            colpoint2 = colpoints[i]
                            intersect_point = self.line_intersection((colpoint1, colpoint2),
                                                                     (hitscan_startpoint, hitscan_endpoint))
                            if intersect_point is not None:
                                hit_point = intersect_point
                                if colpoint1[0] > colpoint2[0]:
                                    rightpoint = colpoint1[0]
                                    leftpoint = colpoint2[0]
                                else:
                                    rightpoint = colpoint2[0]
                                    leftpoint = colpoint1[0]

                                if hitscan_endpoint[1] > hitscan_startpoint[1]:
                                    bottompoint = hitscan_startpoint[1]
                                    toppoint = hitscan_endpoint[1]
                                else:
                                    bottompoint = hitscan_endpoint[1]
                                    toppoint = hitscan_startpoint[1]
                                print("INTERSECT")
                                if leftpoint < intersect_point[0] < rightpoint:
                                    if toppoint < intersect_point[1] < bottompoint:
                                        # The segment hit!
                                        print("HIT")
                if hit_point is not None:
                    hit = entities.HitMarker(hit_point[0], hit_point[1])
                    print("Spawn me one!")
                    world.spawn_entity(hit)

                #world.rewind_to_snapshot(fastforward)  # Fast forward back to the real
        # If we pressed the shoot button
        # Can we actually shoot?
            # Grab the correct state that we're on when we shoot
            # Is this too far back for rewind?
                # pass
            # If not
                # Rewind back to the state
                # If we hit a shootable object then
                # Call takedamage on object


        maxfric = 0.5

        self.angle = self.angle % (2 * math.pi)
        self.angle = round(self.angle, 10)

        speed = math.sqrt(self.xvel**2 + self.yvel**2)
        direction = math.atan2(self.yvel, self.xvel)

        fric = speed*0.0015
        centripmax = 2
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
        self.xacc = throttle * math.cos(self.angle)
        self.yacc = -throttle * math.sin(self.angle)
        self.xvel += self.xacc*dt
        self.yvel += self.yacc*dt

        #self.xvel = round(self.xvel, 4)
        #self.yvel = round(self.yvel, 4)

        self.xpos += self.xvel*dt
        self.ypos += self.yvel*dt

        #self.xpos = round(self.xpos, 0)
        #self.ypos = round(self.ypos, 0)

        # self.xpos = self.xpos%150000
        # self.ypos = self.ypos%150000

        # COLLISION
        players_colliding = self.check_player_col(world)
        if players_colliding:
            # Find what my velocity is with momentum transfer
            for player in players_colliding:
                xv = self.xvel
                yv = self.yvel
                self.xvel = player.xvel
                self.yvel = player.yvel
                player.xvel = xv
                player.yvel = yv

        walls = self.check_wall_col(lvl0, False, self.xpos, self.ypos)

        if walls: # Check if it hit anything
            for col in walls: # Loop through every wall it hit
                # Right side of block
                if self.xvel < 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos - self.xvel*dt, self.ypos):
                        self.xpos = col[0] + col[2]
                        self.xvel = 0
                # Left side of block
                elif self.xvel > 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos - self.xvel*dt, self.ypos):
                        self.xpos = col[0] - self.w
                        self.xvel = 0
                # Bottom side of block
                if self.yvel < 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos, self.ypos - self.yvel*dt):
                        self.ypos = col[1] + col[3]
                        self.yvel = 0
                # Top side of block
                elif self.yvel > 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos, self.ypos - self.yvel*dt):
                        self.ypos = col[1] - self.h
                        self.yvel = 0

        self.netxpos.set(self.xpos, True)
        self.netypos.set(self.ypos, True)
        self.netxvel.set(self.xvel, True)
        self.netyvel.set(self.yvel, True)
        self.netxacc.set(self.xacc, True)
        self.netyacc.set(self.yacc, True)
        self.netangle.set(self.angle, True)
        return None

    def rect_col(self, rect1, rect2):
        # not to the right and not to the left
        if not rect1[0] >= rect2[0] + rect2[2] and not rect1[0] + rect1[2] <= rect2[0]:
            # not below and not above
            if not rect1[1] >= rect2[1] + rect2[3] and not rect1[1] + rect1[3] <= rect2[1]:
                return True
        return False

    def get_collision_bounds(self):
        return [(self.xpos-self.w, self.ypos-self.h),
                (self.xpos+self.w, self.ypos-self.h),
                (self.xpos-self.w, self.ypos+self.h),
                (self.xpos+self.w, self.ypos+self.h)]

    def line_intersection(self, line1, line2):
        """Line intersect function from Paul Draper
        https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines"""
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def check_wall_col(self, lvl0, wall=False, x=False, y=False):
        # If wall is set it will only check collisions with that specific wall, otherwise it checks all walls
        if x == False:
            x = self.xpos
        if y == False:
            y = self.ypos
        walls = []
        if wall:
            if self.rect_col([x, y, self.w, self.h], [wall[0], wall[1], wall[2], wall[3]]):
                return True
            return False
        else:
            for wall in lvl0:
                if self.rect_col([x, y, self.w, self.h], [wall[0], wall[1], wall[2], wall[3]]):
                    walls.append(wall)
        if walls:
            return walls
        return False

    def check_player_col(self, world):
        collided_players = []
        for player in world.player_table:
            if player != self:
                if self.rect_col([self.xpos, self.ypos, self.w, self.h],
                                 [player.xpos, player.ypos, player.w, player.h]):
                    collided_players.append(player)
        return collided_players

class CPlayer(entity.CEntity):

    def __init__(self):
        entity.CEntity.__init__(self)
        self.name = NetworkVar(self, "", 0)
        self.netxpos = NetworkVar(self, 0, 1, True)
        self.netypos = NetworkVar(self, 0, 2, True)
        self.netangle = NetworkVar(self, 0, 3)
        self.netcolour = NetworkVar(self, (0, 0, 0), 4)
        self.netxvel = NetworkVar(self, 0, 5)
        self.netyvel = NetworkVar(self, 0, 6)
        self.netxacc = NetworkVar(self, 0, 7)
        self.netyacc = NetworkVar(self, 0, 8)
        self.orgimage = pg.image.load("sprites/car.png").convert_alpha()
        self.colour = (128, 128, 128)
        self.rotimage = self.orgimage.copy()

    def update(self, world=None ,actions=None):
        if self.netcolour.var != self.colour:
            self.colour = self.netcolour.var
            self.orgimage = pg.image.load("sprites/car.png").convert_alpha()
            self.orgimage.fill(self.colour, None, pg.BLEND_MULT)
            print("CHANGE!", self.netcolour.var)

    def draw(self, pg, screen, cam):
        rectangle = pg.Rect(self.netxpos.var, self.netypos.var, 16, 16)
        deg = self.netangle.var * 180/math.pi

        self.rotimage = pg.transform.rotate(self.orgimage, deg)

        width = self.rotimage.get_rect().width
        drawx = self.netxpos.var - (width-CAR_SIZE)/2
        drawy = self.netypos.var - (width-CAR_SIZE)/2

        screen.blit(self.rotimage, [drawx-cam[0], drawy-cam[1]])
        return rectangle
