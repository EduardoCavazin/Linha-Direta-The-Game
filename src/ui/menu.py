import sys
import pygame
import os
from PIL import Image, ImageSequence
from src.core.utils import load_image
from src.core.screenUtils import get_optimal_screen_size, center_window

pygame.init()

# Calcular tamanho ideal da tela
screen_width, screen_height = get_optimal_screen_size(preferred_width=950, preferred_height=800)

# Centralizar janela
center_window(screen_width, screen_height)
screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Main Menu")

white: tuple = (255, 255, 255)
black: tuple = (0, 0, 0)

base_path = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(base_path, "../.."))
font_path: str = os.path.join(project_root, 'assets', 'fonts', 'Neutrons.ttf')
gif_path: str = os.path.join(project_root, 'assets', 'ui', 'menu', 'backgroundGif.gif')

try:
    font: pygame.font.Font = pygame.font.Font(font_path, 74)
except Exception as e:
    print(f"Erro ao carregar fonte: {e}")
    font: pygame.font.Font = pygame.font.Font(None, 74) 

try:
    gif: Image.Image = Image.open(gif_path)
    frames: list[pygame.Surface] = [
        pygame.transform.scale(
            pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode),
            (screen_width, screen_height)
        ) for frame in ImageSequence.Iterator(gif)
    ]
    frame_count: int = len(frames)
except Exception as e:
    print(f"Erro ao carregar GIF: {e}")
    frames: list[pygame.Surface] = [pygame.Surface((screen_width, screen_height))]
    frames[0].fill((50, 50, 75))  
    frame_count: int = 1

frame_index: int = 0

title_rect = None
start_rect = None
exit_rect = None

def draw_rounded_background(surface: pygame.Surface, rect: pygame.Rect, color: tuple, radius: int) -> None:
    transparent_background: pygame.Surface = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(transparent_background, color, transparent_background.get_rect(), border_radius=radius)
    surface.blit(transparent_background, (rect.x - 10, rect.y - 5))

def show_menu() -> None:
    """Renderiza o menu"""
    global frame_index, title_rect, start_rect, exit_rect

    # Renderizar background animado
    screen.blit(frames[frame_index], (0, 0))
    frame_index = (frame_index + 1) % frame_count

    # Criar textos
    title: pygame.Surface = font.render("Linha Direta", True, white)
    start: pygame.Surface = font.render("Iniciar", True, white)
    exit: pygame.Surface = font.render("Sair", True, white)

    # Instrucoes de controle
    small_font = pygame.font.Font(None, 36)
    instructions = small_font.render("Enter/Espaco: Iniciar | Esc: Sair", True, (200, 200, 200))

    # Posicionar elementos
    title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 120))
    start_rect = start.get_rect(center=(screen_width // 2, screen_height // 2 - 20))
    exit_rect = exit.get_rect(center=(screen_width // 2, screen_height // 2 + 80))
    instructions_rect = instructions.get_rect(center=(screen_width // 2, screen_height // 2 + 180))

    # Desenhar backgrounds dos textos
    for rect in [title_rect, start_rect, exit_rect]:
        draw_rounded_background(screen, rect, (0, 0, 0, 128), 10)
    draw_rounded_background(screen, instructions_rect, (0, 0, 0, 100), 5)

    # Desenhar textos
    screen.blit(title, title_rect)
    screen.blit(start, start_rect)
    screen.blit(exit, exit_rect)
    screen.blit(instructions, instructions_rect)

    pygame.display.flip()
    return None

def run_menu() -> str:
    """Executa o menu e retorna a acao escolhida pelo usuario"""
    clock: pygame.time.Clock = pygame.time.Clock()
    while True:
        # Processar todos os eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "start"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Obter as posicoes dos botoes da funcao show_menu
                if start_rect and start_rect.collidepoint(x, y):
                    return "start"
                elif exit_rect and exit_rect.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()

        # Renderizar o menu
        show_menu()
        clock.tick(10)

def main() -> None:
    """Funcao principal para testar o menu isoladamente"""
    action = run_menu()
    if action == "start":
        print("Iniciando jogo...")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
