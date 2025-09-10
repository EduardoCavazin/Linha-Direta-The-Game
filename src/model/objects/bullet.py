import pygame
from typing import Tuple
from src.model.objects.movableObject import MovableObject
from src.core.constants import Rendering, Bullet as BulletConst

class Bullet(MovableObject):
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int],
                 speed: float, damage: int, rotation: float, is_player_bullet: bool = True) -> None:
        super().__init__(id, position, size, speed, rotation)
        self.damage: int = damage
        self.is_player_bullet: bool = is_player_bullet
        self.update_velocity()

    def update(self, delta_time: float, screen_width: int = Rendering.DEFAULT_WINDOW_WIDTH, screen_height: int = Rendering.DEFAULT_WINDOW_HEIGHT) -> bool:
        self.position += self.directedSpeed * delta_time
        self.hitbox.topleft = (self.position.x, self.position.y)
        if (self.position.x < 0 or self.position.x > screen_width or
            self.position.y < 0 or self.position.y > screen_height):
            return False
        return True

    def draw(self, screen: pygame.Surface) -> None:
        # Cores diferentes para balas do player vs inimigos
        if self.is_player_bullet:
            color = (255, 215, 0)  # Dourado para player
        else:
            color = (255, 100, 100)  # Vermelho claro para inimigos
            
        # Desenhar bala ocupando toda a hitbox (mais visível)
        center = self.hitbox.center
        radius = min(self.hitbox.width, self.hitbox.height) // 2
        
        # Borda escura para contraste
        pygame.draw.circle(screen, (0, 0, 0), center, radius + 1)
        
        # Círculo principal do tamanho da hitbox
        pygame.draw.circle(screen, color, center, radius)
        
        # Brilho central para destaque
        inner_radius = max(1, radius // 3)
        pygame.draw.circle(screen, (255, 255, 255), center, inner_radius)
