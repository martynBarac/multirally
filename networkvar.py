

class NetworkVar:

    def __init__(self, ent, var, _id):
        self.var = var
        self.ent = ent
        self.updated = True

        ent.data_table[_id] = self

    def assign(self, var):
        if var != self.var:
            self.ent.updated = True
        self.var = var
