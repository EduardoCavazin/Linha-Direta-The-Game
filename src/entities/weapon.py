import pygame

class Weapon:
    
    def __init__(self, name, damage, maxAmmo):
        self.name = name
        self.damage = damage
        self.max_ammo = maxAmmo

    def __str__(self):
        return f"{self.name} - Dano: {self.damage}, Capacidade: {self.maxAmmo}"
    
    def __repr__(self):
        return f"{self.name} - Dano: {self.damage}, Capacidade: {self.maxAmmo}"

    def __eq__(self, other):
        return self.name == other.name and self.damage == other.damage and self.max_ammo == other.max_ammo
        
