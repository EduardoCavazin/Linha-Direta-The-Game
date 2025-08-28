"""
Collision Optimization System for Linha Direta: The Game
Provides spatial partitioning and caching for efficient collision detection
"""

import pygame
import math
from typing import List, Tuple, Dict, Set, Optional, Any
from dataclasses import dataclass

@dataclass
class CollisionObject:
    """Wrapper for objects with collision data"""
    obj: Any
    rect: pygame.Rect
    id: str
    is_static: bool = False  # Static objects don't move (walls, tiles)
    last_position: Tuple[float, float] = (0, 0)

class SpatialGrid:
    """Simple spatial partitioning system using a grid"""
    
    def __init__(self, world_width: int, world_height: int, cell_size: int = 128):
        self.world_width = world_width
        self.world_height = world_height
        self.cell_size = cell_size
        self.cols = math.ceil(world_width / cell_size)
        self.rows = math.ceil(world_height / cell_size)
        
        # Grid of sets containing object IDs
        self.grid: List[List[Set[str]]] = [[set() for _ in range(self.cols)] for _ in range(self.rows)]
        self.objects: Dict[str, CollisionObject] = {}
        
        # Cache for frequently accessed cells
        self.cell_cache: Dict[Tuple[int, int], Set[str]] = {}
        
    def _get_cell_coords(self, x: float, y: float) -> Tuple[int, int]:
        """Get grid cell coordinates for a world position"""
        col = max(0, min(self.cols - 1, int(x // self.cell_size)))
        row = max(0, min(self.rows - 1, int(y // self.cell_size)))
        return (row, col)
    
    def _get_cells_for_rect(self, rect: pygame.Rect) -> List[Tuple[int, int]]:
        """Get all grid cells that a rectangle overlaps"""
        cells = []
        
        # Get corner cells
        top_left = self._get_cell_coords(rect.left, rect.top)
        bottom_right = self._get_cell_coords(rect.right - 1, rect.bottom - 1)
        
        # Add all cells in the range
        for row in range(top_left[0], bottom_right[0] + 1):
            for col in range(top_left[1], bottom_right[1] + 1):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    cells.append((row, col))
        
        return cells
    
    def add_object(self, obj_id: str, obj: Any, rect: pygame.Rect, is_static: bool = False):
        """Add an object to the spatial grid"""
        collision_obj = CollisionObject(obj, rect, obj_id, is_static, (rect.centerx, rect.centery))
        self.objects[obj_id] = collision_obj
        
        # Add to appropriate cells
        cells = self._get_cells_for_rect(rect)
        for row, col in cells:
            self.grid[row][col].add(obj_id)
    
    def update_object(self, obj_id: str, new_rect: pygame.Rect):
        """Update an object's position in the spatial grid"""
        if obj_id not in self.objects:
            return
        
        collision_obj = self.objects[obj_id]
        old_rect = collision_obj.rect
        
        # Only update if position actually changed
        if old_rect.center != new_rect.center:
            # Remove from old cells
            old_cells = self._get_cells_for_rect(old_rect)
            for row, col in old_cells:
                self.grid[row][col].discard(obj_id)
            
            # Add to new cells
            new_cells = self._get_cells_for_rect(new_rect)
            for row, col in new_cells:
                self.grid[row][col].add(obj_id)
            
            # Update object data
            collision_obj.rect = new_rect
            collision_obj.last_position = new_rect.center
    
    def remove_object(self, obj_id: str):
        """Remove an object from the spatial grid"""
        if obj_id not in self.objects:
            return
        
        collision_obj = self.objects[obj_id]
        cells = self._get_cells_for_rect(collision_obj.rect)
        
        for row, col in cells:
            self.grid[row][col].discard(obj_id)
        
        del self.objects[obj_id]
    
    def get_nearby_objects(self, rect: pygame.Rect, exclude_id: str = None) -> List[CollisionObject]:
        """Get all objects that could potentially collide with the given rect"""
        nearby_ids = set()
        cells = self._get_cells_for_rect(rect)
        
        for row, col in cells:
            nearby_ids.update(self.grid[row][col])
        
        if exclude_id and exclude_id in nearby_ids:
            nearby_ids.remove(exclude_id)
        
        return [self.objects[obj_id] for obj_id in nearby_ids if obj_id in self.objects]

class CollisionOptimizer:
    """Main collision optimization system"""
    
    def __init__(self, world_width: int = 2000, world_height: int = 2000):
        self.spatial_grid = SpatialGrid(world_width, world_height)
        self.collision_cache: Dict[str, bool] = {}
        self.cache_frame = 0
        self.max_cache_age = 5  # Clear cache every 5 frames
        
        # Performance counters
        self.collision_checks = 0
        self.cache_hits = 0
    
    def add_static_object(self, obj_id: str, obj: Any, rect: pygame.Rect):
        """Add a static object (walls, obstacles that don't move)"""
        self.spatial_grid.add_object(obj_id, obj, rect, is_static=True)
    
    def add_dynamic_object(self, obj_id: str, obj: Any, rect: pygame.Rect):
        """Add a dynamic object (player, enemies, bullets)"""
        self.spatial_grid.add_object(obj_id, obj, rect, is_static=False)
    
    def update_object(self, obj_id: str, new_rect: pygame.Rect):
        """Update a dynamic object's position"""
        self.spatial_grid.update_object(obj_id, new_rect)
    
    def remove_object(self, obj_id: str):
        """Remove an object from the collision system"""
        self.spatial_grid.remove_object(obj_id)
    
    def check_collision_optimized(self, rect: pygame.Rect, exclude_id: str = None, 
                                static_only: bool = False) -> bool:
        """Optimized collision check using spatial partitioning"""
        self.collision_checks += 1
        
        # Generate cache key
        cache_key = f"{rect.center}_{rect.size}_{exclude_id}_{static_only}_{self.cache_frame}"
        
        if cache_key in self.collision_cache:
            self.cache_hits += 1
            return self.collision_cache[cache_key]
        
        # Get nearby objects
        nearby_objects = self.spatial_grid.get_nearby_objects(rect, exclude_id)
        
        # Filter static/dynamic if needed
        if static_only:
            nearby_objects = [obj for obj in nearby_objects if obj.is_static]
        
        # Check actual collisions
        for collision_obj in nearby_objects:
            if rect.colliderect(collision_obj.rect):
                self.collision_cache[cache_key] = True
                return True
        
        self.collision_cache[cache_key] = False
        return False
    
    def get_colliding_objects(self, rect: pygame.Rect, exclude_id: str = None, 
                            static_only: bool = False) -> List[CollisionObject]:
        """Get all objects that are actually colliding with the rect"""
        nearby_objects = self.spatial_grid.get_nearby_objects(rect, exclude_id)
        
        if static_only:
            nearby_objects = [obj for obj in nearby_objects if obj.is_static]
        
        colliding = []
        for collision_obj in nearby_objects:
            if rect.colliderect(collision_obj.rect):
                colliding.append(collision_obj)
        
        return colliding
    
    def update_frame(self):
        """Call this once per frame to manage cache"""
        self.cache_frame += 1
        
        # Clear cache periodically
        if self.cache_frame % self.max_cache_age == 0:
            self.collision_cache.clear()
    
    def get_performance_stats(self) -> Dict[str, int]:
        """Get performance statistics"""
        cache_hit_rate = (self.cache_hits / max(1, self.collision_checks)) * 100
        return {
            "collision_checks": self.collision_checks,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "objects_in_grid": len(self.spatial_grid.objects)
        }