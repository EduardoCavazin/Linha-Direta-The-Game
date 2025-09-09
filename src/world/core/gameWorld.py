import math
import random
import pygame
from typing import List, Tuple, Optional, Dict
from src.model.entities.player import Player
from src.model.entities.enemy import Enemy
from src.model.objects.bullet import Bullet
from src.world.core.map import Map
from src.world.core.room import Room
from src.core.camera import Camera
from src.core.entityFactory import EntityFactory
from src.core.constants import World, Player, Enemy, Bullet, Items, Physics, FireDamage, get_random_drop_offset
from src.core.enums import ItemType, ItemEffect, get_item_effect, get_item_display_name
from src.core.collisionOptimizer import CollisionOptimizer


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
        
        # Initialize collision optimizer
        self.collision_optimizer = CollisionOptimizer(World.CAMERA_WORLD_WIDTH, World.CAMERA_WORLD_HEIGHT)
        
        self.current_room: Optional[Room] = None
        self.player: Optional[Player] = None
        self.bullets: List[Bullet] = []         
        self.enemy_bullets: List[Bullet] = []   
        self.render_queue: List = []
        self.last_teleport_time: float = 0.0 
        self.start_time = pygame.time.get_ticks()
        
        # Fire damage system
        self.last_fire_damage_time: float = 0.0
        
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
                
                # Initialize collision optimizer with static objects
                self._initialize_room_collisions()
                
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
        
    # Input Processing
    
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

    def process_player_mouse(self, mouse_pos: Tuple[int, int]) -> bool:
        """Processa o clique do mouse do jogador. Retorna True se o tiro foi bem-sucedido."""
        if not self.player:
            return False
        
        world_mouse_pos = self.camera.screen_to_world(mouse_pos)
        bullet = self.player.shoot(world_mouse_pos)
        if bullet:
            self.bullets.append(bullet)
            return True
        return False

    # Update Logic
    
    def update(self, delta_time: float = None) -> None:
        if not self.current_room:
            return
        
        # Update collision optimizer frame (for cache management)
        self.collision_optimizer.update_frame()
        
        # Update player
        if self.player:
            self.player.update(delta_time)
            self.camera.follow_target(self.player)
        
        # Update game objects
        self._update_enemies()
        self._update_bullets()
        self._update_enemy_bullets()
            
        # Update collisions and interactions
        self._check_item_collisions()
        self._check_door_collisions()
        self._check_fire_damage(delta_time)
        
        # Update visuals
        try:
            self._update_tile_animations(delta_time)
        except Exception as e:
            print(f"Warning: Tile animation error: {e}")
        
        self._update_render_queue()
    
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
            
            if self.current_room.check_collision((bullet.position.x, bullet.position.y), Bullet.COLLISION_CHECK_SIZE):
                self.bullets.remove(bullet)
                continue
        
        self.current_room.handle_bullet_collisions(self.bullets, self._generate_enemy_drop)
    
    def _check_item_collisions(self) -> None:
        if not self.player or not self.current_room:
            return
        
        for item in self.current_room.items[:]:
            if self.player.collides_with(item):
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
            if self.player.collides_with(door):
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
        # Debug: print(f"TELEPORTE: Mudando para {target_room.id}")
        self.current_room = target_room
        room_width, room_height = self.current_room.size
        self.camera.set_world_bounds(room_width, room_height)
        
        # Initialize collision optimizer with static objects for the new room
        self._initialize_room_collisions()
        
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
            
            # Use optimized collision check
            collision = self.collision_optimizer.check_collision_optimized(temp_rect, static_only=True)
            
            if collision:
                spawn_position = self._find_safe_spawn(spawn_position)
            
            self.player.position = spawn_position
            self.camera.follow_target(self.player)
            
            self.player.moving = False
            
            # Debug: print(f"Player posicionado em: {self.player.position}")
    
    def _find_safe_spawn(self, original_spawn: Tuple[float, float]) -> Tuple[float, float]:
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
                    
                    collision = self.collision_optimizer.check_collision_optimized(test_rect, static_only=True)
                    if not collision:
                        # Debug: print(f"Posição livre encontrada: ({test_x:.1f}, {test_y:.1f})")
                        return (test_x, test_y)
        
        print("Nenhuma posição livre encontrada, usando centro do mapa")
        return (self.current_room.size[0] // 2, self.current_room.size[1] // 2)
    
    def _initialize_room_collisions(self) -> None:
        """Initialize collision optimizer with static objects from current room"""
        if not self.current_room:
            return
        
        # Clear existing static objects
        # Note: We'll keep a simple approach for now - just clear everything and re-add
        self.collision_optimizer = CollisionOptimizer(World.CAMERA_WORLD_WIDTH, World.CAMERA_WORLD_HEIGHT)
        
        # Add wall rectangles as static collision objects
        wall_rects = self.current_room.get_wall_rects()
        for i, wall_rect in enumerate(wall_rects):
            wall_id = f"wall_{self.current_room.id}_{i}"
            self.collision_optimizer.add_static_object(wall_id, None, wall_rect)
        
        # Debug: print(f"Initialized collision optimizer with {len(wall_rects)} static objects")
    
    def get_collision_stats(self) -> Dict[str, int]:
        """Get collision optimization performance stats"""
        return self.collision_optimizer.get_performance_stats()
    

    # Rendering
    
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
    
    def render_debug_hitboxes(self, show_debug: bool, show_detailed: bool = False) -> None:
        """Renderiza os hitboxes de debug se habilitado"""
        if not show_debug:
            return
            
        camera_offset = self.camera.get_offset()
        
        # Debug do player
        if self.player:
            self.player.draw_debug_hitbox(self.screen, camera_offset, (0, 255, 0))  # Verde
            if show_detailed:
                self._draw_hitbox_info(self.player, camera_offset, "Player (Triangular)")
        
        # Debug dos inimigos
        if self.current_room:
            for enemy in self.current_room.enemies:
                if enemy.is_alive():
                    enemy.draw_debug_hitbox(self.screen, camera_offset, (255, 0, 0))  # Vermelho
                    if show_detailed:
                        hitbox_type = "Triangular" if getattr(enemy, 'hitbox_type', 'rect') == "triangle" else "Rectangular"
                        self._draw_hitbox_info(enemy, camera_offset, f"Enemy ({hitbox_type})")
            
            # Debug dos itens  
            for item in self.current_room.items:
                item.draw_debug_hitbox(self.screen, camera_offset, (255, 255, 0))  # Amarelo
                if show_detailed:
                    self._draw_hitbox_info(item, camera_offset, "Item (Rect)")
                
            # Debug das portas
            for door in self.current_room.doors:
                door.draw_debug_hitbox(self.screen, camera_offset, (0, 255, 255))  # Ciano
                if show_detailed:
                    self._draw_hitbox_info(door, camera_offset, "Door (Rect)")
            
            # Debug das estruturas/paredes do mundo
            self._draw_world_structures(camera_offset, show_detailed)
        
        # Debug das balas
        for bullet in self.bullets:
            bullet.draw_debug_hitbox(self.screen, camera_offset, (255, 0, 255))  # Magenta
            if show_detailed:
                self._draw_hitbox_info(bullet, camera_offset, "Player Bullet")
            
        for enemy_bullet in self.enemy_bullets:
            enemy_bullet.draw_debug_hitbox(self.screen, camera_offset, (255, 128, 0))  # Laranja
            if show_detailed:
                self._draw_hitbox_info(enemy_bullet, camera_offset, "Enemy Bullet")
    
    def _draw_hitbox_info(self, obj, camera_offset, label):
        """Desenha informações sobre o hitbox de um objeto"""
        try:
            import pygame
            
            # Posição na tela
            screen_x = int(obj.position[0] - camera_offset[0])
            screen_y = int(obj.position[1] - camera_offset[1]) - 20  # Acima do objeto
            
            # Criar texto
            font = pygame.font.Font(None, 16)
            text = font.render(label, True, (255, 255, 255))
            
            # Background para o texto
            text_rect = text.get_rect()
            text_rect.topleft = (screen_x - text_rect.width // 2, screen_y)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), text_rect)
            
            # Desenhar texto
            self.screen.blit(text, text_rect.topleft)
            
        except Exception as e:
            pass  # Ignorar erros de renderização
    
    def _draw_world_structures(self, camera_offset, show_detailed):
        """Desenha as hitboxes das estruturas/paredes do mundo"""
        if not self.current_room:
            return
            
        try:
            # Obter retângulos das paredes
            wall_rects = self.current_room.get_wall_rects()
            
            # OTIMIZAÇÃO: Só desenhar paredes visíveis na tela
            camera_rect = pygame.Rect(camera_offset[0], camera_offset[1], self.width, self.height)
            
            visible_walls = 0
            for wall_rect in wall_rects:
                # Só processar se estiver visível na câmera
                if not camera_rect.colliderect(wall_rect):
                    continue
                    
                visible_walls += 1
                # Limitar para performance - só mostrar primeiras 100 paredes visíveis
                if visible_walls > 100:
                    break
                # Desenhar hitbox da parede
                screen_rect = wall_rect.copy()
                screen_rect.topleft = (
                    wall_rect.left - camera_offset[0],
                    wall_rect.top - camera_offset[1]
                )
                
                # Cor diferente para estruturas - branco com alpha
                pygame.draw.rect(self.screen, (255, 255, 255), screen_rect, 1)
                
                if show_detailed:
                    # Adicionar informação sobre tile de colisão
                    center_x = screen_rect.centerx
                    center_y = screen_rect.centery - 10
                    
                    font = pygame.font.Font(None, 12)
                    text = font.render("Wall", True, (255, 255, 255))
                    
                    # Background pequeno para o texto
                    text_rect = text.get_rect()
                    text_rect.center = (center_x, center_y)
                    pygame.draw.rect(self.screen, (0, 0, 0, 128), text_rect)
                    
                    self.screen.blit(text, text_rect.topleft)
                    
            # Também desenhar zonas de fogo se existirem
            fire_rects = self.current_room.get_fire_rects()
            for fire_rect in fire_rects:
                screen_rect = fire_rect.copy()
                screen_rect.topleft = (
                    fire_rect.left - camera_offset[0],
                    fire_rect.top - camera_offset[1]
                )
                
                # Cor laranja para zonas de fogo
                pygame.draw.rect(self.screen, (255, 100, 0), screen_rect, 1)
                
                if show_detailed:
                    center_x = screen_rect.centerx
                    center_y = screen_rect.centery - 10
                    
                    font = pygame.font.Font(None, 12)
                    text = font.render("Fire", True, (255, 100, 0))
                    
                    text_rect = text.get_rect()
                    text_rect.center = (center_x, center_y)
                    pygame.draw.rect(self.screen, (0, 0, 0, 128), text_rect)
                    
                    self.screen.blit(text, text_rect.topleft)
                    
        except Exception as e:
            # Debug: print do erro para investigar
            print(f"Debug: Erro ao desenhar estruturas: {e}")

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
            # Objetos sem image mas com draw() method (como balas)
            if hasattr(obj, 'draw'):
                original_pos = obj.position if hasattr(obj, 'position') else None
                obj.position = screen_pos
                obj.draw(self.screen)
                if original_pos:
                    obj.position = original_pos
        else:
            if hasattr(obj, 'draw'):
                original_pos = obj.position if hasattr(obj, 'position') else None
                obj.position = screen_pos
                obj.draw(self.screen)
                if original_pos:
                    obj.position = original_pos
        

    # Utility Methods
    
    def change_room(self, room_index: int) -> None:
        if 0 <= room_index < len(self.map.rooms):
            self.current_room = self.map.rooms[room_index]
            if self.current_room:
                room_width, room_height = self.current_room.size
                self.camera.set_world_bounds(room_width, room_height)
                
                # Initialize collision optimizer with static objects
                self._initialize_room_collisions()
                
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
            
            if bullet.collides_with(self.player):
                damage = bullet.damage
                self.player.take_damage(damage)
                
                # Play hurt sound
                if self.audio_manager:
                    self.audio_manager.play_sound('hurt')
                
                self.enemy_bullets.remove(bullet)
    
    def cleanup(self) -> None:
        self.bullets.clear()
        self.enemy_bullets.clear()  
        self.render_queue.clear()
        print("GameWorld limpo")
    
    # ==========================================
    # FIRE DAMAGE SYSTEM
    # ==========================================
    
    def _check_fire_damage(self, delta_time: float) -> None:
        """Check if player is standing on fire tiles and apply damage"""
        if not self.player or not self.current_room or not self.player.is_alive():
            return
            
        # Check if player is touching fire zones
        player_rect = self.player.rect
        is_on_fire = self.current_room.check_fire_damage(player_rect)
        
        if is_on_fire:
            current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
            
            # Apply damage every DAMAGE_INTERVAL seconds
            if current_time - self.last_fire_damage_time >= FireDamage.DAMAGE_INTERVAL:
                self.player.take_damage(FireDamage.DAMAGE_PER_TICK)
                self.last_fire_damage_time = current_time
                
                # Play hurt sound for fire damage
                if self.audio_manager:
                    self.audio_manager.play_sound('hurt')
                
                print(f"🔥 Player taking fire damage! Health: {self.player.health}")
    
    def _update_tile_animations(self, delta_time: float) -> None:
        """Update animated tiles in current room"""
        if self.current_room:
            old_frames = self.current_room.current_tile_frames.copy()
            self.current_room.update_tile_animations(delta_time)
            
            # Only update background if frames actually changed (for performance)
            if self.current_room.current_tile_frames != old_frames:
                self.current_room.update_background()
