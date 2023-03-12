import entities
import math
import entity
import numpy as np
from constant import *
from networkvar import NetworkVar
import pygame as pg # Needs to be imported for image loading

UPARROW = '1'
LEFTARROW = '2'
RIGHTARROW = '3'
DOWNARROW = '4'


class Player(entity.Entity):
    def __init__(self, x = 0, y = 0, angle = 0, name = "default", owner = None):
        entity.Entity.__init__(self)
        self.class_id = 1
        self.owner = owner
        self.shootable = True
        self.name = NetworkVar(self, name, 0)
        self.netxpos = NetworkVar(self, x, 1, True)
        self.netxpos.quantise = 2
        self.netypos = NetworkVar(self, y, 2, True)
        self.netypos.quantise = 2
        self.angle = angle
        self.netangle = NetworkVar(self, angle, 3)
        self.netangle.quantise = 6
        self.netcolour = NetworkVar(self, (255, 255, 0), 4)
        self.gun_range = 500
        self.dead = False
        self.wheeldirection = 0

        self.xpos = x
        self.ypos = y
        self.w = CAR_SIZE
        self.h = CAR_SIZE
        self.moment_of_inertia = self.w*math.pow(self.h, 3)/12

        self.xvel = 0
        self.yvel = 0
        self.netxvel = NetworkVar(self, self.xvel, 5, True)
        self.netxvel.quantise = 2
        self.netxvel.only_send_to_owner = True
        self.netyvel = NetworkVar(self, self.yvel, 6, True)
        self.netyvel.quantise = 2
        self.netyvel.only_send_to_owner = True
        self.xacc = 0
        self.yacc = 0
        self.omega = 0 # Anglular velocity
        self.netomega = NetworkVar(self, self.omega, 7)
        self.netomega.quantise = 10
        self.netomega.only_send_to_owner = True
        self.alpha = 0 # Angluar acceleration

        self.health = 100
        self.nethealth = NetworkVar(self, self.health, 8)
        self.nethealth.quantise = 0
        self.mass = 10
        self.topSpeed = 10
        self.engine_power = 20
        self.tyre_power = 70
        self.colour = (255, 255, 255)
        self.image = "sprites/car.png"

        self.strength = 2

    def update(self, world, actions = ACTIONS):
        # world variables
        dt = world.dt

        lvl0 = world.level["wall"]

        # Do actions
        throttle = 0
        self.wheeldirection = 0
        self.xacc = 0
        self.yacc = 0
        self.alpha = 0
        wheel_pos_rear = -8
        wheel_pos_front = 8
        if not self.dead:
            #self.yvel=0
            #self.xvel = 0
            if UPARROW in actions:
                if actions[UPARROW]:
                    throttle = self.engine_power
                    #self.yvel =-10
                elif actions[DOWNARROW]:
                    throttle = -self.engine_power/2
                    #self.yvel = 10
                if actions[LEFTARROW]:
                    self.wheeldirection = math.pi/8
                    #self.xvel = -10
                elif actions[RIGHTARROW]:
                    self.wheeldirection = -math.pi/8
                    #self.xvel = 10
            if actions[SHOOT_BUTTON]:
                latency = actions[SHOOT_BUTTON]
                if not world.client_world:
                    self.shoot(world, latency)

        self.angle = self.angle % (2 * math.pi)
        self.angle = round(self.angle, 10)
        speed = np.hypot(self.xvel, self.yvel)
        vlong = self.xvel*math.cos(self.angle) - self.yvel*math.sin(self.angle)
        vlat = self.xvel*math.sin(self.angle) + self.yvel*math.cos(self.angle)
        force_centripital = 0
        force_drag = 0.001*np.sign(vlong)*vlong**2
        force_drag_lat = 1*np.sign(vlat)*vlat**2
        force_drag_lat = np.clip(force_drag_lat, -self.tyre_power, self.tyre_power)
        self.omega = 0
        if self.wheeldirection:
            force_drag = force_drag*1
            force_drag_lat = force_drag_lat*1
            radius = 32/math.sin(self.wheeldirection)
            #force_centripital = self.mass*(vlong**2)/radius
            #force_centripital = np.clip(force_centripital, -self.tyre_power, self.tyre_power)
            self.omega = vlong/radius
        #self.apply_force(math.pi/2, force_centripital)
        self.apply_force(0, throttle)
        self.apply_force(0, -force_drag)
        self.apply_force(math.pi/2, force_drag_lat)



        # Apply the goods
        self.omega += self.alpha * dt
        self.xvel += self.xacc*dt
        self.yvel += self.yacc*dt
        self.angle += self.omega * dt
        self.xpos += self.xvel*dt
        self.ypos += self.yvel*dt


        # COLLISION
        self.do_collision(world, lvl0)
        self.netxpos.set(self.xpos, True)
        self.netypos.set(self.ypos, True)
        self.netxvel.set(self.xvel, True)
        self.netyvel.set(self.yvel, True)
        self.netangle.set(self.angle, True)
        self.netomega.set(self.omega, True)
        self.nethealth.set(self.health, True)
        return None

    def apply_force(self, theta, mag):
        """Apply a force to the car that pushes and gives angular velocity
        theta: Direction of the force relative to the direction of the car
        mag: Magnitude of the force
        """
        # The easy newton
        accel = mag/self.mass
        xcomp = math.cos(self.angle+theta)
        ycomp = -math.sin(self.angle+theta)
        self.xacc += accel*xcomp
        self.yacc += accel*ycomp

    #Breaks when you shoot on a wall
    def shoot(self, world, latency):
        """
        We shoot and do lag compensation
        """

        # Get the hitscan stuff before rewind because client predicts itself in present
        hitscan_endpoint = (
            self.xpos + math.cos(self.angle) * self.gun_range, self.ypos - math.sin(self.angle) * self.gun_range)
        hitscan_startpoint = (self.xpos, self.ypos)
        hit_point = None
        hit_entity = None

        # Rewind the game
        snapshots_behind = latency
        fastforward = None


        if 0 < snapshots_behind < len(world.snapshots) - 1:
            fastforward = world.rewind_to_snapshot_index(-snapshots_behind)  # Rewind to the past

        for _id in world.entdict:
            _entity = world.entdict[_id]
            if _entity is None:
                continue
            if _entity.shootable and _entity != self:
                colpoints = _entity.get_collision_bounds()
                for i in range(len(colpoints)):
                    colpoint1 = colpoints[i - 1]
                    colpoint2 = colpoints[i]
                    intersect_point = self.line_intersection((colpoint1, colpoint2),
                                                             (hitscan_startpoint, hitscan_endpoint))
                    if intersect_point is not None:
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
                        if leftpoint <= intersect_point[0] <= rightpoint:
                            if toppoint >= intersect_point[1] >= bottompoint:
                                hit_point = intersect_point
                                hit_entity = _entity
                                # The segment hit!
        if hit_point is not None:
            hit = entities.HitMarker(hit_point[0], hit_point[1])
            world.spawn_entity(hit)
        if fastforward is not None:
            world.rewind_to_snapshot(fastforward)  # Fast forward back to the real

        if hit_entity is not None:
            hit_entity.get_shot(1)

    def do_collision(self, world, lvl0):
        dt = world.dt
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

        if walls:  # Check if it hit anything
            for col in walls:  # Loop through every wall it hit
                # Right side of block
                if self.xvel < 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos - self.xvel * dt,
                                                                                  self.ypos):
                        self.xpos = col[0] + col[2]
                        self.take_damage(abs(self.xvel)/self.strength)
                        self.xvel = 0
                # Left side of block
                elif self.xvel > 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos - self.xvel * dt,
                                                                                  self.ypos):
                        self.xpos = col[0] - self.w
                        self.take_damage(abs(self.xvel) /self.strength)
                        self.xvel = 0
                # Bottom side of block
                if self.yvel < 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos,
                                                                                  self.ypos - self.yvel * dt):
                        self.ypos = col[1] + col[3]
                        self.take_damage(abs(self.yvel) /self.strength)
                        self.yvel = 0
                # Top side of block
                elif self.yvel > 0:
                    if self.check_wall_col(lvl0, col) and not self.check_wall_col(lvl0, col, self.xpos,
                                                                                  self.ypos - self.yvel * dt):
                        self.ypos = col[1] - self.h
                        self.take_damage(abs(self.yvel)/self.strength)
                        self.yvel = 0

    def rect_col(self, rect1, rect2):
        # not to the right and not to the left
        if not rect1[0] >= rect2[0] + rect2[2] and not rect1[0] + rect1[2] <= rect2[0]:
            # not below and not above
            if not rect1[1] >= rect2[1] + rect2[3] and not rect1[1] + rect1[3] <= rect2[1]:
                return True
        return False

    def get_collision_bounds(self):
        return [(self.xpos-self.w/2, self.ypos-self.h/2),
                (self.xpos+self.w/2, self.ypos-self.h/2),
                (self.xpos-self.w/2, self.ypos+self.h/2),
                (self.xpos+self.w/2, self.ypos+self.h/2)]

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

    def get_shot(self, damage):
        """Take some damage"""
        self.take_damage(damage)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.dead = True
            self.health = 0


class CPlayer(entity.CEntity):
    def __init__(self):
        entity.CEntity.__init__(self)
        self.class_id = 1
        self.name = NetworkVar(self, "", 0)
        self.netxpos = NetworkVar(self, 0, 1, True)
        self.netypos = NetworkVar(self, 0, 2, True)
        self.netangle = NetworkVar(self, 0, 3, True, True)
        self.netcolour = NetworkVar(self, (0, 0, 0), 4)
        self.netxvel = NetworkVar(self, 0, 5, True)
        self.netyvel = NetworkVar(self, 0, 6, True)
        self.netomega = NetworkVar(self, 0, 7)
        self.health = NetworkVar(self, 0, 8)
        self.orgimage = pg.image.load("sprites/car.png").convert_alpha()
        self.colour = (128, 128, 128)
        self.rotimage = self.orgimage.copy()
        self.actor = True

    def update(self, world=None ,actions=None):
        if np.array_equal(self.netcolour.var, self.colour):
            self.colour = list(self.netcolour.var)
            self.orgimage = pg.image.load("sprites/car.png").convert_alpha()
            self.orgimage.fill(self.colour, None, pg.BLEND_MULT)
            print("CHANGE!", self.netcolour.var)

    def draw(self, pg, screen, cam):

        deg = self.netangle.var * 180/math.pi

        self.rotimage = pg.transform.rotate(self.orgimage, deg)

        width = self.rotimage.get_rect().width
        drawx = self.netxpos.var - (width-CAR_SIZE)/2
        drawy = self.netypos.var - (width-CAR_SIZE)/2
        rectangle = pg.Rect(drawx - cam[0], drawy - cam[1], 0.2*self.health.var, 4)
        rectangle2 = pg.Rect(drawx - cam[0], drawy - cam[1], 20, 4)
        screen.blit(self.rotimage, [drawx-cam[0], drawy-cam[1]])
        pg.draw.rect(screen, (244,10,0), rectangle)
        #print(self.health.var)
        pg.draw.rect(screen, (255, 0, 0), rectangle2, 1)
        return rectangle
