import pygame

class Enemy:
    def __init__(self, name, position, damage, speed, health, weapon, ammo, status):
        self.name = name
        self.position = pygame.Vector2(position)
        self.damage = damage
        self.speed = speed
        self.health = health
        self.weapon = weapon
        self.ammo = ammo
        self.status = status

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
            self.die()

    def die(self):
        print("Died")


# enemy = Enemy(health=100, damage=10, speed=5, position=(0, 0), rotation=0)
# print(enemy.health)  # Output: 100