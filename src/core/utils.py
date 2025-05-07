import os
import pygame
from typing import Tuple, Optional

def load_image(filename: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    """
    Carrega uma imagem usando caminho absoluto
    
    Args:
        filename: Nome do arquivo na pasta assets/sprites
        size: Opcional - Tamanho para redimensionar (width, height)
    
    Returns:
        pygame.Surface: A imagem carregada ou uma superfície colorida em caso de erro
    """
    # Obtém o caminho absoluto
    base_path = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(base_path, "../.."))
    image_path = os.path.join(project_root, "assets", "sprites", filename)
    
    try:
        print(f"Carregando imagem: {image_path}")
        image = pygame.image.load(image_path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except Exception as e:
        print(f"Erro ao carregar imagem {filename}: {e}")
        # Criar uma superfície de fallback
        surface = pygame.Surface(size if size else (32, 32))
        surface.fill((255, 0, 255))  # Magenta para indicar erro
        return surface