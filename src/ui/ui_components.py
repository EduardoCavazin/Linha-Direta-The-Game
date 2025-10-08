"""
Componentes UI compartilhados para padronização visual do jogo
"""
import pygame
import random
import math
from typing import Optional, Tuple

# Cores padrão
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HOVER_COLOR = (100, 200, 255)
SELECTED_COLOR = (255, 220, 100)
GOLD = (255, 215, 0)

class Particle:
    """Partícula animada para efeito de fundo"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(100, 200)

    def update(self):
        self.y += self.speed
        if self.y > self.screen_height:
            self.y = 0
            self.x = random.randint(0, self.screen_width)

    def draw(self, surface: pygame.Surface):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

class MenuItem:
    """Item de menu animado com hover e efeitos visuais"""
    def __init__(self, text: str, rect: pygame.Rect, action: str):
        self.text = text
        self.rect = rect
        self.action = action
        self.scale = 1.0
        self.target_scale = 1.0
        self.glow_intensity = 0
        self.pulse_time = 0

    def update(self, is_hovered: bool, dt: float):
        self.target_scale = 1.15 if is_hovered else 1.0
        self.scale += (self.target_scale - self.scale) * 0.15

        if is_hovered:
            self.glow_intensity = min(255, self.glow_intensity + 15)
            self.pulse_time += dt * 5
        else:
            self.glow_intensity = max(0, self.glow_intensity - 10)
            self.pulse_time = 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, base_color: Tuple[int, int, int]) -> pygame.Rect:
        pulse = math.sin(self.pulse_time) * 0.05 + 1 if self.glow_intensity > 0 else 1
        current_scale = self.scale * pulse

        text_surface = font.render(self.text, True, base_color)
        scaled_width = int(text_surface.get_width() * current_scale)
        scaled_height = int(text_surface.get_height() * current_scale)
        scaled_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))

        scaled_rect = scaled_surface.get_rect(center=self.rect.center)

        if self.glow_intensity > 0:
            glow_surface = pygame.Surface((scaled_rect.width + 40, scaled_rect.height + 40), pygame.SRCALPHA)
            glow_color = (*HOVER_COLOR, int(self.glow_intensity * 0.5))
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=15)
            surface.blit(glow_surface, (scaled_rect.x - 20, scaled_rect.y - 20))

        bg_rect = pygame.Rect(scaled_rect.x - 10, scaled_rect.y - 5,
                              scaled_rect.width + 20, scaled_rect.height + 10)
        alpha_value = 128 + int(self.glow_intensity * 0.3)
        draw_rounded_background(surface, bg_rect, (0, 0, 0, alpha_value), 10)

        surface.blit(scaled_surface, scaled_rect)

        return scaled_rect

def draw_rounded_background(surface: pygame.Surface, rect: pygame.Rect, color: tuple, radius: int) -> None:
    """Desenha um fundo arredondado com transparência"""
    transparent_background = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(transparent_background, color, transparent_background.get_rect(), border_radius=radius)
    surface.blit(transparent_background, (rect.x - 10, rect.y - 5))

def draw_pulsing_title(surface: pygame.Surface, text: str, font_size: int,
                       center_pos: Tuple[int, int], color: Tuple[int, int, int] = SELECTED_COLOR) -> pygame.Rect:
    """Desenha um título com efeito de pulso e brilho"""
    title_pulse = math.sin(pygame.time.get_ticks() * 0.002) * 0.03 + 1
    title_font = pygame.font.Font(None, int(font_size * title_pulse))
    title_surface = title_font.render(text, True, color)
    title_rect = title_surface.get_rect(center=center_pos)

    # Brilho do título
    title_glow = pygame.Surface((title_rect.width + 60, title_rect.height + 60), pygame.SRCALPHA)
    glow_alpha = int((math.sin(pygame.time.get_ticks() * 0.003) * 0.5 + 0.5) * 100)
    pygame.draw.rect(title_glow, (*color, glow_alpha), title_glow.get_rect(), border_radius=20)
    surface.blit(title_glow, (title_rect.x - 30, title_rect.y - 30))

    draw_rounded_background(surface, title_rect, (0, 0, 0, 150), 10)
    surface.blit(title_surface, title_rect)

    return title_rect

def create_particle_system(screen_width: int, screen_height: int, count: int = 50) -> list:
    """Cria um sistema de partículas"""
    return [Particle(screen_width, screen_height) for _ in range(count)]

def update_and_draw_particles(particles: list, surface: pygame.Surface):
    """Atualiza e desenha todas as partículas"""
    for particle in particles:
        particle.update()
        particle.draw(surface)
