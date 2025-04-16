from typing import Tuple
from src.model.objects.gameObject import GameObject

class Weapon(GameObject):
    def __init__(self, id: str, name: str, position: Tuple[float, float], size: Tuple[int, int],
                 damage: int, max_ammo: int) -> None:
        super().__init__(id, position, size)
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
            print(f"{self.name} está sem munição!")
            return 0
