from src.model.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        super().__init__(id, name, position, size, speed, health, weapon, ammo, status)
