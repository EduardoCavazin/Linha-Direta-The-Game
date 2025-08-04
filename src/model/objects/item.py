import os
import pygame
from typing import Tuple, Any
from src.model.objects.gameObject import GameObject
from src.core.utils import load_image

class Item(GameObject):
    def __init__(self, id: str, name: str, position: Tuple[float, float], size: Tuple[int, int], effect: str, sprite_name: str = None) -> None:
        super().__init__(id, position, size)
        self.name: str = name
        self.effect: str = effect
        self.value: int = 0  # Valor padrão para efeitos de cura/munição
        
        # Se não foi especificado um sprite, tenta usar o ID
        if sprite_name is None:
            sprite_name = f"sprites/{self.id}.png"
        
        try:
            self.image = load_image(sprite_name, size)
        except Exception as e:
            print(f"❌ Erro ao carregar sprite {sprite_name}: {e}")
            print(f"🔧 Tentando fallback para imagem genérica...")
            # Tenta carregar uma imagem genérica como fallback
            try:
                fallback_sprite = "sprites/player.png" if "health" in sprite_name.lower() else "sprites/ammo.png"
                self.image = load_image(fallback_sprite, size)
                print(f"✅ Fallback carregado: {fallback_sprite}")
            except:
                # Se ainda falhar, cria um círculo colorido em vez de um quadrado
                self.image = pygame.Surface(size, pygame.SRCALPHA)
                color = (0, 255, 0) if "health" in sprite_name.lower() else (0, 100, 255)  # Verde para vida, azul para munição
                pygame.draw.circle(self.image, color, (size[0]//2, size[1]//2), min(size)//2)
                print(f"🎨 Criado ícone colorido: {'verde' if 'health' in sprite_name.lower() else 'azul'}")
    
    @property
    def position(self) -> Tuple[float, float]:
        """Retorna a posição como tupla"""
        return (self._position.x, self._position.y)
    
    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        """Define a posição e atualiza a hitbox"""
        self._position = pygame.Vector2(value)
        self.hitbox.x, self.hitbox.y = value
        
    def use(self, target: Any) -> None:
        if self.effect == "heal":
            target.health += 20
            if target.health > 100:
                target.health = 100
        elif self.effect == "ammo":
            if target.weapon is not None:
                target.ammo = min(target.ammo + 10, target.weapon.max_ammo)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.hitbox.topleft)
