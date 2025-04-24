import pygame
import sys
from src.world.gameWorld import GameWorld


class GameManager:
    def __init__(self, width: int = 800, height: int = 600):
        """
        Inicializa o gerenciador do jogo.
        
        Args:
            width (int): Largura da janela do jogo
            height (int): Altura da janela do jogo
        """
        pygame.init()
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Linha Direta - The Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        
        # Inicializa o mundo do jogo
        self.game_world: GameWorld = GameWorld(self.screen, self.clock, self.width, self.height)

    def handle_events(self) -> None:
        """Gerencia os eventos do jogo, como entradas do teclado e mouse"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.game_world.player_shoot()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.game_world.move_player("up")
        if keys[pygame.K_s]:
            self.game_world.move_player("down")
        if keys[pygame.K_a]:
            self.game_world.move_player("left")
        if keys[pygame.K_d]:
            self.game_world.move_player("right")
        if keys[pygame.K_ESCAPE]:
            self.running = False

    def run(self) -> None:
        """Inicia o loop principal do jogo"""
        while self.running:
            delta_time: float = self.clock.tick(60) / 1000.0
            
            # Gerencia eventos
            self.handle_events()
            
            # Atualiza o estado do jogo
            self.game_world.update(delta_time)
            
            # Renderiza o jogo
            self.game_world.render()
            
            # Atualiza a tela
            pygame.display.flip()

        # Finaliza o pygame e encerra o programa quando o loop termina
        pygame.quit()
        sys.exit()