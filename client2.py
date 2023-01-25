import pygame as pg
import time
import math

import constant
from constant import *
from network import *
from powerup import *
import entity_table
import game
import sys
import numpy as np
import world

"""

TODO: Snapshot list should undo delta compression for easy interp
"""
class Client:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.net_client = Network(self.sock)
        self.net_client.connect(ip, port)
        self.net_client.sock.setblocking(0)
        print("connected!")

        self.latency = 0
        self.action_history = []
        self.action_number = 0
        self.tick_number = 0
        self.tickrate = 16
        self.framerate = 64

        self.entity_dict = {}
        self.static_ents = []
        self.dat_lvl = {"wall":[]}
        self.snapshots = {}
        self.lerp_delay_ticks = 16

        self.camera_ent = None
        self.SCREEN_WIDTH = 640
        self.SCREEN_HEIGHT = 480
        self.SCREEN_SIZE = self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 640, 480
        pg.init()
        self.screen = pg.display.set_mode(self.SCREEN_SIZE)

        self.prediction_car = entity_table.entity_table[1][0](0,0,0,'player')
        self.prediction_world = None
        self.loop_start_time = time.perf_counter()
    def main_loop(self):
        game_running = True
        start_time = time.perf_counter()
        start_time_framerate = time.perf_counter()
        while game_running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_running = False

            try:
                self.net_client.receive_msg()
            except BlockingIOError:
                pass
            self.net_client.load_unread_messages()
            msg = self.net_client.read_oldest_message()

            self.process_server_message(msg)

            end_time = time.perf_counter()
            if end_time - start_time >= 1/self.tickrate:
                self.get_inputs()
                self.client_prediction(self.camera_ent)
                start_time = time.perf_counter()


                self.tick_number+=1
            end_time = time.perf_counter()

            if end_time - start_time_framerate >= 1/self.framerate:
                self.update_entity_table()
                self.draw_entities()
                start_time_framerate = time.perf_counter()

    def get_inputs(self):
        client_actions = ACTIONS.copy()
        keyboard_inputs = pg.key.get_pressed()

        if keyboard_inputs[pg.K_LEFT]:
            client_actions[LEFTARROW] = True
        if keyboard_inputs[pg.K_RIGHT]:
            client_actions[RIGHTARROW] = True
        if keyboard_inputs[pg.K_UP]:
            client_actions[UPARROW] = True
        if keyboard_inputs[pg.K_DOWN]:
            client_actions[DOWNARROW] = True
        if keyboard_inputs[pg.K_c]:
            client_actions[SHOOT_BUTTON] = self.latency

        client_actions[ACTION_NUMBER] = self.action_number
        if self.is_action_different(client_actions):
            self.send_inputs(client_actions)
            self.action_number += 1
            client_actions["TICK"] = self.tick_number
            self.action_history.append(client_actions.copy())
        return

    def is_action_different(self, actions):
        copy_actions = actions.copy()
        del(copy_actions[ACTION_NUMBER])
        copy_actions[SHOOT_BUTTON] = bool(copy_actions[SHOOT_BUTTON])
        if self.action_history:
            prev_action = self.action_history[-1].copy()
            del (prev_action["TICK"])
            del (prev_action[ACTION_NUMBER])
            prev_action[SHOOT_BUTTON] = bool(copy_actions[SHOOT_BUTTON])
            if copy_actions == prev_action:
                return False
        return True

    def send_inputs(self, inputs):
        self.net_client.send_msg(inputs)
        return

    def receive_server_msg(self):
        return

    def process_server_message(self, msg):
        self.process_server_snapshot(msg)
        return

    def process_server_message(self, msg):
        if msg:
            if 'NEW' in msg:  # Add new ents first to not cause confusion
                for new_ent in msg['NEW']:  # in new message: [[class_id, entity_id], [class_id, entity_id], ...]
                    spawned_entity = entity_table.entity_table[new_ent[0]][1]()
                    spawned_entity._id = new_ent[1]
                    self.entity_dict[str(new_ent[1])] = spawned_entity
                    print(msg['NEW'])
                    print("Created new entity", spawned_entity)
                del (msg['NEW'])  # Delete the "NEW" stuff because we don't need it ever again

            if 'DEL' in msg:
                for _id2 in msg['DEL']:
                    if str(_id2) in self.entity_dict:
                        print("Deleted entity", self.entity_dict[str(_id2)])
                        del (self.entity_dict[str(_id2)])
                del (msg['DEL'])

            # This way of doing the camera should be changed to save bandwidth
            if 'CAM' in msg:
                self.camera_ent = self.entity_dict[str(msg['CAM'])]
                del (msg['CAM'])

            if 'LEV' in msg:
                self.dat_lvl = game.load_level(msg['LEV'])
                _world = world.World(msg['LEV'])
                _world.client_world = True
                # TODO make this below more cool
                for level_ent in self.dat_lvl:
                    etable = entity_table.static_entity_table
                    if level_ent in etable:
                        for params in self.dat_lvl[level_ent]:
                            self.static_ents.append(etable[level_ent][1](*params))  # The most sweaty python technique
                self.prediction_world = _world
                del msg['LEV']

            if 'ACT' in msg:
                last_action = int(msg['ACT'])
                del msg['ACT']
            if msg:
                for _id in self.entity_dict:
                    if _id in msg:
                        msg[_id]["TICK"] = str(self.tick_number)
                        self.entity_dict[_id].snapshots.append(msg[_id])
                    else:
                        decompress = self.entity_dict[_id].snapshots[-1].copy()
                        decompress["TICK"] = str(self.tick_number)
                        self.entity_dict[_id].snapshots.append(decompress)

        return

    def update_entity_table(self):
        for _id in self.entity_dict:
            self.entity_dict[_id].apply_data_table(self.tick_number-self.lerp_delay_ticks, self.lerp_delay_ticks)
        return

    def draw_entities(self):
        self.screen.fill((0, 0, 0))
        end_time = time.perf_counter()
        if self.prediction_world is not None: self.prediction_world.dt = end_time-self.loop_start_time
        cam = (0,0)
        for _id in self.entity_dict:
            self.entity_dict[_id].update(self.prediction_world)
            cam = (self.camera_ent.netxpos.var-self.SCREEN_WIDTH//2, self.camera_ent.netypos.var-self.SCREEN_HEIGHT//2)
            self.entity_dict[_id].draw(pg, self.screen, cam)
        self.loop_start_time = time.perf_counter()
        # Draw client ents
        for prop in self.static_ents:
            prop.draw(pg, self.screen, cam)
        if self.dat_lvl is not None:
            for wall in self.dat_lvl["wall"]:
                pg.draw.rect(self.screen, (255, 255, 255), [wall[0] - cam[0], wall[1] - cam[1], wall[2], wall[3]])

        predictor_line_angle = self.prediction_car.angle
        sides = [np.array([-8, -5]), np.array([-8, 5]), np.array([8, 5]), np.array([8, -5])]
        rotation = np.array([[math.cos(predictor_line_angle), -math.sin(predictor_line_angle)],
                             [math.sin(predictor_line_angle), math.cos(predictor_line_angle)]])
        predictor_add_x = (self.prediction_car.xpos) - cam[0] + 6
        predictor_add_y = (self.prediction_car.ypos) - cam[1] + 7
        translation = np.array([predictor_add_x, predictor_add_y])
        for i in range(len(sides)):
            sides[i] = np.dot(sides[i], rotation)
            sides[i] = sides[i] + translation
        for i in range(len(sides)):
            pg.draw.line(self.screen, (0, 255, 0), sides[i - 1], sides[i])
        pg.display.update()
        return

    def client_prediction(self, player_car):
        if self.prediction_world is None or self.action_history is None:
            return

        self.prediction_car.angle = player_car.netangle.var
        self.prediction_car.xpos = player_car.netxpos.var
        self.prediction_car.ypos = player_car.netypos.var
        self.prediction_car.xvel = player_car.netxvel.var
        self.prediction_car.yvel = player_car.netyvel.var
        self.prediction_car.omega = player_car.netomega.var
        self.prediction_car.health = 100
        self.prediction_car.dead = False

        i = 0
        while True:
            if i > len(self.action_history)-1:
                break
            if i == len(self.action_history) - 1:

                time1 = self.action_history[i]["TICK"]
                time2 = self.tick_number
            else:
                time1 = self.action_history[i]["TICK"]
                time2 = self.action_history[i+1]["TICK"]
            time1 = max(time1, self.tick_number-self.lerp_delay_ticks-1)
            self.prediction_world.dt = 10 / self.tickrate
            if time2 >= self.tick_number-self.lerp_delay_ticks:
                for j in range((time2-time1)):
                    self.prediction_car.update(self.prediction_world, self.action_history[i])

                    # Update static entities
                    for sEnt in self.prediction_world.static_entities:
                        sEnt.update(self.prediction_world)
            else:
                self.action_history.pop(i)
                continue

            #print(len(self.action_history))
            i+=1
        return

