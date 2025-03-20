from src.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        super().__init__(id, position, size, status)
        self.name = name
        self.speed = speed
        self.health = health
        self.weapon = weapon
        self.ammo = ammo

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def attack(self, target):
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)