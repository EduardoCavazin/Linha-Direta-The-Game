import os
import xml.etree.ElementTree as ET
import pygame
from typing import Dict, List, Tuple, Optional, Any
from src.world.loaders.assetLoader import AssetLoader, get_asset_loader

class TiledLoader:
    
    def __init__(self, tmx_path: str):
        self.path = tmx_path
        self.asset_loader = get_asset_loader() 
        
        self.width = 0         
        self.height = 0        
        self.tilewidth = 0     
        self.tileheight = 0    
        
        self.layers = []       
        self.objects = []      
        
        self.tilesets = []     
        self.tile_images = {}  
        
        self._load_tmx()
        
        self._load_tilesets()

    def _load_tmx(self) -> None:
        try:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Arquivo TMX não encontrado: {self.path}")
            
            tree = ET.parse(self.path)
            root = tree.getroot()
            
            self.width = int(root.get("width", 0))
            self.height = int(root.get("height", 0))
            self.tilewidth = int(root.get("tilewidth", 0))
            self.tileheight = int(root.get("tileheight", 0))
            
            self._parse_tilesets(root)
            
            self._parse_layers(root)
            
            self._parse_objects(root)
            
        except Exception as e:
            print(f"Erro ao carregar TMX {self.path}: {e}")
            import traceback
            traceback.print_exc()

    def _parse_tilesets(self, root) -> None:
        for tileset in root.findall("tileset"):
            ts_data = {
                "firstgid": int(tileset.get("firstgid", 1)),
                "name": tileset.get("name", ""),
                "tilewidth": int(tileset.get("tilewidth", 0)),
                "tileheight": int(tileset.get("tileheight", 0)),
                "source": tileset.get("source", ""),
                "image_source": "",
                "image_width": 0,
                "image_height": 0,
                "columns": 0,
                "tilecount": 0,
                "image": None 
            }
            
            if not ts_data["source"]:
                image_elem = tileset.find("image")
                if image_elem is not None:
                    ts_data["image_source"] = image_elem.get("source", "")
                    ts_data["image_width"] = int(image_elem.get("width", 0))
                    ts_data["image_height"] = int(image_elem.get("height", 0))
                    ts_data["tilecount"] = int(tileset.get("tilecount", 0))
                    ts_data["columns"] = int(tileset.get("columns", 0))
            
            self.tilesets.append(ts_data)

    def _parse_layers(self, root) -> None:
        for layer in root.findall("layer"):
            layer_data = {
                "id": layer.get("id", "0"),
                "name": layer.get("name", ""),
                "width": int(layer.get("width", 0)),
                "height": int(layer.get("height", 0)),
                "visible": layer.get("visible", "1") != "0",
                "data": []
            }
            
            data_element = layer.find("data")
            if data_element is not None:
                self._parse_layer_data(data_element, layer_data)
            
            self.layers.append(layer_data)

    def _parse_layer_data(self, data_element, layer_data) -> None:
        encoding = data_element.get("encoding", "")
        
        if encoding == "csv":
            raw_data = data_element.text.strip()
            rows = raw_data.split("\n")
            
            for row in rows:
                if row.strip():
                    tile_row = []
                    for tile_id in row.split(","):
                        if tile_id.strip():
                            tile_row.append(int(tile_id.strip()))
                    if tile_row: 
                        layer_data["data"].append(tile_row)
        else:
            tile_row = []
            for tile in data_element.findall("tile"):
                gid = int(tile.get("gid", 0))
                tile_row.append(gid)
                if len(tile_row) == layer_data["width"]:
                    layer_data["data"].append(tile_row)
                    tile_row = []

    def _parse_objects(self, root) -> None:
        for obj_group in root.findall("objectgroup"):
            for obj in obj_group.findall("object"):
                obj_data = {
                    "id": obj.get("id", "0"),
                    "name": obj.get("name", ""),
                    "type": obj.get("type", ""),
                    "x": float(obj.get("x", 0)),
                    "y": float(obj.get("y", 0)),
                    "width": float(obj.get("width", 0)),
                    "height": float(obj.get("height", 0)),
                    "visible": obj.get("visible", "1") != "0",
                    "properties": {}
                }
                
                props = obj.find("properties")
                if props is not None:
                    for prop in props.findall("property"):
                        name = prop.get("name", "")
                        value = prop.get("value", "")
                        obj_data["properties"][name] = value
                
                self.objects.append(obj_data)

    def _load_tilesets(self) -> None:
        try:
            for tileset in self.tilesets:
                if tileset.get("source"):
                    tsx_path = os.path.join(os.path.dirname(self.path), tileset["source"])
                    self._load_tsx(tileset, tsx_path)
                
                if tileset.get("image_source"):
                    image_path = tileset["image_source"]
                    name = os.path.splitext(os.path.basename(image_path))[0]
                
                    tileset["image"] = self.asset_loader.load_tileset(name)
                    
                    if tileset["image"]:
                        self._slice_tileset(tileset)
                    else:
                        tileset["image"] = self._create_fallback_tileset(tileset)
                else:
                    print(f"Tileset sem image_source: {tileset.get('name', 'Unknown')}")
        
        except Exception as e:
            print(f"Erro ao carregar tilesets: {e}")
            import traceback
            traceback.print_exc()

    def _create_fallback_tileset(self, tileset: Dict) -> pygame.Surface:
        tilewidth = tileset.get("tilewidth", 32)
        tileheight = tileset.get("tileheight", 32)
        columns = tileset.get("columns", 1)
        tilecount = tileset.get("tilecount", 1)
        
        rows = (tilecount + columns - 1) // columns
        img_width = columns * tilewidth
        img_height = rows * tileheight
        
        fallback = pygame.Surface((img_width, img_height))
        fallback.fill((255, 0, 255)) 
        
        return fallback

    def _load_tsx(self, tileset: Dict, tsx_path: str) -> None:
        try:
            tsx_path = os.path.normpath(tsx_path)
            
            if not os.path.exists(tsx_path):
                if "Assets.tsx" in tsx_path:
                    alternative_paths = [
                        os.path.join(os.path.dirname(self.path), "Assets.tsx"),
                        "assets/sprites/world/tilesets/Assets.tsx",
                        "assets/sprites/world/Assets.tsx"
                    ]
                    
                    for alt_path in alternative_paths:
                        if os.path.exists(alt_path):
                            tsx_path = alt_path
                            break
                    else:
                        return
                else:
                    return
            
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            tileset["name"] = root.get("name", tileset["name"])
            tileset["tilewidth"] = int(root.get("tilewidth", tileset["tilewidth"]))
            tileset["tileheight"] = int(root.get("tileheight", tileset["tileheight"]))
            tileset["tilecount"] = int(root.get("tilecount", 0))
            tileset["columns"] = int(root.get("columns", 0))
            
            image = root.find("image")
            if image is not None:
                raw_source = image.get("source", "")
                
                if "../" in raw_source:
                    image_name = os.path.basename(raw_source)  
                    tileset["image_source"] = image_name.replace('.png', '')  
                else:
                    tileset["image_source"] = os.path.splitext(raw_source)[0]
                
                tileset["image_width"] = int(image.get("width", 0))
                tileset["image_height"] = int(image.get("height", 0))
            
        
        except Exception as e:
            import traceback
            traceback.print_exc()

    def _slice_tileset(self, tileset: Dict) -> None:
        if "image" not in tileset or tileset["image"] is None:
            return
        
        image = tileset["image"]
        tilewidth = tileset["tilewidth"]
        tileheight = tileset["tileheight"]
        columns = tileset["columns"]
        tilecount = tileset["tilecount"]
        firstgid = tileset["firstgid"]
        
        for i in range(tilecount):
            x = (i % columns) * tilewidth
            y = (i // columns) * tileheight
            
            rect = pygame.Rect(x, y, tilewidth, tileheight)
            tile_img = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
            tile_img.blit(image, (0, 0), rect)
            
            gid = firstgid + i
            self.tile_images[gid] = tile_img

    def get_map_size_pixels(self) -> Tuple[int, int]:
        return (self.width * self.tilewidth, self.height * self.tileheight)
    
    def get_map_size_tiles(self) -> Tuple[int, int]:
        return (self.width, self.height)
    
    def get_tile_size(self) -> Tuple[int, int]:
        return (self.tilewidth, self.tileheight)
    
    def get_objects_by_name(self, name: str) -> List[Dict]:
        return [obj for obj in self.objects if obj["name"] == name]
    
    def get_objects_by_type(self, obj_type: str) -> List[Dict]:
        return [obj for obj in self.objects if obj["type"] == obj_type]
    
    def get_objects_data(self) -> List[Dict]:
        return [{
            "name": obj["name"],
            "type": obj["type"],
            "x": obj["x"],
            "y": obj["y"],
            "width": obj.get("width", 32),
            "height": obj.get("height", 32),
            "properties": obj["properties"]
        } for obj in self.objects]
    
    def create_background(self) -> pygame.Surface:
        width, height = self.get_map_size_pixels()
        background = pygame.Surface((width, height), pygame.SRCALPHA)
        background.fill((40, 40, 40))
        
        for layer in self.layers:
            if not layer["visible"]:
                continue
            
            self._render_layer_to_surface(layer, background)
        
        self._render_object_markers(background)
        
        return background
    
    def _render_layer_to_surface(self, layer: Dict, surface: pygame.Surface) -> None:
        for y, row in enumerate(layer["data"]):
            for x, gid in enumerate(row):
                if gid == 0:
                    continue
                
                tile_img = self.tile_images.get(gid)
                if tile_img:
                    pos_x = x * self.tilewidth
                    pos_y = y * self.tileheight
                    surface.blit(tile_img, (pos_x, pos_y))
    
    def _render_object_markers(self, surface: pygame.Surface) -> None:
        for obj in self.objects:
            color = self._get_object_color(obj)
            
            if obj.get("width", 0) == 0 or obj.get("height", 0) == 0:
                center = (int(obj["x"]), int(obj["y"]))
                pygame.draw.circle(surface, color, center, 8)
                pygame.draw.circle(surface, (255, 255, 255), center, 8, 2)
            else:
                rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                pygame.draw.rect(surface, color, rect, 3)
    
    def _get_object_color(self, obj: Dict) -> Tuple[int, int, int]:
        if obj["name"] == "Player":
            return (0, 255, 0) 
        elif "Enemy" in obj["name"]:
            return (255, 0, 0) 
        elif obj["name"] in ["HealthPack", "AmmoPack"]:
            return (0, 0, 255) 
        elif "Door" in obj["name"]:
            return (255, 255, 0)  
        else:
            return (200, 200, 200) 
    
    def get_collision_matrix(self) -> List[List[bool]]:
        collision_matrix = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for layer in self.layers:
            if layer["name"].lower() in ["colisão", "colisao", "collision"]:
                
                for y, row in enumerate(layer["data"]):
                    for x, gid in enumerate(row):
                        if gid > 0:
                            collision_matrix[y][x] = True
                break
        
        return collision_matrix
    
    def __str__(self) -> str:
        return (f"TiledMap: {os.path.basename(self.path)}\n"
                f"  Size: {self.width}x{self.height} tiles ({self.tilewidth}x{self.tileheight} px)\n"
                f"  Layers: {len(self.layers)}\n"
                f"  Objects: {len(self.objects)}\n"
                f"  Tilesets: {len(self.tilesets)}\n"
                f"  Tiles: {len(self.tile_images)}")