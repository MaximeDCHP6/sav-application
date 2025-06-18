import unittest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import os
import sqlite3

from alder_sav.utils.backup import BackupManager
from alder_sav.utils.exceptions import ValidationError

class TestBackupManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de sauvegardes."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.temp_dir) / "backups"
        self.backup_dir.mkdir()
        
        # Création d'une base de données temporaire
        self.db_path = Path(self.temp_dir) / "test.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Création de la table de sauvegardes
        self.cursor.execute("""
            CREATE TABLE backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                size INTEGER NOT NULL,
                creation_date TIMESTAMP NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT
            )
        """)
        self.conn.commit()
        
        # Initialisation du gestionnaire de sauvegardes
        self.backup_manager = BackupManager(self.db_path, self.backup_dir)

    def tearDown(self):
        """Nettoyage après les tests."""
        self.conn.close()
        shutil.rmtree(self.temp_dir)

    def test_create_backup(self):
        """Test de création d'une sauvegarde."""
        # Création d'une sauvegarde
        backup_path = self.backup_manager.create_backup()
        
        # Vérification
        self.assertTrue(backup_path.exists())
        self.assertTrue(backup_path.is_file())
        self.assertEqual(backup_path.parent, self.backup_dir)
        
        # Vérification dans la base de données
        self.cursor.execute("SELECT * FROM backups")
        backup = self.cursor.fetchone()
        self.assertIsNotNone(backup)
        self.assertEqual(backup[1], backup_path.name)
        self.assertEqual(backup[2], str(backup_path))
        self.assertGreater(backup[3], 0)
        self.assertIsNotNone(backup[4])
        self.assertEqual(backup[5], "automatique")
        self.assertEqual(backup[6], "termine")

    def test_restore_backup(self):
        """Test de restauration d'une sauvegarde."""
        # Création d'une sauvegarde
        backup_path = self.backup_manager.create_backup()
        
        # Modification de la base de données
        self.cursor.execute("INSERT INTO backups (filename, path, size, creation_date, type, status) VALUES (?, ?, ?, ?, ?, ?)",
                          ("test.db", str(self.db_path), 1024, datetime.now(), "test", "test"))
        self.conn.commit()
        
        # Restauration de la sauvegarde
        self.backup_manager.restore_backup(backup_path)
        
        # Vérification
        self.cursor.execute("SELECT * FROM backups")
        backups = self.cursor.fetchall()
        self.assertEqual(len(backups), 1)

    def test_list_backups(self):
        """Test de liste des sauvegardes."""
        # Création de plusieurs sauvegardes
        backup1 = self.backup_manager.create_backup()
        backup2 = self.backup_manager.create_backup()
        
        # Récupération de la liste
        backups = self.backup_manager.list_backups()
        
        # Vérification
        self.assertEqual(len(backups), 2)
        self.assertEqual(backups[0]["filename"], backup1.name)
        self.assertEqual(backups[1]["filename"], backup2.name)

    def test_cleanup_old_backups(self):
        """Test de nettoyage des anciennes sauvegardes."""
        # Création de plusieurs sauvegardes
        self.backup_manager.create_backup()
        self.backup_manager.create_backup()
        
        # Nettoyage des sauvegardes
        self.backup_manager._cleanup_old_backups()
        
        # Vérification
        backups = self.backup_manager.list_backups()
        self.assertEqual(len(backups), 1)

    def test_validate_database(self):
        """Test de validation de la base de données."""
        # Création d'une sauvegarde
        backup_path = self.backup_manager.create_backup()
        
        # Validation de la base de données
        self.assertTrue(self.backup_manager._validate_database(backup_path))
        
        # Test avec une base de données invalide
        invalid_db = self.backup_dir / "invalid.db"
        with open(invalid_db, "w") as f:
            f.write("invalid")
        self.assertFalse(self.backup_manager._validate_database(invalid_db))

    def test_record_backup(self):
        """Test d'enregistrement d'une sauvegarde."""
        # Création d'une sauvegarde
        backup_path = self.backup_manager.create_backup()
        
        # Vérification dans la base de données
        self.cursor.execute("SELECT * FROM backups")
        backup = self.cursor.fetchone()
        self.assertIsNotNone(backup)
        self.assertEqual(backup[1], backup_path.name)
        self.assertEqual(backup[2], str(backup_path))
        self.assertGreater(backup[3], 0)
        self.assertIsNotNone(backup[4])
        self.assertEqual(backup[5], "automatique")
        self.assertEqual(backup[6], "termine")

    def test_invalid_backup_path(self):
        """Test avec un chemin de sauvegarde invalide."""
        with self.assertRaises(ValidationError):
            self.backup_manager.restore_backup(Path("invalid_path"))

    def test_invalid_database_path(self):
        """Test avec un chemin de base de données invalide."""
        with self.assertRaises(ValidationError):
            BackupManager(Path("invalid_path"), self.backup_dir)

    def test_invalid_backup_dir(self):
        """Test avec un répertoire de sauvegardes invalide."""
        with self.assertRaises(ValidationError):
            BackupManager(self.db_path, Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 