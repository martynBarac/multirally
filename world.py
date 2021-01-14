from player import Player
import entity_table
import random
import game

class World:

    def __init__(self, level_name):
        self.player_table = {} # Holds all players {Class: client, ...}
        self.entdict = {} # Holds all entities {id: Class}
        self.level = game.load_level(level_name)
        self.level_name = level_name
        self.dt = 1.5
        self.snapshots = [] # Holds entdicts from last 10 frames [oldest frame, ..., newest frame]
        self.create_ents = [] # a list of any ents that were created
        self.delete_ents = [] # a list of ents that need to be deleted




    def add_new_player(self, client, name):
        spawnx, spawny = self.level["spawn"][0] # Get first spawn point
        new_player = Player(spawnx, spawny, 0, name)
        new_player.netcolour.var = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        self.add_new_entity(new_player)
        self.player_table[new_player] = client

    def destroy_player(self, client):
        for player in self.player_table:
            if self.player_table[player] == client:
                self.destroy_entity(player._id)
                del(self.entdict[player._id])
                del(self.player_table[player])
                return None

    def add_new_entity(self, entity):
        key = None
        # Find next untaken id
        for i in range(1000):
            if i not in self.entdict:
                key = i
                break

        if key is None:
            print("ERROR!!! TOO MANY ENTS IN WORLD!!")
            exit(1)
        entity._id = key
        self.create_ents.append((entity.class_id, key))
        self.entdict[key] = entity

    def destroy_entity(self, _id):
        self.delete_ents.append(_id)
        #del(self.entdict[_id])
        self.entdict[_id] = None

    def update_existing_entity(self, entid, newent):
        self.entdict[entid] = newent

    def get_entity_from_id(self, _id):
        return self.entdict[_id]

    def get_camera_for_player(self, client):
        for player in self.player_table:
            if self.player_table[player] == client:
                print("GOT CAM")
                return player._id

    def send_entire_gamestate(self):
        data_table = {}
        new_ents = []
        print(self.entdict)
        for _id in self.entdict:
            ent = self.entdict[_id]
            if ent != None:
                ent_data_table = ent.prepare_data_table(True)
                data_table[_id] = ent_data_table
                new_ents.append((ent.class_id, _id))
        data_table["NEW"] = new_ents
        return data_table

    def update(self, client_input_table):
        """This function should return any entities that are updated"""

        self.snapshots.append(self.entdict.copy())
        if len(self.snapshots) > 10:
            self.snapshots.pop(0)

        data_table = {}
        for _id in self.entdict:
            ent = self.entdict[_id]
            if ent != None:
                if type(ent) == Player:
                    client = self.player_table[ent]
                    if client in client_input_table:
                        actions = client_input_table[client]
                    else:
                        actions = {'1': False, '2': False, '3': False, '4': False}
                    ent_data_table = ent.update(self, actions)
                else:
                    ent_data_table = ent.update(self)
                    if ent.ent_destroyed:
                        self.destroy_entity(_id)

                if ent.updated:
                    data_table[_id] = ent_data_table
                    ent.updated = False

                if self.create_ents:
                    data_table["NEW"] = self.create_ents
                    self.create_ents = []

                if self.delete_ents:
                    data_table["DEL"] = self.delete_ents
                    self.delete_ents = []
        return data_table
