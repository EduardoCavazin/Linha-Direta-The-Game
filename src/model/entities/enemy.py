from src.model.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        # Defina uma imagem padrão ou use None se não houver uma imagem específica
        image = None  # Ou carregue uma imagem padrão: pygame.image.load("caminho/para/imagem.png")
        super().__init__(id, name, position, size, speed, health, weapon, ammo, image, status)
