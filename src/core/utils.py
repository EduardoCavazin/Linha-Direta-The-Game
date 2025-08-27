import os
import pygame
from typing import Tuple, Optional

def load_image(path: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    
    if not path.startswith('assets/'):
        full_path = os.path.join('assets', path)
    else:
        full_path = path

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Imagem não encontrada: {full_path}")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Imagem não encontrada: {full_path}")
    
    image = pygame.image.load(full_path)
    
    if size:
        image = pygame.transform.scale(image, size)
    
    return image.convert_alpha()

def create_surface(size: Tuple[int, int], alpha: bool = True) -> pygame.Surface:
    """Cria uma superfície com ou sem alpha"""
    if alpha:
        return pygame.Surface(size, pygame.SRCALPHA)
    else:
        return pygame.Surface(size)

def create_overlay(size: Tuple[int, int], color: Tuple[int, int, int, int]) -> pygame.Surface:
    """Cria uma superfície overlay com cor e alpha"""
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    overlay.fill(color)
    return overlay