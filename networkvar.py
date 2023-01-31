import numpy as np

class NetworkVar:

    def __init__(self, ent, var, _id, lerp=False, slerp=False):
        self.var = var
        self.oldvar = var
        self.ent = ent
        self.updated = {} #Updated for client. {Client: Updated}
        self.lerp = lerp
        self.slerp = slerp
        self.quantise = -1
        self.only_send_to_owner = 0

        ent.data_table[_id] = self
        ent.snapshots[_id] = np.array([])
        ent.snapshots_xvals[_id] = np.array([])

    def get(self, dt):
        return self.var

    def set(self, value, check_update=False):
        self.var = value
        if check_update:
            self.check_updated()

    def __delete__(self, instance):
        del self.value

    def __add__(self, value):
        if value:
            self.var = self.var+value
        return self

    def __str__(self):
        return "NET: " + str(self.var)

    def check_updated(self):
        if self.var != self.oldvar:
            self.oldvar = self.var
            self.set_updated()
            return True
        return False

    def set_updated(self):
        for client in self.updated:
            self.ent.updated[client] = True
            self.updated[client] = True

    def send_value(self, client):
        self.updated[client] = False

    def get_updated(self, client):
        if client in self.updated:
            return self.updated[client]
        else:
            self.updated[client] = True
            return True


#Delete this once its done!
class NetworkVarLegacy:

    def __init__(self, ent, var, _id, lerp=False):
        self.var = var
        self.oldvar = var
        self.ent = ent
        self.updated = True
        self.lerp = lerp
        self.quantise = -1

        ent.data_table[_id] = self

    def get(self, dt):
        return self.var

    def set(self, value, check_update=False):
        self.var = value
        if check_update:
            self.check_updated()

    def __delete__(self, instance):
        del self.value

    def __add__(self, value):
        if value:
            self.var = self.var+value
        return self

    def __str__(self):
        return "NET: " + str(self.var)

    def check_updated(self):
        if self.var != self.oldvar:
            self.oldvar = self.var
            self.set_updated()
            return True
        return False

    def set_updated(self):
        self.ent.updated = True
        self.updated = True

    def send_value(self):
        self.updated = False