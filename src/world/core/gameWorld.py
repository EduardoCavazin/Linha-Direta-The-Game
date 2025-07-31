import random
import pygame
from typing import List, Tuple, Optional
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.bullet import Bullet
from src.world.core.map import Map
from src.world.core.room import Room
from src.core.camera import Camera


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int) -> None:
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        
        self.map: Map = Map()
        
        self.camera: Camera = Camera(width, height, 2000, 2000)
        
        self.current_room: Optional[Room] = None
        self.player: Optional[Player] = None
        self.bullets: List[Bullet] = []
        self.render_queue: List = []
        self.last_teleport_time: float = 0.0 
        self.start_time = pygame.time.get_ticks()
        
        self._initialize_world()
    
    def _initialize_world(self) -> None:
        if self.map.rooms:
            # Procura primeiro por uma sala chamada "Mapa1" para começar a sequência
            start_room = None
            
            # Prioridade 1: Mapa1 para começar a sequência
            for room in self.map.rooms:
                if room.id == "Mapa1":
                    start_room = room
                    break
            
            # Prioridade 2: Sala com player
            if not start_room:
                for room in self.map.rooms:
                    if room.player is not None:
                        start_room = room
                        break
            
            # Fallback: primeira sala
            if not start_room:
                start_room = self.map.rooms[0]
            
            self.current_room = start_room
            print(f"Sala inicial selecionada: {self.current_room.id}")
            
            if self.current_room:
                room_width, room_height = self.current_room.size
                self.camera.set_world_bounds(room_width, room_height)
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
        world_bounds = self.current_room.size  
        
        directions = []
        if keys[pygame.K_w]: directions.append("up")
        if keys[pygame.K_s]: directions.append("down")
        if keys[pygame.K_a]: directions.append("left")
        if keys[pygame.K_d]: directions.append("right")
        
        for direction in directions:
            self.player.move(direction, delta_time, obstacles, world_bounds)
        
        if keys[pygame.K_r]:
            self.player.reload()
    
    def process_player_mouse_movement(self, mouse_pos: Tuple[int, int]) -> None:
        if not self.player:
            return
        
        world_mouse_pos = self.camera.screen_to_world(mouse_pos)
        self.player.rotate_to_mouse(world_mouse_pos)

    def process_player_mouse(self, mouse_pos: Tuple[int, int]) -> None:
        if not self.player:
            return
        
        world_mouse_pos = self.camera.screen_to_world(mouse_pos)
        bullet = self.player.shoot(world_mouse_pos)
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
            self.camera.follow_target(self.player)
    
        self._update_enemies()
        self._update_bullets()
        self._check_item_collisions()
        self._check_door_collisions()
        
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
        
        world_width = self.current_room.size[0] if self.current_room else self.width
        world_height = self.current_room.size[1] if self.current_room else self.height
        
        for bullet in self.bullets[:]:
            if not bullet.update(dt, world_width, world_height):
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

    def _check_door_collisions(self) -> None:
        if not self.player or not self.current_room:
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_teleport_time < 1.0:  
            return
        
        player_rect = pygame.Rect(self.player.position[0], self.player.position[1], 
                                self.player.size[0], self.player.size[1])
        
        for door in self.current_room.doors:
            door_rect = pygame.Rect(door.position[0], door.position[1], 
                                  door.size[0], door.size[1])
            
            if player_rect.colliderect(door_rect):
                print(f"Player colidiu com porta: {door.name} (destino: {door.destination})")
                self._handle_door_teleport(door)
                self.last_teleport_time = current_time
                break  

    def _handle_door_teleport(self, door) -> None:
        # Verifica se a porta tem um destino específico
        destination = getattr(door, 'destination', None)
        
        # Lógica de progressão sequencial para "next_map"
        if destination == "next_map":
            target_room = self._get_next_map()
            if target_room:
                print(f"Teletransportando de {self.current_room.id} para {target_room.id} (progressão sequencial)")
                self._teleport_to_room(target_room)
                return
        
        # Destino específico (como "Mapa 3")
        elif destination and destination != "next_room":
            target_room = None
            for room in self.map.rooms:
                if room.id == destination:
                    target_room = room
                    break
            
            if target_room:
                print(f"Teletransportando de {self.current_room.id} para {target_room.id} (destino específico)")
                self._teleport_to_room(target_room)
                return
            else:
                print(f"Sala de destino '{destination}' não encontrada!")
        
        # Comportamento padrão: teleporte aleatório
        possible_rooms = [room for room in self.map.rooms if room != self.current_room]
        if not possible_rooms:
            print("Nenhuma outra sala disponível para teleporte!")
            return

        target_room = random.choice(possible_rooms)
        print(f"Teletransportando de {self.current_room.id} para {target_room.id} (aleatório)")
        self._teleport_to_room(target_room)

    def _get_next_map(self) -> Optional[Room]:
        """Retorna o próximo mapa na sequência: Mapa1 -> Mapa2 -> Mapa 3"""
        current_id = self.current_room.id
        
        if current_id == "Mapa1":
            next_id = "Mapa2"
        elif current_id == "Mapa2":
            next_id = "Mapa 3"
        elif current_id == "Mapa 3":
            next_id = "Mapa1"  # Loop de volta para o início
        else:
            # Se não é um dos mapas principais, vai para Mapa1
            next_id = "Mapa1"
        
        # Busca o próximo mapa
        for room in self.map.rooms:
            if room.id == next_id:
                return room
        
        print(f"Próximo mapa '{next_id}' não encontrado!")
        return None

    def _teleport_to_room(self, target_room: Room) -> None:
        """Realiza o teletransporte para a sala especificada"""
        self.current_room = target_room
        room_width, room_height = self.current_room.size
        self.camera.set_world_bounds(room_width, room_height)

        if self.player:
            spawn_position = self.current_room.spawn_position
            self.player.position = spawn_position
            self.camera.follow_target(self.player)
            print(f"Player posicionado em: {spawn_position}")
    

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
        self.screen.fill((88, 71, 71))
        
        if self.current_room and self.current_room.background:
            bg_pos = self.camera.world_to_screen((0, 0))
            self.screen.blit(self.current_room.background, bg_pos)
        
        for obj in self.render_queue:
            self._render_object_with_camera(obj)

    def _render_object_with_camera(self, obj) -> None:
        """Renderiza um objeto aplicando a transformação da câmera."""
        if not hasattr(obj, 'position'):
            return
        
        obj_pos = obj.position
        if hasattr(obj_pos, 'x') and hasattr(obj_pos, 'y'):
            obj_pos = (obj_pos.x, obj_pos.y)
            
        obj_size = getattr(obj, 'size', (32, 32))
        if hasattr(obj, 'rect'):
            obj_size = (obj.rect.width, obj.rect.height)
        elif hasattr(obj, 'hitbox'):
            obj_size = (obj.hitbox.width, obj.hitbox.height)
            
        if not self.camera.is_visible(obj_pos, obj_size):
            return
            
        screen_pos = self.camera.world_to_screen(obj_pos)
        
        if hasattr(obj, 'rect') and hasattr(obj, 'image'):
            screen_rect = obj.rect.copy()
            screen_rect.center = screen_pos
            self.screen.blit(obj.image, screen_rect)
        elif hasattr(obj, 'hitbox'):
            screen_hitbox = obj.hitbox.copy()
            screen_hitbox.topleft = screen_pos
            pygame.draw.rect(self.screen, (255, 0, 0), screen_hitbox)
        else:
            if hasattr(obj, 'draw'):
                original_pos = obj.position
                obj.position = screen_pos
                obj.draw(self.screen)
                obj.position = original_pos
        

    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    
    def change_room(self, room_index: int) -> None:
        if 0 <= room_index < len(self.map.rooms):
            self.current_room = self.map.rooms[room_index]
            if self.current_room:
                room_width, room_height = self.current_room.size
                self.camera.set_world_bounds(room_width, room_height)
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
