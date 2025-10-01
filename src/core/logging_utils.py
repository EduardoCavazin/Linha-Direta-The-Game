"""
Sistema básico de logging para o jogo
Centraliza todos os logs em uma estrutura organizada
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class GameLogger:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True

    def _setup_logging(self):
        # Configurar o logger principal
        self.logger = logging.getLogger('linha_direta')
        self.logger.setLevel(logging.DEBUG)

        # Evitar duplicação de handlers
        if not self.logger.handlers:
            # Handler para console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)

            # Handler para arquivo (opcional)
            try:
                log_dir = Path("logs")
                log_dir.mkdir(exist_ok=True)
                file_handler = logging.FileHandler(
                    log_dir / f"game_{datetime.now().strftime('%Y%m%d')}.log"
                )
                file_handler.setLevel(logging.DEBUG)

                # Formatters
                detailed_formatter = logging.Formatter(
                    '%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s'
                )
                simple_formatter = logging.Formatter(
                    '[%(levelname)s] %(message)s'
                )

                file_handler.setFormatter(detailed_formatter)
                console_handler.setFormatter(simple_formatter)

                self.logger.addHandler(file_handler)
            except Exception:
                # Se não conseguir criar arquivo, só usa console
                pass

            self.logger.addHandler(console_handler)

    def get_logger(self, name: str = None):
        """Retorna logger específico para um módulo"""
        if name:
            return logging.getLogger(f'linha_direta.{name}')
        return self.logger


# Funções de conveniência
_game_logger = GameLogger()

def get_logger(module_name: str = None) -> logging.Logger:
    """Função principal para obter logger"""
    return _game_logger.get_logger(module_name)

def log_error(message: str, module: str = None, exception: Exception = None):
    """Log de erro com contexto"""
    logger = get_logger(module)
    if exception:
        logger.error(f"{message}: {exception}")
    else:
        logger.error(message)

def log_warning(message: str, module: str = None):
    """Log de warning"""
    logger = get_logger(module)
    logger.warning(message)

def log_info(message: str, module: str = None):
    """Log informativo"""
    logger = get_logger(module)
    logger.info(message)

def log_debug(message: str, module: str = None):
    """Log de debug (só aparece em arquivo)"""
    logger = get_logger(module)
    logger.debug(message)