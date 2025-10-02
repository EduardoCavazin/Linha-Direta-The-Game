import os
import json
from typing import Dict, List, Optional, Tuple, Any
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.item import Item
from src.model.objects.door import Door
from src.model.objects.weapon import Weapon
from src.core.constants import Player as PlayerConst, Enemy as EnemyConst
from src.core.logging_utils import log_error, log_warning

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
            log_error(f"Erro ao carregar {filepath}", "entityFactory", e)
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
            fallback_enemy = self._try_enemy_fallback(obj_name, position, properties)
            if fallback_enemy:
                return fallback_enemy

            log_warning(f"Tipo de entidade desconhecido: {obj_name}", "entityFactory")
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
        elif self._is_enemy_fallback(obj_name):
            entities["enemies"].append(entity)
    
    def create_player(self, position: Tuple[float, float], properties: Dict = None) -> Optional[Player]:
        try:
            config = self.configs["entities"]["Player"]
            sprite_config = config.get("sprite", {})

            player = Player(
                id="player",
                name="Jogador",
                position=position,
                size=tuple(config.get("size", PlayerConst.DEFAULT_SIZE)),
                speed=config.get("speed", PlayerConst.DEFAULT_SPEED),
                health=config.get("health", PlayerConst.DEFAULT_HEALTH),
                weapon=None,  
                ammo=config.get("start_ammo", PlayerConst.STARTING_AMMO),
                status="alive",
                sprite_config=sprite_config,
                hitbox_size=tuple(config.get("hitbox_size", config.get("size", PlayerConst.DEFAULT_SIZE)))
            )
            
            return player
            
        except Exception as e:
            log_error(f"Erro ao criar player", "entityFactory", e)
            return None
    
    def create_enemy(self, enemy_type: str, position: Tuple[float, float], properties: Dict = None) -> Optional[Enemy]:
        try:
            config = self.configs["entities"].get(enemy_type, {})
            if not config:
                log_error(f"Configuração do inimigo {enemy_type} não encontrada", "entityFactory")
                return None
            
            sprite_config = config.get("sprite", {})
            
            enemy = Enemy(
                id=f"{enemy_type.lower()}_{id(position)}",
                name=config.get("name", enemy_type),
                position=position,
                size=tuple(config.get("size", EnemyConst.BASIC_ENEMY_SIZE)),
                speed=config.get("speed", EnemyConst.BASIC_ENEMY_SPEED),
                health=config.get("health", EnemyConst.BASIC_ENEMY_HEALTH),
                weapon=None,
                ammo=0,
                status="alive",
                sprite_config=sprite_config,  
                detection_range=config.get("detection_range", EnemyConst.DETECTION_RANGE),
                drops=config.get("drops", []),
                hitbox_size=tuple(config.get("hitbox_size", config.get("size", EnemyConst.BASIC_ENEMY_SIZE)))
            )
            
            return enemy
            
        except Exception as e:
            log_error(f"Erro ao criar inimigo {enemy_type}", "entityFactory", e)
            return None
    
    def create_item(self, item_type: str, position: Tuple[float, float], properties: Dict = None) -> Optional[Item]:
        try:
            config = self.configs["items"].get(item_type, {})
            if not config:
                log_error(f"Configuração do item {item_type} não encontrada", "entityFactory")
                return None
            
            sprite_name = config.get("sprite", f"assets/sprites/{item_type.lower()}.png")
            
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
            log_error(f"Erro ao criar item {item_type}", "entityFactory", e)
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

            center_x = position[0] + width / 2
            center_y = position[1] + height / 2
            center_position = (center_x, center_y)

            door = Door(
                id=f"{door_type.lower()}_{id(position)}",
                position=center_position,
                size=(width, height),
                locked=locked,
                name=door_type,
                destination=destination
            )

            return door

        except Exception as e:
            log_error(f"Erro ao criar porta {door_type}", "entityFactory", e)
            return None

    def _try_enemy_fallback(self, obj_name: str, position: Tuple[float, float], properties: Dict = None) -> Optional[Enemy]:
        """
        Sistema de fallback hierárquico para inimigos não reconhecidos.
        Tenta criar inimigo na seguinte ordem: BossEnemy -> BasicEnemy
        """
        fallback_hierarchy = []

        if "Boss" in obj_name or "Final" in obj_name:
            fallback_hierarchy = ["BossEnemy", "BasicEnemy"]
        else:
            fallback_hierarchy = ["BasicEnemy"]

        for fallback_type in fallback_hierarchy:
            if fallback_type in self.configs["entities"]:
                log_warning(f"Usando fallback '{fallback_type}' para '{obj_name}'", "entityFactory")
                return self.create_enemy(fallback_type, position, properties)

        log_warning(f"Falha ao criar fallback para '{obj_name}' - nenhuma opção disponível", "entityFactory")
        return None

    def _is_enemy_fallback(self, obj_name: str) -> bool:
        """
        Verifica se a entidade é um tipo que pode ter fallback para inimigo.
        """
        enemy_fallback_types = [
            "FinalBoss", "Boss", "BossEnemy", "StrongEnemy", "BasicEnemy",
            "Enemy", "Inimigo", "Chefe", "MiniBoss"
        ]

        return any(fallback_type in obj_name for fallback_type in enemy_fallback_types)
    
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