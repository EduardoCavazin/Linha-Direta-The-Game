import pygame
from src.core.gameManager import GameManager
from src.ui.menu import run_menu, screen_width, screen_height
from src.ui.leaderboardScreen import run_leaderboard_screen
from src.core.screenUtils import get_screen_info

def main():
    pygame.init()

    screen_info = get_screen_info()
    print(f"Resolucao da tela: {screen_info['desktop_size']}")
    print(f"Tamanho do jogo: {screen_width}x{screen_height}")

    while True:
        action = run_menu()

        if action == "start":
            game = GameManager(width=screen_width, height=screen_height)
            game.run()

        elif action == "leaderboard":
            leaderboard_action = run_leaderboard_screen(screen_width, screen_height)

        else:
            break

    pygame.quit()

if __name__ == "__main__":
    main()
