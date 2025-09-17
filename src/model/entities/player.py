import pygame
from typing import Tuple, Optional, Any, List, Dict
from src.model.entities.entity import Entity
from src.core.utils import load_image, create_surface
from src.model.objects.bullet import Bullet
from src.core.constants import Player as PlayerConst, Animation

class Player(Entity):
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
        sprite_config: Optional[Dict] = None,
        hitbox_size: Optional[Tuple[int, int]] = None
    ) -> None:
        # Setup player sprite
        image = self._load_player_sprite(sprite_config, size)
        
        # Player usa hitbox triangular por padrão
        super().__init__(id, name, position, size, speed, health, weapon, ammo, image, status, 0, sprite_config, hitbox_size, "triangle")
    

    def _load_player_sprite(self, sprite_config: Optional[Dict], size: Tuple[int, int]) -> pygame.Surface:
        """Carrega o sprite do jogador"""
        if sprite_config:
            sprite_path = sprite_config.get("path", "assets/sprites/player_pixelado.png")
        else:
            sprite_path = "assets/sprites/player_pixelado.png"

        spritesheet = load_image(sprite_path)
        
        if spritesheet is None:
            # Fallback para uma superfície colorida se não conseguir carregar
            spritesheet = create_surface(PlayerConst.FALLBACK_SPRITE_SIZE)
            spritesheet.fill(PlayerConst.FALLBACK_SPRITE_COLOR)
        
        return spritesheet

    def update_animation(self, delta_time: float) -> None:
        """Override para controlar animação apenas quando se movendo"""
        if not self.moving:
            self.current_frame = 0
            if self.frames:
                self.base_image = self.frames[0]
            return

        # Chama o método da classe pai se estiver se movendo
        super().update_animation(delta_time)

    def move(
        self,
        directions: List[str],
        delta_time: float,
        obstacles: Optional[list] = None,
        world_bounds: Optional[Tuple[int, int]] = None
    ) -> None:
        self.moving = True

        direction_vector = pygame.Vector2(0, 0)
        for direction in directions:
            if direction == "up":
                direction_vector.y -= 1
            elif direction == "down":
                direction_vector.y += 1
            elif direction == "left":
                direction_vector.x -= 1
            elif direction == "right":
                direction_vector.x += 1

        if direction_vector.length() > 0:
            direction_vector = direction_vector.normalize()

        speed = self.speed * delta_time
        move_vec = direction_vector * speed
        new_pos = self.position + move_vec

        
        collision = self._check_collision(new_pos, obstacles)
        
        if not collision:
            self.position = new_pos
            
            if world_bounds:
                self._apply_world_bounds(world_bounds)

    def _check_collision(self, new_pos: pygame.Vector2, obstacles: Optional[list]) -> bool:
        if not obstacles:
            return False

        temp_rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        temp_rect.center = (int(new_pos.x), int(new_pos.y))

        for obstacle in obstacles:
            if temp_rect.colliderect(obstacle):
                return True
        return False

    def _apply_world_bounds(self, world_bounds: Tuple[int, int]) -> None:
        half_width = self.size[0] // 2
        half_height = self.size[1] // 2

        min_x = half_width
        min_y = half_height
        max_x = world_bounds[0] - half_width
        max_y = world_bounds[1] - half_height

        x = max(min_x, min(self.position.x, max_x))
        y = max(min_y, min(self.position.y, max_y))
        self.position = pygame.Vector2(x, y)

    def reload(self) -> None:
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def update(self, delta_time: float) -> None:
        self.update_animation(delta_time)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        self.moving = False

    def handle_key_press(
        self, 
        key: str, 
        delta_time: float, 
        obstacles: Optional[list] = None,
        world_bounds: Optional[Tuple[int, int]] = None
    ) -> None:
        if key in ["up", "down", "left", "right"]:
            self.move(key, delta_time, obstacles, world_bounds)

    def handle_mouse_click(self):
        return self.shoot()

    def rotate_to_mouse(self, mouse_pos: Tuple[int, int]) -> None:
        self.rotate_towards(mouse_pos)

        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.base_image, -self.rotation)
        self.rect = self.image.get_rect(center=old_center)

    def heal(self, amount: int) -> None:
        old_health = self.health
        self.health = min(self.health + amount, 100)
        actual_heal = self.health - old_health

    def add_ammo(self, amount: int) -> None:
        if not self.weapon:
            return

        old_ammo = self.ammo
        max_ammo = getattr(self.weapon, 'max_ammo', 100) 
        self.ammo = min(self.ammo + amount, max_ammo)
        actual_ammo = self.ammo - old_ammo

        if actual_ammo > 0:
        else:
    
    def take_damage(self, damage: int) -> None:
        if damage <= 0:
            return
            
        old_health = self.health
        self.health = max(0, self.health - damage)
        actual_damage = old_health - self.health
        
        if actual_damage > 0:
            
            if self.health <= 0:
                self.die()  # Use the inherited die() method from Entity
        else:
