import pygame
from typing import List, Optional, Tuple
import math

from src.ui.hud import Hud
from src.world.map import Map


class GameWorld:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int):
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.width: int = width
        self.height: int = height
        
        self.game_map: Map = Map("src/world/rooms")
        self.game_map.generate_seed_test()  # Usar apenas Mapa1 para teste
        self.current_room = self.game_map.current_room
        self.player = self.current_room.player
        
        self.player.screen_width = self.width
        self.player.screen_height = self.height
        
        self.bullets: List = []
        
        self.hud: Hud = Hud(self.screen, self.player, self.clock)
        
        self.render_queue: List = []

    def _update_enemies(self) -> None:
        """Atualiza a lógica dos inimigos."""
        if not self.current_room or not self.current_room.enemies:
            return
        
        for enemy in self.current_room.enemies[:]:  # Usar slice para permitir remoção durante iteração
            if enemy.is_alive():
                # Atualizar comportamento do inimigo (IA simples por enquanto)
                # Futuramente pode incluir pathfinding, ataque, etc.
                pass
            else:
                # Remover inimigo morto
                self.current_room.enemies.remove(enemy)

    def _update_bullets(self) -> None:
        """Atualiza projéteis no jogo."""
        if not self.bullets:
            return
        
        dt = self.clock.get_time() / 1000.0
        
        for bullet in self.bullets[:]:  # Usar slice para permitir remoção
            # Atualizar posição da bala (retorna False se saiu da tela)
            if not bullet.update(dt, self.width, self.height):
                self.bullets.remove(bullet)
                continue
            
            # Verificar colisão com paredes (matriz de colisão)
            if self.current_room.check_collision((bullet.position.x, bullet.position.y), (2, 2)):
                self.bullets.remove(bullet)
                continue
            
            # Verificar colisão com inimigos
            self._check_bullet_enemy_collision(bullet)

    def _check_bullet_enemy_collision(self, bullet) -> None:
        """Verifica colisão entre uma bala e inimigos."""
        # Usar o hitbox da bala em vez de criar um novo
        bullet_rect = bullet.hitbox
    
        for enemy in self.current_room.enemies[:]:
            enemy_rect = pygame.Rect(
                enemy.position.x,
                enemy.position.y,
                enemy.size[0],
                enemy.size[1]
            )
            
            if bullet_rect.colliderect(enemy_rect):
                # Aplicar dano ao inimigo
                enemy.take_damage(bullet.damage)
                
                # Remover a bala
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                
                print(f"💥 Inimigo atingido! Vida restante: {enemy.health}")
                break

    def _check_item_collisions(self) -> None:
        """Verifica colisões entre o player e itens coletáveis."""
        if not self.player or not self.current_room or not self.current_room.items:
            return
        
        player_rect = pygame.Rect(
            self.player.position.x,
            self.player.position.y,
            self.player.size[0],
            self.player.size[1]
        )
        
        for item in self.current_room.items[:]:  # Usar slice para permitir remoção
            item_rect = pygame.Rect(
                item.position[0],
                item.position[1],
                item.size[0],
                item.size[1]
            )
            
            if player_rect.colliderect(item_rect):
                # Item coletado - aplicar efeito e remover
                self._apply_item_effect(item)
                self.current_room.items.remove(item)
                print(f"🎁 Item coletado: {item.name}")

    def _apply_item_effect(self, item) -> None:
        """Aplica o efeito de um item coletado ao player."""
        if not self.player:
            return
        
        # Implementar baseado no efeito do item
        if hasattr(item, 'effect'):
            if item.effect == "health":
                # Curar o player
                if hasattr(item, 'value'):
                    self.player.health = min(self.player.health + item.value, 100)  # Max 100 HP
                    print(f"💚 Vida restaurada: +{item.value}")
            elif item.effect == "ammo":
                # Dar munição
                if hasattr(item, 'value'):
                    self.player.ammo += item.value
                    print(f"🔫 Munição coletada: +{item.value}")

    def _keep_player_in_bounds(self) -> None:
        """Mantém o player dentro dos limites da sala."""
        if not self.player or not self.current_room:
            return
        
        # Obter hitbox do player
        hitbox_size = getattr(self.player, 'hitbox_size', self.player.size)
        
        # Limites da sala
        room_width, room_height = self.current_room.size
        
        # Ajustar posição para manter dentro dos limites
        self.player.position.x = max(0, min(self.player.position.x, room_width - hitbox_size[0]))
        self.player.position.y = max(0, min(self.player.position.y, room_height - hitbox_size[1]))

    def _update_render_queue(self) -> None:
        """Atualiza a fila de renderização com todos os objetos visíveis."""
        self.render_queue.clear()
        
        if not self.current_room:
            return
        
        # Adicionar player
        if self.player:
            self.render_queue.append(self.player)
        
        # Adicionar inimigos
        for enemy in self.current_room.enemies:
            if enemy.is_alive():
                self.render_queue.append(enemy)
        
        # Adicionar itens
        for item in self.current_room.items:
            self.render_queue.append(item)
        
        # Adicionar portas
        for door in self.current_room.doors:
            self.render_queue.append(door)
        
        for bullet in self.bullets:
            self.render_queue.append(bullet)
            
    def update(self, delta_time: float = None) -> None:
        """Atualiza apenas a lógica interna do mundo"""
        if not self.current_room:
            return
        
        # Atualizar entidades
        self._update_enemies()
        self._update_bullets()
        
        # Verificar interações
        self._check_item_collisions()
        
        # Atualizar fila de renderização
        self._update_render_queue()
        
        # Futuramente: 
        # - Verificar condições de vitória/derrota
        # - Atualizar timers
        # - Processar efeitos visuais
        # - etc.

    def handle_player_key_press(self, direction: str) -> None:
        """Recebe comandos de movimento do GameManager"""
        if not self.player or not self.current_room:
            return
            
        # Calcular delta time
        dt = self.clock.get_time() / 1000.0
        speed = self.player.speed * dt
        
        # Aplicar movimento baseado no comando recebido
        current_pos = (self.player.position.x, self.player.position.y)
        hitbox_size = getattr(self.player, 'hitbox_size', self.player.size)
        
        # Calcular novo movimento baseado na direção
        new_pos = current_pos
        if direction == "up":
            new_pos = (current_pos[0], current_pos[1] - speed)
        elif direction == "down":
            new_pos = (current_pos[0], current_pos[1] + speed)
        elif direction == "left":
            new_pos = (current_pos[0] - speed, current_pos[1])
        elif direction == "right":
            new_pos = (current_pos[0] + speed, current_pos[1])
        
        # Verificar colisão e aplicar movimento
        if not self.current_room.check_collision(new_pos, hitbox_size):
            self.player.position.x = new_pos[0]
            self.player.position.y = new_pos[1]
            self._keep_player_in_bounds()

    def handle_player_mouse_click(self) -> None:
        """Recebe comandos de disparo do GameManager"""
        if not self.player or not self.player.weapon:
            return
        
        # Verificar se o player tem munição
        if self.player.ammo <= 0:
            print("⚠️ Sem munição!")
            return
        
        # Reduzir munição
        self.player.ammo -= 1
        
        # Obter posição do mouse
        mouse_pos = pygame.mouse.get_pos()
        
        # Calcular posição inicial da bala (centro do player)
        player_center = (
            self.player.position.x + self.player.size[0] / 2,
            self.player.position.y + self.player.size[1] / 2
        )
        
        # ✅ CORREÇÃO: Calcular ângulo usando math.atan2 (mais preciso)
        
        
        # Vetor direção do player para o mouse
        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        
        # Calcular ângulo em radianos e converter para graus
        angle_rad = math.atan2(dy, dx)
        rotation = math.degrees(angle_rad)
        
        # Criar projétil usando a assinatura correta da sua classe Bullet
        from src.model.objects.bullet import Bullet

        bullet = Bullet(
            id=f"bullet_{len(self.bullets)}",  # ID único
            position=player_center,            # Posição inicial
            size=(8, 8),                      # Tamanho da bala
            speed=500,                        # Velocidade
            damage=self.player.weapon.damage, # Dano
            rotation=rotation                 # Rotação em direção ao mouse
        )
        
        # Adicionar à lista de balas
        self.bullets.append(bullet)
        
        print(f"🔫 Player atirou! Ângulo: {rotation:.1f}°")

    def render(self) -> None:
        if self.current_room.background:
            self.screen.blit(self.current_room.background, (0, 0))
        else:
            self.screen.fill((88, 71, 71))
        
        for obj in self.render_queue:
            obj.draw(self.screen)
        
        for door in self.current_room.doors:
            pygame.draw.rect(self.screen, (100, 100, 255), door.hitbox)
        
        for item in self.current_room.items:
            item.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        self.hud.draw()