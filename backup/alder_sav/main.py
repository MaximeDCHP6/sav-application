import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from sqlalchemy.orm import sessionmaker

# Imports absolus
from alder_sav.config.settings import LOG_CONFIG, APP_NAME, APP_VERSION
from alder_sav.database.models import init_db
from alder_sav.ui.main_window import MainWindow

def setup_logging():
    """Configuration du système de logging"""
    try:
        log_dir = Path(LOG_CONFIG['file']).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, LOG_CONFIG['level']),
            format=LOG_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOG_CONFIG['file']),
                logging.StreamHandler()
            ]
        )
        logging.info("Configuration du logging terminée")
    except Exception as e:
        print(f"Erreur lors de la configuration du logging: {str(e)}")
        raise

def main():
    """Point d'entrée principal de l'application"""
    try:
        print("Démarrage de l'application...")
        
        # Configuration du logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info(f"Démarrage de {APP_NAME} v{APP_VERSION}")
        
        print("Initialisation de la base de données...")
        # Initialisation de la base de données
        engine = init_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        logger.info("Base de données initialisée avec succès")
        
        print("Création de l'application Qt...")
        # Création de l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        
        # Configuration du style
        app.setStyle('Fusion')
        
        print("Création de la fenêtre principale...")
        # Création de la fenêtre principale
        window = MainWindow(session)
        window.show()
        
        logger.info("Interface graphique initialisée avec succès")
        
        print("Lancement de l'application...")
        # Lancement de l'application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"ERREUR CRITIQUE: {str(e)}")
        if 'logger' in locals():
            logger.error(f"Erreur lors du démarrage de l'application: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 