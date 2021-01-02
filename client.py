import pygame as pg
import time
import math
from constant import *
from network import *
from level import *
from powerup import *
import entity_table

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

addr = input("Enter server address: ")
if not addr:
    addr = "192.168.0.20"

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
game_over = False

old_client_actions = ACTIONS.copy()
sock.setblocking(0)
start_time = time.perf_counter()
st = time.perf_counter()
start_time2 = [st]
snapshots = []
msg = None

def do_thing_with_message():
    cf = None
    if msg:
        print(msg)
        st = time.perf_counter()
        start_time2.append(st)
        start_time2.pop(0)
        if 'NEW' in msg:  # Add new ents first to not cause confusion
            for new_ent in msg['NEW']:  # in new message: [[class_id, entity_id], [class_id, entity_id], ...]
                entity_dict[str(new_ent[1])] = entity_table.entity_table[new_ent[0]][1]()
                print("Created new entity", entity_dict[str(new_ent[1])])
            del (msg['NEW'])  # Delete the "NEW" stuff because we don't need it ever again

        if 'DEL' in msg:
            for _id in msg['DEL']:
                print("Deleted entity", entity_dict[str(_id)])
                del (entity_dict[str(_id)])
            del (msg['DEL'])

        # This way of doing the camera should be changed to save bandwidth
        if 'CAM' in msg:
            cf = entity_dict[str(msg['CAM'])]
            del (msg['CAM'])

        snapshots.append(msg)
        if len(snapshots) > 2:
            snapshots.pop(0)

    if len(snapshots) >= 2:
        for _id in snapshots[0]:
            if _id in snapshots[1]:
                entity_dict[_id].apply_data_table_lerp((snapshots[0][_id], snapshots[1][_id]), start_time2[0], time.perf_counter())  # Apply all the data we received to the ents
            else:
                entity_dict[_id].apply_data_table(snapshots[0][_id])
    else:
        if msg:
            for _id in msg:
                entity_dict[_id].apply_data_table(msg[_id])

    return cf


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
        my_client.send_msg(client_actions)
        start_time = time.perf_counter()
        old_client_actions = client_actions.copy()

    try:
        msg = my_client.receive_msg()
    except BlockingIOError:
        msg = None

    data = do_thing_with_message()
    if data is not None:
        camfollowing = data

    i = 0
    while len(my_client.unread_messages) != 0:

        data = do_thing_with_message()
        if data is not None:
            camfollowing = data

        try:
            msg = my_client.receive_msg()
        except BlockingIOError:
            msg = None
        i = i+1

        # If we cant keep up with all the messages then just discard some
        if i > 5000:
            print("CANCEL")
            my_client.unread_messages = ""
            break


    # Draw everything
    screen.fill((0, 0, 0))
    for _id in entity_dict:
        entity_dict[_id].update()
        if camfollowing:
            cam = (camfollowing.netxpos.var-SCREEN_WIDTH//2, camfollowing.netypos.var-SCREEN_HEIGHT//2)
        entity_dict[_id].draw(pg, screen, cam)

    for wall in lvl0:
        pg.draw.rect(screen, (255, 255, 255), [wall[0]-cam[0], wall[1]-cam[1], 32, 32])

    dt = clock.tick(FRAMERATE)
    pg.display.update()


