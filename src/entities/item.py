class Item:
    def __init__(self, name, position, effect):
        self.name = name
        self.position = position
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
