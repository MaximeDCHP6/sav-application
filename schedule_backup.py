import schedule
import time
import logging
from backup_db import main as backup_main

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_backup():
    """Exécute la sauvegarde et gère les erreurs."""
    try:
        backup_main()
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution de la sauvegarde : {e}")

def main():
    """Fonction principale qui planifie les sauvegardes."""
    logging.info("Démarrage du planificateur de sauvegardes")
    
    # Exécuter une sauvegarde immédiatement au démarrage
    run_backup()
    
    # Planifier une vérification toutes les minutes
    schedule.every(1).minutes.do(run_backup)
    
    # Boucle principale
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Erreur dans la boucle principale : {e}")
            time.sleep(60)  # Attendre une minute en cas d'erreur

if __name__ == '__main__':
    main() 