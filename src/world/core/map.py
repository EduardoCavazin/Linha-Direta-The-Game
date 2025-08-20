import os
import random
from typing import Dict, List, Optional, Tuple
from src.world.loaders.tiledLoader import TiledLoader
from src.world.core.room import Room
from src.core.entityFactory import EntityFactory

class Map:
    
    def __init__(self, rooms_folder: str = "assets/sprites/world/tilesets") -> None:
        self.rooms_folder = rooms_folder
        
        self.entity_factory = EntityFactory()
        
        self.rooms: List[Room] = self._load_rooms()
        self.current_room: Optional[Room] = None
        self.sequence: List[Room] = []
        

    def _load_rooms(self) -> List[Room]:
        rooms: List[Room] = []
        
        if not os.path.exists(self.rooms_folder):
            print(f"Pasta não encontrada: {self.rooms_folder}")
            return rooms
        
        for filename in os.listdir(self.rooms_folder):
            if filename.endswith('.tmx'):
                file_path = os.path.join(self.rooms_folder, filename)
                room = self._load_tmx_room(file_path)
                if room:
                    rooms.append(room)
                    print(f"Sala carregada: {room.id}")
        
        if not rooms:
            print("Nenhuma sala foi carregada")
        
        return rooms

    def _load_tmx_room(self, tmx_path: str) -> Optional[Room]:
        try:
            tmx_loader = TiledLoader(tmx_path)
            
            room_id = os.path.splitext(os.path.basename(tmx_path))[0]
            room_size = tmx_loader.get_map_size_pixels()
            collision_matrix = tmx_loader.get_collision_matrix()
            background = tmx_loader.create_background()
            
            entities_data = tmx_loader.get_objects_data()
            room_entities = self.entity_factory.create_room_entities(entities_data)
            
            room = Room(
                id=room_id,
                size=room_size,
                objects=[],
                enemies=room_entities["enemies"],
                items=room_entities["items"], 
                doors=room_entities["doors"],
                player=room_entities["player"],
                cleared=False,
                visited=False,
                background=background,
                collision_matrix=collision_matrix,
                tmx_objects_data=entities_data
            )
            
            return room
            
        except Exception as e:
            print(f"Erro ao carregar TMX {tmx_path}: {e}")
            return None

    def generate_sequence(self, num_rooms: int = 5) -> None:
        start_room = self._find_start_room()
        
        normal_rooms = self._get_normal_rooms(exclude=start_room)
        boss_rooms = self._get_boss_rooms()
        
        self.sequence = self._build_sequence(start_room, normal_rooms, boss_rooms, num_rooms)
        self.current_room = self.sequence[0]
        
        self._log_sequence()

    def _find_start_room(self) -> Optional[Room]:
        return next((room for room in self.rooms if room.player is not None), None)

    def _get_normal_rooms(self, exclude: Room = None) -> List[Room]:
        return [room for room in self.rooms 
                if "boss" not in room.id.lower() 
                and room != exclude]

    def _get_boss_rooms(self) -> List[Room]:
        return [room for room in self.rooms if "boss" in room.id.lower()]

    def _build_sequence(self, start_room: Room, normal_rooms: List[Room], 
                       boss_rooms: List[Room], num_rooms: int) -> List[Room]:
        sequence = [start_room]
        
        num_normal = min(num_rooms - 1, len(normal_rooms))
        if num_normal > 0:
            selected_normal = random.sample(normal_rooms, num_normal)
            sequence.extend(selected_normal)
        
        if boss_rooms:
            sequence.append(random.choice(boss_rooms))
            remaining = [r for r in normal_rooms if r not in sequence]
            if remaining:
                sequence.append(random.choice(remaining))
        
        return sequence

    def _log_sequence(self) -> None:
        for i, room in enumerate(self.sequence):
            room_type = "Boss" if "boss" in room.id.lower() else "Normal"
            print(f"  {i+1}. {room.id} {room_type}")

    def get_next_room(self) -> Optional[Room]:
        if not self.current_room or not self.sequence:
            return None
        
        try:
            current_index = self.sequence.index(self.current_room)
            if current_index + 1 < len(self.sequence):
                self.current_room = self.sequence[current_index + 1]
                self.current_room.visited = True
                return self.current_room
        except ValueError:
            print("Sala atual não encontrada na sequência")
        
        return None

    def get_previous_room(self) -> Optional[Room]:
        if not self.current_room or not self.sequence:
            return None
        
        try:
            current_index = self.sequence.index(self.current_room)
            if current_index > 0:
                self.current_room = self.sequence[current_index - 1]
                print(f"Voltou para: {self.current_room.id}")
                return self.current_room
        except ValueError:
            print("Sala atual não encontrada na sequência")
        
        return None

    def get_room_by_id(self, room_id: str) -> Optional[Room]:
        return next((room for room in self.rooms if room.id == room_id), None)

    def is_sequence_complete(self) -> bool:
        if not self.sequence:
            return False
        return all(room.visited for room in self.sequence)

    def is_last_room(self) -> bool:
        if not self.current_room or not self.sequence:
            return False
        return self.current_room == self.sequence[-1]

    def get_sequence_progress(self) -> Tuple[int, int]:
        if not self.current_room or not self.sequence:
            return (0, 0)
        
        try:
            current_index = self.sequence.index(self.current_room)
            return (current_index + 1, len(self.sequence))
        except ValueError:
            return (0, len(self.sequence))

    def get_map_info(self) -> Dict[str, any]:
        current_progress = self.get_sequence_progress()
        
        return {
            "total_rooms": len(self.rooms),
            "sequence_length": len(self.sequence),
            "current_room": self.current_room.id if self.current_room else None,
            "progress": f"{current_progress[0]}/{current_progress[1]}",
            "is_complete": self.is_sequence_complete(),
            "rooms_loaded": [room.id for room in self.rooms]
        }

    def reset_sequence(self) -> None:
        for room in self.sequence:
            room.visited = False
            room.cleared = False
        
        if self.sequence:
            self.current_room = self.sequence[0]
        
    def cleanup(self) -> None:
        self.sequence.clear()
        self.current_room = None

    def __str__(self) -> str:
        current_name = self.current_room.id if self.current_room else "Nenhuma"
        progress = self.get_sequence_progress()
        return f"Map: {progress[0]}/{progress[1]} salas | Atual: {current_name}"

