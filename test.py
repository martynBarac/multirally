from world import World
from level import *
from entity import *
import network
import select
import server
import time
import socket


def world_test():

    new_world = World(lvl0)
    new_world.add_new_player("127.0.0.1", "Hello", 0, 0, 0)

    print(new_world.entdict)
    print(new_world.player_table)

    print(new_world.update({"127.0.0.1": {1: False, 4: False, 2: False, 3: False}}))
    print(new_world.update({"127.0.0.1": {1: False, 4: False, 2: False, 3: False}}))

    print(new_world.update({"127.0.0.1": {1: True, 4: False, 2: False, 3: False}}))

    for i in range(10):
        print(new_world.update({"127.0.0.1": {1: False, 4: False, 2: False, 3: False}}))

    print(new_world.update({"127.0.0.1": {1: False, 4: False, 2: True, 3: False}}))
    print(new_world.update({"127.0.0.1": {1: False, 4: False, 2: True, 3: False}}))
    print(new_world.update({"127.0.0.1": {1: False, 4: False, 2: True, 3: False}}))

    print(new_world.update({"127.0.0.1": {1: False, 4: True, 2: True, 3: True}}))
    print(new_world.update({"127.0.0.1": {1: False, 4: True, 2: True, 3: True}}))


def server_test():
    my_server = server.Server("192.168.0.17", 27014)
    while True:
        my_server.update()
        time.sleep(1/60)


def client_test():

    port = 27014
    ip = "192.168.0.17"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_client = network.Network(sock)
    my_client.connect(ip, port)
    while True:

        msg = my_client.receive_msg()
        print(msg)
