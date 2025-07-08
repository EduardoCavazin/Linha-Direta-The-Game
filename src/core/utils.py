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
    
    image = pygame.image.load(full_path)
    
    if size:
        image = pygame.transform.scale(image, size)
    
    return image.convert_alpha()