import pygame
from typing import Tuple, Optional, Union
from src.core import mathUtils

class GameObject:
    def __init__(self, 
                 id: str, 
                 position: Tuple[float, float], 
                 size: Tuple[int, int], 
                 hitbox_size: Tuple[int, int] = None,
                 hitbox_type: str = "rect") -> None:
        self.id: str = id
        self._position: pygame.Vector2 = pygame.Vector2(position)
        self.size: Tuple[int, int] = size
        self.hitbox_type: str = hitbox_type  # "rect" or "triangle"
        
        # Use hitbox_size if provided, otherwise use size
        hitbox_dimensions = hitbox_size if hitbox_size else size
        
        if hitbox_type == "triangle":
            # Para hitbox triangular: width = largura dos ombros, height = profundidade
            self.triangle_width = hitbox_dimensions[0] 
            self.triangle_height = hitbox_dimensions[1]
            self.triangle_rotation = 0.0  # Rotação em graus
            
            # Manter hitbox retangular para compatibilidade (bounding box)
            self.hitbox: pygame.Rect = pygame.Rect(
                position[0] - hitbox_dimensions[0] // 2, 
                position[1] - hitbox_dimensions[1] // 2,
                hitbox_dimensions[0], 
                hitbox_dimensions[1]
            )
        else:
            # Hitbox retangular tradicional
            self.hitbox: pygame.Rect = pygame.Rect(
                position[0] - hitbox_dimensions[0] // 2, 
                position[1] - hitbox_dimensions[1] // 2,
                hitbox_dimensions[0], 
                hitbox_dimensions[1]
            )
    
    @property
    def position(self) -> pygame.Vector2:
        """Getter para posição"""
        return self._position
    
    @position.setter  
    def position(self, value: Union[pygame.Vector2, Tuple[float, float]]) -> None:
        """Setter para posição - atualiza hitboxes automaticamente"""
        if isinstance(value, pygame.Vector2):
            self._position = value
        else:
            self._position = pygame.Vector2(value)
        
        # Atualizar hitbox retangular
        self.hitbox.center = (int(self._position.x), int(self._position.y))
    
    def get_triangle_vertices(self) -> Optional[Tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]]:
        """
        Retorna os vértices do hitbox triangular se aplicável.
        
        Returns:
            Tupla com 3 vértices ou None se não for hitbox triangular
        """
        if self.hitbox_type != "triangle":
            return None
            
        return mathUtils.create_triangle_vertices(
            self._position, 
            self.triangle_width, 
            self.triangle_height, 
            self.triangle_rotation
        )
    
    def set_triangle_rotation(self, rotation: float) -> None:
        """
        Define a rotação do hitbox triangular.
        
        Args:
            rotation: Rotação em graus (0 = ponta para cima)
        """
        if self.hitbox_type == "triangle":
            self.triangle_rotation = rotation
    
    def collides_with(self, other: 'GameObject') -> bool:
        """
        Verifica colisão com outro GameObject, usando o tipo de hitbox apropriado.
        
        Args:
            other: Outro GameObject para testar colisão
            
        Returns:
            True se há colisão
        """
        # Otimização: primeiro teste com bounding boxes retangulares
        if not self.hitbox.colliderect(other.hitbox):
            return False
        
        # Se ambos são triangulares
        if self.hitbox_type == "triangle" and other.hitbox_type == "triangle":
            self_vertices = self.get_triangle_vertices()
            other_vertices = other.get_triangle_vertices()
            if self_vertices and other_vertices:
                return mathUtils.triangle_triangle_collision(self_vertices, other_vertices)
        
        # Se este é triangular e o outro retangular
        elif self.hitbox_type == "triangle":
            self_vertices = self.get_triangle_vertices()
            if self_vertices:
                return mathUtils.triangle_rect_collision(self_vertices, other.hitbox)
        
        # Se o outro é triangular e este retangular
        elif other.hitbox_type == "triangle":
            other_vertices = other.get_triangle_vertices()
            if other_vertices:
                return mathUtils.triangle_rect_collision(other_vertices, self.hitbox)
        
        # Ambos retangulares (comportamento original)
        else:
            return self.hitbox.colliderect(other.hitbox)
        
        return False
    
    def draw_debug_hitbox(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0), color: Tuple[int, int, int] = (255, 0, 0)) -> None:
        """
        Desenha o hitbox para debug - triangular ou retangular conforme o tipo.
        
        Args:
            screen: Superfície onde desenhar
            camera_offset: Offset da câmera
            color: Cor do hitbox
        """
        if self.hitbox_type == "triangle":
            vertices = self.get_triangle_vertices()
            if vertices:
                screen_vertices = []
                for vertex in vertices:
                    screen_pos = (
                        int(vertex.x - camera_offset[0]),
                        int(vertex.y - camera_offset[1])
                    )
                    screen_vertices.append(screen_pos)
                
                if len(screen_vertices) >= 3:
                    pygame.draw.polygon(screen, color, screen_vertices, 2)
                    
                    # Desenhar ponto no centro
                    center_screen = (
                        int(self._position.x - camera_offset[0]),
                        int(self._position.y - camera_offset[1])
                    )
                    pygame.draw.circle(screen, color, center_screen, 3)
        else:
            # Hitbox retangular tradicional
            screen_rect = self.hitbox.copy()
            screen_rect.topleft = (
                self.hitbox.left - camera_offset[0],
                self.hitbox.top - camera_offset[1]
            )
            pygame.draw.rect(screen, color, screen_rect, 2)
