import os
import xml.etree.ElementTree as ET
import random
from typing import List, Optional, Tuple

from src.world.room import Room
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.weapon import Weapon
from src.model.objects.item import Item
from src.model.objects.door import Door

def _parse_tuple(s: str, cast: type) -> Tuple:
    return tuple(cast(x) for x in s.split(','))

class Map:
    def __init__(self, rooms_folder: str) -> None:
        """
        :param rooms_folder: pasta que contém arquivos XML de cada sala
        """
        self.rooms_folder: str = rooms_folder
        self.rooms: List[Room] = self.load_rooms()
        self.current_room: Optional[Room] = None
        self.sequence: List[Room] = []

    def load_rooms(self) -> List[Room]:
        rooms: List[Room] = []
        for filename in os.listdir(self.rooms_folder):
            if not filename.endswith('.xml'):
                continue
            path = os.path.join(self.rooms_folder, filename)
            tree = ET.parse(path)
            root = tree.getroot()  # elemento <room>
            rooms.append(self._parse_room_element(root))
        return rooms

    def _parse_room_element(self, room_el: ET.Element) -> Room:
        rid: str = room_el.get('id', '')
        size: Tuple[int, int] = _parse_tuple(room_el.get('size', '0,0'), int)
        cleared: bool = room_el.get('cleared', 'false') == 'true'
        visited: bool = room_el.get('visited', 'false') == 'true'

        # Itens
        items: List[Item] = []
        for item_el in room_el.find('items') or []:
            items.append(Item(
                id=item_el.get('id', ''),
                name=item_el.get('name', ''),
                position=_parse_tuple(item_el.get('position', '0,0'), float),
                size=_parse_tuple(item_el.get('size', '0,0'), int),
                effect=item_el.get('effect', '')
            ))

        # Inimigos
        enemies: List[Enemy] = []
        for enemy_el in room_el.find('enemies') or []:
            # arma do inimigo
            weapon_el = enemy_el.find('weapon')
            weapon = None
            if weapon_el is not None:
                weapon = Weapon(
                    id=weapon_el.get('id', ''),
                    name=weapon_el.get('name', ''),
                    position=_parse_tuple(weapon_el.get('position', '0,0'), float),
                    size=_parse_tuple(weapon_el.get('size', '0,0'), int),
                    damage=int(weapon_el.get('damage', '0')),
                    max_ammo=int(weapon_el.get('max_ammo', '0'))
                )

            enemies.append(Enemy(
                id=enemy_el.get('id', ''),
                name=enemy_el.get('name', ''),
                position=_parse_tuple(enemy_el.get('position', '0,0'), float),
                size=_parse_tuple(enemy_el.get('size', '0,0'), int),
                speed=float(enemy_el.get('speed', '0')),
                health=int(enemy_el.get('health', '0')),
                weapon=weapon,
                ammo=int(enemy_el.get('ammo', '0')),
                status=enemy_el.get('status', 'alive')
            ))

        # Portas
        doors: List[Door] = []
        for door_el in room_el.find('doors') or []:
            doors.append(Door(
                id=door_el.get('id', ''),
                position=_parse_tuple(door_el.get('position', '0,0'), float),
                size=_parse_tuple(door_el.get('size', '0,0'), int),
                locked=door_el.get('locked', 'false') == 'true'
            ))

        # Player (opcional)
        player: Optional[Player] = None
        player_el = room_el.find('player')
        if player_el is not None:
            weapon_el = player_el.find('weapon')
            weapon = None
            if weapon_el is not None:
                weapon = Weapon(
                    id=weapon_el.get('id', ''),
                    name=weapon_el.get('name', ''),
                    position=_parse_tuple(weapon_el.get('position', '0,0'), float),
                    size=_parse_tuple(weapon_el.get('size', '0,0'), int),
                    damage=int(weapon_el.get('damage', '0')),
                    max_ammo=int(weapon_el.get('max_ammo', '0'))
                )
            player = Player(
                id=player_el.get('id', ''),
                name=player_el.get('name', ''),
                position=_parse_tuple(player_el.get('position', '0,0'), float),
                size=_parse_tuple(player_el.get('size', '0,0'), int),
                speed=float(player_el.get('speed', '0')),
                health=int(player_el.get('health', '0')),
                weapon=weapon,
                ammo=int(player_el.get('ammo', '0')),
                status=player_el.get('status', 'alive')
            )

        return Room(
            id=rid,
            size=size,
            objects=[],
            enemies=enemies,
            items=items,
            doors=doors,
            player=player,
            cleared=cleared,
            visited=visited
        )

    def generate_seed(self, num_rooms: int = 5) -> None:
        normal = [r for r in self.rooms if "boss" not in r.id]
        bosses = [r for r in self.rooms if "boss" in r.id]
        if len(normal) < num_rooms or not bosses:
            raise ValueError("Salas insuficientes.")

        self.sequence = random.sample(normal, num_rooms) + [random.choice(bosses)]
        self.current_room = self.sequence[0]

    def get_next_room(self) -> Optional[Room]:
        if self.current_room is None:
            return None
        idx = self.rooms.index(self.current_room)
        if idx + 1 < len(self.rooms):
            self.current_room = self.rooms[idx + 1]
            return self.current_room
        return None

    def is_complete(self) -> bool:
        return not self.sequence

    def __str__(self) -> str:
        curr = self.current_room.id if self.current_room else "Nenhuma"
        return f"Salas restantes: {len(self.sequence)}\nSala atual: {curr}\n"
