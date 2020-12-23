
class Entity:

    def __init__(self):
        self._id = None
        self.ent_destroyed = False
        self.data_table = {}
        self.updated = True
        pass

    def update(self, world):
        pass

    def destroy(self, world):
        self.ent_destroyed = True

