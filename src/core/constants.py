"""
Constantes do jogo - Centralizando todos os magic numbers
Organizado por categorias para fácil manutenção
"""

# World & Camera Settings
class World:
    CAMERA_WORLD_WIDTH = 2000
    CAMERA_WORLD_HEIGHT = 2000
    DEFAULT_SPAWN_X = 100.0
    DEFAULT_SPAWN_Y = 100.0
    TELEPORT_COOLDOWN_SECONDS = 1.0

# Player Settings
class Player:
    DEFAULT_HEALTH = 100
    DEFAULT_SPEED = 200
    DEFAULT_SIZE = (32, 32)
    STARTING_AMMO = 30
    
    # Weapon Settings
    PISTOL_DAMAGE = 25
    PISTOL_MAX_AMMO = 30
    
    # Sprite properties
    FALLBACK_SPRITE_SIZE = (128, 128)
    FALLBACK_SPRITE_COLOR = (0, 150, 255)

# Enemy Settings
class Enemy:
    ATTACK_RANGE = 120.0
    ATTACK_INTERVAL_SECONDS = 1.2
    DETECTION_RANGE = 250.0
    DEFAULT_DAMAGE = 15  # Default damage when no weapon is equipped
    BULLET_SPAWN_OFFSET = 20  # Distance from enemy center to spawn bullet
    
    # Enemy Types
    BASIC_ENEMY_HEALTH = 50
    BASIC_ENEMY_SPEED = 80
    BASIC_ENEMY_SIZE = (32, 32)

# Bullet Settings
class Bullet:
    DEFAULT_SIZE = (8, 8)
    DEFAULT_SPEED = 400
    COLLISION_CHECK_SIZE = (2, 2)
    
    # Player Bullets
    PLAYER_BULLET_SIZE = (8, 8)
    PLAYER_BULLET_SPEED = 500
    
    # Enemy Bullets  
    ENEMY_BULLET_SIZE = (8, 8)
    ENEMY_BULLET_SPEED = 400
    
    # Visual
    COLOR = (255, 215, 0)  # Dourado para as balas

# ==============================================
# ITEM & DROP SETTINGS
# ==============================================
class Items:
    # Drop positioning
    DROP_OFFSET_RANGE = 15  # random.uniform(-15, 15)
    
    # Item values
    HEALTH_PACK_VALUE = 25
    AMMO_PACK_VALUE = 8
    
    # Item sizes
    DEFAULT_ITEM_SIZE = (16, 16)

# ==============================================
# PHYSICS & COLLISION
# ==============================================
class Physics:
    MILLISECONDS_TO_SECONDS = 1000.0
    COLLISION_PADDING = 0.8
    
    # Tile settings
    DEFAULT_TILE_SIZE = (32, 32)
    
    # Rotation/Angle constants
    DIRECTION_OFFSET_DEGREES = 90
    FULL_CIRCLE_DEGREES = 360

# ==============================================
# RENDERING & UI
# ==============================================
class Rendering:
    DEFAULT_WINDOW_WIDTH = 800
    DEFAULT_WINDOW_HEIGHT = 600
    TARGET_FPS = 60
    
    # Font sizes
    PAUSE_FONT_SIZE = 64
    DEFAULT_FONT_SIZE = 24
    
    # UI Colors
    OVERLAY_COLOR = (0, 0, 0, 128)
    TRANSPARENT_BLACK = (0, 0, 0, 128)
    
    # UI Positions
    HEALTH_POS = (10, 10)
    AMMO_POS = (10, 50)
    TIMER_POS = (10, 90)
    
    # Background colors
    DEFAULT_ROOM_COLOR = (64, 64, 64)

# ==============================================
# ANIMATION SETTINGS
# ==============================================
class Animation:
    PLAYER_ANIMATION_SPEED = 0.2
    ENEMY_ANIMATION_SPEED = 0.15
    
    PLAYER_FRAME_COUNT = 4
    PLAYER_FRAME_ROWS = 4

# ==============================================
# GAME LOGIC
# ==============================================
class GameLogic:
    ENEMIES_CLEARED_THRESHOLD = 0
    FIRST_ROOM_INDEX = 0
    
    # Health limits
    MAX_PLAYER_HEALTH = 100
    MIN_HEALTH = 0

# ==============================================
# FIRE DAMAGE SYSTEM
# ==============================================
class FireDamage:
    DAMAGE_PER_TICK = 5  # Damage per fire tick
    DAMAGE_INTERVAL = 1.0  # Seconds between damage ticks
    FIRE_WARNING_COLOR = (255, 100, 0)  # Orange overlay for fire zones

# ==============================================
# FILE PATHS (removing hardcoded paths)
# ==============================================
class Assets:
    PLAYER_SPRITE = "assets/sprites/player_pixelado.png"
    ENEMY_SPRITE = "assets/sprites/Enemy4.png"  # Fixed: added assets/
    DEAD_ENEMY_SPRITE = "assets/sprites/dead_enemy.png"  # Fixed: added assets/
    
    MAPS_FOLDER = "assets/sprites/world/tilesets"
    
    # Audio
    PISTOL_SOUND = "assets/audio/sfx/pistol_sound.wav"
    FOOTSTEP_SOUND = "assets/audio/sfx/footstep.mp3"

# ==============================================
# HELPER FUNCTIONS (para conversões comuns)
# ==============================================
def milliseconds_to_seconds(ms: float) -> float:
    """Converte milissegundos para segundos"""
    return ms / Physics.MILLISECONDS_TO_SECONDS

def seconds_to_milliseconds(seconds: float) -> float:
    """Converte segundos para milissegundos"""
    return seconds * Physics.MILLISECONDS_TO_SECONDS

def get_random_drop_offset() -> tuple[float, float]:
    """Retorna offset aleatório para drop de itens"""
    import random
    offset_x = random.uniform(-Items.DROP_OFFSET_RANGE, Items.DROP_OFFSET_RANGE)
    offset_y = random.uniform(-Items.DROP_OFFSET_RANGE, Items.DROP_OFFSET_RANGE)
    return offset_x, offset_y
