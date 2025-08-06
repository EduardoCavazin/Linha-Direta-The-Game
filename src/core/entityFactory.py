import os
import json
from typing import Dict, List, Optional, Tuple, Any
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.item import Item
from src.model.objects.door import Door
from src.model.objects.weapon import Weapon

class EntityFactory:
    def __init__(self, config_folder: str = "src/config"):
        self.config_folder = config_folder
        self.configs = self._load_configs()
    
    def _load_configs(self) -> Dict[str, Dict]:
        configs = {}
        config_files = {
            "entities": "entities.json",
            "items": "items.json", 
            "weapons": "weapons.json",
            "doors": "doors.json"
        }
        
        for key, filename in config_files.items():
            filepath = os.path.join(self.config_folder, filename)
            configs[key] = self._load_json_config(filepath)
        
        return configs
    
    def _load_json_config(self, filepath: str) -> Dict:
        try:
            with open(filepath, 'r') as file:
                content = ""
                for line in file:
                    if "//" in line:
                        line = line[:line.index("//")]
                    content += line
                
                if content.strip():
                    config = json.loads(content)
                    return config
                else:
                    return {}
        except Exception as e:
            print(f"Erro ao carregar {filepath}: {e}")
            return {}
    
    def create_room_entities(self, objects_data: List[Dict]) -> Dict[str, any]:
        entities = {
            "player": None,
            "enemies": [],
            "items": [],
            "doors": []
        }
        
        for obj_data in objects_data:
            entity = self._create_entity_from_data(obj_data)
            if entity:
                self._add_entity_to_collection(entity, obj_data["name"], entities)
        
        return entities
    
    def _create_entity_from_data(self, obj_data: Dict) -> Optional[any]:
        obj_name = obj_data["name"]
        obj_type = obj_data["type"]
        position = (obj_data["x"], obj_data["y"])
        properties = obj_data["properties"]
        
        if obj_name == "Player":
            return self.create_player(position, properties)
        
        elif obj_name in self.configs["entities"] and obj_name != "Player":
            return self.create_enemy(obj_name, position, properties)
        
        elif obj_name in self.configs["items"]:
            return self.create_item(obj_name, position, properties)
        
        elif obj_name in self.configs["doors"] or obj_name == "Door" or obj_name == "Door2":
            return self.create_door(obj_name, position, obj_data.get("width", 32), obj_data.get("height", 48), properties)
        
        else:
            print(f"Tipo de entidade desconhecido: {obj_name}")
            return None
    
    def _add_entity_to_collection(self, entity: any, obj_name: str, entities: Dict) -> None:
        if obj_name == "Player":
            entities["player"] = entity
        elif obj_name in self.configs["entities"] and obj_name != "Player":
            entities["enemies"].append(entity)
        elif obj_name in self.configs["items"]:
            entities["items"].append(entity)
        elif obj_name in self.configs["doors"] or obj_name == "Door" or obj_name == "Door2":
            entities["doors"].append(entity)
    
    def create_player(self, position: Tuple[float, float], properties: Dict = None) -> Optional[Player]:
        try:
            config = self.configs["entities"].get("Player", {})
            if not config:
                print("Configuração do Player não encontrada!")
                return None
            
            weapon = self._create_weapon_for_entity("Player", config)
            
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
            return None
    
    def create_enemy(self, enemy_type: str, position: Tuple[float, float], properties: Dict = None) -> Optional[Enemy]:
        try:
            config = self.configs["entities"].get(enemy_type, {})
            if not config:
                print(f"Configuração do inimigo {enemy_type} não encontrada!")
                return None
            
            weapon = self._create_weapon_for_entity(enemy_type, config)
            
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
    
    def create_item(self, item_type: str, position: Tuple[float, float], properties: Dict = None) -> Optional[Item]:
        try:
            config = self.configs["items"].get(item_type, {})
            if not config:
                print(f"Configuração do item {item_type} não encontrada")
                return None
            
            sprite_name = config.get("sprite", f"assets/sprites/{item_type.lower()}.png")
            
            print(f"Criando item {item_type} com sprite: {sprite_name}")
            
            item = Item(
                id=f"{item_type.lower()}_{id(position)}",
                name=config.get("name", item_type),
                position=position,
                size=tuple(config.get("size", [24, 24])),  
                effect=config.get("effect", {}).get("type", ""),
                sprite_name=sprite_name
            )
            
            if "effect" in config and "value" in config["effect"]:
                item.value = config["effect"]["value"]
            
            return item
            
        except Exception as e:
            print(f"Erro ao criar item {item_type}: {e}")
            return None
    
    def create_door(self, door_type: str, position: Tuple[float, float], width: float, height: float, properties: Dict = None) -> Optional[Door]:
        try:
            config = self.configs["doors"].get(door_type, {})
            if not config:
                config = self.configs["doors"].get("Door", {})
                if not config:
                    return None

            properties = properties or {}
            locked = properties.get("locked", config.get("locked", False))
            destination = properties.get("destination", config.get("destination", "next_room"))

            door = Door(
                id=f"{door_type.lower()}_{id(position)}",
                position=position,
                size=(width, height),
                locked=locked,
                name=door_type,
                destination=destination
            )

            return door

        except Exception as e:
            print(f"Erro ao criar porta {door_type}: {e}")
            return None
    
    def _create_weapon_for_entity(self, entity_type: str, entity_config: Dict) -> Optional[Weapon]:
        weapon_name = entity_config.get("weapon")
        if not weapon_name or weapon_name not in self.configs["weapons"]:
            return None
        
        weapon_config = self.configs["weapons"][weapon_name]
        return Weapon(
            id=weapon_name.lower(),
            name=weapon_config.get("name", weapon_name),
            damage=weapon_config.get("damage", 10),
            max_ammo=weapon_config.get("max_ammo", 100)
        )