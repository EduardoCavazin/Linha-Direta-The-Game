import pygame
from src.model.objects.movableObject import MovableObject

class Entity(MovableObject):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, image, status, rotation=0):
        # Agora passamos o parâmetro rotation com valor padrão 0
        super().__init__(id, position, size, speed, rotation)
        self.name = name
        self.health = health
        self.weapon = weapon
        self.ammo = ammo
        self.image = image
        self.status = status

    def move(self, direction, delta_time, obstacles=None):
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

        if obstacles:
            new_hitbox = pygame.Rect(new_position.x, new_position.y, self.size[0], self.size[1])
            for obstacle in obstacles:
                if new_hitbox.colliderect(obstacle.hitbox):
                    return  # Movimento bloqueado pela colisão

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
