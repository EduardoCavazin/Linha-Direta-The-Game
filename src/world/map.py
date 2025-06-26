import os
import json
import random
import pygame
import xml.etree.ElementTree as ET  
from typing import List, Optional, Tuple, Dict, Any

from src.world.room import Room
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.weapon import Weapon
from src.model.objects.item import Item
from src.model.objects.door import Door
from src.core.utils import load_image
from src.world.tiledLoader import TiledLoader  # Importar nossa classe TiledLoader

class Map:
    def __init__(self, rooms_folder: str) -> None:
        self.rooms_folder: str = rooms_folder
        self.config: Dict[str, Dict] = self._load_configs()
        self.rooms: List[Room] = self.load_rooms()
        self.current_room: Optional[Room] = None
        self.sequence: List[Room] = []
        
        print(f"Carregadas {len(self.rooms)} salas!")
    
    def _load_configs(self) -> Dict[str, Dict]:
        configs = {}
        config_files = {
            "entities": "src/config/entities.json",
            "items": "src/config/items.json",
            "weapons": "src/config/weapons.json",
            "doors": "src/config/doors.json"
        }
        
        for key, filepath in config_files.items():
            try:
                with open(filepath, 'r') as file:
                    # Remover comentários do tipo // da linha
                    content = ""
                    for line in file:
                        if "//" in line:
                            line = line[:line.index("//")]
                        content += line
                    
                    if content.strip():
                        configs[key] = json.loads(content)
                        print(f"Carregado {filepath}")
                    else:
                        print(f"Arquivo vazio: {filepath}")
                        configs[key] = {}
            except Exception as e:
                print(f"Erro ao carregar {filepath}: {e}")
                configs[key] = {}
        
        return configs

    def load_rooms(self) -> List[Room]:
        rooms: List[Room] = []
        
        # Verificar se a pasta existe
        if not os.path.exists(self.rooms_folder):
            print(f"Pasta de salas não encontrada: {self.rooms_folder}")
            return rooms
            
        # Para cada arquivo na pasta
        for filename in os.listdir(self.rooms_folder):
            file_path = os.path.join(self.rooms_folder, filename)
            
            # Carregar arquivos TMX (Tiled)
            if filename.endswith('.tmx'):
                try:
                    room = self._load_tmx_room(file_path)
                    if room:
                        rooms.append(room)
                        print(f"Carregada sala TMX: {room.id}")
                except Exception as e:
                    print(f"Erro ao carregar sala TMX {filename}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Compatibilidade: carregar arquivos XML antigos
            elif filename.endswith('.xml'):
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()  
                    room = self._parse_room_element(root)
                    if room:
                        rooms.append(room)
                        print(f"Carregada sala XML: {room.id}")
                except Exception as e:
                    print(f"Erro ao carregar sala XML {filename}: {e}")
        
        if not rooms:
            print("Nenhuma sala carregada!")
        
        return rooms
    
    def _load_tmx_room(self, tmx_path: str) -> Optional[Room]:
        try:
            # Carregar o TMX usando nosso TiledLoader
            print(f"Carregando TMX: {tmx_path}")
            tmx_loader = TiledLoader(tmx_path)
            
            # Extrair ID e tamanho da sala
            room_id = os.path.splitext(os.path.basename(tmx_path))[0]
            room_size = tmx_loader.get_map_size_pixels()
            
            print(f"Tamanho da sala: {room_size[0]}x{room_size[1]} pixels")
            
            collision_matrix = tmx_loader.get_collision_matrix()
            print(f"Matriz de colisão extraída: {len(collision_matrix)}x{len(collision_matrix[0]) if collision_matrix else 0}")
            
            # Inicializar listas vazias
            items = []
            enemies = []
            doors = []
            player = None
            
            # Processar objetos do mapa
            print(f"Processando {len(tmx_loader.objects)} objetos")
            for obj in tmx_loader.objects:
                obj_name = obj["name"]
                obj_type = obj["type"]
                obj_x = obj["x"]
                obj_y = obj["y"]
                obj_props = obj["properties"]
                
                print(f"Objeto: {obj_name} ({obj_type}) em ({obj_x}, {obj_y})")
                
                # Player
                if obj_name == "Player":
                    player = self._create_player((obj_x, obj_y), obj_props)
                    if player:
                        print(f"Player criado em ({obj_x}, {obj_y})")
                
                # Inimigos
                elif obj_name in self.config["entities"] and obj_name != "Player":
                    enemy = self._create_enemy(obj_name, (obj_x, obj_y), obj_props)
                    if enemy:
                        enemies.append(enemy)
                        print(f" Inimigo {obj_name} criado em ({obj_x}, {obj_y})")
                
                # Items
                elif obj_name in self.config["items"]:
                    item = self._create_item(obj_name, (obj_x, obj_y), obj_props)
                    if item:
                        items.append(item)
                        print(f"Item {obj_name} criado em ({obj_x}, {obj_y})")
                
                # Portas
                elif obj_name in self.config["doors"] or obj_name == "Door":
                    door = self._create_door(obj_name, (obj_x, obj_y), obj_props)
                    if door:
                        doors.append(door)
                        print(f"Porta {obj_name} criada em ({obj_x}, {obj_y})")
                
                else:
                    print(f"Objeto desconhecido: {obj_name}")
            
            # Criar background usando o método do TiledLoader
            print("Criando background com tiles reais")
            background = tmx_loader.create_background()
            
            print("Sala criada com sucesso")
            return Room(
                id=room_id,
                size=room_size,
                objects=[], 
                enemies=enemies,
                items=items,
                doors=doors,
                player=player,
                cleared=False,
                visited=False,
                background=background,
                collision_matrix=collision_matrix 
            )
        
        except Exception as e:
            print(f"Erro ao carregar TMX {tmx_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_player(self, position: Tuple[float, float], properties: Dict) -> Optional[Player]:
        try:
            config = self.config["entities"].get("Player", {})
            if not config:
                print("Configuração do Player não encontrada!")
                return None
            
            # Configurar arma do player
            weapon_name = config.get("weapon", "Pistol")
            weapon = None
            if weapon_name in self.config["weapons"]:
                weapon_config = self.config["weapons"][weapon_name]
                weapon = Weapon(
                    id=weapon_name.lower(),
                    name=weapon_config.get("name", weapon_name),
                    damage=weapon_config.get("damage", 10),
                    max_ammo=weapon_config.get("max_ammo", 100)
                )
            
            # Criar player
            player = Player(
                id="player",
                name="Player",
                position=position,
                size=tuple(config.get("size", [32, 32])),
                speed=float(config.get("speed", 200.0)),
                health=int(config.get("health", 100)),
                weapon=weapon,
                ammo=int(config.get("ammo", 30)),
                status="alive"
            )
            
            return player
            
        except Exception as e:
            print(f"Erro ao criar Player: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_enemy(self, enemy_type: str, position: Tuple[float, float], properties: Dict) -> Optional[Enemy]:
        try:
            config = self.config["entities"].get(enemy_type, {})
            if not config:
                print(f"Configuração do inimigo {enemy_type} não encontrada!")
                return None
            
            # Configurar arma do inimigo
            weapon_name = config.get("weapon")
            weapon = None
            if weapon_name and weapon_name in self.config["weapons"]:
                weapon_config = self.config["weapons"][weapon_name]
                weapon = Weapon(
                    id=weapon_name.lower(),
                    name=weapon_config.get("name", weapon_name),
                    damage=weapon_config.get("damage", 5),
                    max_ammo=weapon_config.get("max_ammo", 0)
                )
            
            # Criar inimigo
            enemy = Enemy(
                id=f"{enemy_type.lower()}_{id(position)}",
                name=config.get("name", enemy_type),
                position=position,
                size=tuple(config.get("size", [32, 32])),
                speed=float(config.get("speed", 80.0)),
                health=int(config.get("health", 50)),
                weapon=weapon,
                ammo=int(config.get("ammo", 0)),
                status=config.get("status", "alive")
            )
            
            return enemy
            
        except Exception as e:
            print(f"Erro ao criar inimigo {enemy_type}: {e}")
            return None
    
    def _create_item(self, item_type: str, position: Tuple[float, float], properties: Dict) -> Optional[Item]:
        try:
            config = self.config["items"].get(item_type, {})
            if not config:
                print(f"Configuração do item {item_type} não encontrada!")
                return None
            
            # Criar item
            item = Item(
                id=f"{item_type.lower()}_{id(position)}",
                name=config.get("name", item_type),
                position=position,
                size=tuple(config.get("size", [16, 16])),
                effect=config.get("effect", "")
            )
            
            # Adicionar valor do efeito se disponível
            if "value" in config:
                item.value = config["value"]
            
            return item
            
        except Exception as e:
            print(f"Erro ao criar item {item_type}: {e}")
            return None
    
    def _create_door(self, door_type: str, position: Tuple[float, float], properties: Dict) -> Optional[Door]:
        try:
            config = self.config["doors"].get(door_type, {})
            if not config:
                print(f"Configuração da porta {door_type} não encontrada!")
                # Usar configuração padrão se específica não existir
                config = self.config["doors"].get("Door", {})
                if not config:
                    return None
            
            # Obter propriedades específicas do TMX ou do JSON
            destination = properties.get("destination", config.get("destination", "next_room"))
            locked = properties.get("locked", config.get("locked", False))
            
            # Criar porta
            door = Door(
                id=f"{door_type.lower()}_{id(position)}",
                position=position,
                size=tuple(config.get("size", [32, 48])),
                locked=locked
            )
            
            # Definir destino da porta
            door.destination = destination
            
            # Adicionar propriedades extras se necessário
            if "key_item" in config:
                door.key_item = config["key_item"]
            
            if "required_count" in config:
                door.required_count = config["required_count"]
            
            return door
            
        except Exception as e:
            print(f"Erro ao criar porta {door_type}: {e}")
            return None
    
    # Métodos existentes permanecem inalterados
    def _parse_room_element(self, room_el) -> Optional[Room]:
        # Código existente para compatibilidade com XML
        pass

    def generate_seed(self, num_rooms: int = 5) -> None:
        """Gera uma sequência de salas para o jogo."""
        print("Gerando sequência de salas...")
        
        # Encontrar sala inicial (com player)
        start_room = next((r for r in self.rooms if r.player is not None), None)
        if not start_room:
            raise ValueError("❌ Não encontrei nenhuma sala com player definido!")

        # Separar salas normais e de boss
        normal = [r for r in self.rooms
                  if "boss" not in r.id.lower() and r is not start_room]
        bosses = [r for r in self.rooms if "boss" in r.id.lower()]

        # Verificar se temos salas suficientes
        if len(normal) < num_rooms - 1:
            print(f"Aviso: Apenas {len(normal)} salas normais disponíveis, mas {num_rooms - 1} solicitadas")
            num_rooms = len(normal) + 1  # Ajustar para o número disponível
        
        if not bosses:
            print("Aviso: Nenhuma sala de boss encontrada!")
            # Usar sala normal como boss se necessário
            if normal:
                bosses = [normal.pop()]
            else:
                bosses = [start_room]  # Último recurso
        
        # Criar sequência: sala inicial + salas normais + boss
        num_normal = min(num_rooms - 1, len(normal))
        if num_normal > 0:
            selected_normal = random.sample(normal, num_normal)
        else:
            selected_normal = []
            
        self.sequence = [start_room] + selected_normal + [random.choice(bosses)]
        self.current_room = self.sequence[0]
        
        print(f"Sequência gerada: {len(self.sequence)} salas")
        for i, room in enumerate(self.sequence):
            print(f"  {i+1}. {room.id}")

    # Adicione este método temporário para testes
    def generate_seed_test(self) -> None:
        """Gera uma sequência de teste com apenas o Mapa1."""
        print("Gerando sequência de teste...")
        
        # Encontrar o mapa1
        mapa1 = next((r for r in self.rooms if r.id == "Mapa1"), None)
        if not mapa1:
            raise ValueError("❌ Mapa1 não encontrado!")
        
        # Usar apenas o Mapa1 para teste
        self.sequence = [mapa1]
        self.current_room = mapa1
        
        print(f"Sequência de teste gerada: {len(self.sequence)} salas")
        print(f"  1. {mapa1.id}")

    def get_next_room(self) -> Optional[Room]:
        if not self.current_room or not self.sequence:
            return None
            
        current_index = self.sequence.index(self.current_room)
        if current_index + 1 < len(self.sequence):
            self.current_room = self.sequence[current_index + 1]
            return self.current_room
            
        return None

    def is_complete(self) -> bool:
        return all(room.visited for room in self.sequence)

    def __str__(self) -> str:
        curr = self.current_room.id if self.current_room else "Nenhuma"
        return f"Salas restantes: {len(self.sequence)}\nSala atual: {curr}\n"
