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
            if i not in self.entdict:
                key = i
                break
        if key is None:
            print("ERROR!!! TOO MANY ENTS IN WORLD!!")
            exit(1)
        entity._id = key
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

        return data_table


