import pygame
from src.core.gameManager import GameManager
from src.ui.menu import run_menu, screen_width, screen_height
from src.core.screenUtils import get_screen_info

def main():
    """Funcao principal - executa menu e depois o jogo"""
    pygame.init()

    # Mostrar informacoes da tela para debug
    screen_info = get_screen_info()
    print(f"Resolucao da tela: {screen_info['desktop_size']}")
    print(f"Tamanho do jogo: {screen_width}x{screen_height}")

    # Mostrar menu principal
    action = run_menu()

    if action == "start":
        # Iniciar o jogo com as mesmas dimensoes do menu
        game = GameManager(width=screen_width, height=screen_height)
        game.run()

    pygame.quit()

if __name__ == "__main__":
    main()
