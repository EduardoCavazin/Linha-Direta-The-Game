import pygame
from typing import List, Optional

from src.ui.hud import Hud
from src.world.map import Map


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int):
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        
        self.game_map: Map = Map("src/world/rooms")
        self.game_map.generate_seed_test()  # Usar apenas Mapa1 para teste
        self.current_room = self.game_map.current_room
        self.player = self.current_room.player
        
        self.player.screen_width = self.width
        self.player.screen_height = self.height
        
        self.bullets: List = []
        
        self.hud: Hud = Hud(self.screen, self.player, self.clock)
        
        self.render_queue: List = []

    def handle_player_mouse_click(self) -> None:
        bullet = self.player.handle_mouse_click()
        if bullet:
            self.bullets.append(bullet)

    def handle_player_key_press(self, key: str) -> None:
        delta_time: float = self.clock.get_time() / 1000.0
        
        live_enemies = [enemy for enemy in self.current_room.enemies if enemy.is_alive()]
        
        self.player.handle_key_press(key, delta_time, obstacles=live_enemies)

    def update(self, delta_time: float) -> None:
        self.player.update(delta_time)
        self.player.calculate_rotation()
        
        for bullet in self.bullets[:]:
            if not bullet.update(delta_time, screen_width=self.width, screen_height=self.height):
                self.bullets.remove(bullet)
        
        self.current_room.handle_bullet_collisions(self.bullets)
        
        self._update_render_queue()
        
        self._check_item_collisions()
        
        self._check_room_transition()

    def _update_render_queue(self) -> None:
        self.render_queue = []
        
        for enemy in self.current_room.enemies[:]:
            if not enemy.is_alive():
                self.render_queue.append(enemy)
            else:
                enemy.update(self.player.position)
                self.render_queue.append(enemy)
        
        for bullet in self.bullets:
            self.render_queue.append(bullet)
        
        self.render_queue.append(self.player)
    
    def _check_item_collisions(self) -> None:
        for item in self.current_room.items[:]:
            if self.player.hitbox.colliderect(item.hitbox):
                item.use(self.player)
                self.current_room.items.remove(item)
                print(f"Usou {item.name}!")
    
    def _check_room_transition(self) -> None:
        new_room = self.current_room.check_player_door_collision(self.game_map)
        if new_room is not self.current_room:
            self.current_room = new_room
            self.player = self.current_room.player
            self.player.screen_width = self.width
            self.player.screen_height = self.height
            self.hud.player = self.player
            self.bullets = []

    def render(self) -> None:
        if self.current_room.background:
            self.screen.blit(self.current_room.background, (0, 0))
        else:
            self.screen.fill((88, 71, 71))
        
        for obj in self.render_queue:
            obj.draw(self.screen)
        
        for door in self.current_room.doors:
            pygame.draw.rect(self.screen, (100, 100, 255), door.hitbox)
        
        for item in self.current_room.items:
            item.draw(self.screen)
        
        self.hud.draw()