from typing import List, Optional, Any, Tuple

import pygame

from src.model.objects.bullet import Bullet

class Room:
    def __init__(
        self,
        id: str,
        size: Tuple[int, int],
        objects: List[Any],
        enemies: List[Any],
        items: List[Any],
        doors: List[Any],
        player: Optional[Any],
        cleared: bool,
        visited: bool,
        background: pygame.Surface,
        collision_matrix: Optional[List[List[bool]]] = None
    ) -> None:
        self.id: str = id
        self.size: Tuple[int, int] = size
        self.objects: List[Any] = objects
        self.enemies: List[Any] = enemies
        self.items: List[Any] = items
        self.doors: List[Any] = doors
        self.player: Optional[Any] = player
        self.cleared: bool = cleared
        self.visited: bool = visited
        self.background: pygame.Surface = background
        self.collision_matrix = collision_matrix or []
        self.tile_size = (32, 32)  # Tamanho padrão do tile
        
        # Debug: Verificar se a matriz foi recebida
        if self.collision_matrix:
            blocked_count = sum(row.count(True) for row in self.collision_matrix)
            print(f"Room '{self.id}' criada com {blocked_count} tiles de colisão")
        else:
            print(f"Room '{self.id}' criada SEM matriz de colisão!")

    def spawn_enemy(self, enemy: Any) -> None:
        self.enemies.append(enemy)
        
    def spawn_item(self, item: Any) -> None:
        self.items.append(item)
    
    def spawn_door(self, door: Any) -> None:
        self.doors.append(door)
    
    def spawn_object(self, obj: Any) -> None:
        self.objects.append(obj)
        
    def spawn_player(self, player: Any) -> None:
        self.player = player 
        
    def clear_room(self) -> None:
        self.cleared = True
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        for item in self.items:
            item.spawn()
        for door in self.doors:
            door.open()

    def check_player_door_collision(self, game_map: Any) -> Any:
        for door in self.doors:
            if self.player.hitbox.colliderect(door.hitbox) and not door.locked:
                print("Entrando na próxima sala...")
                next_room = game_map.get_next_room()
                if next_room:
                    next_room.spawn_player(self.player)
                    self.player = None  
                    return next_room
        return self 
    
    def handle_bullet_collisions(self, bullets: List[Bullet]) -> None:
        for bullet in bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.hitbox.colliderect(enemy.hitbox):
                    enemy.take_damage(bullet.damage)
                    bullets.remove(bullet)
                    if not enemy.is_alive():
                        enemy.set_dead_state()
                    break

    def check_collision(self, position: Tuple[float, float], hitbox_size: Tuple[int, int]) -> bool:
        if not self.collision_matrix or len(self.collision_matrix) == 0:
            print("Aviso: Nenhuma matriz de colisão disponível!")
            return False
        
        # Usar hitbox menor para movimento mais fluido
        hitbox_width = hitbox_size[0] * 0.7
        hitbox_height = hitbox_size[1] * 0.7
        
        # Calcular as bordas da hitbox
        left = position[0]
        right = position[0] + hitbox_width
        top = position[1] 
        bottom = position[1] + hitbox_height
        
        # Converter para coordenadas de tile
        tile_left = max(0, int(left / self.tile_size[0]))
        tile_right = min(len(self.collision_matrix[0]) - 1, int(right / self.tile_size[0]))
        tile_top = max(0, int(top / self.tile_size[1]))
        tile_bottom = min(len(self.collision_matrix) - 1, int(bottom / self.tile_size[1]))
        
        # Verificar apenas os tiles necessários
        for y in range(tile_top, tile_bottom + 1):
            for x in range(tile_left, tile_right + 1):
                if y < len(self.collision_matrix) and x < len(self.collision_matrix[0]):
                    if self.collision_matrix[y][x]:
                        return True
    
        return False
    
    def render_collision_debug(self, surface: pygame.Surface):
        if not self.collision_matrix:
            return
            
        for y, row in enumerate(self.collision_matrix):
            for x, blocked in enumerate(row):
                if blocked:
                    rect = pygame.Rect(
                        x * self.tile_size[0],
                        y * self.tile_size[1],
                        self.tile_size[0],
                        self.tile_size[1]
                    )
                    pygame.draw.rect(surface, (255, 0, 0, 128), rect, 1)
