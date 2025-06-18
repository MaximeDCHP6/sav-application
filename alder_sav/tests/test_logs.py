import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.logs import LogManager
from alder_sav.utils.exceptions import ValidationError

class TestLogManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de logs."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = Path(self.temp_dir) / "logs"
        self.logs_dir.mkdir()
        
        # Initialisation du gestionnaire de logs
        self.log_manager = LogManager(self.logs_dir)
        
        # Données de test
        self.log_data = {
            "reference": "LOG-001",
            "type": "system",
            "level": "info",
            "timestamp": datetime.now().isoformat(),
            "source": {
                "module": "repairs",
                "function": "create_repair",
                "line": 123
            },
            "user": {
                "id": "USR-001",
                "name": "Jean Dupont",
                "role": "technician"
            },
            "action": {
                "type": "create",
                "entity": "repair",
                "entity_id": "REP-001",
                "details": "Création d'une nouvelle réparation"
            },
            "data": {
                "before": None,
                "after": {
                    "reference": "REP-001",
                    "type": "hardware",
                    "status": "pending"
                }
            },
            "context": {
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0",
                "session_id": "SESS-001"
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "tags": ["système", "réparation"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_log(self):
        """Test de création de log."""
        # Création du log
        log_obj = self.log_manager.create_log(self.log_data)
        
        # Vérification
        self.assertEqual(log_obj["reference"], "LOG-001")
        self.assertEqual(log_obj["type"], "system")
        self.assertEqual(log_obj["level"], "info")
        self.assertTrue("id" in log_obj)
        self.assertTrue("creation_date" in log_obj)

    def test_get_log(self):
        """Test de récupération de log."""
        # Création du log
        log_obj = self.log_manager.create_log(self.log_data)
        
        # Récupération du log
        retrieved_log = self.log_manager.get_log(log_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_log["reference"], "LOG-001")
        self.assertEqual(retrieved_log["source"]["module"], "repairs")
        self.assertEqual(retrieved_log["user"]["name"], "Jean Dupont")
        self.assertEqual(retrieved_log["action"]["type"], "create")

    def test_update_log(self):
        """Test de mise à jour de log."""
        # Création du log
        log_obj = self.log_manager.create_log(self.log_data)
        
        # Mise à jour du log
        updated_data = {
            "level": "warning",
            "action": {
                "type": "update",
                "entity": "repair",
                "entity_id": "REP-001",
                "details": "Mise à jour du statut de la réparation"
            },
            "data": {
                "before": {
                    "status": "pending"
                },
                "after": {
                    "status": "in_progress"
                }
            },
            "metadata": {
                "updated_at": datetime.now().isoformat(),
                "version": "2.0"
            }
        }
        updated_log = self.log_manager.update_log(log_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_log["level"], "warning")
        self.assertEqual(updated_log["action"]["type"], "update")
        self.assertEqual(updated_log["data"]["before"]["status"], "pending")
        self.assertEqual(updated_log["data"]["after"]["status"], "in_progress")
        self.assertEqual(updated_log["metadata"]["version"], "2.0")

    def test_delete_log(self):
        """Test de suppression de log."""
        # Création du log
        log_obj = self.log_manager.create_log(self.log_data)
        
        # Suppression du log
        self.log_manager.delete_log(log_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.log_manager.get_log(log_obj["id"])

    def test_get_log_by_type(self):
        """Test de récupération des logs par type."""
        # Création de logs de différents types
        self.log_manager.create_log({
            **self.log_data,
            "type": "system"
        })
        self.log_manager.create_log({
            **self.log_data,
            "reference": "LOG-002",
            "type": "user"
        })
        
        # Récupération des logs par type
        system_logs = self.log_manager.get_log_by_type("system")
        user_logs = self.log_manager.get_log_by_type("user")
        
        # Vérification
        self.assertEqual(len(system_logs), 1)
        self.assertEqual(len(user_logs), 1)
        self.assertEqual(system_logs[0]["type"], "system")
        self.assertEqual(user_logs[0]["type"], "user")

    def test_get_log_by_level(self):
        """Test de récupération des logs par niveau."""
        # Création de logs de différents niveaux
        self.log_manager.create_log({
            **self.log_data,
            "level": "info"
        })
        self.log_manager.create_log({
            **self.log_data,
            "reference": "LOG-002",
            "level": "error"
        })
        
        # Récupération des logs par niveau
        info_logs = self.log_manager.get_log_by_level("info")
        error_logs = self.log_manager.get_log_by_level("error")
        
        # Vérification
        self.assertEqual(len(info_logs), 1)
        self.assertEqual(len(error_logs), 1)
        self.assertEqual(info_logs[0]["level"], "info")
        self.assertEqual(error_logs[0]["level"], "error")

    def test_get_log_by_user(self):
        """Test de récupération des logs par utilisateur."""
        # Création de logs de différents utilisateurs
        self.log_manager.create_log({
            **self.log_data,
            "user": {
                "id": "USR-001",
                "name": "Jean Dupont",
                "role": "technician"
            }
        })
        self.log_manager.create_log({
            **self.log_data,
            "reference": "LOG-002",
            "user": {
                "id": "USR-002",
                "name": "Marie Martin",
                "role": "manager"
            }
        })
        
        # Récupération des logs par utilisateur
        jean_logs = self.log_manager.get_log_by_user("USR-001")
        marie_logs = self.log_manager.get_log_by_user("USR-002")
        
        # Vérification
        self.assertEqual(len(jean_logs), 1)
        self.assertEqual(len(marie_logs), 1)
        self.assertEqual(jean_logs[0]["user"]["name"], "Jean Dupont")
        self.assertEqual(marie_logs[0]["user"]["name"], "Marie Martin")

    def test_get_log_by_entity(self):
        """Test de récupération des logs par entité."""
        # Création de logs de différentes entités
        self.log_manager.create_log({
            **self.log_data,
            "action": {
                "type": "create",
                "entity": "repair",
                "entity_id": "REP-001"
            }
        })
        self.log_manager.create_log({
            **self.log_data,
            "reference": "LOG-002",
            "action": {
                "type": "create",
                "entity": "warranty",
                "entity_id": "WAR-001"
            }
        })
        
        # Récupération des logs par entité
        repair_logs = self.log_manager.get_log_by_entity("repair", "REP-001")
        warranty_logs = self.log_manager.get_log_by_entity("warranty", "WAR-001")
        
        # Vérification
        self.assertEqual(len(repair_logs), 1)
        self.assertEqual(len(warranty_logs), 1)
        self.assertEqual(repair_logs[0]["action"]["entity"], "repair")
        self.assertEqual(warranty_logs[0]["action"]["entity"], "warranty")

    def test_validate_log(self):
        """Test de validation de log."""
        # Création d'un log valide
        log_obj = self.log_manager.create_log(self.log_data)
        
        # Validation du log
        is_valid = self.log_manager.validate_log(log_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_log_summary(self):
        """Test de récupération du résumé de log."""
        # Création du log
        log_obj = self.log_manager.create_log(self.log_data)
        
        # Récupération du résumé
        summary = self.log_manager.get_log_summary(log_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("level" in summary)
        self.assertTrue("timestamp" in summary)
        self.assertTrue("source" in summary)
        self.assertTrue("user" in summary)
        self.assertTrue("action" in summary)
        self.assertTrue("data" in summary)
        self.assertTrue("context" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_log_type(self):
        """Test avec un type de log invalide."""
        with self.assertRaises(ValidationError):
            self.log_manager.create_log({
                **self.log_data,
                "type": "invalid_type"
            })

    def test_invalid_log_level(self):
        """Test avec un niveau de log invalide."""
        with self.assertRaises(ValidationError):
            self.log_manager.create_log({
                **self.log_data,
                "level": "invalid_level"
            })

    def test_invalid_log_dir(self):
        """Test avec un répertoire de logs invalide."""
        with self.assertRaises(ValidationError):
            LogManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 