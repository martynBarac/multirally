from player import Player
import entity_table
import random
import game

MAX_SNAPSHOT_HISTORY = 100
class World:

    def __init__(self, level_name):
        self.player_table = {} # Holds all players {Class: client, ...}
        self.entdict = {} # Holds all entities {id: Class}
        self.static_entities = [] # Entities that are static in the level
        self.level = game.load_level(level_name)
        self.level_name = level_name
        self.client_world = False

        # Todo refactor static entities as their own thing
        if "LaserWall" in self.level:
            for lw in self.level["LaserWall"]:
                self.add_new_static_entity(entity_table.entities.LaserWall(lw[0], lw[1], lw[2], lw[3]))

        self.dt = 1.5
        self.snapshots = [] # Holds entdicts from last MAX_SNAPSHOT_HISTORY frames [oldest frame, ..., newest frame]
        self.snapshot_number = 0 # Number tells what snapshot this is
        self.create_ents = [] # a list of any ents that were created
        self.delete_ents = [] # a list of ents that need to be deleted
        self.collision_sectors = [[]]
        self.collision_sector_size = 256
        self.entites_to_spawn = [] #Q ueue up entities to spawn in the next frame
        self.add_new_entity(entity_table.entity_table[4][0](128, 128))

    def add_new_player(self, client, name):
        spawnx, spawny = self.level["spawn"][0] # Get first spawn point
        new_player = Player(spawnx, spawny, 0, name, client)
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

    def spawn_entity(self, entity):
        self.entites_to_spawn.append(entity)

    def add_new_entity(self, entity):
        key = None
        # Find next untaken id
        for i in range(1000):
            if i not in self.entdict:
                key = i
                print(key)
                break

        if key is None:
            print("ERROR!!! TOO MANY ENTS IN WORLD!!")
            exit(1)
        entity._id = key
        self.create_ents.append((entity.class_id, key))
        self.entdict[key] = entity

    def add_new_static_entity(self, entity):
        self.static_entities.append(entity)

    def destroy_entity(self, _id):
        self.delete_ents.append(_id)
        # del(self.entdict[_id])
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

    def send_entire_gamestate(self, client):
        data_table = {}
        new_ents = []
        for _id in self.entdict:
            ent = self.entdict[_id]
            if ent is not None:
                ent_data_table = ent.prepare_data_table(client, True)
                data_table[_id] = ent_data_table
                new_ents.append((ent.class_id, _id))
        data_table["NEW"] = new_ents
        return data_table

    def rewind_to_snapshot(self, game_state):
        for _id in game_state:
            if _id in self.entdict:
                if self.entdict[_id] is not None:
                    self.entdict[_id].apply_data_table(game_state[_id])

    def rewind_to_snapshot_number(self, snapshot_number):
        old_data = self.send_entire_gamestate(None)
        game_state = None
        for snapshot in range(len(self.snapshots)):
            if self.snapshots[snapshot][0] == snapshot_number:
                game_state = self.snapshots[snapshot][1]
        if game_state is not None:
            self.rewind_to_snapshot(game_state)
        else:
            print("State " + str(snapshot_number)+ " NOT FOUND")
        return old_data

    def rewind_to_snapshot_index(self, snapshot_index):
        old_data = self.send_entire_gamestate(None)
        game_state = self.snapshots[snapshot_index][1]
        self.rewind_to_snapshot(game_state)
        return old_data

    def update(self, client_input_table):
        """This function should return any entities that are updated"""
        #Spawn queued up entities
        for ent in self.entites_to_spawn:
            self.add_new_entity(ent)
        self.entites_to_spawn = []

        #Update all the entities
        for _id in self.entdict:
            ent = self.entdict[_id]
            if ent is not None:

                if type(ent) == Player:
                    client = self.player_table[ent]
                    if client in client_input_table:
                        actions = client_input_table[client]
                    else:
                        actions = {'1': False, '2': False, '3': False, '4': False, '5': False}
                    ent.update(self, actions)
                else:
                    ent.update(self)
                    if ent.ent_destroyed:
                        self.destroy_entity(_id)

        #Update static entities
        for sEnt in self.static_entities:
            sEnt.update(self)

        #Now prepare a data table for each client to send
        client_data_table = {}
        for player in self.player_table:
            client = self.player_table[player]
            data_table = {}
            for _id in self.entdict:
                ent = self.entdict[_id]
                if ent is not None:
                    if ent.get_updated(client):
                        if ent.actor and ent != player:
                            # If we're on the screen then send info
                            if abs(ent.netxpos.var - player.netxpos.var) < 320 \
                                    or abs(ent.netypos.var - player.netypos.var) < 240:
                                ent_data_table = ent.prepare_data_table(client)
                                data_table[_id] = ent_data_table
                                ent.updated[client] = False
                        else:
                            ent_data_table = ent.prepare_data_table(client)
                            data_table[_id] = ent_data_table
                            ent.updated[client] = False

                    if self.create_ents:
                        data_table["NEW"] = self.create_ents

                    if self.delete_ents:
                        data_table["DEL"] = self.delete_ents
            client_data_table[client] = data_table

        self.snapshots.append((self.snapshot_number, self.send_entire_gamestate(None)))
        if len(self.snapshots) > MAX_SNAPSHOT_HISTORY:
            self.snapshots.pop(0)
        self.snapshot_number = (self.snapshot_number+1)%MAX_SNAPSHOT_HISTORY
        # Clean entities from entdict
        for _id in self.delete_ents:
            if _id in self.entdict:
                self.entdict.pop(_id)
        self.create_ents = []
        self.delete_ents = []
        return client_data_table
