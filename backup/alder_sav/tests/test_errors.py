import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.errors import ErrorManager
from alder_sav.utils.exceptions import ValidationError

class TestErrorManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire d'erreurs."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.errors_dir = Path(self.temp_dir) / "errors"
        self.errors_dir.mkdir()
        
        # Initialisation du gestionnaire d'erreurs
        self.error_manager = ErrorManager(self.errors_dir)
        
        # Données de test
        self.error_data = {
            "reference": "ERR-001",
            "type": "system",
            "level": "error",
            "timestamp": datetime.now().isoformat(),
            "source": {
                "module": "repairs",
                "function": "create_repair",
                "line": 123
            },
            "error": {
                "code": "REP001",
                "name": "RepairCreationError",
                "message": "Impossible de créer la réparation",
                "details": "Le client n'existe pas",
                "stack_trace": "Traceback (most recent call last):\n  File \"repairs.py\", line 123, in create_repair\n    client = get_client(client_id)\n  File \"clients.py\", line 45, in get_client\n    raise ClientNotFoundError(f\"Client {client_id} non trouvé\")\nClientNotFoundError: Client CLT-001 non trouvé"
            },
            "context": {
                "user": {
                    "id": "USR-001",
                    "name": "Jean Dupont",
                    "role": "technician"
                },
                "request": {
                    "method": "POST",
                    "url": "/api/repairs",
                    "data": {
                        "client_id": "CLT-001",
                        "device_id": "DEV-001"
                    }
                },
                "environment": {
                    "os": "Windows 10",
                    "python_version": "3.9.0",
                    "app_version": "1.0.0"
                }
            },
            "resolution": {
                "status": "pending",
                "assigned_to": None,
                "priority": "high",
                "steps": [
                    {
                        "action": "Vérifier l'existence du client",
                        "status": "pending"
                    }
                ]
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

    def test_create_error(self):
        """Test de création d'erreur."""
        # Création de l'erreur
        error_obj = self.error_manager.create_error(self.error_data)
        
        # Vérification
        self.assertEqual(error_obj["reference"], "ERR-001")
        self.assertEqual(error_obj["type"], "system")
        self.assertEqual(error_obj["level"], "error")
        self.assertTrue("id" in error_obj)
        self.assertTrue("creation_date" in error_obj)

    def test_get_error(self):
        """Test de récupération d'erreur."""
        # Création de l'erreur
        error_obj = self.error_manager.create_error(self.error_data)
        
        # Récupération de l'erreur
        retrieved_error = self.error_manager.get_error(error_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_error["reference"], "ERR-001")
        self.assertEqual(retrieved_error["error"]["code"], "REP001")
        self.assertEqual(retrieved_error["error"]["name"], "RepairCreationError")
        self.assertEqual(retrieved_error["context"]["user"]["name"], "Jean Dupont")

    def test_update_error(self):
        """Test de mise à jour d'erreur."""
        # Création de l'erreur
        error_obj = self.error_manager.create_error(self.error_data)
        
        # Mise à jour de l'erreur
        updated_data = {
            "resolution": {
                "status": "in_progress",
                "assigned_to": {
                    "id": "USR-002",
                    "name": "Marie Martin",
                    "role": "manager"
                },
                "priority": "high",
                "steps": [
                    {
                        "action": "Vérifier l'existence du client",
                        "status": "completed",
                        "result": "Client non trouvé dans la base de données"
                    },
                    {
                        "action": "Créer le client",
                        "status": "pending"
                    }
                ]
            },
            "metadata": {
                "updated_at": datetime.now().isoformat(),
                "version": "2.0"
            }
        }
        updated_error = self.error_manager.update_error(error_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_error["resolution"]["status"], "in_progress")
        self.assertEqual(updated_error["resolution"]["assigned_to"]["name"], "Marie Martin")
        self.assertEqual(len(updated_error["resolution"]["steps"]), 2)
        self.assertEqual(updated_error["resolution"]["steps"][0]["status"], "completed")
        self.assertEqual(updated_error["metadata"]["version"], "2.0")

    def test_delete_error(self):
        """Test de suppression d'erreur."""
        # Création de l'erreur
        error_obj = self.error_manager.create_error(self.error_data)
        
        # Suppression de l'erreur
        self.error_manager.delete_error(error_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.error_manager.get_error(error_obj["id"])

    def test_get_error_by_type(self):
        """Test de récupération des erreurs par type."""
        # Création d'erreurs de différents types
        self.error_manager.create_error({
            **self.error_data,
            "type": "system"
        })
        self.error_manager.create_error({
            **self.error_data,
            "reference": "ERR-002",
            "type": "user"
        })
        
        # Récupération des erreurs par type
        system_errors = self.error_manager.get_error_by_type("system")
        user_errors = self.error_manager.get_error_by_type("user")
        
        # Vérification
        self.assertEqual(len(system_errors), 1)
        self.assertEqual(len(user_errors), 1)
        self.assertEqual(system_errors[0]["type"], "system")
        self.assertEqual(user_errors[0]["type"], "user")

    def test_get_error_by_level(self):
        """Test de récupération des erreurs par niveau."""
        # Création d'erreurs de différents niveaux
        self.error_manager.create_error({
            **self.error_data,
            "level": "error"
        })
        self.error_manager.create_error({
            **self.error_data,
            "reference": "ERR-002",
            "level": "warning"
        })
        
        # Récupération des erreurs par niveau
        error_errors = self.error_manager.get_error_by_level("error")
        warning_errors = self.error_manager.get_error_by_level("warning")
        
        # Vérification
        self.assertEqual(len(error_errors), 1)
        self.assertEqual(len(warning_errors), 1)
        self.assertEqual(error_errors[0]["level"], "error")
        self.assertEqual(warning_errors[0]["level"], "warning")

    def test_get_error_by_resolution_status(self):
        """Test de récupération des erreurs par statut de résolution."""
        # Création d'erreurs de différents statuts de résolution
        self.error_manager.create_error({
            **self.error_data,
            "resolution": {
                "status": "pending"
            }
        })
        self.error_manager.create_error({
            **self.error_data,
            "reference": "ERR-002",
            "resolution": {
                "status": "resolved"
            }
        })
        
        # Récupération des erreurs par statut de résolution
        pending_errors = self.error_manager.get_error_by_resolution_status("pending")
        resolved_errors = self.error_manager.get_error_by_resolution_status("resolved")
        
        # Vérification
        self.assertEqual(len(pending_errors), 1)
        self.assertEqual(len(resolved_errors), 1)
        self.assertEqual(pending_errors[0]["resolution"]["status"], "pending")
        self.assertEqual(resolved_errors[0]["resolution"]["status"], "resolved")

    def test_validate_error(self):
        """Test de validation d'erreur."""
        # Création d'une erreur valide
        error_obj = self.error_manager.create_error(self.error_data)
        
        # Validation de l'erreur
        is_valid = self.error_manager.validate_error(error_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_error_summary(self):
        """Test de récupération du résumé d'erreur."""
        # Création de l'erreur
        error_obj = self.error_manager.create_error(self.error_data)
        
        # Récupération du résumé
        summary = self.error_manager.get_error_summary(error_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("level" in summary)
        self.assertTrue("timestamp" in summary)
        self.assertTrue("source" in summary)
        self.assertTrue("error" in summary)
        self.assertTrue("context" in summary)
        self.assertTrue("resolution" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_error_type(self):
        """Test avec un type d'erreur invalide."""
        with self.assertRaises(ValidationError):
            self.error_manager.create_error({
                **self.error_data,
                "type": "invalid_type"
            })

    def test_invalid_error_level(self):
        """Test avec un niveau d'erreur invalide."""
        with self.assertRaises(ValidationError):
            self.error_manager.create_error({
                **self.error_data,
                "level": "invalid_level"
            })

    def test_invalid_error_dir(self):
        """Test avec un répertoire d'erreurs invalide."""
        with self.assertRaises(ValidationError):
            ErrorManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 