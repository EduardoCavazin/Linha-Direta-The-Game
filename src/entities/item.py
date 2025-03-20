from src.entities.entity import Entity

class Item(Entity):
    def __init__(self, id, name, position, size, effect, status="inactive"):
        super().__init__(id, position, size, status)
        self.name = name
        self.effect = effect

    def use(self, target):
        if self.effect == "heal":
            target.health += 20
            if target.health > 100:
                target.health = 100
        elif self.effect == "ammo":
            target.ammo += 10
            if target.ammo > target.weapon.max_ammo:
                target.ammo = target.weapon.max_ammo