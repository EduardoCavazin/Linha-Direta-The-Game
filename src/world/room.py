from typing import List, Optional, Any, Tuple

class Room:
    def __init__(
        self,
        id: str,
        size: Tuple[int, int],
        objects: Optional[List[Any]] = None,
        enemies: Optional[List[Any]] = None,
        items: Optional[List[Any]] = None,
        doors: Optional[List[Any]] = None,
        player: Optional[Any] = None,
        cleared: bool = False,
        visited: bool = False
    ) -> None:
        self.id: str = id
        self.size: Tuple[int, int] = size
        self.objects: List[Any] = objects if objects is not None else []
        self.enemies: List[Any] = enemies if enemies is not None else []
        self.items: List[Any] = items if items is not None else []
        self.doors: List[Any] = doors if doors is not None else []
        self.player: Optional[Any] = player
        self.cleared: bool = cleared
        self.visited: bool = visited

    def spawn_enemy(self, enemy: Any) -> None:
        self.enemies.append(enemy)
        
    def spawn_item(self, item: Any) -> None:
        self.items.append(item)
    
    def spawn_door(self, door: Any) -> None:
        self.doors.append(door)
    
    def spawn_object(self, obj: Any) -> None:
        self.objects.append(obj)
        
    def spawn_player(self, player: Any) -> None:
        self.player = player 
        
    def clear_room(self) -> None:
        self.cleared = True
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        for item in self.items:
            item.spawn()
        for door in self.doors:
            door.open()

    def check_player_door_collision(self, game_map: Any) -> Any:
        for door in self.doors:
            if self.player.hitbox.colliderect(door.hitbox) and not door.locked:
                print("Entrando na próxima sala...")
                next_room = game_map.get_next_room()
                if next_room:
                    next_room.spawn_player(self.player)
                    self.player = None  
                    return next_room
        return self 
