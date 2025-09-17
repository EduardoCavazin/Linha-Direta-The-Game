from typing import Tuple

class Weapon:
    def __init__(self, id: str, name: str, damage: int, max_ammo: int) -> None:
        self.id: str = id
        self.name: str = name
        self.damage: int = damage
        self.max_ammo: int = max_ammo
        self.current_ammo: int = max_ammo

    def reload(self) -> None:
        self.current_ammo = self.max_ammo

    def shoot(self) -> int:
        if self.current_ammo > 0:
            self.current_ammo -= 1
            return self.damage
        else:
            return 0
