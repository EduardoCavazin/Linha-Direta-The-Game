import sys
import pygame
import os
from PIL import Image, ImageSequence
from typing import Optional

pygame.init()

# Configurações da tela
screen_width: int = 1280
screen_height: int = 800
screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Main Menu")

white: tuple = (255, 255, 255)
black: tuple = (0, 0, 0)

# Caminho para a fonte
font_path: str = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'fonts', 'Neutrons.ttf')
font: pygame.font.Font = pygame.font.Font(font_path, 74)

# Caminho para o background GIF e processamento dos frames
gif_path: str = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'ui', 'menu', 'backgroundGif.gif')
gif: Image.Image = Image.open(gif_path)
frames: list[pygame.Surface] = [
    pygame.transform.scale(
        pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode),
        (screen_width, screen_height)
    ) for frame in ImageSequence.Iterator(gif)
]
frame_count: int = len(frames)
frame_index: int = 0

# Variáveis globais para os retângulos dos elementos de interface
title_rect: Optional[pygame.Rect] = None
option1_rect: Optional[pygame.Rect] = None
option2_rect: Optional[pygame.Rect] = None
option3_rect: Optional[pygame.Rect] = None

def draw_rounded_background(surface: pygame.Surface, rect: pygame.Rect, color: tuple, radius: int) -> None:
    transparent_background: pygame.Surface = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(transparent_background, color, transparent_background.get_rect(), border_radius=radius)
    surface.blit(transparent_background, (rect.x - 10, rect.y - 5))

def show_menu() -> None:
    global frame_index, title_rect, option1_rect, option2_rect, option3_rect
    screen.blit(frames[frame_index], (0, 0))
    frame_index = (frame_index + 1) % frame_count

    title: pygame.Surface = font.render("Linha Direta", True, white)
    option1: pygame.Surface = font.render("Start", True, white)
    option2: pygame.Surface = font.render("Settings", True, white)
    option3: pygame.Surface = font.render("Exit", True, white)

    title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 150))
    option1_rect = option1.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    option2_rect = option2.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
    option3_rect = option3.get_rect(center=(screen_width // 2, screen_height // 2 + 150))

    for rect in [title_rect, option1_rect, option2_rect, option3_rect]:
        draw_rounded_background(screen, rect, (0, 0, 0, 128), 10)

    screen.blit(title, title_rect)
    screen.blit(option1, option1_rect)
    screen.blit(option2, option2_rect)
    screen.blit(option3, option3_rect)

    pygame.display.flip()

def main() -> None:
    clock: pygame.time.Clock = pygame.time.Clock()
    while True:
        show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if option1_rect is not None and option1_rect.collidepoint(x, y):
                    print("Starting the game...")
                elif option2_rect is not None and option2_rect.collidepoint(x, y):
                    print("Opening settings...")
                elif option3_rect is not None and option3_rect.collidepoint(x, y):
                    print("Exiting...")
                    pygame.quit()
                    sys.exit()
        clock.tick(10)

if __name__ == "__main__":
    main()
