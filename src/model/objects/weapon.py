from src.model.objects.gameObject import GameObject

class Weapon(GameObject):
    def __init__(self, id, name, position, size, damage, max_ammo):
        super().__init__(id, position, size)
        self.name = name
        self.damage = damage
        self.max_ammo = max_ammo
        self.current_ammo = max_ammo

    def reload(self):
        self.current_ammo = self.max_ammo

    def shoot(self):
        if self.current_ammo > 0:
            self.current_ammo -= 1
            return self.damage
        else:
            print(f"{self.name} está sem munição!")
            return 0