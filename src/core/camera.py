import pygame
from typing import Tuple, Optional
from src.model.entities.entity import Entity


class Camera:
    def __init__(self, width: int, height: int, world_width: int, world_height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.world_width: int = world_width
        self.world_height: int = world_height
        
        self.x: float = 0.0
        self.y: float = 0.0
        
        self.offset_x: float = width // 2
        self.offset_y: float = height // 2
        
        self.smoothing: bool = True
        self.smoothing_factor: float = 0.1  

        self.min_x: float = 0
        self.min_y: float = 0
        self.max_x: float = max(0, world_width - width)
        self.max_y: float = max(0, world_height - height)
    
    def follow_target(self, target: Entity) -> None:
        if not target:
            return
            
        target_x = target.position[0] - self.offset_x
        target_y = target.position[1] - self.offset_y
        
        if self.smoothing:
            self.x += (target_x - self.x) * self.smoothing_factor
            self.y += (target_y - self.y) * self.smoothing_factor
        else:
            self.x = target_x
            self.y = target_y
        
        self._apply_bounds()
    
    def _apply_bounds(self) -> None:
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.y = max(self.min_y, min(self.max_y, self.y))
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[float, float]:
        screen_x = world_pos[0] - self.x
        screen_y = world_pos[1] - self.y
        return (screen_x, screen_y)
    
    def get_offset(self) -> Tuple[float, float]:
        """Retorna o offset atual da câmera para conversão mundo->tela"""
        return (self.x, self.y)
    
    def screen_to_world(self, screen_pos: Tuple[float, float]) -> Tuple[float, float]:
        world_x = screen_pos[0] + self.x
        world_y = screen_pos[1] + self.y
        return (world_x, world_y)
    
    def get_view_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_visible(self, obj_pos: Tuple[float, float], obj_size: Tuple[int, int]) -> bool:
        obj_rect = pygame.Rect(obj_pos[0], obj_pos[1], obj_size[0], obj_size[1])
        view_rect = self.get_view_rect()
        return view_rect.colliderect(obj_rect)
    
    def set_position(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self._apply_bounds()
    
    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
        self._apply_bounds()
    
    def set_world_bounds(self, world_width: int, world_height: int) -> None:
        self.world_width = world_width
        self.world_height = world_height
        self.max_x = max(0, world_width - self.width)
        self.max_y = max(0, world_height - self.height)
        self._apply_bounds()
    
    def set_smoothing(self, enabled: bool, factor: float = 0.1) -> None:
        self.smoothing = enabled
        self.smoothing_factor = max(0.0, min(1.0, factor))
