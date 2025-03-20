import pygame

class Entity:
    def __init__(self, id, position, size, status):
        self.id = id
        self.position = pygame.Vector2(position)
        self.size = size
        self.status = status
        self.hitbox = pygame.Rect(position[0], position[1], size[0], size[1])
        
    
    def move(self, direction):
        if direction == "up":
            self.position.y -= self.speed
        elif direction == "down":
            self.position.y += self.speed
        elif direction == "left":
            self.position.x -= self.speed
        elif direction == "right":
            self.position.x += self.speed
        
        self.hitbox.topleft = (self.position.x, self.position.y)
        
    def is_alive(self):
        return self.status != "dead"
    
    def die(self):
        self.status = "dead"
        print(f"Entity {self.id} has died.")