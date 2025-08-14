import math
import pygame
from typing import Tuple, Optional, Any, List, Dict
from src.model.entities.entity import Entity
from src.core.utils import load_image
from src.model.objects.bullet import Bullet


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
        sprite_config: Optional[Dict] = None
    ) -> None:

        # Usar sprite_config se fornecido, senão usar padrão
        if sprite_config:
            sprite_path = sprite_config.get("path", "sprites/player_pixelado.png")
            self.animation_speed = sprite_config.get("animation_speed", 0.2)
        else:
            sprite_path = "sprites/player_pixelado.png"
            self.animation_speed = 0.2

        self.spritesheet: pygame.Surface = load_image(sprite_path)
        self.frame_count: int = 4  
        self.frame_rows: int = 4
        self.frame_width: int = self.spritesheet.get_width() // self.frame_count
        self.frame_height: int = self.spritesheet.get_height() // self.frame_rows  

        self.frames: List[pygame.Surface] = self._load_animation_frames(size)

        self.current_frame: int = 0
        self.animation_timer: float = 0

        self.base_player_image: pygame.Surface = self.frames[0]

        self.image: pygame.Surface = self.base_player_image
        self.rect: pygame.Rect = self.image.get_rect(center=position)

        self._rect: pygame.Rect = self.rect.copy()

        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)
        self.moving: bool = False

        self._position: pygame.Vector2 = pygame.Vector2(position)

        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)

    def _load_animation_frames(self, size: Tuple[int, int]) -> List[pygame.Surface]:
        frames = []
        for y in range(self.frame_rows):
            for x in range(self.frame_count):
                # Ignora o frame extra no canto inferior esquerdo se não for útil
                if y == 3 and x == 0:  # Frame extra no canto inferior esquerdo
                    # Adiciona o frame extra também (pode ser usado como frame especial)
                    frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                    frame.blit(self.spritesheet, (0, 0), 
                              (x * self.frame_width, y * self.frame_height, 
                               self.frame_width, self.frame_height))
                    frame = pygame.transform.scale(frame, size)
                    frames.append(frame)
                else:
                    frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                    frame.blit(self.spritesheet, (0, 0), 
                              (x * self.frame_width, y * self.frame_height, 
                               self.frame_width, self.frame_height))
                    frame = pygame.transform.scale(frame, size)
                    frames.append(frame)
        return frames

    @property
    def position(self) -> Tuple[float, float]:
        return (self._position.x, self._position.y)

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
        self.rect.center = (int(self._position.x), int(self._position.y))
        self._rect.center = (int(self._position.x), int(self._position.y))

    def update_animation(self, delta_time: float) -> None:
        if not self.moving:
            self.current_frame = 0
            self.base_player_image = self.frames[0]
            return

        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            # Usa os primeiros 4 frames para animação de caminhada (primeira linha da spritesheet)
            self.current_frame = (self.current_frame + 1) % 4
            self.base_player_image = self.frames[self.current_frame]

    def move(
        self,
        directions: List[str],  # Agora recebe uma lista de strings!
        delta_time: float,
        obstacles: Optional[list] = None,
        world_bounds: Optional[Tuple[int, int]] = None
    ) -> None:
        self.moving = True

        # Debug movimento
        old_pos = self.position
        print(f"🚶 MOVE: directions={directions}, old_pos={old_pos}, delta_time={delta_time:.3f}")

        direction_vector = pygame.Vector2(0, 0)
        for direction in directions:
            if direction == "up":
                direction_vector.y -= 1
            if direction == "down":
                direction_vector.y += 1
            if direction == "left":
                direction_vector.x -= 1
            if direction == "right":
                direction_vector.x += 1

        if direction_vector.length() > 0:
            direction_vector = direction_vector.normalize()

        speed = self.speed * delta_time
        move_vec = direction_vector * speed
        new_pos = (self.position[0] + move_vec.x, self.position[1] + move_vec.y)

        print(f"📍 CALC: speed={speed:.2f}, move_vec={move_vec}, new_pos={new_pos}")
        
        collision = self._check_collision(new_pos, obstacles)
        print(f"💥 COLLISION: {collision}, obstacles_count={len(obstacles) if obstacles else 0}")
        
        if not collision:
            self.position = new_pos
            print(f"✅ MOVED: new_position={self.position}")
            if world_bounds:
                self._clamp_to_bounds(world_bounds)
        else:
            print(f"❌ BLOCKED: collision detected")

    def _check_collision(self, new_pos: Tuple[float, float], obstacles: Optional[list]) -> bool:
        if not obstacles:
            return False

        temp_rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        temp_rect.center = (int(new_pos[0]), int(new_pos[1]))

        for obstacle in obstacles:
            if temp_rect.colliderect(obstacle):
                return True
        return False

    def _clamp_to_bounds(self, world_bounds: Tuple[int, int]) -> None:
        half_width = self.size[0] // 2
        half_height = self.size[1] // 2

        min_x = half_width
        min_y = half_height
        max_x = world_bounds[0] - half_width
        max_y = world_bounds[1] - half_height

        x, y = self.position
        x = max(min_x, min(x, max_x))
        y = max(min_y, min(y, max_y))
        self.position = (x, y)

    def reload(self) -> None:
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def shoot(self, target_world_pos: Optional[Tuple[float, float]] = None) -> Optional['Bullet']:
        if not self.weapon or self.ammo <= 0:
            return None

        self.ammo -= 1

        from src.model.objects.bullet import Bullet

        if target_world_pos is None:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = mouse_pos
        else:
            mouse_x, mouse_y = target_world_pos

        player_x, player_y = self.position

        dx = mouse_x - player_x
        dy = mouse_y - player_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            dx, dy = 1, 0
        else:
            dx = dx / distance
            dy = dy / distance

        offset = 25 
        bullet_x = player_x + (dx * offset)
        bullet_y = player_y + (dy * offset)

        bullet_angle = math.degrees(math.atan2(mouse_y - player_y, mouse_x - player_x))

        bullet = Bullet(
            id=f"bullet_{id(self)}_{self.ammo}",
            position=(bullet_x, bullet_y),
            size=(8, 8),
            speed=500,
            damage=self.weapon.damage,
            rotation=bullet_angle
        )

        return bullet

    def update(self, delta_time: float) -> None:
        # Remove a rotação automática baseada no mouse aqui
        # A rotação será controlada pelo GameWorld que tem acesso à câmera
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
        self.image = pygame.transform.rotate(self.base_player_image, -self.rotation)
        self.rect = self.image.get_rect(center=old_center)

    def heal(self, amount: int) -> None:
        """Cura o jogador por uma quantidade específica"""
        old_health = self.health
        self.health = min(self.health + amount, 100)  # Máximo de 100 de vida
        actual_heal = self.health - old_health
        if actual_heal > 0:
            print(f"❤️ +{actual_heal} de vida! Vida atual: {self.health}/100")
        else:
            print("🔸 Vida já está no máximo!")

    def add_ammo(self, amount: int) -> None:
        """Adiciona munição ao jogador"""
        if not self.weapon:
            print("🔸 Não há arma equipada!")
            return

        old_ammo = self.ammo
        max_ammo = getattr(self.weapon, 'max_ammo', 100)  # Use max_ammo da arma ou 100 como padrão
        self.ammo = min(self.ammo + amount, max_ammo)
        actual_ammo = self.ammo - old_ammo

        if actual_ammo > 0:
            print(f"🔫 +{actual_ammo} munições! Munição atual: {self.ammo}/{max_ammo}")
        else:
            print("🔸 Munição já está no máximo!")
    
    def take_damage(self, damage: int) -> None:
        """Faz o jogador tomar dano"""
        if damage <= 0:
            return
            
        old_health = self.health
        self.health = max(0, self.health - damage)
        actual_damage = old_health - self.health
        
        if actual_damage > 0:
            print(f"💥 -{actual_damage} de vida! Vida atual: {self.health}/100")
            
            # Verifica se o jogador morreu
            if self.health <= 0:
                self.alive = False
                print("💀 Game Over!")
        else:
            print("🛡️ Nenhum dano recebido!")