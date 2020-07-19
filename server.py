
import time
from network import *
from constant import *
import random
import select
import pygame as pg

print("Initialising")
my_server = Network("192.168.0.22", 27014)
my_server.sock.setblocking(0)
my_server.sock.bind((my_server.IP, my_server.PORT))

player_list = []
client_dict = {} # Client dict client_address:[username, Player, inputs]
MAXPLAYERS = 1

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
                        new_player = decode_player_data(msg, existing_player.name,
                                                        existing_player.xpos,
                                                        existing_player.ypos,
                                                        existing_player.xvel,
                                                        existing_player.yvel,
                                                        existing_player.health,
                                                        existing_player.colour
                                                        )
                    else:
                        new_player = decode_player_data(msg, "ERR", 32, 32, 0, 0, 100, (255, 255, 255))

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
        if sent_times > BUFFERSIZE//6:
            break

    for s in writeable:
        for pl in player_list:
            msg = encode_player_data(pl, True)
            msg = list_to_bytes(msg)
            s.send(msg)

    time.sleep(0.1)


clock = pg.time.Clock()
game_over = False
powerups = [[50, 500, POWERUP_HEALTH]]
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
            
            # Send powerup data (probably wrong and yucky)
            powmsg = [HEAD_POWERINFO]
            for po in powerups:
				x = "x"+str(po[0])
				y = "y"+str(po[1])
				typ = "t"+str(po[2])
				powmsg.append([x, y, typ])
			powmsg = list_to_bytes(powmsg)
			s.send(powmsg)

    dt = TICKRATE
    time.sleep(1/TICKRATE)
