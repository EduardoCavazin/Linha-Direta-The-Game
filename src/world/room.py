

class Room:
    def __init__(self, id, size, objects=None, enemies=None, items=None, doors=None, player=None, cleared=False, visited = False):
        self.id = id
        self.size = size
        self.objects = objects if objects else []
        self.enemies = enemies if enemies else []
        self.items = items if items else []
        self.doors = doors if doors else []
        self.player = player
        self.cleared = cleared
        self.visited = visited

    def spawn_enemy(self, enemy):
        self.enemies.append(enemy)
        
    def spawn_item(self, item):
        self.items.append(item)
    
    def spawn_door(self, door):
        self.doors.append(door)
    
    def spawn_object(self, obj):  
        self.objects.append(obj)
        
    def spawn_player(self, player):
        self.player = player 
    
    def clear_room(self):
        self.cleared = True
        
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]

        for item in self.items:
            item.spawn()
        
        for door in self.doors:
            door.open()

    def check_player_door_collision(self, game_map):
        for door in self.doors:
            if self.player.hitbox.colliderect(door.hitbox) and not door.locked:
                print("Entrando na próxima sala...")
                next_room = game_map.get_next_room()
                if next_room:
                    next_room.spawn_player(self.player)
                    self.player = None  #remove da sala anterior
                    return next_room
        return self  #se não mudou

    
    

