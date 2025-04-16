import pygame
from typing import Tuple
from src.model.objects.gameObject import GameObject

class Door(GameObject):
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int], locked: bool = False) -> None:
        super().__init__(id, position, size)
        self.locked: bool = locked
        self.opened: bool = False

    def open(self) -> None:
        if not self.locked:
            self.opened = True

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False
