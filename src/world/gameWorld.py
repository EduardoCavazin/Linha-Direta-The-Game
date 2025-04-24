import pygame
from typing import List

from src.ui.hud import Hud
from src.world.map import Map


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int):
        """
        Inicializa o mundo do jogo.
        
        Args:
            screen (pygame.Surface): A superfície de renderização do jogo
            clock (pygame.time.Clock): O relógio do jogo para controle de tempo
            width (int): Largura da tela
            height (int): Altura da tela
        """
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        
        # Inicializa o mapa e a sala atual
        self.game_map: Map = Map("src/world/rooms")
        self.game_map.generate_seed(1)
        self.current_room = self.game_map.current_room
        self.player = self.current_room.player
        
        # Lista de projéteis
        self.bullets: List = []
        
        # HUD do jogo
        self.hud: Hud = Hud(self.screen, self.player, self.clock)
        
        # Lista de objetos a serem renderizados
        self.render_queue: List = []

    def player_shoot(self) -> None:
        """Faz o jogador atirar e adiciona o projétil à lista de projéteis"""
        bullet = self.player.shoot()
        if bullet:
            self.bullets.append(bullet)

    def move_player(self, direction: str) -> None:
        """
        Move o jogador na direção especificada.
        
        Args:
            direction (str): A direção para mover o jogador ('up', 'down', 'left', 'right')
        """
        delta_time: float = self.clock.get_time() / 1000.0  # Tempo desde o último frame em segundos
        self.player.move(
            direction, 
            delta_time, 
            obstacles=self.current_room.enemies, 
            screen_width=self.width, 
            screen_height=self.height
        )

    def update(self, delta_time: float) -> None:
        """
        Atualiza todos os elementos do jogo.
        
        Args:
            delta_time (float): Tempo desde o último frame em segundos
        """
        # Atualiza o jogador
        self.player.update_animation(delta_time)
        self.player.calculate_rotation()
        
        # Atualiza os projéteis
        for bullet in self.bullets[:]:
            if not bullet.update(delta_time, screen_width=self.width, screen_height=self.height):
                self.bullets.remove(bullet)
        
        # Detecta colisões de projéteis
        self.current_room.handle_bullet_collisions(self.bullets)
        
        # Atualiza os inimigos
        self.render_queue = []
        for enemy in self.current_room.enemies[:]:
            if not enemy.is_alive():
                self.current_room.enemies.remove(enemy)
                print(f"{enemy.name} foi derrotado!")
            else:
                enemy.update(self.player.position)
                self.render_queue.append(enemy)
        
        # Adiciona os projéteis à fila de renderização
        for bullet in self.bullets:
            self.render_queue.append(bullet)
        
        # Adiciona o jogador à fila de renderização
        self.render_queue.append(self.player)
        
        # Checa colisão com itens
        for item in self.current_room.items[:]:
            if self.player.hitbox.colliderect(item.hitbox):
                item.use(self.player)
                self.current_room.items.remove(item)
                print(f"Usou {item.name}!")
        
        # Verifica transição de sala
        new_room = self.current_room.check_player_door_collision(self.game_map)
        if new_room is not self.current_room:
            self.current_room = new_room
            self.player = self.current_room.player
            self.hud.player = self.player
            self.bullets = []  # Limpa os projéteis ao mudar de sala

    def render(self) -> None:
        """Renderiza todos os elementos do jogo"""
        # Desenha o fundo
        self.screen.fill((88, 71, 71))
        
        # Renderiza todos os objetos na fila de renderização
        for obj in self.render_queue:
            obj.draw(self.screen)
        
        # Renderiza portas e itens
        for door in self.current_room.doors:
            pygame.draw.rect(self.screen, (100, 100, 255), door.hitbox)
        for item in self.current_room.items:
            pygame.draw.rect(self.screen, (0, 255, 0), item.hitbox)
        
        # Desenha a HUD
        self.hud.draw()