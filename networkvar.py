

class NetworkVar:

    def __init__(self, ent, var):
        self.var = var
        self.ent = ent
        self.updated = True

        ent.network_vars.append(self)

    def assign(self, var):
        if var != self.var:
            self.ent.updated = True
        self.var = var
