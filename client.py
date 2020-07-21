import pygame as pg
import time
import math
from player import Player
from network import *
from constant import *
from level import *
import random

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

my_client = Network(IP, PORT)
my_client.connect(IP, PORT)
print("connected!")
username = input("Enter your username: ")
colour = input("Enter your colour")
if not colour:
    colour = (255, 255, 255)
else:
    colour = decode_rgb(colour)

my_player = Player(32, 32, 0,username)
my_player.colour = colour
message = encode_player_data(my_player, True)
my_client.send_msg_list(message)


player_list = []
client_dict = {}
while True:
    msg = my_client.recv_msg_list()
    if msg:
        if len(msg) > 0:
            if msg[0] == HEAD_PINFO:
                new_player = return_error_player(msg)
                existing_player = find_player_from_name(new_player.name, player_list)
                if existing_player:
                    new_player = update_existing_player(msg, existing_player)
                player_list = update_player_list(new_player, player_list)

            if msg[0] == "START":
                print("Starting Game")
                break

# Open up the pygame window now
pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)
clock = pg.time.Clock()

dt = 0
game_over = False
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

    message = encode_action_data(client_actions)
    my_client.send_msg_list(message)

    msg = my_client.recv_msg_list()
    if msg:
        if len(msg) > 0:
            if msg[0] == HEAD_PINFO:
                new_player = return_error_player(msg)
                existing_player = find_player_from_name(new_player.name, player_list)
                if existing_player:
                    new_player = update_existing_player(msg, existing_player)

                if new_player.name == my_player.name:
                    my_player = new_player
                player_list = update_player_list(new_player, player_list)

    for player in player_list:
        if player == my_player:
            player.update(client_actions, dt) # predict and interpolate for smoothness
        else:
            player.update(ACTIONS ,dt)

    player_list = update_player_list(my_player, player_list)

    # Draw everything
    camera_pos = (my_player.xpos-SCREEN_WIDTH/2, my_player.ypos-SCREEN_HEIGHT/2)
    screen.fill((0, 0, 0))
    for player in player_list:
        color_image = pg.Surface(player.image.get_size())
        color_image.fill(player.colour)
        draw_image = pg.transform.rotate(player.image, math.degrees(player.angle))
        draw_image.set_colorkey((255, 0, 255))
        draw_image.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        screen.blit(draw_image, (player.xpos-camera_pos[0], player.ypos-camera_pos[1]))

    for wall in lvl0:
        pg.draw.rect(screen, (255, 255, 255), [wall[0]-camera_pos[0], wall[1]-camera_pos[1], 32, 32])
    dt = clock.tick(FRAMERATE)
    pg.display.update()
