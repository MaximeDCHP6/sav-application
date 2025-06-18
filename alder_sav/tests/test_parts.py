import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.parts import PartManager
from alder_sav.utils.exceptions import ValidationError

class TestPartManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de pièces détachées."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.parts_dir = Path(self.temp_dir) / "parts"
        self.parts_dir.mkdir()
        
        # Initialisation du gestionnaire de pièces détachées
        self.part_manager = PartManager(self.parts_dir)
        
        # Données de test
        self.part_data = {
            "reference": "PART-001",
            "type": "screen",
            "status": "in_stock",
            "name": "Écran iPhone 13",
            "brand": "Apple",
            "model": "iPhone 13",
            "compatibility": [
                {
                    "brand": "Apple",
                    "model": "iPhone 13",
                    "variant": "standard"
                }
            ],
            "specifications": {
                "color": "noir",
                "resolution": "2532x1170",
                "size": "6.1 pouces",
                "technology": "OLED",
                "material": "verre trempé"
            },
            "stock": {
                "quantity": 10,
                "min_quantity": 5,
                "location": "A-123",
                "condition": "new",
                "batch_number": "BATCH-001",
                "expiry_date": None
            },
            "pricing": {
                "purchase_price": Decimal("150.00"),
                "selling_price": Decimal("199.99"),
                "currency": "EUR",
                "vat_rate": 20.0,
                "margin": Decimal("33.33")
            },
            "supplier": {
                "id": "SUP-001",
                "name": "TechParts",
                "contact": {
                    "email": "contact@techparts.com",
                    "phone": "+33123456789"
                }
            },
            "warranty": {
                "type": "standard",
                "duration": 12,
                "coverage": ["manufacturing_defects", "installation"],
                "provider": "TechParts"
            },
            "usage_history": [
                {
                    "repair_id": "REP-001",
                    "date": datetime.now().isoformat(),
                    "quantity": 1,
                    "status": "used"
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Pièce de qualité premium",
                "tags": ["premium", "new"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_part(self):
        """Test de création de pièce détachée."""
        # Création de la pièce détachée
        part_obj = self.part_manager.create_part(self.part_data)
        
        # Vérification
        self.assertEqual(part_obj["reference"], "PART-001")
        self.assertEqual(part_obj["type"], "screen")
        self.assertEqual(part_obj["status"], "in_stock")
        self.assertEqual(part_obj["name"], "Écran iPhone 13")
        self.assertEqual(len(part_obj["compatibility"]), 1)
        self.assertTrue("id" in part_obj)
        self.assertTrue("creation_date" in part_obj)

    def test_get_part(self):
        """Test de récupération de pièce détachée."""
        # Création de la pièce détachée
        part_obj = self.part_manager.create_part(self.part_data)
        
        # Récupération de la pièce détachée
        retrieved_part = self.part_manager.get_part(part_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_part["reference"], "PART-001")
        self.assertEqual(retrieved_part["brand"], "Apple")
        self.assertEqual(retrieved_part["specifications"]["resolution"], "2532x1170")
        self.assertEqual(retrieved_part["stock"]["quantity"], 10)

    def test_update_part(self):
        """Test de mise à jour de pièce détachée."""
        # Création de la pièce détachée
        part_obj = self.part_manager.create_part(self.part_data)
        
        # Mise à jour de la pièce détachée
        updated_data = {
            "status": "low_stock",
            "stock": {
                "quantity": 3,
                "updated_at": datetime.now().isoformat()
            },
            "pricing": {
                "selling_price": Decimal("179.99")
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_part = self.part_manager.update_part(part_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_part["status"], "low_stock")
        self.assertEqual(updated_part["stock"]["quantity"], 3)
        self.assertEqual(updated_part["pricing"]["selling_price"], Decimal("179.99"))

    def test_delete_part(self):
        """Test de suppression de pièce détachée."""
        # Création de la pièce détachée
        part_obj = self.part_manager.create_part(self.part_data)
        
        # Suppression de la pièce détachée
        self.part_manager.delete_part(part_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.part_manager.get_part(part_obj["id"])

    def test_get_part_by_type(self):
        """Test de récupération des pièces détachées par type."""
        # Création de pièces détachées de différents types
        self.part_manager.create_part({
            **self.part_data,
            "type": "screen"
        })
        self.part_manager.create_part({
            **self.part_data,
            "reference": "PART-002",
            "type": "battery"
        })
        
        # Récupération des pièces détachées par type
        screen_parts = self.part_manager.get_parts_by_type("screen")
        battery_parts = self.part_manager.get_parts_by_type("battery")
        
        # Vérification
        self.assertEqual(len(screen_parts), 1)
        self.assertEqual(len(battery_parts), 1)
        self.assertEqual(screen_parts[0]["type"], "screen")
        self.assertEqual(battery_parts[0]["type"], "battery")

    def test_get_part_by_status(self):
        """Test de récupération des pièces détachées par statut."""
        # Création de pièces détachées avec différents statuts
        self.part_manager.create_part({
            **self.part_data,
            "status": "in_stock"
        })
        self.part_manager.create_part({
            **self.part_data,
            "reference": "PART-002",
            "status": "out_of_stock"
        })
        
        # Récupération des pièces détachées par statut
        in_stock_parts = self.part_manager.get_parts_by_status("in_stock")
        out_of_stock_parts = self.part_manager.get_parts_by_status("out_of_stock")
        
        # Vérification
        self.assertEqual(len(in_stock_parts), 1)
        self.assertEqual(len(out_of_stock_parts), 1)
        self.assertEqual(in_stock_parts[0]["status"], "in_stock")
        self.assertEqual(out_of_stock_parts[0]["status"], "out_of_stock")

    def test_get_part_by_supplier(self):
        """Test de récupération des pièces détachées par fournisseur."""
        # Création de pièces détachées pour différents fournisseurs
        self.part_manager.create_part({
            **self.part_data,
            "supplier": {
                "id": "SUP-001",
                "name": "TechParts"
            }
        })
        self.part_manager.create_part({
            **self.part_data,
            "reference": "PART-002",
            "supplier": {
                "id": "SUP-002",
                "name": "PartsPro"
            }
        })
        
        # Récupération des pièces détachées par fournisseur
        supplier1_parts = self.part_manager.get_parts_by_supplier("SUP-001")
        supplier2_parts = self.part_manager.get_parts_by_supplier("SUP-002")
        
        # Vérification
        self.assertEqual(len(supplier1_parts), 1)
        self.assertEqual(len(supplier2_parts), 1)
        self.assertEqual(supplier1_parts[0]["supplier"]["id"], "SUP-001")
        self.assertEqual(supplier2_parts[0]["supplier"]["id"], "SUP-002")

    def test_validate_part(self):
        """Test de validation de pièce détachée."""
        # Création d'une pièce détachée valide
        part_obj = self.part_manager.create_part(self.part_data)
        
        # Validation de la pièce détachée
        is_valid = self.part_manager.validate_part(part_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_part_summary(self):
        """Test de récupération du résumé de pièce détachée."""
        # Création de la pièce détachée
        part_obj = self.part_manager.create_part(self.part_data)
        
        # Récupération du résumé
        summary = self.part_manager.get_part_summary(part_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("name" in summary)
        self.assertTrue("brand" in summary)
        self.assertTrue("compatibility" in summary)
        self.assertTrue("specifications" in summary)
        self.assertTrue("stock" in summary)
        self.assertTrue("pricing" in summary)
        self.assertTrue("supplier" in summary)
        self.assertTrue("warranty" in summary)

    def test_invalid_part_type(self):
        """Test avec un type de pièce détachée invalide."""
        with self.assertRaises(ValidationError):
            self.part_manager.create_part({
                **self.part_data,
                "type": "invalid_type"
            })

    def test_invalid_part_status(self):
        """Test avec un statut de pièce détachée invalide."""
        with self.assertRaises(ValidationError):
            self.part_manager.create_part({
                **self.part_data,
                "status": "invalid_status"
            })

    def test_invalid_part_dir(self):
        """Test avec un répertoire de pièces détachées invalide."""
        with self.assertRaises(ValidationError):
            PartManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 