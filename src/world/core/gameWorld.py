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


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int) -> None:
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        
        self.map: Map = Map()
        self.entity_factory: EntityFactory = EntityFactory()
        
        self.camera: Camera = Camera(width, height, 2000, 2000)
        
        self.current_room: Optional[Room] = None
        self.player: Optional[Player] = None
        self.bullets: List[Bullet] = []         # Balas do jogador
        self.enemy_bullets: List[Bullet] = []   # Balas dos inimigos
        self.render_queue: List = []
        self.last_teleport_time: float = 0.0 
        self.start_time = pygame.time.get_ticks()
        
        self._initialize_world()
    
    def _initialize_world(self) -> None:
        if self.map.rooms:
            self.current_room = self.map.rooms[0]
            if self.current_room:
                room_width, room_height = self.current_room.size
                self.camera.set_world_bounds(room_width, room_height)
                # Trava todas as portas no início
                self._lock_room_doors()
                # Se a sala inicial não tem inimigos, desbloqueia as portas
                if self.current_room.get_alive_enemies_count() == 0:
                    self._unlock_room_doors()
            self._spawn_player()
        else:
            print("ERRO: Nenhuma sala carregada!")
    
    def _lock_room_doors(self) -> None:
        """Trava todas as portas da sala atual"""
        if not self.current_room:
            return
            
        for door in self.current_room.doors:
            door.lock()
    
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

        # Chame move apenas uma vez, passando todas as direções
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
        
        if self.player:
            self.player.update(delta_time)
            self.camera.follow_target(self.player)
    
        self._update_enemies()
        self._update_bullets()
        self._update_enemy_bullets()
        self._check_item_collisions()
        self._check_door_collisions()
        
        self._update_render_queue()
    
    def _update_enemies(self) -> None:
        if not self.player or not self.current_room:
            return
        
        player_pos = self.player.position
        delta_time = self.clock.get_time() / 1000.0
        
        # Armazena o número de inimigos vivos antes do update
        enemies_alive_before = self.current_room.get_alive_enemies_count()
        
        for enemy in self.current_room.enemies[:]:
            if enemy.is_alive():
                # Update do inimigo que pode retornar uma bala
                enemy_bullet = enemy.update(player_pos, delta_time)
                if enemy_bullet:
                    self.enemy_bullets.append(enemy_bullet)
                    print(f"🔫 Inimigo {enemy.id} atirou!")
            else:
                self.current_room.enemies.remove(enemy)
        
        # Verifica se a sala foi limpa após eliminar inimigos
        enemies_alive_after = self.current_room.get_alive_enemies_count()
        
        # Se havia inimigos antes e agora não há mais, a sala foi limpa
        if enemies_alive_before > 0 and enemies_alive_after == 0:
            self.current_room.mark_cleared()
            self._unlock_room_doors()
            print("🎉 Sala limpa! As portas foram desbloqueadas.")
    
    def _unlock_room_doors(self) -> None:
        """Desbloqueia todas as portas da sala atual"""
        if not self.current_room:
            return
            
        for door in self.current_room.doors:
            door.unlock()
    
    def _generate_enemy_drop(self, enemy_position: Tuple[float, float]) -> None:
        """Gera um item aleatório na posição do inimigo morto com 50/50 de chance entre heal e ammo"""
        if not self.current_room:
            return
        
        # 50% de chance de dropar heal, 50% de chance de dropar ammo
        drop_type = random.choice(["HealthPack", "AmmoPack"])
        
        # Adiciona um pequeno offset aleatório para evitar sobreposição
        offset_x = random.uniform(-15, 15)
        offset_y = random.uniform(-15, 15)
        drop_position = (enemy_position[0] + offset_x, enemy_position[1] + offset_y)
        
        print(f"🎯 Gerando drop na posição: {drop_position}")
        
        dropped_item = self.entity_factory.create_item(drop_type, drop_position)
        
        if dropped_item:
            # Configura os valores dos itens baseado no tipo
            if drop_type == "HealthPack":
                dropped_item.effect = "heal"
                dropped_item.value = 25  # Cura 25 de vida
            elif drop_type == "AmmoPack":
                dropped_item.effect = "ammo"
                dropped_item.value = 8   # Adiciona 8 munições
            
            self.current_room.items.append(dropped_item)
            
            item_name = "Kit Médico" if drop_type == "HealthPack" else "Munição"
            print(f"💎 {item_name} foi dropado!")
        else:
            print("❌ Falha ao criar o item dropado!")
    
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
        
        # Passa o callback para gerar drops quando inimigos morrerem
        self.current_room.handle_bullet_collisions(self.bullets, self._generate_enemy_drop)
    
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
                # Verifica se a sala está limpa antes de permitir o teleporte
                if not self.current_room.is_clear():
                    enemies_remaining = self.current_room.get_alive_enemies_count()
                    print(f"Não é possível avançar! Elimine os {enemies_remaining} inimigos restantes.")
                    return
                
                self._handle_door_teleport(door)
                self.last_teleport_time = current_time
                break  

    def _handle_door_teleport(self, door) -> None:
        possible_rooms = [room for room in self.map.rooms if room != self.current_room]
        if not possible_rooms:
            print("Nenhuma outra sala disponível para teleporte!")
            return

        target_room = random.choice(possible_rooms)
        print(f"Teletransportando de {self.current_room.id} para {target_room.id}")

        self.current_room = target_room
        room_width, room_height = self.current_room.size
        self.camera.set_world_bounds(room_width, room_height)
        
        # Configura o estado das portas da nova sala
        self._lock_room_doors()
        if self.current_room.is_clear():
            self._unlock_room_doors()
            print("Sala já estava limpa - portas desbloqueadas.")
        else:
            enemies_count = self.current_room.get_alive_enemies_count()
            print(f"Nova sala com {enemies_count} inimigos - elimine todos para desbloquear as portas.")

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
        self.render_queue.extend(self.enemy_bullets)  # Adiciona balas inimigas também
        
        # Debug: mostra quantos itens estão sendo renderizados (apenas quando há mudança)
        if len(self.current_room.items) > 0 and not hasattr(self, '_last_items_count'):
            self._last_items_count = len(self.current_room.items)
            print(f"🎨 Renderizando {len(self.current_room.items)} itens na tela")
        elif len(self.current_room.items) != getattr(self, '_last_items_count', 0):
            self._last_items_count = len(self.current_room.items)
            print(f"🎨 Renderizando {len(self.current_room.items)} itens na tela")
        
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
                
                # Configura o estado das portas da nova sala
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
        """Atualiza as balas inimigas e verifica colisões"""
        if not self.current_room or not self.player:
            return
        
        delta_time = self.clock.get_time() / 1000.0
        
        for bullet in self.enemy_bullets[:]:
            # Atualiza a bala com delta_time
            if not bullet.update(delta_time, self.width, self.height):
                self.enemy_bullets.remove(bullet)
                continue
            
            # Verifica colisão com paredes usando o método check_collision da room
            bullet_pos = (bullet.position.x, bullet.position.y)
            bullet_size = (bullet.hitbox.width, bullet.hitbox.height)
            if self.current_room.check_collision(bullet_pos, bullet_size):
                self.enemy_bullets.remove(bullet)
                continue
            
            # Verifica colisão com o jogador
            if bullet.hitbox.colliderect(self.player.rect):
                # Player toma dano
                damage = bullet.damage
                self.player.take_damage(damage)
                print(f"💥 Player tomou {damage} de dano! Vida: {self.player.health}")
                
                # Remove a bala
                self.enemy_bullets.remove(bullet)
    
    def cleanup(self) -> None:
        self.bullets.clear()
        self.enemy_bullets.clear()  # Limpa balas inimigas também
        self.render_queue.clear()
        print("GameWorld limpo")
