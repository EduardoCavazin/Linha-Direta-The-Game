import pygame
from typing import Tuple, Optional
from src.model.entities.entity import Entity


class Camera:
    """
    Sistema de câmera que segue o jogador e permite movimento por todo o mapa.
    """
    
    def __init__(self, width: int, height: int, world_width: int, world_height: int) -> None:
        """
        Inicializa a câmera.
        
        Args:
            width: Largura da tela/viewport
            height: Altura da tela/viewport  
            world_width: Largura total do mundo/mapa
            world_height: Altura total do mundo/mapa
        """
        self.width: int = width
        self.height: int = height
        self.world_width: int = world_width
        self.world_height: int = world_height
        
        # Posição da câmera no mundo
        self.x: float = 0.0
        self.y: float = 0.0
        
        # Offset para centralizar o jogador na tela
        self.offset_x: float = width // 2
        self.offset_y: float = height // 2
        
        # Configurações de suavização
        self.smoothing: bool = True
        self.smoothing_factor: float = 0.1  # Quanto menor, mais suave
        
        # Bordas da câmera (para não mostrar área vazia do mapa)
        self.min_x: float = 0
        self.min_y: float = 0
        self.max_x: float = max(0, world_width - width)
        self.max_y: float = max(0, world_height - height)
    
    def follow_target(self, target: Entity) -> None:
        """
        Faz a câmera seguir uma entidade (normalmente o jogador).
        
        Args:
            target: Entidade a ser seguida
        """
        if not target:
            return
            
        # Calcula a posição desejada da câmera para centralizar o alvo
        target_x = target.position[0] - self.offset_x
        target_y = target.position[1] - self.offset_y
        
        if self.smoothing:
            # Movimento suave da câmera
            self.x += (target_x - self.x) * self.smoothing_factor
            self.y += (target_y - self.y) * self.smoothing_factor
        else:
            # Movimento direto
            self.x = target_x
            self.y = target_y
        
        # Aplica os limites do mundo
        self._apply_bounds()
    
    def _apply_bounds(self) -> None:
        """Aplica os limites da câmera para não mostrar área vazia."""
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.y = max(self.min_y, min(self.max_y, self.y))
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Converte coordenadas do mundo para coordenadas da tela.
        
        Args:
            world_pos: Posição no mundo
            
        Returns:
            Posição na tela
        """
        screen_x = world_pos[0] - self.x
        screen_y = world_pos[1] - self.y
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Converte coordenadas da tela para coordenadas do mundo.
        
        Args:
            screen_pos: Posição na tela
            
        Returns:
            Posição no mundo
        """
        world_x = screen_pos[0] + self.x
        world_y = screen_pos[1] + self.y
        return (world_x, world_y)
    
    def get_view_rect(self) -> pygame.Rect:
        """
        Retorna o retângulo que representa a área visível da câmera.
        
        Returns:
            Retângulo da área visível
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_visible(self, obj_pos: Tuple[float, float], obj_size: Tuple[int, int]) -> bool:
        """
        Verifica se um objeto está visível na câmera.
        
        Args:
            obj_pos: Posição do objeto
            obj_size: Tamanho do objeto
            
        Returns:
            True se o objeto está visível
        """
        obj_rect = pygame.Rect(obj_pos[0], obj_pos[1], obj_size[0], obj_size[1])
        view_rect = self.get_view_rect()
        return view_rect.colliderect(obj_rect)
    
    def set_position(self, x: float, y: float) -> None:
        """
        Define a posição da câmera diretamente.
        
        Args:
            x: Posição X
            y: Posição Y
        """
        self.x = x
        self.y = y
        self._apply_bounds()
    
    def move(self, dx: float, dy: float) -> None:
        """
        Move a câmera por uma quantidade específica.
        
        Args:
            dx: Movimento em X
            dy: Movimento em Y
        """
        self.x += dx
        self.y += dy
        self._apply_bounds()
    
    def set_world_bounds(self, world_width: int, world_height: int) -> None:
        """
        Atualiza os limites do mundo.
        
        Args:
            world_width: Nova largura do mundo
            world_height: Nova altura do mundo
        """
        self.world_width = world_width
        self.world_height = world_height
        self.max_x = max(0, world_width - self.width)
        self.max_y = max(0, world_height - self.height)
        self._apply_bounds()
    
    def set_smoothing(self, enabled: bool, factor: float = 0.1) -> None:
        """
        Configura a suavização da câmera.
        
        Args:
            enabled: Se a suavização está ativada
            factor: Fator de suavização (0.0 a 1.0)
        """
        self.smoothing = enabled
        self.smoothing_factor = max(0.0, min(1.0, factor))
