from player import Player
import entity_table


class World:

    def __init__(self, level):
        self.player_table = {} # Holds all players {Class: client, ...}
        self.entdict = {} # Holds all entities {id: Class}
        self.walls = level
        self.dt = 1
        self.snapshots = [] # Holds entdicts from last 10 frames [oldest frame, ..., newest frame]
        self.create_ents = [] # a list of any ents that were created

    def add_new_player(self, client, name, spawnx, spawny, spawnang):
        new_player = Player(spawnx, spawny, spawnang, name)
        self.add_new_entity(new_player)
        self.player_table[new_player] = client

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
        self.create_ents.append(entity.class_id)
        self.entdict[key] = entity

    def destroy_entity(self, _id):
        del(self.entdict[_id])
        self.entdict[_id] = None

    def update_existing_entity(self, entid, newent):
        self.entdict[entid] = newent

    def get_entity_from_id(self, _id):
        return self.entdict[_id]

    def update(self, client_input_table):
        """This function should return any entities that are updated"""

        data_table = {}
        self.snapshots.append(self.entdict.copy())
        if len(self.snapshots) > 10:
            self.snapshots.pop(0)

        for _id in range(len(self.entdict)):
            ent = self.entdict[_id]
            if type(ent) == Player:
                client = self.player_table[ent]
                actions = client_input_table[client]
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

        return data_table
