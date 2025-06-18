import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.roles import RoleManager
from alder_sav.utils.exceptions import ValidationError

class TestRoleManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de rôles."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.roles_dir = Path(self.temp_dir) / "roles"
        self.roles_dir.mkdir()
        
        # Initialisation du gestionnaire de rôles
        self.role_manager = RoleManager(self.roles_dir)
        
        # Données de test
        self.role_data = {
            "reference": "ROL-001",
            "type": "system",
            "status": "active",
            "name": "Technicien SAV",
            "description": "Rôle pour les techniciens du service après-vente",
            "permissions": {
                "repairs": {
                    "view": True,
                    "create": True,
                    "update": True,
                    "delete": False
                },
                "clients": {
                    "view": True,
                    "create": True,
                    "update": True,
                    "delete": False
                },
                "devices": {
                    "view": True,
                    "create": True,
                    "update": True,
                    "delete": False
                },
                "parts": {
                    "view": True,
                    "create": True,
                    "update": True,
                    "delete": False
                },
                "warranties": {
                    "view": True,
                    "create": False,
                    "update": False,
                    "delete": False
                },
                "users": {
                    "view": True,
                    "create": False,
                    "update": False,
                    "delete": False
                },
                "reports": {
                    "view": True,
                    "create": True,
                    "update": False,
                    "delete": False
                }
            },
            "access_level": "standard",
            "restrictions": {
                "max_repairs_per_day": 10,
                "allowed_device_types": [
                    "smartphone",
                    "tablet",
                    "laptop"
                ],
                "allowed_repair_types": [
                    "hardware",
                    "software"
                ],
                "working_hours": {
                    "monday": {"start": "09:00", "end": "18:00"},
                    "tuesday": {"start": "09:00", "end": "18:00"},
                    "wednesday": {"start": "09:00", "end": "18:00"},
                    "thursday": {"start": "09:00", "end": "18:00"},
                    "friday": {"start": "09:00", "end": "18:00"}
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0",
                "tags": ["technicien", "sav"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_role(self):
        """Test de création de rôle."""
        # Création du rôle
        role_obj = self.role_manager.create_role(self.role_data)
        
        # Vérification
        self.assertEqual(role_obj["reference"], "ROL-001")
        self.assertEqual(role_obj["type"], "system")
        self.assertEqual(role_obj["status"], "active")
        self.assertEqual(role_obj["name"], "Technicien SAV")
        self.assertTrue("id" in role_obj)
        self.assertTrue("creation_date" in role_obj)

    def test_get_role(self):
        """Test de récupération de rôle."""
        # Création du rôle
        role_obj = self.role_manager.create_role(self.role_data)
        
        # Récupération du rôle
        retrieved_role = self.role_manager.get_role(role_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_role["reference"], "ROL-001")
        self.assertEqual(retrieved_role["name"], "Technicien SAV")
        self.assertEqual(retrieved_role["access_level"], "standard")
        self.assertTrue(retrieved_role["permissions"]["repairs"]["view"])
        self.assertFalse(retrieved_role["permissions"]["warranties"]["create"])

    def test_update_role(self):
        """Test de mise à jour de rôle."""
        # Création du rôle
        role_obj = self.role_manager.create_role(self.role_data)
        
        # Mise à jour du rôle
        updated_data = {
            "permissions": {
                "repairs": {
                    "view": True,
                    "create": True,
                    "update": True,
                    "delete": True
                },
                "warranties": {
                    "view": True,
                    "create": True,
                    "update": True,
                    "delete": False
                }
            },
            "restrictions": {
                "max_repairs_per_day": 15,
                "allowed_device_types": [
                    "smartphone",
                    "tablet",
                    "laptop",
                    "desktop"
                ]
            },
            "metadata": {
                "updated_at": datetime.now().isoformat(),
                "version": "2.0"
            }
        }
        updated_role = self.role_manager.update_role(role_obj["id"], updated_data)
        
        # Vérification
        self.assertTrue(updated_role["permissions"]["repairs"]["delete"])
        self.assertTrue(updated_role["permissions"]["warranties"]["create"])
        self.assertEqual(updated_role["restrictions"]["max_repairs_per_day"], 15)
        self.assertEqual(len(updated_role["restrictions"]["allowed_device_types"]), 4)
        self.assertEqual(updated_role["metadata"]["version"], "2.0")

    def test_delete_role(self):
        """Test de suppression de rôle."""
        # Création du rôle
        role_obj = self.role_manager.create_role(self.role_data)
        
        # Suppression du rôle
        self.role_manager.delete_role(role_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.role_manager.get_role(role_obj["id"])

    def test_get_role_by_type(self):
        """Test de récupération des rôles par type."""
        # Création de rôles de différents types
        self.role_manager.create_role({
            **self.role_data,
            "type": "system"
        })
        self.role_manager.create_role({
            **self.role_data,
            "reference": "ROL-002",
            "type": "custom"
        })
        
        # Récupération des rôles par type
        system_roles = self.role_manager.get_role_by_type("system")
        custom_roles = self.role_manager.get_role_by_type("custom")
        
        # Vérification
        self.assertEqual(len(system_roles), 1)
        self.assertEqual(len(custom_roles), 1)
        self.assertEqual(system_roles[0]["type"], "system")
        self.assertEqual(custom_roles[0]["type"], "custom")

    def test_get_role_by_status(self):
        """Test de récupération des rôles par statut."""
        # Création de rôles de différents statuts
        self.role_manager.create_role({
            **self.role_data,
            "status": "active"
        })
        self.role_manager.create_role({
            **self.role_data,
            "reference": "ROL-002",
            "status": "inactive"
        })
        
        # Récupération des rôles par statut
        active_roles = self.role_manager.get_role_by_status("active")
        inactive_roles = self.role_manager.get_role_by_status("inactive")
        
        # Vérification
        self.assertEqual(len(active_roles), 1)
        self.assertEqual(len(inactive_roles), 1)
        self.assertEqual(active_roles[0]["status"], "active")
        self.assertEqual(inactive_roles[0]["status"], "inactive")

    def test_get_role_by_access_level(self):
        """Test de récupération des rôles par niveau d'accès."""
        # Création de rôles de différents niveaux d'accès
        self.role_manager.create_role({
            **self.role_data,
            "access_level": "standard"
        })
        self.role_manager.create_role({
            **self.role_data,
            "reference": "ROL-002",
            "access_level": "admin"
        })
        
        # Récupération des rôles par niveau d'accès
        standard_roles = self.role_manager.get_role_by_access_level("standard")
        admin_roles = self.role_manager.get_role_by_access_level("admin")
        
        # Vérification
        self.assertEqual(len(standard_roles), 1)
        self.assertEqual(len(admin_roles), 1)
        self.assertEqual(standard_roles[0]["access_level"], "standard")
        self.assertEqual(admin_roles[0]["access_level"], "admin")

    def test_validate_role(self):
        """Test de validation de rôle."""
        # Création d'un rôle valide
        role_obj = self.role_manager.create_role(self.role_data)
        
        # Validation du rôle
        is_valid = self.role_manager.validate_role(role_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_role_summary(self):
        """Test de récupération du résumé de rôle."""
        # Création du rôle
        role_obj = self.role_manager.create_role(self.role_data)
        
        # Récupération du résumé
        summary = self.role_manager.get_role_summary(role_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("name" in summary)
        self.assertTrue("description" in summary)
        self.assertTrue("permissions" in summary)
        self.assertTrue("access_level" in summary)
        self.assertTrue("restrictions" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_role_type(self):
        """Test avec un type de rôle invalide."""
        with self.assertRaises(ValidationError):
            self.role_manager.create_role({
                **self.role_data,
                "type": "invalid_type"
            })

    def test_invalid_role_status(self):
        """Test avec un statut de rôle invalide."""
        with self.assertRaises(ValidationError):
            self.role_manager.create_role({
                **self.role_data,
                "status": "invalid_status"
            })

    def test_invalid_role_dir(self):
        """Test avec un répertoire de rôles invalide."""
        with self.assertRaises(ValidationError):
            RoleManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 