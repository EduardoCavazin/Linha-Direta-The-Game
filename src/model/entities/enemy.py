import math
import pygame
from typing import Tuple, Optional, Any, TYPE_CHECKING
from src.model.entities.entity import Entity
from src.core.utils import load_image
from src.core.constants import Enemy as EnemyConst, Animation, Bullet as BulletConst
from src.core.enums import EntityStatus

if TYPE_CHECKING:
    from src.model.objects.bullet import Bullet

class Enemy(Entity):
    def __init__(
        self,
        id: str,
        name: str,
        position: Tuple[float, float],
        size: Tuple[int, int],
        speed: float,
        health: int,
        weapon: Optional[Any],
        ammo: int,
        status: str,
        sprite_config: dict = None,
        detection_range: float = EnemyConst.DETECTION_RANGE,
        drops: list = None
    ) -> None:
        sprite_config = sprite_config or {}
        sprite_path = sprite_config.get("path", "sprites/enemy.png") 
        
        image = load_image(sprite_path, size)
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, image, status)
        
        self.detection_range = detection_range
        self.drops = drops or []
        
        self.frame_count = sprite_config.get("frames", 1)
        self.animation_speed = sprite_config.get("animation_speed", Animation.ENEMY_ANIMATION_SPEED)
        
        self.base_enemy_image: pygame.Surface = load_image("sprites/Enemy4.png", size)
        self.base_enemy_rect: pygame.Rect = self.base_enemy_image.get_rect(topleft=position)
        
        self.image: pygame.Surface = self.base_enemy_image
        self.rect: pygame.Rect = self.image.get_rect(topleft=position)
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)
        
        self.attack_range: float = EnemyConst.ATTACK_RANGE     
        self.attack_cooldown: float = 0.0    
        self.attack_interval: float = EnemyConst.ATTACK_INTERVAL_SECONDS    
        self.last_attack_time: float = 0.0
        
    @property
    def position(self) -> pygame.Vector2:
        return self._position
    
    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
    
    def update(self, player_pos: Tuple[float, float], delta_time: float = 0.016) -> Optional['Bullet']:
        if not self.is_alive():
            return None
            
        self.rotate_towards(player_pos)
        
        angle_rad = math.radians(self.rotation)
        self.direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))
        
        self.image = pygame.transform.rotate(self.base_enemy_image, -self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        return self._try_attack_player(player_pos)
    
    def _try_attack_player(self, player_pos: Tuple[float, float]) -> Optional['Bullet']:
        if self.attack_cooldown > 0:
            return None
        
        distance = self._calculate_distance_to_player(player_pos)
        
        if distance <= self.attack_range:
            self.attack_cooldown = self.attack_interval
            return self._shoot_at_player(player_pos)
        
        return None
    
    def _calculate_distance_to_player(self, player_pos: Tuple[float, float]) -> float:
        enemy_x, enemy_y = self.position.x, self.position.y
        player_x, player_y = player_pos
        return math.sqrt((player_x - enemy_x) ** 2 + (player_y - enemy_y) ** 2)
    
    def _shoot_at_player(self, player_pos: Tuple[float, float]) -> Optional['Bullet']:
        from src.model.objects.bullet import Bullet
        
        enemy_x, enemy_y = self.position.x, self.position.y
        player_x, player_y = player_pos
        
        dx = player_x - enemy_x
        dy = player_y - enemy_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return None
        
        dx = dx / distance
        dy = dy / distance
        
        offset = EnemyConst.BULLET_SPAWN_OFFSET
        bullet_x = enemy_x + (dx * offset)
        bullet_y = enemy_y + (dy * offset)
        
        bullet_angle = math.degrees(math.atan2(dy, dx))
        
        damage = self.weapon.damage if self.weapon else EnemyConst.DEFAULT_DAMAGE
        
        bullet = Bullet(
            id=f"enemy_bullet_{id(self)}_{pygame.time.get_ticks()}",
            position=(bullet_x, bullet_y),
            size=BulletConst.DEFAULT_SIZE,          
            speed=BulletConst.ENEMY_BULLET_SPEED,            
            damage=damage,
            rotation=bullet_angle
        )
        
        return bullet
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)
        
    def set_dead_state(self) -> None:
        self.status = EntityStatus.DEAD.value
        
        try:
            self.base_enemy_image = load_image("sprites/dead_enemy.png", self.size)
            self.image = pygame.transform.rotate(self.base_enemy_image, -self.rotation)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.hitbox = self.rect
        except Exception as e:
            print(f"Erro ao carregar imagem de inimigo morto: {e}")
        
        self.speed = 0
    
    def is_alive(self) -> bool:
        return self.health > 0 and self.status != "dead"
