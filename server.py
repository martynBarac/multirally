
import time
from network import *
from constant import *
import random
import select

print("Initialising")
my_server = Network("192.168.0.18", 27014)
my_server.sock.setblocking(0)
my_server.sock.bind((my_server.IP, my_server.PORT))

player_list = []
client_dict = {} # Client dict client_address:(username, Player)
MAXPLAYERS = 2

my_server.sock.listen(MAXPLAYERS)

maybe_readable = [my_server.sock]
maybe_writeable = []

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
            msg = s.recv(1024)
            addr = s.getsockname()
            msg = bytes_to_list(msg)[0]
            print(msg)
            if msg:
                if msg[0] == HEAD_PINFO:
                    new_player = decode_player_data(msg)
                    player_list = update_player_list(new_player, player_list)
                    username = new_player.name
                    client_dict[addr] = (username, new_player)
                    print("Player: " + str(addr), username + " connected!")
                    print(len(player_list))

    if len(player_list) >= MAXPLAYERS:
        for s in writeable:
            print("STARTING GAME!!")
            s.send(b"START:")
        #break

    else:
        for s in writeable:
            for pl in player_list:
                msg = encode_player_data(pl)
                msg = list_to_bytes(msg)
                working = s.send(msg)

game_over = False
while not game_over:
    msg, addr = my_server.recv_msg_list()
    if msg:
        if msg[0] == HEAD_PINFO:
            if addr in client_dict:
                new_player = decode_player_data(msg)
                player_list = update_player_list(new_player, player_list)

    random_update_chance = random.randrange(0, 300)
    if random_update_chance == 5:
        for client in client_dict:
            for player in player_list:
                message = encode_player_data(player)
                my_server.send_msg(message, client)

