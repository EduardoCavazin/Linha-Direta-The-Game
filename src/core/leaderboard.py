"""
Sistema de Leaderboard - Gerencia rankings e scores dos jogadores
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class LeaderboardEntry:
    def __init__(self, name: str, time: int, score: int = 0, date: str = None):
        self.name = name
        self.time = time  # Tempo em milissegundos
        self.score = score
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "time": self.time,
            "score": self.score,
            "date": self.date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LeaderboardEntry':
        return cls(
            name=data.get("name", "Anonymous"),
            time=data.get("time", 0),
            score=data.get("score", 0),
            date=data.get("date", "")
        )
    
    def get_time_formatted(self) -> str:
        """Converte tempo em milissegundos para formato mm:ss"""
        seconds = self.time // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

class Leaderboard:
    def __init__(self, file_path: str = "leaderboard.json"):
        self.file_path = file_path
        self.entries: List[LeaderboardEntry] = []
        self.load_scores()
    
    def load_scores(self) -> None:
        """Carrega scores do arquivo JSON"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [LeaderboardEntry.from_dict(entry) for entry in data.get("scores", [])]
                    # Ordenar por tempo (menor tempo = melhor)
                    self.entries.sort(key=lambda x: x.time)
            else:
                self.entries = []
        except Exception as e:
            print(f"Erro ao carregar leaderboard: {e}")
            self.entries = []
    
    def save_scores(self) -> None:
        """Salva scores no arquivo JSON"""
        try:
            # Manter apenas top 20 para não crescer muito
            top_entries = self.entries[:20]
            
            data = {
                "scores": [entry.to_dict() for entry in top_entries],
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar leaderboard: {e}")
    
    def add_score(self, name: str, time: int, score: int = 0) -> int:
        """
        Adiciona um novo score ao leaderboard
        Retorna a posição no ranking (1-based) ou -1 se não entrou no top
        """
        entry = LeaderboardEntry(name, time, score)
        self.entries.append(entry)
        
        # Reordenar por tempo (menor tempo = melhor)
        self.entries.sort(key=lambda x: x.time)
        
        # Encontrar posição da entrada adicionada
        for i, e in enumerate(self.entries):
            if e.name == entry.name and e.time == entry.time and e.date == entry.date:
                position = i + 1
                self.save_scores()
                return position
        
        return -1
    
    def get_top_scores(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Retorna os melhores scores limitado ao número especificado"""
        return self.entries[:limit]
    
    def get_player_best(self, name: str) -> Optional[LeaderboardEntry]:
        """Retorna o melhor score de um jogador específico"""
        player_entries = [entry for entry in self.entries if entry.name.lower() == name.lower()]
        return player_entries[0] if player_entries else None
    
    def is_top_score(self, time: int, limit: int = 10) -> bool:
        """Verifica se um tempo entraria no top N"""
        if len(self.entries) < limit:
            return True
        return time < self.entries[limit - 1].time

    def clear_scores(self) -> bool:
        """Limpa todos os scores do leaderboard"""
        try:
            self.entries.clear()
            self._save_to_file()
            return True
        except Exception as e:
            print(f"Erro ao limpar leaderboard: {e}")
            return False