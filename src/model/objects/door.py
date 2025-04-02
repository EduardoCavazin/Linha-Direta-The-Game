from src.model.objects.gameObject import GameObject

class Door(GameObject):
    def __init__(self, id, position, size, locked=False):
        super().__init__(id, position, size)
        self.locked = locked
        self.opened = False

    def open(self):
        if not self.locked:
            self.opened = True

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False
