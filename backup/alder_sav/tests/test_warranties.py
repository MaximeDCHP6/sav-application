import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.warranties import WarrantyManager
from alder_sav.utils.exceptions import ValidationError

class TestWarrantyManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de garanties."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.warranties_dir = Path(self.temp_dir) / "warranties"
        self.warranties_dir.mkdir()
        
        # Initialisation du gestionnaire de garanties
        self.warranty_manager = WarrantyManager(self.warranties_dir)
        
        # Données de test
        self.warranty_data = {
            "reference": "WAR-001",
            "type": "manufacturer",
            "status": "active",
            "device": {
                "id": "DEV-001",
                "type": "smartphone",
                "brand": "Apple",
                "model": "iPhone 13",
                "serial_number": "SN123456789",
                "purchase_date": (datetime.now() - timedelta(days=30)).isoformat()
            },
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "contact": {
                    "email": "jean.dupont@example.com",
                    "phone": "+33123456789"
                }
            },
            "coverage": {
                "type": "standard",
                "duration": 365,
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=335)).isoformat(),
                "terms": [
                    "Réparation des défauts de fabrication",
                    "Remplacement des pièces défectueuses",
                    "Maintenance préventive"
                ],
                "exclusions": [
                    "Dommages accidentels",
                    "Modifications non autorisées",
                    "Utilisation abusive"
                ]
            },
            "service": {
                "provider": "Apple",
                "contact": {
                    "phone": "+33123456789",
                    "email": "support@apple.com"
                },
                "process": "Réparation en centre agréé",
                "response_time": 48
            },
            "claims": [],
            "history": [
                {
                    "date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "action": "created",
                    "notes": "Garantie créée à l'achat"
                }
            ],
            "metadata": {
                "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Garantie constructeur standard",
                "tags": ["smartphone", "apple", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_warranty(self):
        """Test de création de garantie."""
        # Création de la garantie
        warranty_obj = self.warranty_manager.create_warranty(self.warranty_data)
        
        # Vérification
        self.assertEqual(warranty_obj["reference"], "WAR-001")
        self.assertEqual(warranty_obj["type"], "manufacturer")
        self.assertEqual(warranty_obj["status"], "active")
        self.assertEqual(warranty_obj["device"]["model"], "iPhone 13")
        self.assertEqual(len(warranty_obj["coverage"]["terms"]), 3)
        self.assertTrue("id" in warranty_obj)
        self.assertTrue("creation_date" in warranty_obj)

    def test_get_warranty(self):
        """Test de récupération de garantie."""
        # Création de la garantie
        warranty_obj = self.warranty_manager.create_warranty(self.warranty_data)
        
        # Récupération de la garantie
        retrieved_warranty = self.warranty_manager.get_warranty(warranty_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_warranty["reference"], "WAR-001")
        self.assertEqual(retrieved_warranty["coverage"]["type"], "standard")
        self.assertEqual(retrieved_warranty["service"]["provider"], "Apple")
        self.assertEqual(len(retrieved_warranty["coverage"]["terms"]), 3)

    def test_update_warranty(self):
        """Test de mise à jour de garantie."""
        # Création de la garantie
        warranty_obj = self.warranty_manager.create_warranty(self.warranty_data)
        
        # Mise à jour de la garantie
        updated_data = {
            "status": "expired",
            "coverage": {
                "end_date": datetime.now().isoformat()
            },
            "history": [
                {
                    "date": datetime.now().isoformat(),
                    "action": "expired",
                    "notes": "Garantie expirée"
                }
            ],
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_warranty = self.warranty_manager.update_warranty(warranty_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_warranty["status"], "expired")
        self.assertEqual(updated_warranty["coverage"]["end_date"], datetime.now().isoformat())
        self.assertEqual(len(updated_warranty["history"]), 2)

    def test_delete_warranty(self):
        """Test de suppression de garantie."""
        # Création de la garantie
        warranty_obj = self.warranty_manager.create_warranty(self.warranty_data)
        
        # Suppression de la garantie
        self.warranty_manager.delete_warranty(warranty_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.warranty_manager.get_warranty(warranty_obj["id"])

    def test_get_warranty_by_type(self):
        """Test de récupération des garanties par type."""
        # Création de garanties de différents types
        self.warranty_manager.create_warranty({
            **self.warranty_data,
            "type": "manufacturer"
        })
        self.warranty_manager.create_warranty({
            **self.warranty_data,
            "reference": "WAR-002",
            "type": "extended"
        })
        
        # Récupération des garanties par type
        manufacturer_warranties = self.warranty_manager.get_warranties_by_type("manufacturer")
        extended_warranties = self.warranty_manager.get_warranties_by_type("extended")
        
        # Vérification
        self.assertEqual(len(manufacturer_warranties), 1)
        self.assertEqual(len(extended_warranties), 1)
        self.assertEqual(manufacturer_warranties[0]["type"], "manufacturer")
        self.assertEqual(extended_warranties[0]["type"], "extended")

    def test_get_warranty_by_status(self):
        """Test de récupération des garanties par statut."""
        # Création de garanties avec différents statuts
        self.warranty_manager.create_warranty({
            **self.warranty_data,
            "status": "active"
        })
        self.warranty_manager.create_warranty({
            **self.warranty_data,
            "reference": "WAR-002",
            "status": "expired"
        })
        
        # Récupération des garanties par statut
        active_warranties = self.warranty_manager.get_warranties_by_status("active")
        expired_warranties = self.warranty_manager.get_warranties_by_status("expired")
        
        # Vérification
        self.assertEqual(len(active_warranties), 1)
        self.assertEqual(len(expired_warranties), 1)
        self.assertEqual(active_warranties[0]["status"], "active")
        self.assertEqual(expired_warranties[0]["status"], "expired")

    def test_get_warranty_by_client(self):
        """Test de récupération des garanties par client."""
        # Création de garanties pour différents clients
        self.warranty_manager.create_warranty({
            **self.warranty_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.warranty_manager.create_warranty({
            **self.warranty_data,
            "reference": "WAR-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des garanties par client
        client1_warranties = self.warranty_manager.get_warranties_by_client("CLI-001")
        client2_warranties = self.warranty_manager.get_warranties_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_warranties), 1)
        self.assertEqual(len(client2_warranties), 1)
        self.assertEqual(client1_warranties[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_warranties[0]["client"]["id"], "CLI-002")

    def test_validate_warranty(self):
        """Test de validation de garantie."""
        # Création d'une garantie valide
        warranty_obj = self.warranty_manager.create_warranty(self.warranty_data)
        
        # Validation de la garantie
        is_valid = self.warranty_manager.validate_warranty(warranty_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_warranty_summary(self):
        """Test de récupération du résumé de garantie."""
        # Création de la garantie
        warranty_obj = self.warranty_manager.create_warranty(self.warranty_data)
        
        # Récupération du résumé
        summary = self.warranty_manager.get_warranty_summary(warranty_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("device" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("coverage" in summary)
        self.assertTrue("service" in summary)
        self.assertTrue("claims" in summary)
        self.assertTrue("history" in summary)

    def test_invalid_warranty_type(self):
        """Test avec un type de garantie invalide."""
        with self.assertRaises(ValidationError):
            self.warranty_manager.create_warranty({
                **self.warranty_data,
                "type": "invalid_type"
            })

    def test_invalid_warranty_status(self):
        """Test avec un statut de garantie invalide."""
        with self.assertRaises(ValidationError):
            self.warranty_manager.create_warranty({
                **self.warranty_data,
                "status": "invalid_status"
            })

    def test_invalid_warranty_dir(self):
        """Test avec un répertoire de garanties invalide."""
        with self.assertRaises(ValidationError):
            WarrantyManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 