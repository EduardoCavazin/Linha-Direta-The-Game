import os
import pygame
from typing import Dict, Optional, Tuple
from src.core.utils import load_image
from src.core.constants import Rendering

class AssetLoader:
    def __init__(self):
        self._tileset_cache: Dict[str, pygame.Surface] = {}
        self._background_cache: Dict[str, pygame.Surface] = {}
        self._texture_cache: Dict[str, pygame.Surface] = {}
        
    def load_tileset(self, name: str, size: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        cache_key = f"{name}_{size}" if size else name
        
        if cache_key in self._tileset_cache:
            return self._tileset_cache[cache_key]
        
        try:
            possible_paths = [
                f"assets/sprites/world/{name}.png",          
                f"sprites/world/{name}.png",
                f"world/{name}.png",
                f"{name}.png"
            ]
            
            for image_path in possible_paths:
                try:
                    image = load_image(image_path, size)
                    self._tileset_cache[cache_key] = image
                    return image
                except Exception as e:
                    continue
                
            return None
            
        except Exception as e:
            print(f"Erro ao carregar tileset {name}: {e}")
            return None
    
    def load_texture(self, name: str, size: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        cache_key = f"{name}_{size}" if size else name
        
        if cache_key in self._texture_cache:
            return self._texture_cache[cache_key]
        
        try:
            image_path = f"world/textures/{name}.png"
            image = load_image(image_path, size)
            self._texture_cache[cache_key] = image
            return image
        except Exception as e:
            print(f"Erro ao carregar textura {name}: {e}")
            return None
    
    def create_room_background(self, room_id: str, size: Tuple[int, int], fill_color: Tuple[int, int, int] = Rendering.DEFAULT_ROOM_COLOR) -> pygame.Surface:
        cache_key = f"bg_{room_id}_{size[0]}x{size[1]}"
        
        if cache_key in self._background_cache:
            return self._background_cache[cache_key]
        
        background = pygame.Surface(size)
        background.fill(fill_color)
        
        self._add_background_pattern(background, size)
        
        self._background_cache[cache_key] = background
        return background
    
    def _add_background_pattern(self, surface: pygame.Surface, size: Tuple[int, int]) -> None:
        grid_color = (80, 80, 80)
        grid_size = 32
        
        for x in range(0, size[0], grid_size):
            pygame.draw.line(surface, grid_color, (x, 0), (x, size[1]), 1)
        
        for y in range(0, size[1], grid_size):
            pygame.draw.line(surface, grid_color, (0, y), (size[0], y), 1)
    
    def preload_common_assets(self) -> None:
        common_tilesets = [
            "Colisao",
            "Contrucoes1", 
            "Pisos",
            "Veiculos"
        ]
        
        for tileset_name in common_tilesets:
            self.load_tileset(tileset_name)
    
    def get_cache_info(self) -> Dict[str, int]:
        return {
            "tilesets": len(self._tileset_cache),
            "backgrounds": len(self._background_cache), 
            "textures": len(self._texture_cache),
            "total": len(self._tileset_cache) + len(self._background_cache) + len(self._texture_cache)
        }
    
    def clear_cache(self, cache_type: str = "all") -> None:
        if cache_type == "all" or cache_type == "tilesets":
            self._tileset_cache.clear()
            
        if cache_type == "all" or cache_type == "backgrounds":
            self._background_cache.clear()
            
        if cache_type == "all" or cache_type == "textures":
            self._texture_cache.clear()
            
    
    def get_tileset_info(self, tileset_name: str) -> Optional[Dict[str, any]]:
        if tileset_name in self._tileset_cache:
            surface = self._tileset_cache[tileset_name]
            return {
                "name": tileset_name,
                "size": surface.get_size(),
                "flags": surface.get_flags(),
                "bitsize": surface.get_bitsize()
            }
        return None

_asset_loader_instance: Optional[AssetLoader] = None

def get_asset_loader() -> AssetLoader:
    global _asset_loader_instance
    if _asset_loader_instance is None:
        _asset_loader_instance = AssetLoader()
    return _asset_loader_instance