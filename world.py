from player import Player


class World:

    def __init__(self, level):
        self.player_table = {}
        self.entdict = {}
        self.walls = level
        self.dt = 1
        self.snapshots = []

    def add_new_player(self, client, name, spawnx, spawny, spawnang):
        new_player = Player(spawnx, spawny, spawnang, name)
        self.add_new_entity(new_player)
        self.player_table[new_player] = client

    def add_new_entity(self, entity):

        key = None
        for i in range(1000):
            if not self.entdict[i]:
                key = i
                break
        if not key:
            print("ERROR!!! TOO MANY ENTS IN WORLD!!")
            exit(1)
        self.entdict[key] = entity

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

        for _id in len(self.entdict):
            ent = self.entdict[_id]
            if type(ent) == Player:
                client = self.player_table[ent]
                actions = client_input_table[client]
                ent_data_table = ent.update(self, actions)
            else:
                ent_data_table = ent.update(self)

            if ent.updated:
                data_table[_id] = ent_data_table


