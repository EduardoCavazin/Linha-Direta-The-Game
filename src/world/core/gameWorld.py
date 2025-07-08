import pygame
from typing import List, Tuple, Optional
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.bullet import Bullet
from src.world.core.map import Map
from src.world.core.room import Room


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int) -> None:
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        
        self.map: Map = Map()
        
        self.current_room: Optional[Room] = None
        self.player: Optional[Player] = None
        self.bullets: List[Bullet] = []
        self.render_queue: List = []
        
        self._initialize_world()
    
    def _initialize_world(self) -> None:
        if self.map.rooms:
            self.current_room = self.map.rooms[0]
            self._spawn_player()
        else:
            print("ERRO: Nenhuma sala carregada!")
    
    def _spawn_player(self) -> None:
        spawn_pos = self.current_room.spawn_position if self.current_room else (100, 100)
        
        from src.model.objects.weapon import Weapon
        weapon = Weapon("pistol", "Pistola", 25, 12)
        
        self.player = Player(
            id="player_main",
            name="Jogador",
            position=spawn_pos,
            size=(32, 32),
            speed=200,
            health=100,
            weapon=weapon,
            ammo=12,
            status="alive"
        )
        
    # ==========================================
    # INPUT PROCESSING 
    # ==========================================
    
    def process_player_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        if not self.player or not self.current_room:
            return
        
        delta_time = self.clock.get_time() / 1000.0
        obstacles = self.current_room.get_wall_rects()
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
    
    def process_player_mouse_movement(self, mouse_pos: Tuple[int, int]) -> None:
        if not self.player:
            return
        
        self.player.rotate_to_mouse(mouse_pos)

    def process_player_mouse(self, mouse_pos: Tuple[int, int]) -> None:
        if not self.player:
            return
        
        bullet = self.player.shoot()
        if bullet:
            self.bullets.append(bullet)

    # ==========================================
    # UPDATE LOGIC
    # ==========================================
    
    def update(self, delta_time: float = None) -> None:
        if not self.current_room:
            return
        
        if self.player:
            self.player.update(delta_time)
    
        self._update_enemies()
        self._update_bullets()
        self._check_item_collisions()
        
        self._update_render_queue()
    
    def _update_enemies(self) -> None:
        if not self.player or not self.current_room:
            return
        
        player_pos = self.player.position
        
        for enemy in self.current_room.enemies[:]:
            if enemy.is_alive():
                enemy.update(player_pos)
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
        
        self.current_room.handle_bullet_collisions(self.bullets)
    
    def _check_item_collisions(self) -> None:
        if not self.player or not self.current_room:
            return
        
        player_rect = pygame.Rect(self.player.position[0], self.player.position[1], 
                                self.player.size[0], self.player.size[1])
        
        for item in self.current_room.items[:]:
            if player_rect.colliderect(item.hitbox):
                if item.effect == "heal":
                    self.player.heal(item.value)
                elif item.effect == "ammo":
                    self.player.add_ammo(item.value)
                
                self.current_room.items.remove(item)

    # ==========================================
    # RENDERING 
    # ==========================================
    
    def _update_render_queue(self) -> None:
        self.render_queue.clear()
        
        if not self.current_room:
            return
        
        if self.player:
            self.render_queue.append(self.player)
        
        for enemy in self.current_room.enemies:
            if enemy.is_alive():
                self.render_queue.append(enemy)
        
        self.render_queue.extend(self.current_room.items)
        self.render_queue.extend(self.current_room.doors)
        self.render_queue.extend(self.bullets)
        
    def render(self) -> None:
        if self.current_room and self.current_room.background:
            self.screen.blit(self.current_room.background, (0, 0))
        else:
            self.screen.fill((88, 71, 71))
        
        for obj in self.render_queue:
            obj.draw(self.screen)
        

    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    
    def change_room(self, room_index: int) -> None:
        if 0 <= room_index < len(self.map.rooms):
            self.current_room = self.map.rooms[room_index]
            if self.player:
                self.player.position = self.current_room.spawn_position
        else:
            print(f"Sala {room_index} não existe")
    
    def get_current_room_info(self) -> dict:
        if not self.current_room:
            return {}
        
        return {
            "id": self.current_room.id,
            "size": self.current_room.size,
            "enemies": len(self.current_room.enemies),
            "items": len(self.current_room.items),
            "doors": len(self.current_room.doors)
        }
    
    def cleanup(self) -> None:
        self.bullets.clear()
        self.render_queue.clear()
        print("GameWorld limpo")
