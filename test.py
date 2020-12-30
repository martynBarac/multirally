from world import World
from level import *
from entity import *
from powerup import *

def world_test():
    new_world = World(lvl0)
    new_world.add_new_player("127.0.0.1", "Hello", 0, 0, 0)

    new_world.add_new_entity(Powerup(16.01, 0, 0))

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



world_test()