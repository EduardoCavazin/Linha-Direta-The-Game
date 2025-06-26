import pygame
import sys
from enum import Enum, auto
from src.world.gameWorld import GameWorld


WIDTH: int = 960
HEIGHT: int = 960
TARGET_FPS: int = 60

class GameState(Enum):
    """Estados possíveis para o jogo"""
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    MENU = auto()

class GameManager:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, fps: int = TARGET_FPS) -> None:
        pygame.init()
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Linha Direta - The Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.target_fps: int = fps
        
        # Usar o GameState em vez de boolean para controlar o estado do jogo
        self.state: GameState = GameState.RUNNING
        
        self.game_world: GameWorld = GameWorld(self.screen, self.clock, self.width, self.height)

    def toggle_pause(self) -> None:
        """Alterna entre os estados pausado e rodando"""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING

    def handle_events(self) -> None:
        # Processar eventos do sistema
        self._process_system_events()
        
        # Processar entrada do teclado
        self._process_keyboard_input()

    def _process_system_events(self) -> None:
        """Processa eventos do sistema como fechar o jogo"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.GAME_OVER
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == GameState.RUNNING:
                self.game_world.handle_player_mouse_click()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Tecla P para pausar
                    self.toggle_pause()

    def _process_keyboard_input(self) -> None:
        """Processa entrada do teclado - responsabilidade única de I/O"""
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.RUNNING:
            # Detectar múltiplas direções para movimento diagonal suave
            directions = []
            
            if keys[pygame.K_w]:
                directions.append("up")
            if keys[pygame.K_s]:
                directions.append("down")
            if keys[pygame.K_a]:
                directions.append("left")
            if keys[pygame.K_d]:
                directions.append("right")
            
            # Enviar todas as direções pressionadas para o GameWorld
            for direction in directions:
                self.game_world.handle_player_key_press(direction)
        
        # Ações do sistema
        if keys[pygame.K_ESCAPE]:
            self.state = GameState.GAME_OVER
    
    def _draw_pause_overlay(self) -> None:
        """Desenha um overlay quando o jogo está pausado"""
        # Criar uma superfície semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Preto com 50% de transparência
        
        # Desenhar o overlay
        self.screen.blit(overlay, (0, 0))
        
        # Criar texto de pausa
        try:
            font = pygame.font.Font("assets/fonts/techno_hideo.ttf", 64)
        except:
            font = pygame.font.Font(None, 64)
            
        pause_text = font.render("PAUSADO", True, (255, 255, 255))
        
        # Centralizar o texto
        text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        
        # Desenhar o texto
        self.screen.blit(pause_text, text_rect)

    def run(self) -> None:
        """Loop principal do jogo"""
        try:
            while self.state != GameState.GAME_OVER:
                # Calcular o delta time para atualizações consistentes
                delta_time: float = self.clock.tick(self.target_fps) / 1000.0
                
                # Processar eventos de entrada (em qualquer estado)
                self.handle_events()
                
                # Atualizar o jogo apenas se estiver rodando
                if self.state == GameState.RUNNING:
                    self.game_world.update(delta_time)
                
                # Renderizar o jogo
                self.game_world.render()
                
                # Renderizar overlay de pausa se necessário
                if self.state == GameState.PAUSED:
                    self._draw_pause_overlay()
                
                # Atualizar a tela
                pygame.display.flip()
        except Exception as e:
            print(f"Erro no jogo: {e}")
            # Poderia salvar o erro em um arquivo de log aqui
        finally:
            # Encerramento limpo, executado mesmo em caso de erro
            pygame.quit()
            sys.exit()