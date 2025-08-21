"""
Game Enums - Centralized enumeration definitions
Eliminates magic strings and provides type safety
"""
from enum import Enum, auto

# ==============================================
# ENTITY STATES
# ==============================================

class EntityStatus(Enum):
    """Status of entities (Player, Enemy)"""
    ALIVE = "alive"
    DEAD = "dead"
    
    def __str__(self) -> str:
        return self.value

# ==============================================
# ITEM SYSTEM
# ==============================================

class ItemType(Enum):
    """Types of items that can be found/dropped"""
    HEALTH_PACK = "HealthPack"
    AMMO_PACK = "AmmoPack"
    
    def __str__(self) -> str:
        return self.value

class ItemEffect(Enum):
    """Effects that items have when collected"""
    HEAL = "heal"
    AMMO = "ammo"
    
    def __str__(self) -> str:
        return self.value

# ==============================================
# ROOM STATES  
# ==============================================

class RoomStatus(Enum):
    """Status of rooms in the game"""
    LOCKED = "locked"
    CLEARED = "cleared"
    VISITED = "visited"
    ACTIVE = "active"
    
    def __str__(self) -> str:
        return self.value

# ==============================================
# WEAPON TYPES
# ==============================================

class WeaponType(Enum):
    """Types of weapons available"""
    PISTOL = "pistol"
    RIFLE = "rifle"
    SHOTGUN = "shotgun"
    
    def __str__(self) -> str:
        return self.value

# ==============================================
# DIRECTION/MOVEMENT
# ==============================================

class Direction(Enum):
    """Movement directions"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    IDLE = "idle"
    
    def __str__(self) -> str:
        return self.value

# ==============================================
# GAME STATES
# ==============================================

class GameState(Enum):
    """Overall game states"""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()

# ==============================================
# MAPPING HELPERS
# ==============================================

def get_item_effect(item_type: ItemType) -> ItemEffect:
    """Maps item types to their effects"""
    mapping = {
        ItemType.HEALTH_PACK: ItemEffect.HEAL,
        ItemType.AMMO_PACK: ItemEffect.AMMO
    }
    return mapping[item_type]

def get_item_display_name(item_type: ItemType) -> str:
    """Gets display name for items (can be localized later)"""
    mapping = {
        ItemType.HEALTH_PACK: "Health Kit",
        ItemType.AMMO_PACK: "Ammo Pack"
    }
    return mapping[item_type]
