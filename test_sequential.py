#!/usr/bin/env python3
"""
Teste da progressão sequencial: Mapa1 -> Mapa2 -> Mapa 3
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.world.core.gameWorld import GameWorld
import pygame

def test_sequential_progression():
    print("=== TESTE DE PROGRESSÃO SEQUENCIAL ===")
    
    # Inicializar pygame mínimo
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Criar GameWorld
    game_world = GameWorld(screen, clock, 800, 600)
    
    print(f"Sala inicial: {game_world.current_room.id}")
    
    # Verificar portas na sala inicial
    print(f"Portas na sala inicial:")
    for door in game_world.current_room.doors:
        print(f"  - {door.name}: destino = {door.destination}")
    
    # Testar progressão sequencial
    door = None
    for d in game_world.current_room.doors:
        if d.name == "Door":
            door = d
            break
    
    if door:
        print(f"\n=== TESTANDO PROGRESSÃO SEQUENCIAL ===")
        
        # Teste 1: Mapa1 -> Mapa2
        current = game_world.current_room.id
        print(f"Estado atual: {current}")
        game_world._handle_door_teleport(door)
        new_current = game_world.current_room.id
        print(f"Após porta: {new_current}")
        print(f"✅ Progressão {current} -> {new_current}: {'OK' if new_current == 'Mapa2' else 'ERRO'}")
        
        # Teste 2: Mapa2 -> Mapa 3
        current = game_world.current_room.id
        game_world._handle_door_teleport(door)
        new_current = game_world.current_room.id
        print(f"Após porta: {new_current}")
        print(f"✅ Progressão {current} -> {new_current}: {'OK' if new_current == 'Mapa 3' else 'ERRO'}")
        
        # Teste 3: Mapa 3 -> Mapa1 (loop)
        current = game_world.current_room.id
        game_world._handle_door_teleport(door)
        new_current = game_world.current_room.id
        print(f"Após porta: {new_current}")
        print(f"✅ Progressão {current} -> {new_current}: {'OK' if new_current == 'Mapa1' else 'ERRO'}")
        
    else:
        print("❌ Porta 'Door' não encontrada na sala inicial")
    
    pygame.quit()
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_sequential_progression()
