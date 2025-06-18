import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.technicians import TechnicianManager
from alder_sav.utils.exceptions import ValidationError

class TestTechnicianManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de techniciens."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.technician_dir = Path(self.temp_dir) / "technicians"
        self.technician_dir.mkdir()
        
        # Initialisation du gestionnaire de techniciens
        self.technician_manager = TechnicianManager(self.technician_dir)
        
        # Données de test
        self.technician_data = {
            "name": "John Doe",
            "specialty": "electronique",
            "status": "actif",
            "contact": {
                "email": "john.doe@example.com",
                "phone": "0123456789",
                "address": {
                    "street": "123 Test Street",
                    "city": "Test City",
                    "postal_code": "12345",
                    "country": "France"
                }
            },
            "skills": [
                "reparation_ordinateurs",
                "maintenance_reseaux",
                "diagnostic_materiel"
            ],
            "certifications": [
                {
                    "name": "CompTIA A+",
                    "date": (datetime.now() - timedelta(days=365)).isoformat(),
                    "expiry_date": (datetime.now() + timedelta(days=730)).isoformat()
                },
                {
                    "name": "Cisco CCNA",
                    "date": (datetime.now() - timedelta(days=180)).isoformat(),
                    "expiry_date": (datetime.now() + timedelta(days=545)).isoformat()
                }
            ],
            "availability": {
                "schedule": {
                    "monday": {"start": "09:00", "end": "18:00"},
                    "tuesday": {"start": "09:00", "end": "18:00"},
                    "wednesday": {"start": "09:00", "end": "18:00"},
                    "thursday": {"start": "09:00", "end": "18:00"},
                    "friday": {"start": "09:00", "end": "18:00"}
                },
                "max_interventions_per_day": 5
            },
            "performance": {
                "interventions_completed": 150,
                "average_rating": 4.5,
                "response_time": 2.5
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_technician(self):
        """Test de création d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Vérification
        self.assertEqual(technician["name"], "John Doe")
        self.assertEqual(technician["specialty"], "electronique")
        self.assertEqual(technician["status"], "actif")
        self.assertEqual(len(technician["skills"]), 3)
        self.assertEqual(len(technician["certifications"]), 2)
        self.assertTrue("id" in technician)
        self.assertTrue("creation_date" in technician)

    def test_get_technician(self):
        """Test de récupération d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Récupération du technicien
        retrieved_technician = self.technician_manager.get_technician(technician["id"])
        
        # Vérification
        self.assertEqual(retrieved_technician["name"], "John Doe")
        self.assertEqual(retrieved_technician["specialty"], "electronique")
        self.assertEqual(retrieved_technician["status"], "actif")

    def test_update_technician(self):
        """Test de mise à jour d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Mise à jour du technicien
        updated_data = {
            "status": "inactif",
            "contact": {
                "email": "john.doe.new@example.com",
                "phone": "0987654321"
            },
            "skills": [
                "reparation_ordinateurs",
                "maintenance_reseaux",
                "diagnostic_materiel",
                "virtualisation"
            ]
        }
        updated_technician = self.technician_manager.update_technician(technician["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_technician["status"], "inactif")
        self.assertEqual(updated_technician["contact"]["email"], "john.doe.new@example.com")
        self.assertEqual(len(updated_technician["skills"]), 4)

    def test_delete_technician(self):
        """Test de suppression d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Suppression du technicien
        self.technician_manager.delete_technician(technician["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.technician_manager.get_technician(technician["id"])

    def test_get_technician_by_status(self):
        """Test de récupération des techniciens par statut."""
        # Création de techniciens avec différents statuts
        self.technician_manager.create_technician(self.technician_data)
        self.technician_manager.create_technician({
            **self.technician_data,
            "name": "Jane Smith",
            "status": "inactif"
        })
        
        # Récupération des techniciens par statut
        actifs = self.technician_manager.get_technician_by_status("actif")
        inactifs = self.technician_manager.get_technician_by_status("inactif")
        
        # Vérification
        self.assertEqual(len(actifs), 1)
        self.assertEqual(len(inactifs), 1)
        self.assertEqual(actifs[0]["status"], "actif")
        self.assertEqual(inactifs[0]["status"], "inactif")

    def test_get_technician_by_specialty(self):
        """Test de récupération des techniciens par spécialité."""
        # Création de techniciens de différentes spécialités
        self.technician_manager.create_technician({
            **self.technician_data,
            "specialty": "electronique"
        })
        self.technician_manager.create_technician({
            **self.technician_data,
            "name": "Jane Smith",
            "specialty": "reseaux"
        })
        self.technician_manager.create_technician({
            **self.technician_data,
            "name": "Bob Wilson",
            "specialty": "electronique"
        })
        
        # Récupération des techniciens par spécialité
        electronique = self.technician_manager.get_technician_by_specialty("electronique")
        reseaux = self.technician_manager.get_technician_by_specialty("reseaux")
        
        # Vérification
        self.assertEqual(len(electronique), 2)
        self.assertEqual(len(reseaux), 1)
        self.assertEqual(electronique[0]["specialty"], "electronique")
        self.assertEqual(reseaux[0]["specialty"], "reseaux")

    def test_get_technician_by_skill(self):
        """Test de récupération des techniciens par compétence."""
        # Création de techniciens avec différentes compétences
        self.technician_manager.create_technician(self.technician_data)
        self.technician_manager.create_technician({
            **self.technician_data,
            "name": "Jane Smith",
            "skills": ["reparation_telephones", "maintenance_reseaux"]
        })
        
        # Récupération des techniciens par compétence
        reseaux = self.technician_manager.get_technician_by_skill("maintenance_reseaux")
        telephones = self.technician_manager.get_technician_by_skill("reparation_telephones")
        
        # Vérification
        self.assertEqual(len(reseaux), 2)
        self.assertEqual(len(telephones), 1)
        self.assertTrue("maintenance_reseaux" in reseaux[0]["skills"])
        self.assertTrue("reparation_telephones" in telephones[0]["skills"])

    def test_get_technician_availability(self):
        """Test de récupération de la disponibilité d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Récupération de la disponibilité
        availability = self.technician_manager.get_technician_availability(technician["id"])
        
        # Vérification
        self.assertTrue("schedule" in availability)
        self.assertTrue("max_interventions_per_day" in availability)
        self.assertEqual(availability["max_interventions_per_day"], 5)

    def test_update_technician_availability(self):
        """Test de mise à jour de la disponibilité d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Mise à jour de la disponibilité
        new_availability = {
            "schedule": {
                "monday": {"start": "08:00", "end": "17:00"},
                "tuesday": {"start": "08:00", "end": "17:00"},
                "wednesday": {"start": "08:00", "end": "17:00"},
                "thursday": {"start": "08:00", "end": "17:00"},
                "friday": {"start": "08:00", "end": "17:00"}
            },
            "max_interventions_per_day": 6
        }
        updated_availability = self.technician_manager.update_technician_availability(
            technician["id"],
            new_availability
        )
        
        # Vérification
        self.assertEqual(updated_availability["schedule"]["monday"]["start"], "08:00")
        self.assertEqual(updated_availability["max_interventions_per_day"], 6)

    def test_get_technician_performance(self):
        """Test de récupération des performances d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Récupération des performances
        performance = self.technician_manager.get_technician_performance(technician["id"])
        
        # Vérification
        self.assertTrue("interventions_completed" in performance)
        self.assertTrue("average_rating" in performance)
        self.assertTrue("response_time" in performance)
        self.assertEqual(performance["interventions_completed"], 150)
        self.assertEqual(performance["average_rating"], 4.5)

    def test_update_technician_performance(self):
        """Test de mise à jour des performances d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Mise à jour des performances
        new_performance = {
            "interventions_completed": 151,
            "average_rating": 4.6,
            "response_time": 2.3
        }
        updated_performance = self.technician_manager.update_technician_performance(
            technician["id"],
            new_performance
        )
        
        # Vérification
        self.assertEqual(updated_performance["interventions_completed"], 151)
        self.assertEqual(updated_performance["average_rating"], 4.6)
        self.assertEqual(updated_performance["response_time"], 2.3)

    def test_validate_technician(self):
        """Test de validation d'un technicien."""
        # Création d'un technicien valide
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Validation du technicien
        is_valid = self.technician_manager.validate_technician(technician["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_technician_stats(self):
        """Test de récupération des statistiques d'un technicien."""
        # Création du technicien
        technician = self.technician_manager.create_technician(self.technician_data)
        
        # Récupération des statistiques
        stats = self.technician_manager.get_technician_stats(technician["id"])
        
        # Vérification
        self.assertTrue("specialty" in stats)
        self.assertTrue("status" in stats)
        self.assertTrue("skills" in stats)
        self.assertTrue("certifications" in stats)
        self.assertTrue("performance" in stats)

    def test_invalid_technician_specialty(self):
        """Test avec une spécialité de technicien invalide."""
        with self.assertRaises(ValidationError):
            self.technician_manager.create_technician({
                **self.technician_data,
                "specialty": "invalid_specialty"
            })

    def test_invalid_technician_status(self):
        """Test avec un statut de technicien invalide."""
        with self.assertRaises(ValidationError):
            self.technician_manager.create_technician({
                **self.technician_data,
                "status": "invalid_status"
            })

    def test_invalid_technician_dir(self):
        """Test avec un répertoire de techniciens invalide."""
        with self.assertRaises(ValidationError):
            TechnicianManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 