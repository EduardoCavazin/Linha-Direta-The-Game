from typing import Tuple, Any, Optional
from src.model.objects.gameObject import GameObject

class Item(GameObject):
    def __init__(self, id: str, name: str, position: Tuple[float, float], size: Tuple[int, int], effect: str) -> None:
        super().__init__(id, position, size)
        self.name: str = name
        self.effect: str = effect

    def use(self, target: Any) -> None:
        if self.effect == "heal":
            target.health += 20
            if target.health > 100:
                target.health = 100
        elif self.effect == "ammo":
            target.ammo += 10
            if target.weapon is not None and target.ammo > target.weapon.max_ammo:
                target.ammo = target.weapon.max_ammo
