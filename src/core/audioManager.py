import pygame

class AudioManager:
    def __init__(self) -> None:
        self.sounds: dict = {}
        self.music_volume: float = 0.5
        self.sfx_volume: float = 0.7
        
        self._load_sounds()
        
    def _load_sounds(self) -> None:
        sound_files = {
            'shoot': 'assets/audio/sfx/pistol_sound.wav',
            'footstep': 'assets/audio/sfx/footstep.mp3',
        }
        
        for name, file_path in sound_files.items():
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
            except pygame.error as e:
                print(f"Não foi possível carregar: {file_path} - {e}")
                self.sounds[name] = pygame.mixer.Sound(buffer=b'\x00' * 1024)
    
    def play_sound(self, sound_name: str) -> None:
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_background_music(self) -> None:
        music_files = [
            'assets/audio/music/Soundtrack1 (1).mp3',
            'assets/audio/music/Soundtrack1 (2).mp3'
        ]
        
        for music_file in music_files:
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1) 
                return
            except pygame.error as e:
                print(f"Não foi possível carregar: {music_file} - {e}")
        
    
    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)