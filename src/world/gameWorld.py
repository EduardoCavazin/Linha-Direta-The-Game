import pygame
from typing import List

from src.ui.hud import Hud
from src.world.map import Map


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int):
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        
        self.game_map: Map = Map("src/world/rooms")
        self.game_map.generate_seed(1)
        self.current_room = self.game_map.current_room
        self.player = self.current_room.player
        
        self.bullets: List = []
        
        self.hud: Hud = Hud(self.screen, self.player, self.clock)
        
        self.render_queue: List = []

    def player_shoot(self) -> None:
        bullet = self.player.shoot()
        if bullet:
            self.bullets.append(bullet)

    def move_player(self, direction: str) -> None:
        delta_time: float = self.clock.get_time() / 1000.0
        
        live_enemies = [enemy for enemy in self.current_room.enemies if enemy.is_alive()]
        
        self.player.move(
            direction, 
            delta_time, 
            obstacles=live_enemies, 
            screen_width=self.width, 
            screen_height=self.height
        )

    def update(self, delta_time: float) -> None:
        self.player.update_animation(delta_time)
        self.player.calculate_rotation()
        
        for bullet in self.bullets[:]:
            if not bullet.update(delta_time, screen_width=self.width, screen_height=self.height):
                self.bullets.remove(bullet)
        
        self.current_room.handle_bullet_collisions(self.bullets)
        
        self.render_queue = []
        for enemy in self.current_room.enemies[:]:
            if not enemy.is_alive():
                self.render_queue.append(enemy)
                print(f"{enemy.name} foi derrotado!")
            else:
                enemy.update(self.player.position)
                self.render_queue.append(enemy)
        
        for bullet in self.bullets:
            self.render_queue.append(bullet)
        
        self.render_queue.append(self.player)
        
        for item in self.current_room.items[:]:
            if self.player.hitbox.colliderect(item.hitbox):
                item.use(self.player)
                self.current_room.items.remove(item)
                print(f"Usou {item.name}!")
        
        new_room = self.current_room.check_player_door_collision(self.game_map)
        if new_room is not self.current_room:
            self.current_room = new_room
            self.player = self.current_room.player
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