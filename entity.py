
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

    def prepare_data_table(self):

        if not self.updated:
            return None

        datatable_to_send = {}
        for _id in self.data_table:
            netvar = self.data_table[_id]

            # If the netvar is updated add it to the table to send
            if netvar.updated:
                datatable_to_send[_id] = netvar.var
                netvar.send_value()

        return datatable_to_send

    def apply_data_table(self, datatable_to_receive):
        for _id in datatable_to_receive:
            self.data_table[_id].var = datatable_to_receive[_id]

