import math
import pygame
from typing import Tuple, Optional, Any, TYPE_CHECKING
from src.model.entities.entity import Entity
from src.core.utils import load_image
from src.core.constants import Enemy as EnemyConst, Animation, Bullet as BulletConst
from src.core.enums import EntityStatus
from src.core.mathUtils import calculate_angle_to_target

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
        drops: list = None,
        hitbox_size: Optional[Tuple[int, int]] = None
    ) -> None:
        sprite_config = sprite_config or {}
        sprite_path = sprite_config.get("path", "assets/sprites/enemy2.png") 
        
        image = load_image(sprite_path)
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, image, status, 0, sprite_config, hitbox_size)
        
        self.detection_range = detection_range
        self.drops = drops or []
        
        self.attack_range: float = EnemyConst.ATTACK_RANGE     
        self.attack_cooldown: float = 0.0    
        self.attack_interval: float = EnemyConst.ATTACK_INTERVAL_SECONDS    
        self.last_attack_time: float = 0.0
    
    def update(self, player_pos: Tuple[float, float], delta_time: float = 0.016) -> Optional['Bullet']:
        if not self.is_alive():
            return None
            
        # Update animation
        self.update_animation(delta_time)
            
        self.rotate_towards(player_pos)
        
        angle_rad = math.radians(self.rotation)
        self.direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))
        
        self.image = pygame.transform.rotate(self.base_image, -self.rotation)
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
        return self.get_distance_to(player_pos)
    
    def _shoot_at_player(self, player_pos: Tuple[float, float]) -> Optional['Bullet']:
        from src.model.objects.bullet import Bullet
        
        enemy_pos = (self.position.x, self.position.y)
        distance = self.get_distance_to(player_pos)
        
        if distance == 0:
            return None
        
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        dx = dx / distance
        dy = dy / distance
        
        offset = EnemyConst.BULLET_SPAWN_OFFSET
        bullet_x = enemy_pos[0] + (dx * offset)
        bullet_y = enemy_pos[1] + (dy * offset)
        
        bullet_angle = calculate_angle_to_target(enemy_pos, player_pos)
        
        damage = self.weapon.damage if self.weapon else EnemyConst.DEFAULT_DAMAGE
        
        bullet = Bullet(
            id=f"enemy_bullet_{id(self)}_{pygame.time.get_ticks()}",
            position=(bullet_x, bullet_y),
            size=BulletConst.DEFAULT_SIZE,          
            speed=BulletConst.ENEMY_BULLET_SPEED,            
            damage=damage,
            rotation=bullet_angle,
            is_player_bullet=False  # Balas dos inimigos
        )
        
        return bullet
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)
        
    def set_dead_state(self) -> None:
        self.status = EntityStatus.DEAD.value
        
        try:
            self.base_image = load_image("assets/sprites/dead_enemy.png", self.size)
            self.image = pygame.transform.rotate(self.base_image, -self.rotation)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.hitbox = self.rect
        except Exception as e:
            print(f"Erro ao carregar imagem de inimigo morto: {e}")
        
        self.speed = 0
    
    def is_alive(self) -> bool:
        return self.health > 0 and self.status != "dead"
