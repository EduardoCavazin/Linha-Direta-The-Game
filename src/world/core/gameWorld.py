import math
import random
import pygame
from typing import List, Tuple, Optional
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.bullet import Bullet
from src.world.core.map import Map
from src.world.core.room import Room
from src.core.camera import Camera
from src.core.entityFactory import EntityFactory
from src.core.constants import World, Player, Enemy, Bullet, Items, Physics, get_random_drop_offset
from src.core.enums import ItemType, ItemEffect, get_item_effect, get_item_display_name


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int, audio_manager=None) -> None:
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        self.audio_manager = audio_manager  # Referência para o AudioManager
        
        self.map: Map = Map()
        self.entity_factory: EntityFactory = EntityFactory()
        
        self.camera: Camera = Camera(width, height, World.CAMERA_WORLD_WIDTH, World.CAMERA_WORLD_HEIGHT)
        
        self.current_room: Optional[Room] = None
        self.player: Optional[Player] = None
        self.bullets: List[Bullet] = []         
        self.enemy_bullets: List[Bullet] = []   
        self.render_queue: List = []
        self.last_teleport_time: float = 0.0 
        self.start_time = pygame.time.get_ticks()
        
        self._initialize_world()
    
    def _initialize_world(self) -> None:
        if self.map.rooms:
            start_room = None
            
            for room in self.map.rooms:
                if room.id == "Mapa1":
                    start_room = room
                    break
            
            if not start_room:
                for room in self.map.rooms:
                    if room.player is not None:
                        start_room = room
                        break
            
            if not start_room:
                start_room = self.map.rooms[0]
            
            self.current_room = start_room
            
            if self.current_room:
                room_width, room_height = self.current_room.size
                self.camera.set_world_bounds(room_width, room_height)
                
                self._lock_room_doors()
                
                if self.current_room.get_alive_enemies_count() == 0:
                    self._unlock_room_doors()
            self._spawn_player()
        else:
            print("ERRO: Nenhuma sala carregada!")
    
    def _lock_room_doors(self) -> None:
        if not self.current_room:
            return
            
        for door in self.current_room.doors:
            door.lock()
    
    def _spawn_player(self) -> None:
        spawn_pos = self.current_room.spawn_position if self.current_room else (World.DEFAULT_SPAWN_X, World.DEFAULT_SPAWN_Y)
        
        self.player = self.entity_factory.create_player(spawn_pos)
        
        if self.player:
            from src.model.objects.weapon import Weapon
            weapon = Weapon("pistol", "Pistola", Player.PISTOL_DAMAGE, Player.PISTOL_MAX_AMMO)
            self.player.weapon = weapon
            self.player.ammo = Player.STARTING_AMMO
            
        else:
            print("ERRO: Falha ao criar player principal com EntityFactory!")
        
    # ==========================================
    # INPUT PROCESSING 
    # ==========================================
    
    def process_player_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        if not self.player or not self.current_room:
            return

        delta_time = self.clock.get_time() / Physics.MILLISECONDS_TO_SECONDS
        obstacles = self.current_room.get_wall_rects()
        world_bounds = self.current_room.size  

        directions = []
        if keys[pygame.K_w]: directions.append("up")
        if keys[pygame.K_s]: directions.append("down")
        if keys[pygame.K_a]: directions.append("left")
        if keys[pygame.K_d]: directions.append("right")

        self.player.move(directions, delta_time, obstacles, world_bounds)

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
        
        try:
            if self.player:
                self.player.update(delta_time)
                self.camera.follow_target(self.player)
        except AttributeError as e:
            print(f"ERRO no player.update(): {e}")
            import traceback
            traceback.print_exc()
            return
        
        try:
            self._update_enemies()
        except AttributeError as e:
            print(f"ERRO no _update_enemies(): {e}")
            import traceback
            traceback.print_exc()
            return
            
        try:
            self._update_bullets()
        except AttributeError as e:
            print(f"ERRO no _update_bullets(): {e}")
            import traceback
            traceback.print_exc()
            return
            
        try:
            self._update_enemy_bullets()
        except AttributeError as e:
            print(f"ERRO no _update_enemy_bullets(): {e}")
            import traceback
            traceback.print_exc()
            return
            
        try:
            self._check_item_collisions()
        except AttributeError as e:
            print(f"ERRO no _check_item_collisions(): {e}")
            import traceback
            traceback.print_exc()
            return
            
        try:
            self._check_door_collisions()
        except AttributeError as e:
            print(f"ERRO no _check_door_collisions(): {e}")
            import traceback
            traceback.print_exc()
            return
            
        try:
            self._update_render_queue()
        except AttributeError as e:
            print(f"ERRO no _update_render_queue(): {e}")
            import traceback
            traceback.print_exc()
            return
    
    def _update_enemies(self) -> None:
        if not self.player or not self.current_room:
            return
        
        player_pos = self.player.position
        delta_time = self.clock.get_time() / Physics.MILLISECONDS_TO_SECONDS
        
        enemies_alive_before = self.current_room.get_alive_enemies_count()
        
        for enemy in self.current_room.enemies[:]:
            if enemy.is_alive():
                enemy_bullet = enemy.update(player_pos, delta_time)
                if enemy_bullet:
                    self.enemy_bullets.append(enemy_bullet)
                    # Tocar som de tiro do inimigo
                    if self.audio_manager:
                        self.audio_manager.play_sound('shoot')
            else:
                self.current_room.enemies.remove(enemy)
        
        enemies_alive_after = self.current_room.get_alive_enemies_count()
        
        if enemies_alive_before > 0 and enemies_alive_after == 0:
            self.current_room.mark_cleared()
            self._unlock_room_doors()
            print("Sala limpa! As portas foram desbloqueadas.")
    
    def _unlock_room_doors(self) -> None:
        if not self.current_room:
            return
            
        for door in self.current_room.doors:
            door.unlock()
    
    def _generate_enemy_drop(self, enemy_position: Tuple[float, float]) -> None:
        if not self.current_room:
            return
        
        drop_type = random.choice([ItemType.HEALTH_PACK, ItemType.AMMO_PACK])
        
        offset_x, offset_y = get_random_drop_offset()
        drop_position = (enemy_position[0] + offset_x, enemy_position[1] + offset_y)
        
        
        dropped_item = self.entity_factory.create_item(drop_type.value, drop_position)
        
        if dropped_item:
            item_effect = get_item_effect(drop_type)
            dropped_item.effect = item_effect.value
            
            if drop_type == ItemType.HEALTH_PACK:
                dropped_item.value = Items.HEALTH_PACK_VALUE  
            elif drop_type == ItemType.AMMO_PACK:
                dropped_item.value = Items.AMMO_PACK_VALUE   
            
            self.current_room.items.append(dropped_item)
            
            item_name = get_item_display_name(drop_type)
            print(f" {item_name} foi dropado!")
        else:
            print(" Falha ao criar o item dropado!")
    
    def _update_bullets(self) -> None:
        if not self.bullets:
            return
        
        dt = self.clock.get_time() / Physics.MILLISECONDS_TO_SECONDS
        
        world_width = self.current_room.size[0] if self.current_room else self.width
        world_height = self.current_room.size[1] if self.current_room else self.height
        
        for bullet in self.bullets[:]:
            if not bullet.update(dt, world_width, world_height):
                self.bullets.remove(bullet)
                continue
            
            if self.current_room.check_collision((bullet.position.x, bullet.position.y), (2, 2)):
                self.bullets.remove(bullet)
                continue
        
        self.current_room.handle_bullet_collisions(self.bullets, self._generate_enemy_drop)
    
    def _check_item_collisions(self) -> None:
        if not self.player or not self.current_room:
            return
        
        for item in self.current_room.items[:]:
            if self.player.rect.colliderect(item.hitbox):
                print(f"ITEM COLETADO: {item.name} - {item.effect}")
                if item.effect == ItemEffect.HEAL.value:
                    self.player.heal(item.value)
                elif item.effect == ItemEffect.AMMO.value:
                    self.player.add_ammo(item.value)
            
                self.current_room.items.remove(item)

    def _check_door_collisions(self) -> None:
        if not self.player or not self.current_room:
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_teleport_time < 1.0:  
            return
        
        for door in self.current_room.doors:
            door_rect = pygame.Rect(door.position[0], door.position[1], 
                                  door.size[0], door.size[1])
        
            if self.player.rect.colliderect(door_rect):
                if not self.current_room.is_clear():
                    enemies_remaining = self.current_room.get_alive_enemies_count()
                    print(f"Não é possível avançar! Elimine os {enemies_remaining} inimigos restantes.")
                    return
                
                self._handle_door_teleport(door)
                self.last_teleport_time = current_time
                break  

    def _handle_door_teleport(self, door) -> None:
        destination = getattr(door, 'destination', None)
        
        if destination == "next_map":
            target_room = self._get_next_map()
            if target_room:
                print(f"Teletransportando de {self.current_room.id} para {target_room.id} (progressão sequencial)")
                self._teleport_to_room(target_room)
                return
        
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
        
        possible_rooms = [room for room in self.map.rooms if room != self.current_room]
        if not possible_rooms:
            print("Nenhuma outra sala disponível para teleporte!")
            return

        target_room = random.choice(possible_rooms)
        print(f"Teletransportando de {self.current_room.id} para {target_room.id} (aleatório)")
        self._teleport_to_room(target_room)

    def _get_next_map(self) -> Optional[Room]:
        current_id = self.current_room.id
        
        if current_id == "Mapa1":
            next_id = "Mapa2"
        elif current_id == "Mapa2":
            next_id = "Mapa 3"
        elif current_id == "Mapa 3":
            next_id = "Mapa1"  
        else:
            next_id = "Mapa1"
        
        for room in self.map.rooms:
            if room.id == next_id:
                return room
        
        print(f"Próximo mapa '{next_id}' não encontrado!")
        return None

    def _teleport_to_room(self, target_room: Room) -> None:
        print(f"TELEPORTE: Mudando para {target_room.id}")
        self.current_room = target_room
        room_width, room_height = self.current_room.size
        self.camera.set_world_bounds(room_width, room_height)
        
        self._lock_room_doors()
        if self.current_room.is_clear():
            self._unlock_room_doors()
            print("Sala já estava limpa - portas desbloqueadas.")
        else:
            enemies_count = self.current_room.get_alive_enemies_count()
            print(f"Nova sala com {enemies_count} inimigos - elimine todos para desbloquear as portas.")

        if self.player:
            spawn_position = self.current_room.spawn_position

            temp_rect = pygame.Rect(0, 0, self.player.size[0], self.player.size[1])
            temp_rect.center = (int(spawn_position[0]), int(spawn_position[1]))
            
            obstacles = self.current_room.get_wall_rects()
            collision = any(temp_rect.colliderect(obs) for obs in obstacles)
            
            if collision:
                spawn_position = self._find_safe_spawn(spawn_position, obstacles)
            
            self.player.position = spawn_position
            self.camera.follow_target(self.player)
            
            self.player.moving = False
            
            print(f"Player posicionado em: {self.player.position}")
    
    def _find_safe_spawn(self, original_spawn: Tuple[float, float], obstacles: List[pygame.Rect]) -> Tuple[float, float]:
        spawn_x, spawn_y = original_spawn
        
        player_w, player_h = self.player.size
        
        for distance in [50, 100, 150, 200]:
            for angle in range(0, 360, 30):
                
                rad = math.radians(angle)
                test_x = spawn_x + distance * math.cos(rad)
                test_y = spawn_y + distance * math.sin(rad)
                
                if (player_w//2 <= test_x <= self.current_room.size[0] - player_w//2 and 
                    player_h//2 <= test_y <= self.current_room.size[1] - player_h//2):
                    
                    test_rect = pygame.Rect(0, 0, player_w, player_h)
                    test_rect.center = (int(test_x), int(test_y))
                    
                    collision = any(test_rect.colliderect(obs) for obs in obstacles)
                    if not collision:
                        print(f"Posição livre encontrada: ({test_x:.1f}, {test_y:.1f})")
                        return (test_x, test_y)
        
        print("Nenhuma posição livre encontrada, usando centro do mapa")
        return (self.current_room.size[0] // 2, self.current_room.size[1] // 2)
    

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
        self.render_queue.extend(self.enemy_bullets) 
        
        if len(self.current_room.items) > 0 and not hasattr(self, '_last_items_count'):
            self._last_items_count = len(self.current_room.items)
        elif len(self.current_room.items) != getattr(self, '_last_items_count', 0):
            self._last_items_count = len(self.current_room.items)
        
    def render(self) -> None:
        self.screen.fill((88, 71, 71))
        
        if self.current_room and self.current_room.background:
            bg_pos = self.camera.world_to_screen((0, 0))
            self.screen.blit(self.current_room.background, bg_pos)
        
        for obj in self.render_queue:
            self._render_object_with_camera(obj)

    def _render_object_with_camera(self, obj) -> None:
        if not hasattr(obj, 'position'):
            return
        
        obj_pos = obj.position
        if hasattr(obj_pos, 'x') and hasattr(obj_pos, 'y'):
            obj_pos = (obj_pos.x, obj_pos.y)
            
        obj_size = getattr(obj, 'size', (32, 32))
        if hasattr(obj, 'rect') and obj.rect is not None:
            obj_size = (obj.rect.width, obj.rect.height)
        elif hasattr(obj, 'hitbox') and obj.hitbox is not None:
            obj_size = (obj.hitbox.width, obj.hitbox.height)
            
        if not self.camera.is_visible(obj_pos, obj_size):
            return
            
        screen_pos = self.camera.world_to_screen(obj_pos)
        
        if hasattr(obj, 'image') and obj.image is not None:
            if hasattr(obj, 'rect') and obj.rect is not None:
                screen_rect = obj.rect.copy()
                screen_rect.center = screen_pos
                self.screen.blit(obj.image, screen_rect)
            elif hasattr(obj, 'hitbox') and obj.hitbox is not None:
                self.screen.blit(obj.image, screen_pos)
            else:
                self.screen.blit(obj.image, screen_pos)
        elif hasattr(obj, 'hitbox') and obj.hitbox is not None:
            screen_hitbox = obj.hitbox.copy()
            screen_hitbox.topleft = screen_pos
            pygame.draw.rect(self.screen, (255, 0, 0), screen_hitbox)
        else:
            if hasattr(obj, 'draw'):
                original_pos = obj.position if hasattr(obj, 'position') else None
                obj.position = screen_pos
                obj.draw(self.screen)
                if original_pos:
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
                
                self._lock_room_doors()
                if self.current_room.is_clear():
                    self._unlock_room_doors()
                
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
    
    def _update_enemy_bullets(self) -> None:
        if not self.current_room or not self.player:
            return
        
        delta_time = self.clock.get_time() / 1000.0
        
        for bullet in self.enemy_bullets[:]:
            if not bullet.update(delta_time, self.width, self.height):
                self.enemy_bullets.remove(bullet)
                continue
            
            bullet_pos = (bullet.position.x, bullet.position.y)
            bullet_size = (bullet.hitbox.width, bullet.hitbox.height)
            if self.current_room.check_collision(bullet_pos, bullet_size):
                self.enemy_bullets.remove(bullet)
                continue
            
            if bullet.hitbox.colliderect(self.player.hitbox):
                damage = bullet.damage
                self.player.take_damage(damage)
                
                self.enemy_bullets.remove(bullet)
    
    def cleanup(self) -> None:
        self.bullets.clear()
        self.enemy_bullets.clear()  
        self.render_queue.clear()
        print("GameWorld limpo")
