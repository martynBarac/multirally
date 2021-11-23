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
import winsound

SNAPSHOT_BUFFER = 30
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
"""
if len(sys.argv) >= 2:
    addr = "110.33.73.252:2302"
else:
    addr = socket.gethostbyname(socket.gethostname())
"""

addr = socket.gethostbyname(socket.gethostname())

addr = addr.split(":")
if len(addr) > 1:
    PORT = int(addr[1])
else:
    PORT = 2302

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
latency = TICKRATE*SNAPSHOT_BUFFER
game_over = False

old_client_actions = ACTIONS.copy()
prediction_amplifier = 9
old_xpos = 0
old_ypos = 0
sock.setblocking(0)
start_time = time.perf_counter()
st = time.perf_counter()
start_time2 = [st]
snapshots = []
action_number = 0
server_reaction_time = 0
action_history = np.array([]) #TODO This list needs purge
server_action_numbers = [0]
camfollowing_oldnetangle = 0
server_last_action = None
client_prediction_car = entity_table.entity_table[1][0](0,0,0,'player')
client_prediction_world = None
CLIENT_PREDICTION_PRESICION = 2
msg = None
static_ents = [] # Entities that are static in the level
myfont = pg.font.SysFont('Comic Sans MS', 30)

class Dat:
    lvl = {"wall":[]}


def do_thing_with_message(_world):
    cf = None
    last_action = None
    if msg:
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
            _world.client_world = True
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
        if len(snapshots) > SNAPSHOT_BUFFER: #Snapshot Buffer
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

debug_dots_enable = False
debug_dots_server = []
debug_dots_client = []
_once = True
delta_time_start = time.perf_counter()
time_to_correct_position = time.perf_counter()
client_actions = ACTIONS.copy()
while not game_over:
    # Handle client inputs
    for event in pg.event.get():
        if event.type == pg.QUIT:
            game_over = True
    if time.perf_counter() - start_time > 1/16:
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
        if keyboard_inputs[pg.K_SPACE]:
            client_actions[SHOOT_BUTTON] = latency
    else:
        stuff = client_actions.copy()
        client_actions = stuff
    # delta compression
    if client_actions != old_client_actions and time.perf_counter() - start_time > 1/16:
        old_client_actions = client_actions.copy()
        action_number += 1
        print("SEND", action_number)
        client_actions[ACTION_NUMBER] = action_number
        my_client.send_msg(client_actions)
        start_time = time.perf_counter()
        client_actions["TIME"] = time.perf_counter()
        if len(action_history) > 0:
            action_history[-1]["TIME2"] = time.perf_counter() # Save the moment we released the key
        action_history = np.append(action_history, client_actions)
    #else:
    #    client_actions[ACTION_NUMBER] = action_number
    #    client_actions["TIME"] = time.perf_counter()

    if camfollowing:
        #reset prediction car to server car
        old_xpos = client_prediction_car.xpos
        old_ypos = client_prediction_car.ypos
        client_prediction_car.angle = camfollowing.netangle.var
        client_prediction_car.xpos = camfollowing.netxpos.var
        client_prediction_car.ypos = camfollowing.netypos.var
        client_prediction_car.xvel = camfollowing.netxvel.var
        client_prediction_car.yvel = camfollowing.netyvel.var
        client_prediction_car.xacc = camfollowing.netxacc.var
        client_prediction_car.yacc = camfollowing.netyacc.var

    # Client prediction
    if client_prediction_world is not None and server_last_action is not None:
        # Apply new thing and do last action
        done = False
        latency = 0
        oldaction = None
        nowtime = time.perf_counter()
        time_to_correct_position = time.perf_counter()
        for action in action_history:
            # Only predict actions that are after the last action recieved
            if action['a'] >= server_last_action:
                time_pressed = action["TIME"]
                time_released = action.get("TIME2", False)
                time_held = time.perf_counter()-action["TIME"]

                if not done:
                    latency = server_reaction_time - action["TIME"]
                    # When we press a key, how long until the server responds?
                    done = True
                if action['a'] > server_last_action:
                    # We want to predict how long the server thinks we have been pressing the button down
                    # And exclude calculating part the server already knows about
                    dt2 = time_held
                    if time_released:
                        dt2 = time_released - time_pressed

                if action['a'] == server_last_action:
                    dt2 = latency
                    if time_released:
                        dt2 = latency-(time.perf_counter()-time_released)
                client_prediction_world.dt = dt2*10/CLIENT_PREDICTION_PRESICION
                for i in range(CLIENT_PREDICTION_PRESICION):
                    client_prediction_car.update(client_prediction_world, action)
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

    # Draw server ents
    for _id in entity_dict:
        entity_dict[_id].update()
        if camfollowing:
            #cam = (0,0)
            #cam = (camfollowing.netxpos.var-SCREEN_WIDTH//2, camfollowing.netypos.var-SCREEN_HEIGHT//2)
            cam = (client_prediction_car.xpos - SCREEN_WIDTH // 2, client_prediction_car.ypos - SCREEN_HEIGHT // 2)
        if entity_dict[_id] != camfollowing:
            entity_dict[_id].draw(pg, screen, cam)

    # Draw client ents
    for prop in static_ents:
        prop.draw(pg, screen, cam)

    for wall in Dat.lvl["wall"]:
        pg.draw.rect(screen, (255, 255, 255), [wall[0]-cam[0], wall[1]-cam[1], wall[2], wall[3]])
    predictor_line_angle = client_prediction_car.angle
    sides = [np.array([-8, -5]), np.array([-8, 5]), np.array([8, 5]), np.array([8, -5])]
    rotation = np.array([[math.cos(predictor_line_angle),-math.sin(predictor_line_angle)],
                          [math.sin(predictor_line_angle), math.cos(predictor_line_angle)]])
    predictor_add_x = (client_prediction_car.xpos) - cam[0] + 6
    predictor_add_y = (client_prediction_car.ypos) - cam[1] + 7
    translation = np.array([predictor_add_x,predictor_add_y])
    for i in range(len(sides)):
        sides[i] = np.dot(sides[i], rotation)
        sides[i] = sides[i] + translation
    for i in range(len(sides)):
        pg.draw.line(screen, (0, 255, 0), sides[i - 1], sides[i])
    predictor_end_x = math.cos(predictor_line_angle)*50+predictor_add_x
    predictor_end_y = math.sin(predictor_line_angle)*50+predictor_add_y

    # draw dots
    if debug_dots_enable:
        debug_dots_client.append((client_prediction_car.xpos, client_prediction_car.ypos))
        debug_dots_server.append((camfollowing.netxpos.var, camfollowing.netypos.var))
        if len(debug_dots_client) > 600:
            debug_dots_client.pop(0)
            debug_dots_server.pop(0)
        for dot_pos in debug_dots_server:
            dot_pos_rel = (dot_pos[0] - cam[0], dot_pos[1] - cam[1])
            pg.draw.circle(screen, (255,0,0), dot_pos_rel, 8)
        for dot_pos in debug_dots_client:
            dot_pos_rel = (dot_pos[0]-cam[0], dot_pos[1]-cam[1])
            pg.draw.circle(screen, (0,255,0), dot_pos_rel, 8, 1)

    # Draw debug hud
    try:
        textsurface = myfont.render(str(round(latency*1000))+"   "+str(len(action_history)), False, (0, 200, 0))
        screen.blit(textsurface, (0, 0))
    except NameError:
        pass

    # Draw hitscan
    hitscan_startpoint = (SCREEN_WIDTH//2+6, SCREEN_HEIGHT//2+6)
    hitscan_endpoint = (hitscan_startpoint[0] + math.cos(predictor_line_angle) * 500,
                        hitscan_startpoint[1] - math.sin(predictor_line_angle) * 500)
    pg.draw.line(screen, (255,0,0), hitscan_startpoint, hitscan_endpoint, 1)
    pg.display.update()