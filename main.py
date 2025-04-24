import pygame
from src.core.gameManager import GameManager

def main():
    """Função principal que inicializa e executa o jogo"""
    game = GameManager()
    game.run()

if __name__ == "__main__":
    main()
