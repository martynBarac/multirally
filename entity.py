import constant
import math
import numpy
import numpy as np


class Entity:
    def __init__(self):
        self._id = None
        self.class_id = 0
        self.ent_destroyed = False
        self.data_table = {} # {id: netvar}
        self.updated = {} # Updated for client. {Client: Updated}
        # If the entity is an actor then it should have x and y netvars and be displayed in the world
        # By convention call x netxpos and y netypos in your actor
        self.actor = True
        # If the entity is shootable it needs collision bounds
        self.shootable = False
        self.owner = None
        self.snapshots = {}
        self.snapshots_xvals = {}
        pass

    def update(self, world):
        pass

    def destroy(self, world):
        self.ent_destroyed = True

    def get_collision_bounds(self):
        """Collision polygon for hit detection: [(x1, y1)... (xn, yn)]"""
        return []

    def prepare_data_table(self, client, send_everything=False):
        """Client: Client we're sending the data to"""

        if not self.get_updated(client) and not send_everything:
            return None

        datatable_to_send = {}
        for _id in self.data_table:
            netvar = self.data_table[_id]
            # If the netvar is only for the owner
            if netvar.only_send_to_owner or send_everything:
                if self.owner != client: # This client is not the owner so
                    continue #skip sending
            # If the netvar is updated add it to the table to send
            if netvar.get_updated(client) or send_everything:
                if netvar.quantise == 0:
                    datatable_to_send[_id] = int(netvar.var)
                elif netvar.quantise != -1:
                    datatable_to_send[_id] = round(netvar.var, netvar.quantise)
                else:
                    datatable_to_send[_id] = netvar.var
            if netvar.get_updated(client):
                netvar.send_value(client)

        return datatable_to_send

    def get_updated(self, client):
        if client in self.updated:
            return self.updated[client]
        else:
            self.updated[client] = True
            return False

    def apply_data_table(self, tick, delay):
        for netvar in self.snapshots:
            if self.data_table[netvar].lerp:
                yvals = self.snapshots[netvar]
                xvals = self.snapshots_xvals[netvar]
                if len(xvals) != 0:
                    y = np.interp(tick, xvals, yvals)
                    self.data_table[netvar].var = y
                    mask = self.snapshots_xvals[netvar] > tick-delay*2
                    self.snapshots_xvals[netvar] = self.snapshots_xvals[netvar][mask]
                    self.snapshots[netvar] = self.snapshots[netvar][mask]
            else:
                self.data_table[netvar].var = self.snapshots[netvar][-1]
                self.snapshots[netvar] = [self.snapshots[netvar][-1]]
                self.snapshots_xvals[netvar] = [self.snapshots[netvar][-1]]

    def set_state(self, input_datatable):
        for netvar in input_datatable:
            self.data_table[netvar].var = input_datatable[netvar]
        return


class CEntity(Entity):
    def __init__(self):
        Entity.__init__(self)

    def update(self, world):
        pass

