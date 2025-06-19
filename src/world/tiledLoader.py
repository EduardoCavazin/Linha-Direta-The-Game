import os
import xml.etree.ElementTree as ET
import pygame
from typing import Dict, List, Tuple, Optional, Any

class TiledLoader:
    """
    Carregador de mapas TMX do Tiled sem dependências externas.
    Lê arquivos TMX e TSX diretamente usando o parser XML nativo do Python.
    """
    
    def __init__(self, tmx_path: str):
        """
        Inicializa o carregador de mapas TMX.
        
        Args:
            tmx_path: Caminho para o arquivo TMX do Tiled
        """
        self.path = tmx_path
        self.base_dir = os.path.dirname(tmx_path)
        
        # Propriedades do mapa
        self.width = 0         # Largura do mapa em tiles
        self.height = 0        # Altura do mapa em tiles
        self.tilewidth = 0     # Largura de cada tile em pixels
        self.tileheight = 0    # Altura de cada tile em pixels
        
        # Camadas e objetos
        self.layers = []       # Camadas de tiles
        self.objects = []      # Objetos do mapa
        
        # Tilesets
        self.tilesets = []     # Informações sobre tilesets
        self.tile_images = {}  # Dicionário de imagens de tiles por GID
        
        # Carregar arquivo TMX
        self._load_tmx()
        
        # Carregar tilesets e suas imagens
        self._load_tilesets()
    
    def _load_tmx(self) -> None:
        """Carrega e parseia o arquivo TMX."""
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Arquivo TMX não encontrado: {self.path}")
            
            # Parsear XML
            tree = ET.parse(self.path)
            root = tree.getroot()
            
            # Extrair propriedades básicas do mapa
            self.width = int(root.get("width", 0))
            self.height = int(root.get("height", 0))
            self.tilewidth = int(root.get("tilewidth", 0))
            self.tileheight = int(root.get("tileheight", 0))
            
            # Processar tilesets
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
                    "tilecount": 0
                }
                
                self.tilesets.append(ts_data)
            
            # Processar camadas de tiles
            for layer in root.findall("layer"):
                layer_data = {
                    "id": layer.get("id", "0"),
                    "name": layer.get("name", ""),
                    "width": int(layer.get("width", 0)),
                    "height": int(layer.get("height", 0)),
                    "visible": layer.get("visible", "1") != "0",
                    "data": []
                }
                
                # Extrair dados de tiles
                data_element = layer.find("data")
                if data_element is not None:
                    # Verificar codificação
                    encoding = data_element.get("encoding", "")
                    
                    if encoding == "csv":
                        # Formato CSV
                        raw_data = data_element.text.strip()
                        rows = raw_data.split("\n")
                        
                        for row in rows:
                            if row.strip():
                                tile_row = []
                                for tile_id in row.split(","):
                                    if tile_id.strip():
                                        tile_row.append(int(tile_id.strip()))
                                layer_data["data"].append(tile_row)
                    else:
                        # Formato XML
                        tile_row = []
                        for tile in data_element.findall("tile"):
                            gid = int(tile.get("gid", 0))
                            tile_row.append(gid)
                            if len(tile_row) == layer_data["width"]:
                                layer_data["data"].append(tile_row)
                                tile_row = []
                
                self.layers.append(layer_data)
            
            # Processar grupos de objetos
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
                    
                    # Extrair propriedades personalizadas
                    props = obj.find("properties")
                    if props is not None:
                        for prop in props.findall("property"):
                            name = prop.get("name", "")
                            value = prop.get("value", "")
                            obj_data["properties"][name] = value
                    
                    self.objects.append(obj_data)
            
            print(f"✅ TMX carregado: {self.width}x{self.height} tiles, {len(self.objects)} objetos")
        
        except Exception as e:
            print(f"❌ Erro ao carregar TMX {self.path}: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_tilesets(self) -> None:
        """Carrega os tilesets referenciados no mapa."""
        try:
            for tileset in self.tilesets:
                # Se o tileset tem um source externo (arquivo .tsx)
                if tileset["source"]:
                    tsx_path = os.path.join(self.base_dir, tileset["source"])
                    self._load_tsx(tileset, tsx_path)
                
                # Carregar a imagem do tileset
                if tileset["image_source"]:
                    # Ajustar caminho relativo
                    img_path = tileset["image_source"]
                    if not os.path.isabs(img_path):
                        # Se o caminho no TSX é relativo, usar o mesmo diretório do TSX
                        if tileset["source"]:
                            tsx_dir = os.path.dirname(os.path.join(self.base_dir, tileset["source"]))
                            img_path = os.path.join(tsx_dir, img_path)
                        else:
                            # Se não tiver TSX externo, usar o diretório do TMX
                            img_path = os.path.join(self.base_dir, img_path)
                    
                    # Tentar carregar a imagem
                    try:
                        # Verificar se o arquivo existe
                        if not os.path.exists(img_path):
                            # Se não existe, tentar subir um nível
                            img_path = os.path.join(self.base_dir, "..", os.path.basename(img_path))
                            
                            if not os.path.exists(img_path):
                                print(f"⚠️ Imagem não encontrada: {img_path}")
                                continue
                        
                        # Carregar a imagem com Pygame
                        tileset["image"] = pygame.image.load(img_path).convert_alpha()
                        print(f"✅ Imagem carregada: {img_path}")
                        
                        # Recortar os tiles da imagem e armazená-los
                        self._slice_tileset(tileset)
                        
                    except Exception as e:
                        print(f"❌ Erro ao carregar imagem {img_path}: {e}")
                        tileset["image"] = None
        
        except Exception as e:
            print(f"❌ Erro ao carregar tilesets: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_tsx(self, tileset: Dict, tsx_path: str) -> None:
        """Carrega um arquivo TSX externo."""
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(tsx_path):
                print(f"⚠️ Arquivo TSX não encontrado: {tsx_path}")
                return
            
            # Parsear XML
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            # Atualizar informações do tileset
            tileset["name"] = root.get("name", tileset["name"])
            tileset["tilewidth"] = int(root.get("tilewidth", tileset["tilewidth"]))
            tileset["tileheight"] = int(root.get("tileheight", tileset["tileheight"]))
            tileset["tilecount"] = int(root.get("tilecount", 0))
            tileset["columns"] = int(root.get("columns", 0))
            
            # Obter imagem do tileset
            image = root.find("image")
            if image is not None:
                tileset["image_source"] = image.get("source", "")
                tileset["image_width"] = int(image.get("width", 0))
                tileset["image_height"] = int(image.get("height", 0))
            
            print(f"✅ TSX carregado: {tsx_path}")
        
        except Exception as e:
            print(f"❌ Erro ao carregar TSX {tsx_path}: {e}")
    
    def _slice_tileset(self, tileset: Dict) -> None:
        """Recorta os tiles de um tileset e os armazena no dicionário tile_images."""
        if "image" not in tileset or tileset["image"] is None:
            return
        
        image = tileset["image"]
        tilewidth = tileset["tilewidth"]
        tileheight = tileset["tileheight"]
        columns = tileset["columns"]
        tilecount = tileset["tilecount"]
        firstgid = tileset["firstgid"]
        
        # Recortar cada tile do tileset
        for i in range(tilecount):
            # Calcular posição do tile na imagem
            x = (i % columns) * tilewidth
            y = (i // columns) * tileheight
            
            # Recortar tile
            rect = pygame.Rect(x, y, tilewidth, tileheight)
            tile_img = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
            tile_img.blit(image, (0, 0), rect)
            
            # Armazenar no dicionário (GID = firstgid + índice)
            self.tile_images[firstgid + i] = tile_img
    
    def get_map_size_pixels(self) -> Tuple[int, int]:
        """Retorna o tamanho do mapa em pixels."""
        return (self.width * self.tilewidth, self.height * self.tileheight)
    
    def get_map_size_tiles(self) -> Tuple[int, int]:
        """Retorna o tamanho do mapa em tiles."""
        return (self.width, self.height)
    
    def get_tile_size(self) -> Tuple[int, int]:
        """Retorna o tamanho de cada tile."""
        return (self.tilewidth, self.tileheight)
    
    def get_objects_by_name(self, name: str) -> List[Dict]:
        """Retorna todos os objetos com o nome especificado."""
        return [obj for obj in self.objects if obj["name"] == name]
    
    def get_objects_by_type(self, obj_type: str) -> List[Dict]:
        """Retorna todos os objetos com o tipo especificado."""
        return [obj for obj in self.objects if obj["type"] == obj_type]
    
    def create_background(self) -> pygame.Surface:
        """
        Cria um background renderizando as camadas de tiles.
        """
        width, height = self.get_map_size_pixels()
        background = pygame.Surface((width, height), pygame.SRCALPHA)
        background.fill((40, 40, 40))  # Cor de fundo base
        
        # Renderizar cada camada
        for layer in self.layers:
            if not layer["visible"]:
                continue
                
            layer_name = layer["name"]
            print(f"🎨 Renderizando camada: {layer_name}")
            
            # Percorrer os tiles da camada
            for y, row in enumerate(layer["data"]):
                for x, gid in enumerate(row):
                    if gid == 0:  # Tile vazio
                        continue
                    
                    # Obter imagem do tile
                    tile_img = self.tile_images.get(gid)
                    if tile_img:
                        # Calcular posição do tile no mapa
                        pos_x = x * self.tilewidth
                        pos_y = y * self.tileheight
                        
                        # Desenhar o tile
                        background.blit(tile_img, (pos_x, pos_y))
        
        # Desenhar objetos como retângulos coloridos para visualização
        for obj in self.objects:
            obj_rect = pygame.Rect(
                obj["x"], 
                obj["y"], 
                obj.get("width", self.tilewidth), 
                obj.get("height", self.tileheight)
            )
            
            # Cor baseada no tipo/nome do objeto
            color = (200, 200, 200)  # Padrão: cinza claro
            
            if obj["name"] == "Player":
                color = (0, 255, 0)  # Verde para o player
            elif "Enemy" in obj["name"]:
                color = (255, 0, 0)  # Vermelho para inimigos
            elif obj["name"] in ["HealthPack", "AmmoPack"]:
                color = (0, 0, 255)  # Azul para itens
            elif "Door" in obj["name"]:
                color = (255, 255, 0)  # Amarelo para portas
            
            # Para pontos (como o Player)
            if obj.get("width", 0) == 0 or obj.get("height", 0) == 0:
                center_x = obj["x"]
                center_y = obj["y"]
                pygame.draw.circle(background, color, (int(center_x), int(center_y)), 5)
                # Adicionar uma pequena "aura" para destacar
                pygame.draw.circle(background, color, (int(center_x), int(center_y)), 10, 2)
            else:
                # Para objetos com dimensões
                pygame.draw.rect(background, color, obj_rect, 2)
        
        return background
    
    def __str__(self) -> str:
        """Representação em string do mapa carregado."""
        return (f"TiledMap: {os.path.basename(self.path)}\n"
                f"  Size: {self.width}x{self.height} tiles ({self.tilewidth}x{self.tileheight} px)\n"
                f"  Layers: {len(self.layers)}\n"
                f"  Objects: {len(self.objects)}\n"
                f"  Tilesets: {len(self.tilesets)}")