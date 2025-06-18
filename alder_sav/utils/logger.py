import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

from ..config.settings import LOG_CONFIG

class Logger:
    """Gestionnaire de logs de l'application."""
    
    def __init__(self):
        """Initialise le gestionnaire de logs."""
        self.logger = logging.getLogger('alder_sav')
        self.logger.setLevel(LOG_CONFIG['level'])
        
        # Création du répertoire de logs si nécessaire
        log_dir = Path(LOG_CONFIG['file']).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration du format
        formatter = logging.Formatter(LOG_CONFIG['format'])
        
        # Handler pour fichier avec rotation
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_CONFIG['file'],
            maxBytes=LOG_CONFIG['max_size'],
            backupCount=LOG_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Enregistre un message de niveau DEBUG.
        
        Args:
            message: Message à enregistrer
            **kwargs: Informations supplémentaires
        """
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Enregistre un message de niveau INFO.
        
        Args:
            message: Message à enregistrer
            **kwargs: Informations supplémentaires
        """
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Enregistre un message de niveau WARNING.
        
        Args:
            message: Message à enregistrer
            **kwargs: Informations supplémentaires
        """
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Enregistre un message de niveau ERROR.
        
        Args:
            message: Message à enregistrer
            **kwargs: Informations supplémentaires
        """
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Enregistre un message de niveau CRITICAL.
        
        Args:
            message: Message à enregistrer
            **kwargs: Informations supplémentaires
        """
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Enregistre un message avec des informations supplémentaires.
        
        Args:
            level: Niveau de log
            message: Message à enregistrer
            **kwargs: Informations supplémentaires
        """
        extra = {
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        self.logger.log(level, message, extra=extra)
    
    def get_log_file(self) -> Path:
        """Retourne le chemin du fichier de log actuel.
        
        Returns:
            Path: Chemin du fichier de log
        """
        return Path(LOG_CONFIG['file'])
    
    def get_log_files(self) -> list[Path]:
        """Retourne la liste des fichiers de log (actuel et backups).
        
        Returns:
            list[Path]: Liste des fichiers de log
        """
        log_dir = Path(LOG_CONFIG['file']).parent
        log_files = []
        
        # Fichier actuel
        if os.path.exists(LOG_CONFIG['file']):
            log_files.append(Path(LOG_CONFIG['file']))
        
        # Fichiers de backup
        for i in range(1, LOG_CONFIG['backup_count'] + 1):
            backup_file = log_dir / f"{Path(LOG_CONFIG['file']).stem}.{i}"
            if os.path.exists(backup_file):
                log_files.append(backup_file)
        
        return log_files
    
    def clear_logs(self):
        """Efface tous les fichiers de log."""
        for log_file in self.get_log_files():
            try:
                os.remove(log_file)
                self.info(f"Fichier de log supprimé : {log_file}")
            except Exception as e:
                self.error(f"Erreur lors de la suppression du fichier de log {log_file} : {str(e)}")
    
    def set_level(self, level: str):
        """Change le niveau de log.
        
        Args:
            level: Nouveau niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level = level.upper()
        if level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            self.logger.setLevel(getattr(logging, level))
            self.info(f"Niveau de log changé pour {level}")
        else:
            self.error(f"Niveau de log invalide : {level}")

# Instance unique du logger
logger = Logger() 