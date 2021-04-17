
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
        pass

    def update(self, world):
        pass

    def destroy(self, world):
        self.ent_destroyed = True

    def prepare_data_table(self, client, send_everything=False):
        """Client: Client we're sending the data to"""

        if not self.get_updated(client) and not send_everything:
            return None

        datatable_to_send = {}
        for _id in self.data_table:
            netvar = self.data_table[_id]

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

    def apply_data_table(self, datatable_to_receive):
        if datatable_to_receive is not None:
            for _id in datatable_to_receive:
                __id = int(_id)
                self.data_table[__id].var = datatable_to_receive[_id]
                # print(self.data_table[__id].var)

    def apply_data_table_lerp(self, snapshots, starttime, curtime):
        if snapshots[0] is not None:
            for _id in snapshots[0]:
                __id = int(_id)
                if self.data_table[__id].lerp and _id in snapshots[1]:
                    # Lerp from https://en.wikipedia.org/wiki/Linear_interpolation
                    interp_time = 1/15
                    y0 = snapshots[0][_id]
                    y1 = snapshots[1][_id]
                    x0 = starttime
                    x1 = starttime+interp_time # interp time
                    x = curtime

                    numerator = y0*(x1-x)+y1*(x-x0)
                    denominator = x1 - x0
                    if curtime > x1:
                        self.data_table[__id].var=y1
                    else:
                        self.data_table[__id].var = numerator/denominator
                else:
                    self.data_table[__id].var = snapshots[0][_id]
        elif snapshots[1] is not None:
            for _id in snapshots[1]:
                __id = int(_id)
                self.data_table[__id].var = snapshots[1][_id]





class EntityLegacy:

    def __init__(self):
        self._id = None
        self.class_id = 0
        self.ent_destroyed = False
        self.data_table = {}
        self.updated = True
        # If the entity is an actor then it should have x and y netvars and be displayed in the world
        # By convention call x netxpos and y netypos in your actor
        self.actor = True
        pass

    def update(self, world):
        pass

    def destroy(self, world):
        self.ent_destroyed = True

    def prepare_data_table(self, send_everything=False):

        if not self.updated and not send_everything:
            return None

        datatable_to_send = {}
        for _id in self.data_table:
            netvar = self.data_table[_id]

            # If the netvar is updated add it to the table to send
            if netvar.updated or send_everything:
                if netvar.quantise == 0:
                    datatable_to_send[_id] = int(netvar.var)
                elif netvar.quantise != -1:
                    datatable_to_send[_id] = round(netvar.var, netvar.quantise)
                else:
                    datatable_to_send[_id] = netvar.var
            if netvar.updated:
                netvar.send_value()

        return datatable_to_send

    def apply_data_table(self, datatable_to_receive):
        for _id in datatable_to_receive:
            __id = int(_id)
            self.data_table[__id].var = datatable_to_receive[_id]
            # print(self.data_table[__id].var)

    def apply_data_table_lerp(self, snapshots, starttime, curtime):


        for _id in snapshots[0]:
            __id = int(_id)
            if self.data_table[__id].lerp and _id in snapshots[1]:
                # Lerp from https://en.wikipedia.org/wiki/Linear_interpolation
                interp_time = 1/15
                y0 = snapshots[0][_id]
                y1 = snapshots[1][_id]
                x0 = starttime
                x1 = starttime+interp_time # interp time
                x = curtime

                numerator = y0*(x1-x)+y1*(x-x0)
                denominator = x1 - x0
                if curtime > x1:
                    self.data_table[__id].var=y1
                else:
                    self.data_table[__id].var = numerator/denominator
            else:
                self.data_table[__id].var = snapshots[0][_id]


class CEntity(Entity):
    def __init__(self):
        Entity.__init__(self)

    def update(self):
        pass

