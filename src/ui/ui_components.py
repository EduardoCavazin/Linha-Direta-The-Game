import pygame
import random
import math
from typing import Tuple

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HOVER_COLOR = (100, 200, 255)
SELECTED_COLOR = (255, 220, 100)
GOLD = (255, 215, 0)

class Particle:
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
    transparent_background = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(transparent_background, color, transparent_background.get_rect(), border_radius=radius)
    surface.blit(transparent_background, (rect.x - 10, rect.y - 5))

def create_particle_system(screen_width: int, screen_height: int, count: int = 50) -> list:
    return [Particle(screen_width, screen_height) for _ in range(count)]

def update_and_draw_particles(particles: list, surface: pygame.Surface):
    for particle in particles:
        particle.update()
        particle.draw(surface)
