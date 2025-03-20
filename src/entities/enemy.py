from src.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        super().__init__(id, position, size, speed, health, status)
        self.name = name
        self.weapon = weapon
        self.ammo = ammo

    def attack(self, target):
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)