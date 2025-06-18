import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.users import UserManager
from alder_sav.utils.exceptions import ValidationError

class TestUserManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire d'utilisateurs."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.users_dir = Path(self.temp_dir) / "users"
        self.users_dir.mkdir()
        
        # Initialisation du gestionnaire d'utilisateurs
        self.user_manager = UserManager(self.users_dir)
        
        # Données de test
        self.user_data = {
            "reference": "USR-001",
            "type": "employee",
            "status": "active",
            "personal_info": {
                "first_name": "Jean",
                "last_name": "Dupont",
                "email": "jean.dupont@aldersav.com",
                "phone": "+33612345678",
                "mobile": "+33612345678",
                "birth_date": "1990-01-01",
                "gender": "male",
                "address": {
                    "street": "123 rue de la Paix",
                    "city": "Paris",
                    "postal_code": "75000",
                    "country": "France"
                }
            },
            "professional_info": {
                "position": "Technicien SAV",
                "department": "Réparation",
                "hire_date": "2023-01-01",
                "contract_type": "CDI",
                "working_hours": {
                    "monday": {"start": "09:00", "end": "18:00"},
                    "tuesday": {"start": "09:00", "end": "18:00"},
                    "wednesday": {"start": "09:00", "end": "18:00"},
                    "thursday": {"start": "09:00", "end": "18:00"},
                    "friday": {"start": "09:00", "end": "18:00"}
                },
                "skills": [
                    "Réparation smartphone",
                    "Réparation ordinateur",
                    "Diagnostic logiciel"
                ],
                "certifications": [
                    {
                        "name": "Apple Certified Technician",
                        "date": "2023-01-01",
                        "expiry_date": "2024-01-01"
                    }
                ]
            },
            "security": {
                "username": "jdupont",
                "password_hash": "hashed_password",
                "role": "technician",
                "permissions": [
                    "view_repairs",
                    "create_repairs",
                    "update_repairs",
                    "delete_repairs"
                ],
                "last_login": datetime.now().isoformat(),
                "failed_attempts": 0,
                "locked_until": None
            },
            "activity": {
                "repairs_completed": 150,
                "average_rating": 4.5,
                "last_activity": datetime.now().isoformat(),
                "current_tasks": [
                    {
                        "type": "repair",
                        "reference": "REP-001",
                        "status": "in_progress"
                    }
                ]
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

    def test_create_user(self):
        """Test de création d'utilisateur."""
        # Création de l'utilisateur
        user_obj = self.user_manager.create_user(self.user_data)
        
        # Vérification
        self.assertEqual(user_obj["reference"], "USR-001")
        self.assertEqual(user_obj["type"], "employee")
        self.assertEqual(user_obj["status"], "active")
        self.assertEqual(user_obj["personal_info"]["first_name"], "Jean")
        self.assertEqual(user_obj["professional_info"]["position"], "Technicien SAV")
        self.assertTrue("id" in user_obj)
        self.assertTrue("creation_date" in user_obj)

    def test_get_user(self):
        """Test de récupération d'utilisateur."""
        # Création de l'utilisateur
        user_obj = self.user_manager.create_user(self.user_data)
        
        # Récupération de l'utilisateur
        retrieved_user = self.user_manager.get_user(user_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_user["reference"], "USR-001")
        self.assertEqual(retrieved_user["personal_info"]["email"], "jean.dupont@aldersav.com")
        self.assertEqual(retrieved_user["professional_info"]["department"], "Réparation")
        self.assertEqual(retrieved_user["security"]["role"], "technician")

    def test_update_user(self):
        """Test de mise à jour d'utilisateur."""
        # Création de l'utilisateur
        user_obj = self.user_manager.create_user(self.user_data)
        
        # Mise à jour de l'utilisateur
        updated_data = {
            "personal_info": {
                "phone": "+33612345679",
                "email": "jean.dupont@aldersav.fr"
            },
            "professional_info": {
                "position": "Technicien SAV Senior",
                "skills": [
                    "Réparation smartphone",
                    "Réparation ordinateur",
                    "Diagnostic logiciel",
                    "Formation"
                ]
            },
            "security": {
                "permissions": [
                    "view_repairs",
                    "create_repairs",
                    "update_repairs",
                    "delete_repairs",
                    "manage_users"
                ]
            },
            "metadata": {
                "updated_at": datetime.now().isoformat(),
                "version": "2.0"
            }
        }
        updated_user = self.user_manager.update_user(user_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_user["personal_info"]["phone"], "+33612345679")
        self.assertEqual(updated_user["professional_info"]["position"], "Technicien SAV Senior")
        self.assertEqual(len(updated_user["professional_info"]["skills"]), 4)
        self.assertEqual(len(updated_user["security"]["permissions"]), 5)
        self.assertEqual(updated_user["metadata"]["version"], "2.0")

    def test_delete_user(self):
        """Test de suppression d'utilisateur."""
        # Création de l'utilisateur
        user_obj = self.user_manager.create_user(self.user_data)
        
        # Suppression de l'utilisateur
        self.user_manager.delete_user(user_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.user_manager.get_user(user_obj["id"])

    def test_get_user_by_type(self):
        """Test de récupération des utilisateurs par type."""
        # Création d'utilisateurs de différents types
        self.user_manager.create_user({
            **self.user_data,
            "type": "employee"
        })
        self.user_manager.create_user({
            **self.user_data,
            "reference": "USR-002",
            "type": "admin"
        })
        
        # Récupération des utilisateurs par type
        employee_users = self.user_manager.get_user_by_type("employee")
        admin_users = self.user_manager.get_user_by_type("admin")
        
        # Vérification
        self.assertEqual(len(employee_users), 1)
        self.assertEqual(len(admin_users), 1)
        self.assertEqual(employee_users[0]["type"], "employee")
        self.assertEqual(admin_users[0]["type"], "admin")

    def test_get_user_by_status(self):
        """Test de récupération des utilisateurs par statut."""
        # Création d'utilisateurs de différents statuts
        self.user_manager.create_user({
            **self.user_data,
            "status": "active"
        })
        self.user_manager.create_user({
            **self.user_data,
            "reference": "USR-002",
            "status": "inactive"
        })
        
        # Récupération des utilisateurs par statut
        active_users = self.user_manager.get_user_by_status("active")
        inactive_users = self.user_manager.get_user_by_status("inactive")
        
        # Vérification
        self.assertEqual(len(active_users), 1)
        self.assertEqual(len(inactive_users), 1)
        self.assertEqual(active_users[0]["status"], "active")
        self.assertEqual(inactive_users[0]["status"], "inactive")

    def test_get_user_by_role(self):
        """Test de récupération des utilisateurs par rôle."""
        # Création d'utilisateurs de différents rôles
        self.user_manager.create_user({
            **self.user_data,
            "security": {
                **self.user_data["security"],
                "role": "technician"
            }
        })
        self.user_manager.create_user({
            **self.user_data,
            "reference": "USR-002",
            "security": {
                **self.user_data["security"],
                "role": "manager"
            }
        })
        
        # Récupération des utilisateurs par rôle
        technician_users = self.user_manager.get_user_by_role("technician")
        manager_users = self.user_manager.get_user_by_role("manager")
        
        # Vérification
        self.assertEqual(len(technician_users), 1)
        self.assertEqual(len(manager_users), 1)
        self.assertEqual(technician_users[0]["security"]["role"], "technician")
        self.assertEqual(manager_users[0]["security"]["role"], "manager")

    def test_validate_user(self):
        """Test de validation d'utilisateur."""
        # Création d'un utilisateur valide
        user_obj = self.user_manager.create_user(self.user_data)
        
        # Validation de l'utilisateur
        is_valid = self.user_manager.validate_user(user_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_user_summary(self):
        """Test de récupération du résumé d'utilisateur."""
        # Création de l'utilisateur
        user_obj = self.user_manager.create_user(self.user_data)
        
        # Récupération du résumé
        summary = self.user_manager.get_user_summary(user_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("personal_info" in summary)
        self.assertTrue("professional_info" in summary)
        self.assertTrue("security" in summary)
        self.assertTrue("activity" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_user_type(self):
        """Test avec un type d'utilisateur invalide."""
        with self.assertRaises(ValidationError):
            self.user_manager.create_user({
                **self.user_data,
                "type": "invalid_type"
            })

    def test_invalid_user_status(self):
        """Test avec un statut d'utilisateur invalide."""
        with self.assertRaises(ValidationError):
            self.user_manager.create_user({
                **self.user_data,
                "status": "invalid_status"
            })

    def test_invalid_user_dir(self):
        """Test avec un répertoire d'utilisateurs invalide."""
        with self.assertRaises(ValidationError):
            UserManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 