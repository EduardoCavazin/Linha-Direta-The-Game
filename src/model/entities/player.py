import math
import pygame
from typing import Tuple, Optional, Any, List
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
        sprite_config: dict = None
    ) -> None:
        sprite_config = sprite_config or {}
        sprite_path = sprite_config.get("path", "sprites/Player_Movement.png")
        
        print(f"[Player] Sprite config recebido: {sprite_config}")  # DEBUG
        print(f"[Player] Carregando sprite: {sprite_path}")  # DEBUG
        
        # Carregar sprite completo
        sprite_sheet = load_image(sprite_path, None)  # Não redimensionar ainda
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, sprite_sheet, status)
        
        # Configurações de animação
        self.frame_count = sprite_config.get("frames", 4)
        self.animation_speed = sprite_config.get("animation_speed", 0.15)
        self.directions = sprite_config.get("directions", ["down", "left", "right", "up"])
        
        # Sistema de animação simplificado
        self.current_direction = 0  # Índice da direção (0=down, 1=left, 2=right, 3=up)
        self.current_frame = 0
        self.animation_timer = 0.0
        self.is_moving = False
        
        # Carregar todos os frames
        self.animation_frames = self._load_animation_frames(sprite_sheet, size)
        
        # Definir imagem inicial
        self.image = self.animation_frames[self.current_direction][0]
        
        # Para rotação (se necessário)
        self.rotation = 0

    def _load_animation_frames(self, sprite_sheet: pygame.Surface, target_size: Tuple[int, int]) -> List[List[pygame.Surface]]:
        """Carrega todos os frames de animação organizados por direção"""
        frames = []
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()
        
        frame_width = sheet_width // self.frame_count
        frame_height = sheet_height // len(self.directions)
        
        for direction_index in range(len(self.directions)):
            direction_frames = []
            for frame_index in range(self.frame_count):
                # Extrair frame
                frame_rect = pygame.Rect(
                    frame_index * frame_width,
                    direction_index * frame_height,
                    frame_width,
                    frame_height
                )
                
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(sprite_sheet, (0, 0), frame_rect)
                
                # Redimensionar para o tamanho alvo
                frame_surface = pygame.transform.scale(frame_surface, target_size)
                direction_frames.append(frame_surface)
            
            frames.append(direction_frames)
        
        return frames

    @property
    def position(self) -> Tuple[float, float]:
        return (self._position.x, self._position.y)

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
        # CORREÇÃO: Usar hitbox em vez de rect
        self.hitbox.center = (int(self._position.x), int(self._position.y))

    def update_animation(self, delta_time: float) -> None:
        """Atualiza animação baseada no movimento"""
        if not self.is_moving:
            self.current_frame = 0
            self.animation_timer = 0
        else:
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % self.frame_count
        
        # Atualizar imagem atual
        self.image = self.animation_frames[self.current_direction][self.current_frame]

    def move(
        self,
        directions: List[str],  
        delta_time: float,
        obstacles: Optional[list] = None,
        world_bounds: Optional[Tuple[int, int]] = None
    ) -> None:
        if not directions:
            self.is_moving = False
            return
        
        self.is_moving = True
        
        # Definir direção da animação baseada no movimento
        if "up" in directions:
            self.current_direction = 3  # up
        elif "down" in directions:
            self.current_direction = 0  # down
        elif "left" in directions:
            self.current_direction = 1  # left
        elif "right" in directions:
            self.current_direction = 2  # right
        
        # Calcular movimento (código existente)
        direction_x = 0
        direction_y = 0
        
        if "left" in directions:
            direction_x -= 1
        if "right" in directions:
            direction_x += 1
        if "up" in directions:
            direction_y -= 1
        if "down" in directions:
            direction_y += 1
        
        # Normalizar diagonal
        if direction_x != 0 and direction_y != 0:
            direction_x *= 0.7071
            direction_y *= 0.7071
        
        new_x = self._position.x + direction_x * self.speed * delta_time
        new_y = self._position.y + direction_y * self.speed * delta_time
        
        # Verificar colisões e limites (código existente)
        new_pos = pygame.Vector2(new_x, new_y)
        
        if world_bounds:
            new_pos.x = max(self.size[0]//2, min(new_pos.x, world_bounds[0] - self.size[0]//2))
            new_pos.y = max(self.size[1]//2, min(new_pos.y, world_bounds[1] - self.size[1]//2))
        
        self.position = (new_pos.x, new_pos.y)
        self.update_animation(delta_time)

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
        """Update simplificado"""
        # Apenas atualizar animação se necessário
        if hasattr(self, 'update_animation'):
            self.update_animation(delta_time)

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o player na tela"""
        screen.blit(self.image, self.hitbox.topleft)

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
        """Rotaciona player em direção ao mouse (opcional)"""
        # Se quiser rotação, pode implementar aqui
        # Por enquanto, mantém apenas a animação direcional
        pass
    
    def heal(self, amount: int) -> None:
        old_health = self.health
        self.health = min(self.health + amount, 100) 
        actual_heal = self.health - old_health
        if actual_heal > 0:
            print(f" +{actual_heal} de vida! Vida atual: {self.health}/100")
        else:
            print("Vida já está no máximo!")
    
    def add_ammo(self, amount: int) -> None:
        if not self.weapon:
            print(" Não há arma equipada!")
            return
            
        old_ammo = self.ammo
        max_ammo = getattr(self.weapon, 'max_ammo', 100)  
        self.ammo = min(self.ammo + amount, max_ammo)
        actual_ammo = self.ammo - old_ammo
        
        if actual_ammo > 0:
            print(f"+{actual_ammo} munições! Munição atual: {self.ammo}/{max_ammo}")
        else:
            print(" Munição já está no máximo!")
    
    def take_damage(self, damage: int) -> None:
        if damage <= 0:
            return
            
        old_health = self.health
        self.health = max(0, self.health - damage)
        actual_damage = old_health - self.health
        
        if actual_damage > 0:
            print(f" -{actual_damage} de vida! Vida atual: {self.health}/100")
            
            if self.health <= 0:
                self.alive = False
                print(" Game Over!")
        else:
            print(" Nenhum dano recebido!")
