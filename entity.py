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
        self.snapshots = {"TICK":[]}
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
            if netvar.only_send_to_owner:
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
            return True

    def apply_data_table(self, tick, delay):
        i = 0
        while True:
            xvals = self.snapshots["TICK"]
            for netvar in self.snapshots:
                if netvar == "TICK": continue
                if self.data_table[netvar].lerp:
                    yvals = self.snapshots[netvar]
                    y = np.interp(tick, xvals, yvals)
                    self.data_table[netvar].var = y
                else:
                    self.data_table[netvar].var = self.snapshots[netvar][-1]
                    self.snapshots[netvar] = [self.snapshots[netvar][-1]]
            i+=1


    def apply_data_table_lerp(self, datatable1, datatable2, x, x0, x1):
        if datatable1 is not None:
            if datatable2 is not None:
                for _id in datatable1:
                    if _id == "TICK": continue
                    __id = int(_id)
                    if _id not in datatable2 or not self.data_table[__id].lerp:
                        self.data_table[__id].var = datatable1[_id]
                    elif self.data_table[__id].slerp:
                        y0 = datatable1[_id]
                        y1 = datatable2[_id]
                        #if abs(y0-y1) <= math.pi:
                        #    y = y0 * (x1-x)/(x1-x0) + y1 * (x-x0)/(x1-x0)
                        #    self.data_table[__id].var = y
                        #else:
                        self.data_table[__id].var = y0
                    elif self.data_table[__id].lerp:
                        y0 = datatable1[_id]
                        y1 = datatable2[_id]
                        if x1 == x0:
                            y = y1
                        else:
                            y = y0 * (x1 - x) / (x1 - x0) + y1 * (x - x0) / (x1 - x0)
                        self.data_table[__id].var = y
        return


class CEntity(Entity):
    def __init__(self):
        Entity.__init__(self)


    def update(self, world):
        pass

