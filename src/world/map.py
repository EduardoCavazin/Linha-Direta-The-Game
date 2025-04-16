import json
import random
from typing import List

from src.world.room import Room
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.weapon import Weapon
from src.model.objects.item import Item
from src.model.objects.door import Door

class Map:
    def __init__(self, map_file: str) -> None:
        self.map_file: str = map_file
        self.rooms: List[Room] = self.load_rooms()
        self.current_room: Room | None = None
        self.sequence: List[Room] = []

    def load_rooms(self) -> List[Room]:
        with open(self.map_file, 'r') as file:
            data = json.load(file)
            rooms: List[Room] = []

            for room_data in data["rooms"]:
                # Carrega os itens
                items_data = room_data.get("items", [])
                items = [Item(**item_data) for item_data in items_data]

                # Carrega os inimigos
                enemies_data = room_data.get("enemies", [])
                enemies = []
                for enemy_data in enemies_data:
                    weapon_data = enemy_data.pop("weapon", None)
                    weapon = Weapon(**weapon_data) if weapon_data else None
                    enemy_data.setdefault("status", "alive")
                    enemy = Enemy(**enemy_data, weapon=weapon)
                    enemies.append(enemy)

                # Carrega as portas
                doors_data = room_data.get("doors", [])
                doors = [Door(**door_data) for door_data in doors_data]

                # Carrega o player
                player_data = room_data.get("player")
                player = None
                if player_data:
                    weapon_data = player_data.pop("weapon", None)
                    weapon = Weapon(**weapon_data) if weapon_data else None
                    player_data.setdefault("status", "alive")
                    player = Player(**player_data, weapon=weapon)

                room = Room(
                    id=room_data["id"],
                    size=tuple(room_data["size"]),
                    items=items,
                    enemies=enemies,
                    doors=doors,
                    player=player,
                    cleared=room_data.get("cleared", False),
                    visited=room_data.get("visited", False)
                )
                rooms.append(room)
        return rooms

    def generate_seed(self, num_rooms: int = 5) -> None:
        if len(self.rooms) < num_rooms + 1:
            raise ValueError("Não há salas suficientes para gerar uma sequência válida.")

        normal_rooms = [room for room in self.rooms if "boss" not in room.id]
        boss_rooms = [room for room in self.rooms if "boss" in room.id]

        if not boss_rooms:
            raise ValueError("Nenhuma sala de chefe disponível no JSON!")

        self.sequence = random.sample(normal_rooms, num_rooms)
        self.sequence.append(random.choice(boss_rooms))
        self.current_room = self.sequence[0]

    def get_next_room(self) -> Room | None:
        try:
            current_index = self.rooms.index(self.current_room)
        except ValueError:
            return None
        if current_index + 1 < len(self.rooms):
            self.current_room = self.rooms[current_index + 1]
            return self.current_room
        return None

    def is_complete(self) -> bool:
        return not self.sequence

    def __str__(self) -> str:
        current = self.current_room.id if self.current_room is not None else 'Nenhuma'
        return f"Salas restantes: {len(self.sequence)}\nSala atual: {current}\n"
