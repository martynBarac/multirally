import pygame as pg
import time
import math
from constant import *
from network import *
from powerup import *
import entity_table
import game
import sys
import numpy as np
import world

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
"""
if len(sys.argv) >= 2:
    addr = "110.33.73.252:27014"
else:
    addr = socket.gethostbyname(socket.gethostname())
"""

addr = socket.gethostbyname(socket.gethostname())

addr = addr.split(":")
if len(addr) > 1:
    PORT = int(addr[1])
else:
    PORT = 27014

IP = addr[0]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_client = Network(sock)
my_client.connect(IP, PORT)
print("connected!")

player_list = []
client_dict = {}
entity_dict = {}

# Open up the pygame window now
pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)
clock = pg.time.Clock()
cam = (0, 0)
camfollowing = None
dt = 0
dt2 = 0
game_over = False

old_client_actions = ACTIONS.copy()
sock.setblocking(0)
start_time = time.perf_counter()
st = time.perf_counter()
start_time2 = [st]
snapshots = []
action_number = 0
server_reaction_time = 0
action_history = np.array([])
server_action_numbers = [0]
camfollowing_oldnetangle = 0
server_last_action = None
client_prediction_car = entity_table.entity_table[1][0](0,0,0,'player')
client_prediction_world = None
msg = None
static_ents = [] # Entities that are static in the level

class Dat:
    lvl = {"wall":[]}


def do_thing_with_message(_world):
    cf = None
    last_action = None
    if msg:
        #print(msg)
        st = time.perf_counter()
        start_time2.append(st)
        start_time2.pop(0)
        if 'NEW' in msg:  # Add new ents first to not cause confusion
            for new_ent in msg['NEW']:  # in new message: [[class_id, entity_id], [class_id, entity_id], ...]
                entity_dict[str(new_ent[1])] = entity_table.entity_table[new_ent[0]][1]()
                print("Created new entity", entity_dict[str(new_ent[1])])
            del (msg['NEW'])  # Delete the "NEW" stuff because we don't need it ever again

        if 'DEL' in msg:
            for _id2 in msg['DEL']:
                if str(_id2) in entity_dict:
                    print("Deleted entity", entity_dict[str(_id2)])
                    del (entity_dict[str(_id2)])
            del (msg['DEL'])

        # This way of doing the camera should be changed to save bandwidth
        if 'CAM' in msg:
            cf = entity_dict[str(msg['CAM'])]
            del (msg['CAM'])

        if 'LEV' in msg:
            Dat.lvl = game.load_level(msg['LEV'])
            _world = world.World(msg['LEV'])
            #TODO make this below more cool
            if "LaserWall" in Dat.lvl:
                for lw in Dat.lvl["LaserWall"]:
                    static_ents.append(entity_table.entities.CLaserWall(lw[0], lw[1], lw[2], lw[3]))
            del msg['LEV']
        if 'ACT' in msg:
            last_action = int(msg['ACT'])
            del msg['ACT']

        server_action_numbers.append(last_action)
        snapshots.append(msg)
        if len(snapshots) > 8: #Snapshot Buffer
            snapshots.pop(0)
            server_action_numbers.pop(0)

    if len(snapshots) >= 2:
        for _id in snapshots[0]:
            if _id in snapshots[1]:
                entity_dict[_id].apply_data_table_lerp((snapshots[0][_id], snapshots[1][_id]), start_time2[0], time.perf_counter())  # Apply all the data we received to the ents
            else:
                try:
                    entity_dict[_id].apply_data_table(snapshots[0][_id])
                except KeyError:
                    pass
    else:
        if msg:
            for _id in msg:
                entity_dict[_id].apply_data_table(msg[_id])

    return cf, server_action_numbers[0], _world


while not game_over:
    # Handle client inputs
    for event in pg.event.get():
        if event.type == pg.QUIT:
            game_over = True

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
    if client_actions != old_client_actions and time.perf_counter() - start_time > 0.01:
        old_client_actions = client_actions.copy()
        action_number += 1
        print("SEND", action_number)
        client_actions[ACTION_NUMBER] = action_number
        my_client.send_msg(client_actions)
        start_time = time.perf_counter()

    else:
        client_actions[ACTION_NUMBER] = action_number
    client_actions["TIME"] = time.perf_counter()
    action_history = np.append(action_history, client_actions)
    if camfollowing:
        client_prediction_car.angle = camfollowing.netangle.var
    # Client prediction
    if client_prediction_world is not None and server_last_action is not None:
        # Apply new thing and do last action
        done = False
        latency = 0
        oldaction = None
        for action in action_history:
            # Only predict actions that are after the last action recieved
            if action['a'] >= server_last_action:
                if not done:
                    latency = server_reaction_time - action["TIME"] # When we press a key, how long until the server responds?
                    done = True
                # We want to predict how long the server thinks we have been pressing the button down
                # And exclude calculating part the server already knows about
                if action["TIME"]+ latency > time.perf_counter():
                    delta_time_start = time.perf_counter()
                    # Calculate delta time
                    if oldaction is not None:
                        client_prediction_world.dt = (action["TIME"] - oldaction["TIME"])*9
                    else:
                        client_prediction_world.dt = dt2*13000
                    # Apply the prediction
                    client_prediction_car.update(client_prediction_world, action)
                    client_prediction_car.xacc =0
                    client_prediction_car.yacc =0
                    dt2 = (time.perf_counter() - delta_time_start)
                else:
                    del action # Get rid of actions the server has already responded to
            else:
                del action
            try:
                oldaction = action
            except NameError:
                oldaction = None
                
    try:
        msg = my_client.receive_msg()
    except BlockingIOError:
        msg = None
    old_server_last_action = server_last_action
    data, server_last_action, client_prediction_world = do_thing_with_message(client_prediction_world)
    if data is not None:
        camfollowing = data

    msgs = my_client.read_unread_messages()
    for msg in msgs:
        data, server_last_action, client_prediction_world = do_thing_with_message(client_prediction_world)
        if data is not None:
            camfollowing = data
        print("yea")
    # Get the time it takes for the server to respond to new input
    if server_last_action != old_server_last_action:
        server_reaction_time = time.perf_counter()



    # Draw everything
    screen.fill((0, 0, 0))
    for _id in entity_dict:
        entity_dict[_id].update()
        if camfollowing:
            cam = (camfollowing.netxpos.var-SCREEN_WIDTH//2, camfollowing.netypos.var-SCREEN_HEIGHT//2)
        entity_dict[_id].draw(pg, screen, cam)

    for prop in static_ents:
        prop.draw(pg, screen, cam)

    for wall in Dat.lvl["wall"]:
        pg.draw.rect(screen, (255, 255, 255), [wall[0]-cam[0], wall[1]-cam[1], wall[2], wall[3]])
    predictor_line_angle = -client_prediction_car.angle
    predictor_end_x = SCREEN_WIDTH//2+math.cos(predictor_line_angle)*50
    predictor_end_y = SCREEN_HEIGHT//2+math.sin(predictor_line_angle)*50
    pg.draw.line(screen, (0,255,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), (predictor_end_x, predictor_end_y))
    dt = clock.tick(FRAMERATE/2)
    pg.display.update()
