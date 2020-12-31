class NetworkVar:

    def __init__(self, ent, var, _id, lerp=False):
        self.var = var
        self.oldvar = var
        self.ent = ent
        self.updated = True
        self.lerp = lerp

        ent.data_table[_id] = self

    def get(self, obj, objtype=None):
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