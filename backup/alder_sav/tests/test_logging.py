import unittest
import os
import json
from datetime import datetime
from decimal import Decimal
from alder_sav.utils.logging import LogManager
from alder_sav.utils.exceptions import LoggingError

class TestLogManager(unittest.TestCase):
    """Tests pour le gestionnaire de logs."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.log_manager = LogManager()
        self.test_log_file = "test.log"

    def tearDown(self):
        """Nettoyage après les tests."""
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def test_log_levels(self):
        """Test des différents niveaux de log."""
        # Tester chaque niveau de log
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            message = f"Test message {level}"
            self.log_manager.log(level, message)
            
            # Vérifier que le message a été enregistré
            logs = self.log_manager.get_logs()
            self.assertTrue(any(log["level"] == level and log["message"] == message for log in logs))

    def test_log_formatting(self):
        """Test du formatage des logs."""
        # Créer un log avec des données structurées
        log_data = {
            "user_id": 123,
            "action": "login",
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_manager.log("INFO", "User action", extra=log_data)
        
        # Vérifier le format
        logs = self.log_manager.get_logs()
        log = next(log for log in logs if log["message"] == "User action")
        
        self.assertEqual(log["level"], "INFO")
        self.assertEqual(log["extra"]["user_id"], 123)
        self.assertEqual(log["extra"]["action"], "login")
        self.assertIn("timestamp", log["extra"])

    def test_log_rotation(self):
        """Test de la rotation des logs."""
        # Configurer la rotation
        self.log_manager.configure_rotation(
            max_size=1024,  # 1 KB
            backup_count=3
        )
        
        # Générer des logs pour dépasser la taille maximale
        large_message = "x" * 2000  # 2 KB
        for _ in range(5):
            self.log_manager.log("INFO", large_message)
        
        # Vérifier la rotation
        log_files = [f for f in os.listdir() if f.startswith("test.log")]
        self.assertLessEqual(len(log_files), 4)  # Fichier actuel + 3 backups

    def test_log_filtering(self):
        """Test du filtrage des logs."""
        # Ajouter des logs de différents niveaux
        self.log_manager.log("DEBUG", "Debug message")
        self.log_manager.log("INFO", "Info message")
        self.log_manager.log("WARNING", "Warning message")
        self.log_manager.log("ERROR", "Error message")
        
        # Filtrer par niveau
        error_logs = self.log_manager.get_logs(level="ERROR")
        self.assertEqual(len(error_logs), 1)
        self.assertEqual(error_logs[0]["message"], "Error message")
        
        # Filtrer par message
        warning_logs = self.log_manager.get_logs(message="Warning")
        self.assertEqual(len(warning_logs), 1)
        self.assertEqual(warning_logs[0]["level"], "WARNING")

    def test_log_aggregation(self):
        """Test de l'agrégation des logs."""
        # Ajouter des logs similaires
        for _ in range(3):
            self.log_manager.log("ERROR", "Database connection failed")
        
        # Vérifier l'agrégation
        stats = self.log_manager.get_log_statistics()
        self.assertEqual(stats["ERROR"]["Database connection failed"], 3)

    def test_log_export(self):
        """Test de l'export des logs."""
        # Ajouter des logs
        self.log_manager.log("INFO", "Test message 1")
        self.log_manager.log("WARNING", "Test message 2")
        
        # Exporter les logs
        exported_logs = self.log_manager.export_logs()
        self.assertEqual(len(exported_logs), 2)
        self.assertEqual(exported_logs[0]["message"], "Test message 1")
        self.assertEqual(exported_logs[1]["message"], "Test message 2")

    def test_log_import(self):
        """Test de l'import des logs."""
        # Logs à importer
        import_logs = [
            {"level": "INFO", "message": "Imported message 1"},
            {"level": "WARNING", "message": "Imported message 2"}
        ]
        
        # Importer les logs
        self.log_manager.import_logs(import_logs)
        
        # Vérifier l'import
        logs = self.log_manager.get_logs()
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["message"], "Imported message 1")
        self.assertEqual(logs[1]["message"], "Imported message 2")

    def test_log_cleanup(self):
        """Test du nettoyage des logs."""
        # Ajouter des logs
        self.log_manager.log("INFO", "Test message")
        
        # Nettoyer les logs
        self.log_manager.cleanup_logs()
        
        # Vérifier le nettoyage
        logs = self.log_manager.get_logs()
        self.assertEqual(len(logs), 0)

    def test_log_compression(self):
        """Test de la compression des logs."""
        # Ajouter des logs
        for _ in range(100):
            self.log_manager.log("INFO", "Test message")
        
        # Compresser les logs
        self.log_manager.compress_logs()
        
        # Vérifier la compression
        log_files = [f for f in os.listdir() if f.endswith(".gz")]
        self.assertTrue(len(log_files) > 0)

    def test_log_encryption(self):
        """Test du chiffrement des logs."""
        # Ajouter des logs sensibles
        self.log_manager.log("INFO", "Sensitive data", sensitive=True)
        
        # Vérifier le chiffrement
        logs = self.log_manager.get_logs()
        log = next(log for log in logs if log["message"] == "Sensitive data")
        self.assertTrue(log["encrypted"])

    def test_log_retention(self):
        """Test de la rétention des logs."""
        # Configurer la rétention
        self.log_manager.configure_retention(days=7)
        
        # Ajouter des logs
        self.log_manager.log("INFO", "Test message")
        
        # Vérifier la rétention
        retention_info = self.log_manager.get_retention_info()
        self.assertEqual(retention_info["days"], 7)

    def test_log_alerting(self):
        """Test des alertes de log."""
        # Configurer les alertes
        self.log_manager.configure_alerting(
            threshold=3,
            level="ERROR"
        )
        
        # Ajouter des logs d'erreur
        for _ in range(4):
            self.log_manager.log("ERROR", "Critical error")
        
        # Vérifier l'alerte
        alerts = self.log_manager.get_alerts()
        self.assertTrue(len(alerts) > 0)

if __name__ == '__main__':
    unittest.main() 