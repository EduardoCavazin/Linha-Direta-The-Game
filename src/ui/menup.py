import sys
import pygame
import os
from PIL import Image, ImageSequence

pygame.init()

screen_width = 1280
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Main Menu")

white = (255, 255, 255)
black = (0, 0, 0)

font_path = os.path.join(os.path.dirname(
    __file__), '..', '..', 'assets', 'fonts', 'Neutrons.ttf')
font = pygame.font.Font(font_path, 74)

gif_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'ui', 'menu', 'backgroundGif.gif')
gif = Image.open(gif_path)
frames = [pygame.transform.scale(pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode), (screen_width, screen_height)) for frame in ImageSequence.Iterator(gif)]
frame_count = len(frames)
frame_index = 0

title_rect = None
option1_rect = None
option2_rect = None
option3_rect = None

def draw_rounded_background(surface, rect, color, radius):
    transparent_background = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(transparent_background, color, transparent_background.get_rect(), border_radius=radius)
    surface.blit(transparent_background, (rect.x - 10, rect.y - 5))

def show_menu():
    global frame_index, title_rect, option1_rect, option2_rect, option3_rect
    screen.blit(frames[frame_index], (0, 0))
    frame_index = (frame_index + 1) % frame_count

    title = font.render("Linha Direta", True, white)
    option1 = font.render("Start", True, white)
    option2 = font.render("Settings", True, white)
    option3 = font.render("Exit", True, white)

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

def main():
    clock = pygame.time.Clock()
    while True:
        show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if option1_rect.collidepoint(x, y):
                    print("Starting the game...")
                elif option2_rect.collidepoint(x, y):
                    print("Opening settings...")
                elif option3_rect.collidepoint(x, y):
                    print("Exiting...")
                    pygame.quit()
                    sys.exit()
        clock.tick(10)

if __name__ == "__main__":
    main()
