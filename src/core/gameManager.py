import pygame
import sys
from src.world.gameWorld import GameWorld


class GameManager:
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Linha Direta - The Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        
        self.game_world: GameWorld = GameWorld(self.screen, self.clock, self.width, self.height)

    def handle_events(self) -> None:
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
        while self.running:
            delta_time: float = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            
            self.game_world.update(delta_time)
            
            self.game_world.render()
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()