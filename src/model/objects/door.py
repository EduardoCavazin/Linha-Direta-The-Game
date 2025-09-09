from typing import Tuple
import pygame
from src.model.objects.gameObject import GameObject

class Door(GameObject):
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int], locked: bool = False, name: str = "Door", destination: str = "next_room") -> None:
        super().__init__(id, position, size)
        self.locked: bool = locked
        self.opened: bool = False
        self.name: str = name  
        self.destination: str = destination
        
        # Garantir que o hitbox está centrado corretamente
        self.hitbox.center = (int(position[0]), int(position[1])) 

    @property
    def position(self) -> Tuple[float, float]:
        return (self._position.x, self._position.y)

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position.x, self._position.y = value
        self.hitbox.center = (int(value[0]), int(value[1]))

    def open(self) -> None:
        if not self.locked:
            self.opened = True

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha a porta com cores baseadas no estado"""
        if self.locked:
            # Porta trancada - vermelha
            color = (200, 50, 50)  # Vermelho escuro
            border_color = (255, 100, 100)  # Vermelho claro para borda
        else:
            # Porta destrancada - azul preenchida
            color = (50, 100, 200)  # Azul
            border_color = (100, 150, 255)  # Azul claro para borda
        
        # Desenhar retângulo preenchido
        pygame.draw.rect(screen, color, self.hitbox)
        
        # Desenhar borda para destaque
        pygame.draw.rect(screen, border_color, self.hitbox, 2)
        
        # Adicionar um pequeno indicador no centro
        center_x, center_y = self.hitbox.center
        indicator_size = min(self.hitbox.width, self.hitbox.height) // 4
        indicator_rect = pygame.Rect(
            center_x - indicator_size // 2,
            center_y - indicator_size // 2,
            indicator_size,
            indicator_size
        )
        
        if self.locked:
            # Desenhar "X" para porta trancada
            pygame.draw.line(screen, (255, 255, 255), 
                           indicator_rect.topleft, indicator_rect.bottomright, 2)
            pygame.draw.line(screen, (255, 255, 255), 
                           indicator_rect.topright, indicator_rect.bottomleft, 2)
        else:
            # Desenhar "✓" para porta destrancada
            check_points = [
                (indicator_rect.left + 2, indicator_rect.centery),
                (indicator_rect.centerx - 1, indicator_rect.bottom - 3),
                (indicator_rect.right - 2, indicator_rect.top + 2)
            ]
            pygame.draw.lines(screen, (255, 255, 255), False, check_points, 2)
