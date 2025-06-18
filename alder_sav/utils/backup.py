import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from config.settings import BACKUP_CONFIG, DATABASE

class BackupManager:
    """Gestionnaire de sauvegardes"""
    
    def __init__(self):
        self.backup_dir = Path(DATABASE['backup_path'])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self):
        """Création d'une sauvegarde"""
        try:
            # Génération du nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"backup_{timestamp}.db"
            
            # Copie de la base de données
            shutil.copy2(DATABASE['path'], backup_file)
            
            # Enregistrement de la sauvegarde dans la base de données
            self._record_backup(backup_file)
            
            # Nettoyage des anciennes sauvegardes
            self._cleanup_old_backups()
            
            return True, f"Sauvegarde créée avec succès: {backup_file}"
        
        except Exception as e:
            return False, f"Erreur lors de la création de la sauvegarde: {str(e)}"
    
    def restore_backup(self, backup_file):
        """Restauration d'une sauvegarde"""
        try:
            # Vérification de l'existence du fichier
            if not os.path.exists(backup_file):
                return False, "Le fichier de sauvegarde n'existe pas"
            
            # Vérification de la validité de la base de données
            if not self._validate_database(backup_file):
                return False, "Le fichier de sauvegarde est corrompu"
            
            # Sauvegarde de la base actuelle
            current_db = DATABASE['path']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_backup = self.backup_dir / f"pre_restore_{timestamp}.db"
            shutil.copy2(current_db, temp_backup)
            
            try:
                # Restauration de la sauvegarde
                shutil.copy2(backup_file, current_db)
                return True, "Sauvegarde restaurée avec succès"
            
            except Exception as e:
                # En cas d'erreur, restauration de la base actuelle
                shutil.copy2(temp_backup, current_db)
                return False, f"Erreur lors de la restauration: {str(e)}"
            
            finally:
                # Suppression de la sauvegarde temporaire
                if os.path.exists(temp_backup):
                    os.remove(temp_backup)
        
        except Exception as e:
            return False, f"Erreur lors de la restauration: {str(e)}"
    
    def list_backups(self):
        """Liste des sauvegardes disponibles"""
        try:
            backups = []
            for file in self.backup_dir.glob("backup_*.db"):
                stat = file.stat()
                backups.append({
                    'file': file.name,
                    'path': str(file),
                    'size': stat.st_size,
                    'date': datetime.fromtimestamp(stat.st_mtime)
                })
            
            return True, sorted(backups, key=lambda x: x['date'], reverse=True)
        
        except Exception as e:
            return False, f"Erreur lors de la liste des sauvegardes: {str(e)}"
    
    def _record_backup(self, backup_file):
        """Enregistrement d'une sauvegarde dans la base de données"""
        try:
            conn = sqlite3.connect(DATABASE['path'])
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO backups (date, chemin_fichier, taille, statut)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.now(),
                str(backup_file),
                os.path.getsize(backup_file),
                "Succès"
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la sauvegarde: {str(e)}")
    
    def _cleanup_old_backups(self):
        """Nettoyage des anciennes sauvegardes"""
        try:
            # Récupération de toutes les sauvegardes
            success, backups = self.list_backups()
            if not success:
                return
            
            # Suppression des sauvegardes trop anciennes
            retention_date = datetime.now() - timedelta(days=BACKUP_CONFIG['retention_days'])
            for backup in backups:
                if backup['date'] < retention_date:
                    os.remove(backup['path'])
            
            # Limitation du nombre de sauvegardes
            if len(backups) > BACKUP_CONFIG['max_backups']:
                for backup in backups[BACKUP_CONFIG['max_backups']:]:
                    os.remove(backup['path'])
        
        except Exception as e:
            print(f"Erreur lors du nettoyage des sauvegardes: {str(e)}")
    
    def _validate_database(self, db_file):
        """Validation de la base de données"""
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Vérification des tables essentielles
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN ('users', 'clients', 'frps')
            """)
            
            tables = cursor.fetchall()
            conn.close()
            
            return len(tables) == 3
        
        except Exception:
            return False 