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
        collision_matrix: Optional[List[List[bool]]] = None,
        fire_matrix: Optional[List[List[bool]]] = None,
        animated_tiles: Optional[dict] = None,
        tile_size: Tuple[int, int] = (32, 32),
        tmx_objects_data: Optional[List[dict]] = None,
        tmx_loader: Optional[Any] = None
    ) -> None:
        self.id: str = id
        self.size: Tuple[int, int] = size
        self.background: pygame.Surface = background
        self.tile_size: Tuple[int, int] = tile_size
        
        self.cleared: bool = cleared
        self.visited: bool = visited
        
        self.objects: List[Any] = objects or []
        self.enemies: List[Any] = enemies or []
        self.items: List[Any] = items or []
        self.doors: List[Any] = doors or []
        
        self.collision_matrix: Optional[List[List[bool]]] = collision_matrix
        self.fire_matrix: Optional[List[List[bool]]] = fire_matrix
        self.animated_tiles: dict = animated_tiles or {}
        self._wall_rects_cache: Optional[List[pygame.Rect]] = None
        self._fire_rects_cache: Optional[List[pygame.Rect]] = None
        
        # Animation state tracking
        self.animation_time: float = 0.0
        self.current_tile_frames: dict = {}  # tile_gid -> current_frame_index
        self.tmx_loader = tmx_loader  # Keep reference for background updates
        
        self.tmx_objects_data = tmx_objects_data
        self.spawn_position: Tuple[float, float] = self._extract_spawn_position(player)
        
    def _extract_spawn_position(self, player: Optional[Any]) -> Tuple[float, float]:
        if self.tmx_objects_data:
            for obj in self.tmx_objects_data:
                if obj.get("name") == "Player":
                    spawn_x = obj.get("x", 100.0)
                    spawn_y = obj.get("y", 100.0)
                    print(f" Spawn do TMX encontrado: ({spawn_x}, {spawn_y})")
                    return (spawn_x, spawn_y)
        
        if player and hasattr(player, 'position'):
            return player.position
            
        return (100.0, 100.0)

    # ==========================================
    # COLLISION SYSTEM
    # ==========================================
    
    def check_collision(self, position: Tuple[float, float], hitbox_size: Tuple[int, int]) -> bool:
        if not self.collision_matrix:
            return False
        
        padding = 0.8  
        hitbox_width = hitbox_size[0] * padding
        hitbox_height = hitbox_size[1] * padding
        
        left = position[0]
        right = position[0] + hitbox_width
        top = position[1]
        bottom = position[1] + hitbox_height
        
        return self._check_tiles_in_area(left, right, top, bottom)

    def _check_tiles_in_area(self, left: float, right: float, top: float, bottom: float) -> bool:
        tile_left = max(0, int(left // self.tile_size[0]))
        tile_right = min(len(self.collision_matrix[0]) - 1, int(right // self.tile_size[0]))
        tile_top = max(0, int(top // self.tile_size[1]))
        tile_bottom = min(len(self.collision_matrix) - 1, int(bottom // self.tile_size[1]))
        
        for y in range(tile_top, tile_bottom + 1):
            for x in range(tile_left, tile_right + 1):
                if (0 <= y < len(self.collision_matrix) and 
                    0 <= x < len(self.collision_matrix[0]) and
                    self.collision_matrix[y][x]):
                    return True
        
        return False

    def get_wall_rects(self) -> List[pygame.Rect]:
        if self._wall_rects_cache is not None:
            return self._wall_rects_cache
        
        wall_rects = []
        if not self.collision_matrix:
            return wall_rects
        
        for y, row in enumerate(self.collision_matrix):
            for x, blocked in enumerate(row):
                if blocked:
                    rect = pygame.Rect(
                        x * self.tile_size[0],
                        y * self.tile_size[1],
                        self.tile_size[0],
                        self.tile_size[1]
                    )
                    wall_rects.append(rect)
        
        self._wall_rects_cache = wall_rects
        return wall_rects

    def invalidate_collision_cache(self) -> None:
        self._wall_rects_cache = None
        self._fire_rects_cache = None
    
    def get_fire_rects(self) -> List[pygame.Rect]:
        """Get fire damage zone rectangles for damage checking"""
        if self._fire_rects_cache is not None:
            return self._fire_rects_cache
            
        fire_rects = []
        if not self.fire_matrix:
            return fire_rects
            
        for y, row in enumerate(self.fire_matrix):
            for x, is_fire in enumerate(row):
                if is_fire:
                    fire_rect = pygame.Rect(
                        x * self.tile_size[0],
                        y * self.tile_size[1],
                        self.tile_size[0],
                        self.tile_size[1]
                    )
                    fire_rects.append(fire_rect)
        
        self._fire_rects_cache = fire_rects
        return fire_rects
    
    def check_fire_damage(self, entity_rect: pygame.Rect) -> bool:
        """Check if entity is touching fire zones - returns True if taking damage"""
        fire_rects = self.get_fire_rects()
        for fire_rect in fire_rects:
            if entity_rect.colliderect(fire_rect):
                return True
        return False
    
    def update_tile_animations(self, delta_time: float) -> None:
        """Update animated tile frames based on elapsed time"""
        if not self.animated_tiles:
            return
            
        self.animation_time += delta_time * 1000  # Convert to milliseconds
        
        for tile_gid, animation_data in self.animated_tiles.items():
            frames = animation_data["frames"]
            total_duration = animation_data["total_duration"]
            
            # Calculate current time in animation cycle
            cycle_time = self.animation_time % total_duration
            
            # Find which frame should be showing
            elapsed = 0
            current_frame_index = 0
            
            for i, frame in enumerate(frames):
                elapsed += frame["duration"]
                if cycle_time < elapsed:
                    current_frame_index = i
                    break
            
            # Store current frame for this tile
            self.current_tile_frames[tile_gid] = current_frame_index
    
    def get_current_tile_gid(self, original_gid: int) -> int:
        """Get the current tile GID for animated tiles, or original GID for static tiles"""
        if original_gid in self.animated_tiles:
            frame_index = self.current_tile_frames.get(original_gid, 0)
            animation_data = self.animated_tiles[original_gid]
            frames = animation_data["frames"]
            
            if frame_index < len(frames):
                # Get the actual tile GID for this frame
                frame_tileid = frames[frame_index]["tileid"]
                tileset_firstgid = animation_data["tileset_firstgid"]
                return tileset_firstgid + frame_tileid
        
        return original_gid
    
    def needs_background_update(self) -> bool:
        """Check if background needs updating due to animated tiles"""
        return len(self.animated_tiles) > 0
    
    def update_background(self) -> None:
        """Update background with current animated tile frames"""
        if self.animated_tiles and self.tmx_loader:
            # Create mapping of original GID to current GID
            current_tile_mapping = {}
            for original_gid in self.animated_tiles:
                current_tile_mapping[original_gid] = self.get_current_tile_gid(original_gid)
            
            # Recreate background with animated frames
            self.background = self.tmx_loader.create_animated_background(current_tile_mapping)

    # ==========================================
    # BULLET COLLISION 
    # ==========================================
    
    def handle_bullet_collisions(self, bullets: List[Bullet], on_enemy_death_callback=None) -> None:
        if not bullets or not self.enemies:
            return
        
        for bullet in bullets[:]:
            if self._process_bullet_collision(bullet, bullets, on_enemy_death_callback):
                break  

    def _process_bullet_collision(self, bullet: Bullet, bullets: List[Bullet], on_enemy_death_callback=None) -> bool:
        bullet_rect = pygame.Rect(bullet.position.x, bullet.position.y, 8, 8)
        
        for enemy in self.enemies[:]:
            if not enemy.is_alive():
                continue
                
            enemy_rect = pygame.Rect(
                enemy.position[0], 
                enemy.position[1], 
                enemy.size[0], 
                enemy.size[1]
            )
            
            if bullet_rect.colliderect(enemy_rect):
                enemy.take_damage(bullet.damage)
                
                if bullet in bullets:
                    bullets.remove(bullet)
                
                if not enemy.is_alive():
                    if hasattr(enemy.position, 'x') and hasattr(enemy.position, 'y'):
                        enemy_position = (enemy.position.x, enemy.position.y)
                    else:
                        enemy_position = enemy.position
                        
                    enemy.set_dead_state()
                    print(f"Inimigo {enemy.id} eliminado!")
                    
                    if on_enemy_death_callback:
                        on_enemy_death_callback(enemy_position)
                
                return True
        
        return False 

    # ==========================================
    # ROOM STATE 
    # ==========================================
    
    def mark_cleared(self) -> None:
        if not self.cleared:
            self.cleared = True
            print(f"Sala {self.id} limpa")

    def mark_visited(self) -> None:
        if not self.visited:
            self.visited = True
            print(f"Sala {self.id} visitada")

    def is_clear(self) -> bool:
        return all(not enemy.is_alive() for enemy in self.enemies)

    def get_alive_enemies_count(self) -> int:
        return sum(1 for enemy in self.enemies if enemy.is_alive())

    def remove_dead_enemies(self) -> int:
        initial_count = len(self.enemies)
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        removed = initial_count - len(self.enemies)
        
        return removed

    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def get_room_bounds(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.size[0], self.size[1])

    def is_position_in_bounds(self, position: Tuple[float, float], margin: int = 0) -> bool:
        x, y = position
        return (margin <= x <= self.size[0] - margin and 
                margin <= y <= self.size[1] - margin)

    def get_room_info(self) -> dict:
        return {
            "id": self.id,
            "size": self.size,
            "spawn_position": self.spawn_position,
            "cleared": self.cleared,
            "visited": self.visited,
            "enemies_alive": self.get_alive_enemies_count(),
            "items_count": len(self.items),
            "doors_count": len(self.doors),
            "has_collision_matrix": bool(self.collision_matrix)
        }

    
