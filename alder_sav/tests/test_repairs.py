import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.repairs import RepairManager
from alder_sav.utils.exceptions import ValidationError

class TestRepairManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de réparations."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.repairs_dir = Path(self.temp_dir) / "repairs"
        self.repairs_dir.mkdir()
        
        # Initialisation du gestionnaire de réparations
        self.repair_manager = RepairManager(self.repairs_dir)
        
        # Données de test
        self.repair_data = {
            "reference": "REP-001",
            "type": "hardware",
            "status": "pending",
            "device": {
                "id": "DEV-001",
                "type": "smartphone",
                "brand": "Apple",
                "model": "iPhone 13",
                "serial_number": "SN123456789"
            },
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "contact": {
                    "email": "jean.dupont@example.com",
                    "phone": "+33123456789"
                }
            },
            "diagnosis": {
                "issue": "Écran cassé",
                "description": "L'écran est fissuré et ne répond plus au toucher",
                "symptoms": ["écran noir", "tactile non fonctionnel"],
                "priority": "high",
                "estimated_time": 48,
                "technician_notes": "Remplacement de l'écran nécessaire"
            },
            "parts": [
                {
                    "id": "PART-001",
                    "name": "Écran iPhone 13",
                    "quantity": 1,
                    "price": Decimal("199.99")
                }
            ],
            "labor": {
                "hours": 2,
                "rate": Decimal("50.00"),
                "total": Decimal("100.00")
            },
            "pricing": {
                "parts_total": Decimal("199.99"),
                "labor_total": Decimal("100.00"),
                "tax_rate": 20.0,
                "tax_amount": Decimal("60.00"),
                "total": Decimal("359.99")
            },
            "schedule": {
                "start_date": datetime.now().isoformat(),
                "estimated_end_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "actual_end_date": None,
                "technician": {
                    "id": "TECH-001",
                    "name": "Pierre Martin"
                }
            },
            "warranty": {
                "type": "repair",
                "duration": 90,
                "coverage": ["parts", "labor"],
                "start_date": None,
                "end_date": None
            },
            "history": [
                {
                    "date": datetime.now().isoformat(),
                    "status": "pending",
                    "notes": "Réparation créée"
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Réparation urgente",
                "tags": ["urgent", "hardware"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_repair(self):
        """Test de création de réparation."""
        # Création de la réparation
        repair_obj = self.repair_manager.create_repair(self.repair_data)
        
        # Vérification
        self.assertEqual(repair_obj["reference"], "REP-001")
        self.assertEqual(repair_obj["type"], "hardware")
        self.assertEqual(repair_obj["status"], "pending")
        self.assertEqual(repair_obj["device"]["model"], "iPhone 13")
        self.assertEqual(len(repair_obj["parts"]), 1)
        self.assertTrue("id" in repair_obj)
        self.assertTrue("creation_date" in repair_obj)

    def test_get_repair(self):
        """Test de récupération de réparation."""
        # Création de la réparation
        repair_obj = self.repair_manager.create_repair(self.repair_data)
        
        # Récupération de la réparation
        retrieved_repair = self.repair_manager.get_repair(repair_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_repair["reference"], "REP-001")
        self.assertEqual(retrieved_repair["diagnosis"]["issue"], "Écran cassé")
        self.assertEqual(retrieved_repair["pricing"]["total"], Decimal("359.99"))
        self.assertEqual(retrieved_repair["schedule"]["technician"]["name"], "Pierre Martin")

    def test_update_repair(self):
        """Test de mise à jour de réparation."""
        # Création de la réparation
        repair_obj = self.repair_manager.create_repair(self.repair_data)
        
        # Mise à jour de la réparation
        updated_data = {
            "status": "in_progress",
            "diagnosis": {
                "technician_notes": "Remplacement de l'écran en cours"
            },
            "schedule": {
                "actual_end_date": (datetime.now() + timedelta(days=1)).isoformat()
            },
            "history": [
                {
                    "date": datetime.now().isoformat(),
                    "status": "in_progress",
                    "notes": "Réparation en cours"
                }
            ],
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_repair = self.repair_manager.update_repair(repair_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_repair["status"], "in_progress")
        self.assertEqual(updated_repair["diagnosis"]["technician_notes"], "Remplacement de l'écran en cours")
        self.assertTrue(updated_repair["schedule"]["actual_end_date"] is not None)

    def test_delete_repair(self):
        """Test de suppression de réparation."""
        # Création de la réparation
        repair_obj = self.repair_manager.create_repair(self.repair_data)
        
        # Suppression de la réparation
        self.repair_manager.delete_repair(repair_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.repair_manager.get_repair(repair_obj["id"])

    def test_get_repair_by_type(self):
        """Test de récupération des réparations par type."""
        # Création de réparations de différents types
        self.repair_manager.create_repair({
            **self.repair_data,
            "type": "hardware"
        })
        self.repair_manager.create_repair({
            **self.repair_data,
            "reference": "REP-002",
            "type": "software"
        })
        
        # Récupération des réparations par type
        hardware_repairs = self.repair_manager.get_repairs_by_type("hardware")
        software_repairs = self.repair_manager.get_repairs_by_type("software")
        
        # Vérification
        self.assertEqual(len(hardware_repairs), 1)
        self.assertEqual(len(software_repairs), 1)
        self.assertEqual(hardware_repairs[0]["type"], "hardware")
        self.assertEqual(software_repairs[0]["type"], "software")

    def test_get_repair_by_status(self):
        """Test de récupération des réparations par statut."""
        # Création de réparations avec différents statuts
        self.repair_manager.create_repair({
            **self.repair_data,
            "status": "pending"
        })
        self.repair_manager.create_repair({
            **self.repair_data,
            "reference": "REP-002",
            "status": "in_progress"
        })
        
        # Récupération des réparations par statut
        pending_repairs = self.repair_manager.get_repairs_by_status("pending")
        in_progress_repairs = self.repair_manager.get_repairs_by_status("in_progress")
        
        # Vérification
        self.assertEqual(len(pending_repairs), 1)
        self.assertEqual(len(in_progress_repairs), 1)
        self.assertEqual(pending_repairs[0]["status"], "pending")
        self.assertEqual(in_progress_repairs[0]["status"], "in_progress")

    def test_get_repair_by_client(self):
        """Test de récupération des réparations par client."""
        # Création de réparations pour différents clients
        self.repair_manager.create_repair({
            **self.repair_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.repair_manager.create_repair({
            **self.repair_data,
            "reference": "REP-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des réparations par client
        client1_repairs = self.repair_manager.get_repairs_by_client("CLI-001")
        client2_repairs = self.repair_manager.get_repairs_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_repairs), 1)
        self.assertEqual(len(client2_repairs), 1)
        self.assertEqual(client1_repairs[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_repairs[0]["client"]["id"], "CLI-002")

    def test_validate_repair(self):
        """Test de validation de réparation."""
        # Création d'une réparation valide
        repair_obj = self.repair_manager.create_repair(self.repair_data)
        
        # Validation de la réparation
        is_valid = self.repair_manager.validate_repair(repair_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_repair_summary(self):
        """Test de récupération du résumé de réparation."""
        # Création de la réparation
        repair_obj = self.repair_manager.create_repair(self.repair_data)
        
        # Récupération du résumé
        summary = self.repair_manager.get_repair_summary(repair_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("device" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("diagnosis" in summary)
        self.assertTrue("parts" in summary)
        self.assertTrue("labor" in summary)
        self.assertTrue("pricing" in summary)
        self.assertTrue("schedule" in summary)
        self.assertTrue("warranty" in summary)

    def test_invalid_repair_type(self):
        """Test avec un type de réparation invalide."""
        with self.assertRaises(ValidationError):
            self.repair_manager.create_repair({
                **self.repair_data,
                "type": "invalid_type"
            })

    def test_invalid_repair_status(self):
        """Test avec un statut de réparation invalide."""
        with self.assertRaises(ValidationError):
            self.repair_manager.create_repair({
                **self.repair_data,
                "status": "invalid_status"
            })

    def test_invalid_repair_dir(self):
        """Test avec un répertoire de réparations invalide."""
        with self.assertRaises(ValidationError):
            RepairManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 