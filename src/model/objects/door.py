from typing import Tuple
from src.model.objects.gameObject import GameObject

class Door(GameObject):
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int], locked: bool = False, name: str = "Door", destination: str = "next_room") -> None:
        super().__init__(id, position, size)
        self.locked: bool = locked
        self.opened: bool = False
        self.name: str = name  
        self.destination: str = destination 

    @property
    def position(self) -> Tuple[float, float]:
        return (self._position.x, self._position.y)

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position.x, self._position.y = value
        self.hitbox.x, self.hitbox.y = value

    def open(self) -> None:
        if not self.locked:
            self.opened = True

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False
