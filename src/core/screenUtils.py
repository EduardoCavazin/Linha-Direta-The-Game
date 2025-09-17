"""
Utilidades para gerenciamento de tela e resolução
"""
import pygame
from typing import Tuple

def get_optimal_screen_size(preferred_width: int = 950, preferred_height: int = 800, margin: int = 100) -> Tuple[int, int]:
    """
    Calcula o tamanho ideal da tela baseado na resolução disponível

    Args:
        preferred_width: Largura preferida
        preferred_height: Altura preferida
        margin: Margem de segurança em pixels

    Returns:
        Tupla com (largura, altura) ideais
    """
    pygame.init()

    # Obter informações da tela
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h

    # Calcular tamanho máximo disponível (com margem)
    max_width = screen_width - margin
    max_height = screen_height - margin

    # Usar o tamanho preferido se couber, senão ajustar
    width = min(preferred_width, max_width)
    height = min(preferred_height, max_height)

    # Manter proporção se necessário reduzir muito
    if width < preferred_width or height < preferred_height:
        # Calcular escala para manter proporção
        scale_x = max_width / preferred_width
        scale_y = max_height / preferred_height
        scale = min(scale_x, scale_y)

        width = int(preferred_width * scale)
        height = int(preferred_height * scale)

    return width, height

def center_window(width: int, height: int) -> None:
    """
    Centraliza a janela na tela
    """
    import os
    pygame.init()

    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h

    # Calcular posição para centralizar
    pos_x = (screen_width - width) // 2
    pos_y = (screen_height - height) // 2

    # Definir posição da janela (antes de criar a surface)
    os.environ['SDL_WINDOW_POS'] = f'{pos_x},{pos_y}'

def get_screen_info() -> dict:
    """
    Retorna informações sobre a tela
    """
    pygame.init()
    info = pygame.display.Info()

    return {
        "screen_width": info.current_w,
        "screen_height": info.current_h,
        "desktop_size": (info.current_w, info.current_h)
    }