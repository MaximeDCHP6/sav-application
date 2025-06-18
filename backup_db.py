import os
import shutil
from datetime import datetime, timedelta
import sqlite3
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

def get_backup_dir():
    """Crée et retourne le répertoire de sauvegarde."""
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def get_db_path():
    """Retourne le chemin de la base de données."""
    return Path('instance/sav.db')

def get_settings():
    """Récupère les paramètres de sauvegarde depuis la base de données."""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT backup_frequency, backup_retention FROM settings LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'frequency': result[0],  # heures
                'retention': result[1]   # jours
            }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des paramètres : {e}")
    
    # Valeurs par défaut si erreur
    return {
        'frequency': 1,  # 1 heure
        'retention': 30  # 30 jours
    }

def create_backup():
    """Crée une sauvegarde de la base de données."""
    try:
        db_path = get_db_path()
        if not db_path.exists():
            logging.error("Base de données non trouvée")
            return False

        backup_dir = get_backup_dir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'sav_{timestamp}.db'

        # Copie de la base de données
        shutil.copy2(db_path, backup_path)
        logging.info(f"Sauvegarde créée : {backup_path}")
        return True

    except Exception as e:
        logging.error(f"Erreur lors de la création de la sauvegarde : {e}")
        return False

def cleanup_old_backups():
    """Supprime les anciennes sauvegardes selon la période de rétention."""
    try:
        settings = get_settings()
        retention_days = settings['retention']
        backup_dir = get_backup_dir()
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        for backup_file in backup_dir.glob('sav_*.db'):
            try:
                # Extraire la date du nom de fichier
                date_str = backup_file.stem.split('_')[1]
                backup_date = datetime.strptime(date_str, '%Y%m%d')
                
                if backup_date < cutoff_date:
                    backup_file.unlink()
                    logging.info(f"Sauvegarde supprimée : {backup_file}")
            except Exception as e:
                logging.error(f"Erreur lors de la suppression de {backup_file} : {e}")

    except Exception as e:
        logging.error(f"Erreur lors du nettoyage des sauvegardes : {e}")

def main():
    """Fonction principale."""
    try:
        settings = get_settings()
        backup_dir = get_backup_dir()
        
        # Vérifier si une sauvegarde est nécessaire
        latest_backup = max(backup_dir.glob('sav_*.db'), key=os.path.getctime, default=None)
        if latest_backup:
            last_backup_time = datetime.fromtimestamp(os.path.getctime(latest_backup))
            time_since_last_backup = datetime.now() - last_backup_time
            
            if time_since_last_backup < timedelta(hours=settings['frequency']):
                logging.info("Pas besoin de nouvelle sauvegarde")
                return

        # Créer une nouvelle sauvegarde
        if create_backup():
            cleanup_old_backups()
        else:
            logging.error("Échec de la création de la sauvegarde")

    except Exception as e:
        logging.error(f"Erreur dans la fonction principale : {e}")

if __name__ == '__main__':
    main() 