import pygame
from src.model.objects.gameObject import GameObject

class Entity(GameObject):
    def __init__(self, id, position, size, speed, health, name, weapon, ammo, image, status):
        super().__init__(id, position, size)
        self.speed = speed  # Velocidade em pixels por segundo
        self.health = health
        self.name = name
        self.weapon = weapon
        self.ammo = ammo
        self.image = image
        self.status = status

    def move(self, direction, delta_time, obstacles=None):
        """
        Move a entidade em uma direção específica, ajustando pelo delta time.

        :param direction: Direção do movimento ("up", "down", "left", "right").
        :param delta_time: Tempo decorrido entre os quadros (em segundos).
        :param obstacles: Lista de obstáculos para verificar colisões (opcional).
        """
        new_position = self.position.copy()
        distance = self.speed * delta_time  # Distância baseada no tempo

        if direction == "up":
            new_position.y -= distance
        elif direction == "down":
            new_position.y += distance
        elif direction == "left":
            new_position.x -= distance
        elif direction == "right":
            new_position.x += distance

        # Verificar colisões, se necessário
        if obstacles:
            new_hitbox = pygame.Rect(new_position.x, new_position.y, self.size[0], self.size[1])
            for obstacle in obstacles:
                if new_hitbox.colliderect(obstacle.hitbox):
                    return  # Movimento bloqueado pela colisão

        # Atualizar posição e hitbox
        self.position = new_position
        self.hitbox.topleft = (self.position.x, self.position.y)
    
    def attack(self, target):
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        self.status = "dead"
        print(f"Entity {self.id} has died.")
    
    def draw(self, screen):
        screen.blit(self.image, self.position)
