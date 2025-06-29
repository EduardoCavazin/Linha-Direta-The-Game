import pygame
from typing import List, Optional, Tuple
import math

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

    def _update_enemies(self) -> None:
        if not self.current_room or not self.current_room.enemies:
            return
        
        for enemy in self.current_room.enemies[:]: 
            if enemy.is_alive():
                # Atualizar comportamento do inimigo (IA simples por enquanto)
                # Futuramente pode incluir pathfinding, ataque, etc.
                pass
            else:
                self.current_room.enemies.remove(enemy)

    def _update_bullets(self) -> None:
        if not self.bullets:
            return
        
        dt = self.clock.get_time() / 1000.0
        
        for bullet in self.bullets[:]: 
            if not bullet.update(dt, self.width, self.height):
                self.bullets.remove(bullet)
                continue
            
            if self.current_room.check_collision((bullet.position.x, bullet.position.y), (2, 2)):
                self.bullets.remove(bullet)
                continue
            
            self._check_bullet_enemy_collision(bullet)

    def _check_bullet_enemy_collision(self, bullet) -> None:
        bullet_rect = bullet.hitbox
    
        for enemy in self.current_room.enemies[:]:
            enemy_rect = pygame.Rect(
                enemy.position.x,
                enemy.position.y,
                enemy.size[0],
                enemy.size[1]
            )
            
            if bullet_rect.colliderect(enemy_rect):
                enemy.take_damage(bullet.damage)
                
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                
                print(f"Inimigo atingido! Vida restante: {enemy.health}")
                break

    def _check_item_collisions(self) -> None:
        if not self.player or not self.current_room or not self.current_room.items:
            return
        
        player_rect = pygame.Rect(
            self.player.position.x,
            self.player.position.y,
            self.player.size[0],
            self.player.size[1]
        )
        
        for item in self.current_room.items[:]: 
            item_rect = pygame.Rect(
                item.position[0],
                item.position[1],
                item.size[0],
                item.size[1]
            )
            
            if player_rect.colliderect(item_rect):
                self._apply_item_effect(item)
                self.current_room.items.remove(item)
                print(f"Item coletado: {item.name}")

    def _apply_item_effect(self, item) -> None:
        if not self.player:
            return
        
        if hasattr(item, 'effect'):
            if item.effect == "health":
                if hasattr(item, 'value'):
                    self.player.health = min(self.player.health + item.value, 100)
                    print(f"Vida restaurada: +{item.value}")
            elif item.effect == "ammo":
                if hasattr(item, 'value'):
                    self.player.ammo += item.value
                    print(f" Munição coletada: +{item.value}")

    def _keep_player_in_bounds(self) -> None:
        if not self.player or not self.current_room:
            return
        
        hitbox_size = getattr(self.player, 'hitbox_size', self.player.size)
        
        room_width, room_height = self.current_room.size
        
        self.player.position.x = max(0, min(self.player.position.x, room_width - hitbox_size[0]))
        self.player.position.y = max(0, min(self.player.position.y, room_height - hitbox_size[1]))

    def _update_render_queue(self) -> None:
        self.render_queue.clear()
        
        if not self.current_room:
            return
        
        if self.player:
            self.render_queue.append(self.player)
        
        for enemy in self.current_room.enemies:
            if enemy.is_alive():
                self.render_queue.append(enemy)
        
        for item in self.current_room.items:
            self.render_queue.append(item)
        
        for door in self.current_room.doors:
            self.render_queue.append(door)
        
        for bullet in self.bullets:
            self.render_queue.append(bullet)
            
    def update(self, delta_time: float = None) -> None:
        if not self.current_room:
            return
        
        self._update_enemies()
        self._update_bullets()
        
        self._check_item_collisions()
        
        self._update_render_queue()
    

    def process_player_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        if not self.player or not self.current_room:
            return
        
        delta_time = self.clock.get_time() / 1000.0
        
        obstacles = self._get_collision_obstacles()
        screen_bounds = (self.width, self.height)
        
        directions = []
        if keys[pygame.K_w]: directions.append("up")
        if keys[pygame.K_s]: directions.append("down")
        if keys[pygame.K_a]: directions.append("left")
        if keys[pygame.K_d]: directions.append("right")
        
        for direction in directions:
            self.player.move(direction, delta_time, obstacles, screen_bounds)
        
        if keys[pygame.K_r]:
            self.player.reload()

    def process_player_mouse(self, mouse_pos: Tuple[int, int]) -> None:
        if not self.player:
            return
        
        self.player.rotate_to_mouse(mouse_pos)
        
        bullet = self.player.shoot()
        if bullet:
            self.bullets.append(bullet)

    def _get_collision_obstacles(self) -> List:
        obstacles = []
        if self.current_room:
            obstacles.extend(self.current_room.get_wall_rects())
        return obstacles

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
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        self.hud.draw()