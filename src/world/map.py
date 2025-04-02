import json
import random

from src.world.room import Room
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.weapon import Weapon
from src.model.objects.item import Item
from src.model.objects.door import Door  # Nova classe de porta

class Map:
    def __init__(self, map_file):
        self.map_file = map_file
        self.rooms = self.load_rooms()
        self.current_room = None
        self.sequence = []

    def load_rooms(self):
        with open(self.map_file, 'r') as file:
            data = json.load(file)
            rooms = []

            for room_data in data["rooms"]:
                # Carregar itens
                items_data = room_data.get("items", [])
                items = [Item(**item_data) for item_data in items_data]

                # Carregar inimigos
                enemies_data = room_data.get("enemies", [])
                enemies = []
                for enemy_data in enemies_data:
                    weapon_data = enemy_data.pop("weapon")
                    weapon = Weapon(**weapon_data)
                    enemy = Enemy(**enemy_data, weapon=weapon)
                    enemies.append(enemy)

                # Carregar portas
                doors_data = room_data.get("doors", [])
                doors = [Door(**door_data) for door_data in doors_data]

                # Carregar player
                player_data = room_data.get("player")
                player = None
                if player_data:
                    weapon_data = player_data.pop("weapon")
                    weapon = Weapon(**weapon_data)
                    player = Player(**player_data, weapon=weapon)

                # Criar sala
                room = Room(
                    id=room_data["id"],
                    size=room_data["size"],
                    items=items,
                    enemies=enemies,
                    doors=doors,
                    player=player
                )

                rooms.append(room)
        return rooms

    def generate_seed(self, num_rooms=5):
        if len(self.rooms) < num_rooms + 1:
            raise ValueError("Não há salas suficientes para gerar uma sequência válida.")

        normal_rooms = [room for room in self.rooms if "boss" not in room.id]
        boss_rooms = [room for room in self.rooms if "boss" in room.id]

        if not boss_rooms:
            raise ValueError("Nenhuma sala de chefe disponível no JSON!")

        self.sequence = random.sample(normal_rooms, num_rooms)
        self.sequence.append(random.choice(boss_rooms))
        self.current_room = self.sequence[0]

    def next_room(self):
        if self.sequence:
            self.sequence.pop(0)
            self.current_room = self.sequence[0] if self.sequence else None
            if self.current_room:
                self.current_room.visited = True
        else:
            self.current_room = None

    def is_complete(self):
        return not self.sequence

    def __str__(self):
        return (
            f"Salas restantes: {len(self.sequence)}\n"
            f"Sala atual: {self.current_room.id if self.current_room else 'Nenhuma'}\n"
        )
