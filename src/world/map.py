import json
import random
from src.world.room import Room

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
                room = Room(
                    id=room_data["id"],
                    size=room_data["size"],
                    objects=room_data.get("objects", []),
                    enemies=room_data.get("enemies", []),
                    items=room_data.get("items", []),
                    doors=room_data.get("doors", []),
                    player=room_data.get("player"),
                    cleared=room_data.get("cleared", False)
                )
                rooms.append(room)
        return rooms

    def generate_seed(self, num_rooms=5):
        if len(self.rooms) < num_rooms + 1: 
            raise ValueError("Não há salas suficientes para gerar uma sequência válida.")

        normal_rooms = [room for room in self.rooms if "boss" not in room.id] 
        boss_rooms = [room for room in self.rooms if "boss" in room.id]

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
