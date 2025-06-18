import unittest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.settings import SettingsManager
from alder_sav.utils.exceptions import ValidationError

class TestSettingsManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de paramètres."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.settings_dir = Path(self.temp_dir) / "settings"
        self.settings_dir.mkdir()
        
        # Initialisation du gestionnaire de paramètres
        self.settings_manager = SettingsManager(self.settings_dir)
        
        # Données de test
        self.settings_data = {
            "reference": "SET-001",
            "type": "system",
            "category": "general",
            "values": {
                "company": {
                    "name": "Alder SAV",
                    "address": "123 Rue du Commerce",
                    "city": "Paris",
                    "postal_code": "75001",
                    "country": "France",
                    "phone": "+33123456789",
                    "email": "contact@aldersav.com",
                    "website": "www.aldersav.com"
                },
                "business": {
                    "currency": "EUR",
                    "tax_rate": Decimal("20.00"),
                    "timezone": "Europe/Paris",
                    "language": "fr",
                    "date_format": "DD/MM/YYYY",
                    "time_format": "HH:mm:ss"
                },
                "notifications": {
                    "email": {
                        "enabled": True,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "use_tls": True,
                        "sender": "noreply@aldersav.com"
                    },
                    "sms": {
                        "enabled": False,
                        "provider": "twilio",
                        "sender": "ALDERSAV"
                    }
                },
                "security": {
                    "password_policy": {
                        "min_length": 8,
                        "require_uppercase": True,
                        "require_lowercase": True,
                        "require_numbers": True,
                        "require_special": True
                    },
                    "session": {
                        "timeout": 30,
                        "max_attempts": 3,
                        "lockout_duration": 15
                    }
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "author": "ADMIN-001",
                "tags": ["système", "configuration", "général"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_settings(self):
        """Test de création de paramètres."""
        # Création des paramètres
        settings_obj = self.settings_manager.create_settings(self.settings_data)
        
        # Vérification
        self.assertEqual(settings_obj["reference"], "SET-001")
        self.assertEqual(settings_obj["type"], "system")
        self.assertEqual(settings_obj["category"], "general")
        self.assertTrue("id" in settings_obj)
        self.assertTrue("creation_date" in settings_obj)

    def test_get_settings(self):
        """Test de récupération de paramètres."""
        # Création des paramètres
        settings_obj = self.settings_manager.create_settings(self.settings_data)
        
        # Récupération des paramètres
        retrieved_settings = self.settings_manager.get_settings(settings_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_settings["reference"], "SET-001")
        self.assertEqual(retrieved_settings["type"], "system")
        self.assertEqual(retrieved_settings["values"]["company"]["name"], "Alder SAV")

    def test_update_settings(self):
        """Test de mise à jour de paramètres."""
        # Création des paramètres
        settings_obj = self.settings_manager.create_settings(self.settings_data)
        
        # Mise à jour des paramètres
        updated_data = {
            "values": {
                "company": {
                    "name": "Alder SAV - Nouveau nom",
                    "phone": "+33987654321"
                }
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_settings = self.settings_manager.update_settings(settings_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_settings["values"]["company"]["name"], "Alder SAV - Nouveau nom")
        self.assertEqual(updated_settings["values"]["company"]["phone"], "+33987654321")

    def test_delete_settings(self):
        """Test de suppression de paramètres."""
        # Création des paramètres
        settings_obj = self.settings_manager.create_settings(self.settings_data)
        
        # Suppression des paramètres
        self.settings_manager.delete_settings(settings_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.settings_manager.get_settings(settings_obj["id"])

    def test_get_settings_by_type(self):
        """Test de récupération des paramètres par type."""
        # Création de paramètres de différents types
        self.settings_manager.create_settings({
            **self.settings_data,
            "type": "system"
        })
        self.settings_manager.create_settings({
            **self.settings_data,
            "reference": "SET-002",
            "type": "user"
        })
        
        # Récupération des paramètres par type
        system_settings = self.settings_manager.get_settings_by_type("system")
        user_settings = self.settings_manager.get_settings_by_type("user")
        
        # Vérification
        self.assertEqual(len(system_settings), 1)
        self.assertEqual(len(user_settings), 1)
        self.assertEqual(system_settings[0]["type"], "system")
        self.assertEqual(user_settings[0]["type"], "user")

    def test_get_settings_by_category(self):
        """Test de récupération des paramètres par catégorie."""
        # Création de paramètres de différentes catégories
        self.settings_manager.create_settings({
            **self.settings_data,
            "category": "general"
        })
        self.settings_manager.create_settings({
            **self.settings_data,
            "reference": "SET-002",
            "category": "security"
        })
        
        # Récupération des paramètres par catégorie
        general_settings = self.settings_manager.get_settings_by_category("general")
        security_settings = self.settings_manager.get_settings_by_category("security")
        
        # Vérification
        self.assertEqual(len(general_settings), 1)
        self.assertEqual(len(security_settings), 1)
        self.assertEqual(general_settings[0]["category"], "general")
        self.assertEqual(security_settings[0]["category"], "security")

    def test_validate_settings(self):
        """Test de validation de paramètres."""
        # Création de paramètres valides
        settings_obj = self.settings_manager.create_settings(self.settings_data)
        
        # Validation des paramètres
        is_valid = self.settings_manager.validate_settings(settings_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_settings_summary(self):
        """Test de récupération du résumé des paramètres."""
        # Création des paramètres
        settings_obj = self.settings_manager.create_settings(self.settings_data)
        
        # Récupération du résumé
        summary = self.settings_manager.get_settings_summary(settings_obj["id"])
        
        # Vérification
        self.assertTrue("type" in summary)
        self.assertTrue("category" in summary)
        self.assertTrue("values" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_settings_type(self):
        """Test avec un type de paramètres invalide."""
        with self.assertRaises(ValidationError):
            self.settings_manager.create_settings({
                **self.settings_data,
                "type": "invalid_type"
            })

    def test_invalid_settings_category(self):
        """Test avec une catégorie de paramètres invalide."""
        with self.assertRaises(ValidationError):
            self.settings_manager.create_settings({
                **self.settings_data,
                "category": "invalid_category"
            })

    def test_invalid_settings_dir(self):
        """Test avec un répertoire de paramètres invalide."""
        with self.assertRaises(ValidationError):
            SettingsManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 