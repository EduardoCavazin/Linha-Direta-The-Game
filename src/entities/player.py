import pygame

class Player:
    def __init__(self, name, position, speed, health, weapon, ammo, status):
        self.name = name
        self.position = pygame.Vector2(position)
        self.speed = speed
        self.health = health
        self.weapon = weapon
        self.ammo = ammo
        self.status = status
        self.image = pygame.image.load('assets\sprites\player.png')  # Carregar a imagem do jogador
        self.image = pygame.transform.scale(self.image, (50, 50))  # Redimensionar a imagem, se necessário

    def move(self, direction):
        if direction == "up":
            self.position.y -= self.speed
        elif direction == "down":
            self.position.y += self.speed
        elif direction == "left":
            self.position.x -= self.speed
        elif direction == "right":
            self.position.x += self.speed

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def is_alive(self):
        return self.status != "dead"

    def attack(self, target):
        if self.weapon is not None and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)

    def reload(self):
        self.ammo = self.weapon.max_ammo

    def die(self):
        self.status = "dead"
        print(f"{self.name} has died.")

    def draw(self, screen):
        screen.blit(self.image, self.position)