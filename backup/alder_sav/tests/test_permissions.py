import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.permissions import PermissionManager
from alder_sav.utils.exceptions import ValidationError

class TestPermissionManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de permissions."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.permissions_dir = Path(self.temp_dir) / "permissions"
        self.permissions_dir.mkdir()
        
        # Initialisation du gestionnaire de permissions
        self.permission_manager = PermissionManager(self.permissions_dir)
        
        # Données de test
        self.permission_data = {
            "reference": "PER-001",
            "type": "system",
            "status": "active",
            "name": "Gestion des réparations",
            "description": "Permissions pour la gestion des réparations",
            "module": "repairs",
            "actions": {
                "view": {
                    "name": "Voir les réparations",
                    "description": "Permet de voir la liste des réparations",
                    "level": "read"
                },
                "create": {
                    "name": "Créer une réparation",
                    "description": "Permet de créer une nouvelle réparation",
                    "level": "write"
                },
                "update": {
                    "name": "Modifier une réparation",
                    "description": "Permet de modifier une réparation existante",
                    "level": "write"
                },
                "delete": {
                    "name": "Supprimer une réparation",
                    "description": "Permet de supprimer une réparation",
                    "level": "admin"
                }
            },
            "scope": {
                "type": "module",
                "entities": ["repairs"],
                "conditions": {
                    "status": ["pending", "in_progress", "completed"],
                    "user_role": ["technician", "manager"]
                }
            },
            "dependencies": [
                {
                    "module": "clients",
                    "action": "view"
                },
                {
                    "module": "devices",
                    "action": "view"
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0",
                "tags": ["réparation", "sav"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_permission(self):
        """Test de création de permission."""
        # Création de la permission
        permission_obj = self.permission_manager.create_permission(self.permission_data)
        
        # Vérification
        self.assertEqual(permission_obj["reference"], "PER-001")
        self.assertEqual(permission_obj["type"], "system")
        self.assertEqual(permission_obj["status"], "active")
        self.assertEqual(permission_obj["name"], "Gestion des réparations")
        self.assertTrue("id" in permission_obj)
        self.assertTrue("creation_date" in permission_obj)

    def test_get_permission(self):
        """Test de récupération de permission."""
        # Création de la permission
        permission_obj = self.permission_manager.create_permission(self.permission_data)
        
        # Récupération de la permission
        retrieved_permission = self.permission_manager.get_permission(permission_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_permission["reference"], "PER-001")
        self.assertEqual(retrieved_permission["module"], "repairs")
        self.assertEqual(retrieved_permission["actions"]["view"]["level"], "read")
        self.assertEqual(retrieved_permission["actions"]["delete"]["level"], "admin")

    def test_update_permission(self):
        """Test de mise à jour de permission."""
        # Création de la permission
        permission_obj = self.permission_manager.create_permission(self.permission_data)
        
        # Mise à jour de la permission
        updated_data = {
            "actions": {
                "view": {
                    "name": "Voir les réparations",
                    "description": "Permet de voir la liste des réparations",
                    "level": "read"
                },
                "create": {
                    "name": "Créer une réparation",
                    "description": "Permet de créer une nouvelle réparation",
                    "level": "write"
                },
                "update": {
                    "name": "Modifier une réparation",
                    "description": "Permet de modifier une réparation existante",
                    "level": "write"
                },
                "delete": {
                    "name": "Supprimer une réparation",
                    "description": "Permet de supprimer une réparation",
                    "level": "write"
                }
            },
            "scope": {
                "type": "module",
                "entities": ["repairs", "warranties"],
                "conditions": {
                    "status": ["pending", "in_progress", "completed", "cancelled"],
                    "user_role": ["technician", "manager", "admin"]
                }
            },
            "metadata": {
                "updated_at": datetime.now().isoformat(),
                "version": "2.0"
            }
        }
        updated_permission = self.permission_manager.update_permission(permission_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_permission["actions"]["delete"]["level"], "write")
        self.assertEqual(len(updated_permission["scope"]["entities"]), 2)
        self.assertEqual(len(updated_permission["scope"]["conditions"]["status"]), 4)
        self.assertEqual(len(updated_permission["scope"]["conditions"]["user_role"]), 3)
        self.assertEqual(updated_permission["metadata"]["version"], "2.0")

    def test_delete_permission(self):
        """Test de suppression de permission."""
        # Création de la permission
        permission_obj = self.permission_manager.create_permission(self.permission_data)
        
        # Suppression de la permission
        self.permission_manager.delete_permission(permission_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.permission_manager.get_permission(permission_obj["id"])

    def test_get_permission_by_type(self):
        """Test de récupération des permissions par type."""
        # Création de permissions de différents types
        self.permission_manager.create_permission({
            **self.permission_data,
            "type": "system"
        })
        self.permission_manager.create_permission({
            **self.permission_data,
            "reference": "PER-002",
            "type": "custom"
        })
        
        # Récupération des permissions par type
        system_permissions = self.permission_manager.get_permission_by_type("system")
        custom_permissions = self.permission_manager.get_permission_by_type("custom")
        
        # Vérification
        self.assertEqual(len(system_permissions), 1)
        self.assertEqual(len(custom_permissions), 1)
        self.assertEqual(system_permissions[0]["type"], "system")
        self.assertEqual(custom_permissions[0]["type"], "custom")

    def test_get_permission_by_status(self):
        """Test de récupération des permissions par statut."""
        # Création de permissions de différents statuts
        self.permission_manager.create_permission({
            **self.permission_data,
            "status": "active"
        })
        self.permission_manager.create_permission({
            **self.permission_data,
            "reference": "PER-002",
            "status": "inactive"
        })
        
        # Récupération des permissions par statut
        active_permissions = self.permission_manager.get_permission_by_status("active")
        inactive_permissions = self.permission_manager.get_permission_by_status("inactive")
        
        # Vérification
        self.assertEqual(len(active_permissions), 1)
        self.assertEqual(len(inactive_permissions), 1)
        self.assertEqual(active_permissions[0]["status"], "active")
        self.assertEqual(inactive_permissions[0]["status"], "inactive")

    def test_get_permission_by_module(self):
        """Test de récupération des permissions par module."""
        # Création de permissions de différents modules
        self.permission_manager.create_permission({
            **self.permission_data,
            "module": "repairs"
        })
        self.permission_manager.create_permission({
            **self.permission_data,
            "reference": "PER-002",
            "module": "warranties"
        })
        
        # Récupération des permissions par module
        repairs_permissions = self.permission_manager.get_permission_by_module("repairs")
        warranties_permissions = self.permission_manager.get_permission_by_module("warranties")
        
        # Vérification
        self.assertEqual(len(repairs_permissions), 1)
        self.assertEqual(len(warranties_permissions), 1)
        self.assertEqual(repairs_permissions[0]["module"], "repairs")
        self.assertEqual(warranties_permissions[0]["module"], "warranties")

    def test_validate_permission(self):
        """Test de validation de permission."""
        # Création d'une permission valide
        permission_obj = self.permission_manager.create_permission(self.permission_data)
        
        # Validation de la permission
        is_valid = self.permission_manager.validate_permission(permission_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_permission_summary(self):
        """Test de récupération du résumé de permission."""
        # Création de la permission
        permission_obj = self.permission_manager.create_permission(self.permission_data)
        
        # Récupération du résumé
        summary = self.permission_manager.get_permission_summary(permission_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("name" in summary)
        self.assertTrue("description" in summary)
        self.assertTrue("module" in summary)
        self.assertTrue("actions" in summary)
        self.assertTrue("scope" in summary)
        self.assertTrue("dependencies" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_permission_type(self):
        """Test avec un type de permission invalide."""
        with self.assertRaises(ValidationError):
            self.permission_manager.create_permission({
                **self.permission_data,
                "type": "invalid_type"
            })

    def test_invalid_permission_status(self):
        """Test avec un statut de permission invalide."""
        with self.assertRaises(ValidationError):
            self.permission_manager.create_permission({
                **self.permission_data,
                "status": "invalid_status"
            })

    def test_invalid_permission_dir(self):
        """Test avec un répertoire de permissions invalide."""
        with self.assertRaises(ValidationError):
            PermissionManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 