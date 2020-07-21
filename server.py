
import time
from network import *
from constant import *
import random
import select
import pygame as pg

print("Initialising")
my_server = Network("192.168.0.20", 27014)
my_server.sock.setblocking(0)
my_server.sock.bind((my_server.IP, my_server.PORT))

player_list = []
client_dict = {} # Client dict client_address:[username, Player, inputs]
MAXPLAYERS = 2

my_server.sock.listen(MAXPLAYERS)

maybe_readable = [my_server.sock]
maybe_writeable = []
sent_times = 0
dt = 0

while True:
    readable, writeable, exception = select.select(maybe_readable, maybe_writeable, maybe_readable)
    for s in readable:
        if s == my_server.sock:
            conn, addr = s.accept()
            conn.setblocking(0)
            maybe_readable.append(conn)
            maybe_writeable.append(conn)
            print(addr, "Connected!")

        else:
            print("waiting..")
            msg = s.recv(BUFFERSIZE)
            msg = bytes_to_list(msg)
            if len(msg) > 0:
                msg = msg[0]
            addr = s.getpeername()
            print(msg)
            if msg:
                if msg[0] == HEAD_PINFO:
                    if addr in client_dict:
                        client_dict[addr][1] = existing_player
                        new_player = update_existing_player(msg, existing_player)
                    else:
                        new_player = return_error_player(msg)

                    player_list = update_player_list(new_player, player_list)
                    username = new_player.name
                    client_dict[addr] = [username, new_player, ACTIONS]
                    print("Player: " + str(addr), username + " connected!")
                    print(len(player_list))

    if len(player_list) >= MAXPLAYERS:

        for s in writeable:
            print("STARTING GAME!!")
            s.send(b"START:")
        sent_times += 1
        if sent_times > 30:
            break

    for s in writeable:
        for pl in player_list:
            msg = encode_player_data(pl, True)
            msg = list_to_bytes(msg)
            s.send(msg)

    time.sleep(0.1)


clock = pg.time.Clock()
game_over = False
print(len(maybe_readable))
while not game_over:
    readable, writeable, exception = select.select(maybe_readable, maybe_writeable, maybe_readable)
    for s in readable:
        msg = s.recv(BUFFERSIZE)
        msg = bytes_to_list(msg)[0]
        addr = s.getpeername()

        if msg:
            if msg[0] == HEAD_PLAYERINPUT:
                player_actions = decode_action_data(msg)
                client_dict[addr][2] = player_actions

    for client_addr in client_dict:
        new_player = client_dict[client_addr][1]
        player_actions = client_dict[client_addr][2]
        new_player.update(player_actions, dt)

    for s in writeable:
        for client_addr in client_dict:
            pl = client_dict[client_addr][1]
            msg = encode_player_data(pl)
            msg = list_to_bytes(msg)
            s.send(msg)

    dt = TICKRATE
    time.sleep(1/TICKRATE)
