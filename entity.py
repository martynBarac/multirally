
class Entity:

    def __init__(self):
        self._id = None
        self.class_id = 0
        self.ent_destroyed = False
        self.data_table = {}
        self.updated = True
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

