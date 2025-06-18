import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.inventory import InventoryManager
from alder_sav.utils.exceptions import ValidationError

class TestInventoryManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de stocks."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.inventory_dir = Path(self.temp_dir) / "inventory"
        self.inventory_dir.mkdir()
        
        # Initialisation du gestionnaire de stocks
        self.inventory_manager = InventoryManager(self.inventory_dir)
        
        # Données de test
        self.inventory_data = {
            "reference": "INV-001",
            "type": "product",
            "status": "active",
            "product": {
                "id": "PRD-001",
                "name": "Smartphone XYZ",
                "sku": "SP-XYZ-001",
                "category": "electronics",
                "brand": "TechBrand",
                "model": "XYZ-2023"
            },
            "stock": {
                "quantity": 100,
                "min_quantity": 10,
                "max_quantity": 200,
                "reserved": 0,
                "available": 100,
                "unit": "piece"
            },
            "location": {
                "warehouse": "WH-001",
                "zone": "A",
                "aisle": "1",
                "shelf": "2",
                "bin": "3"
            },
            "pricing": {
                "cost": Decimal("500.00"),
                "retail": Decimal("999.99"),
                "currency": "EUR"
            },
            "supplier": {
                "id": "SUP-001",
                "name": "TechSupplier",
                "contact": "contact@techsupplier.com",
                "lead_time": 7
            },
            "movements": [
                {
                    "type": "initial",
                    "quantity": 100,
                    "date": datetime.now().isoformat(),
                    "reference": "INIT-001",
                    "notes": "Stock initial"
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Stock standard",
                "tags": ["nouveau", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_inventory(self):
        """Test de création de stock."""
        # Création du stock
        inventory_obj = self.inventory_manager.create_inventory(self.inventory_data)
        
        # Vérification
        self.assertEqual(inventory_obj["reference"], "INV-001")
        self.assertEqual(inventory_obj["type"], "product")
        self.assertEqual(inventory_obj["status"], "active")
        self.assertEqual(inventory_obj["stock"]["quantity"], 100)
        self.assertEqual(inventory_obj["stock"]["available"], 100)
        self.assertTrue("id" in inventory_obj)
        self.assertTrue("creation_date" in inventory_obj)

    def test_get_inventory(self):
        """Test de récupération de stock."""
        # Création du stock
        inventory_obj = self.inventory_manager.create_inventory(self.inventory_data)
        
        # Récupération du stock
        retrieved_inventory = self.inventory_manager.get_inventory(inventory_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_inventory["reference"], "INV-001")
        self.assertEqual(retrieved_inventory["product"]["name"], "Smartphone XYZ")
        self.assertEqual(retrieved_inventory["stock"]["quantity"], 100)
        self.assertEqual(retrieved_inventory["pricing"]["retail"], Decimal("999.99"))

    def test_update_inventory(self):
        """Test de mise à jour de stock."""
        # Création du stock
        inventory_obj = self.inventory_manager.create_inventory(self.inventory_data)
        
        # Mise à jour du stock
        updated_data = {
            "stock": {
                "quantity": 80,
                "reserved": 20,
                "available": 60
            },
            "movements": [
                {
                    "type": "sale",
                    "quantity": -20,
                    "date": datetime.now().isoformat(),
                    "reference": "SALE-001",
                    "notes": "Vente de 20 unités"
                }
            ],
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_inventory = self.inventory_manager.update_inventory(inventory_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_inventory["stock"]["quantity"], 80)
        self.assertEqual(updated_inventory["stock"]["reserved"], 20)
        self.assertEqual(updated_inventory["stock"]["available"], 60)
        self.assertEqual(len(updated_inventory["movements"]), 2)

    def test_delete_inventory(self):
        """Test de suppression de stock."""
        # Création du stock
        inventory_obj = self.inventory_manager.create_inventory(self.inventory_data)
        
        # Suppression du stock
        self.inventory_manager.delete_inventory(inventory_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.inventory_manager.get_inventory(inventory_obj["id"])

    def test_get_inventory_by_type(self):
        """Test de récupération des stocks par type."""
        # Création de stocks de différents types
        self.inventory_manager.create_inventory({
            **self.inventory_data,
            "type": "product"
        })
        self.inventory_manager.create_inventory({
            **self.inventory_data,
            "reference": "INV-002",
            "type": "component"
        })
        
        # Récupération des stocks par type
        product_inventories = self.inventory_manager.get_inventories_by_type("product")
        component_inventories = self.inventory_manager.get_inventories_by_type("component")
        
        # Vérification
        self.assertEqual(len(product_inventories), 1)
        self.assertEqual(len(component_inventories), 1)
        self.assertEqual(product_inventories[0]["type"], "product")
        self.assertEqual(component_inventories[0]["type"], "component")

    def test_get_inventory_by_status(self):
        """Test de récupération des stocks par statut."""
        # Création de stocks avec différents statuts
        self.inventory_manager.create_inventory({
            **self.inventory_data,
            "status": "active"
        })
        self.inventory_manager.create_inventory({
            **self.inventory_data,
            "reference": "INV-002",
            "status": "inactive"
        })
        
        # Récupération des stocks par statut
        active_inventories = self.inventory_manager.get_inventories_by_status("active")
        inactive_inventories = self.inventory_manager.get_inventories_by_status("inactive")
        
        # Vérification
        self.assertEqual(len(active_inventories), 1)
        self.assertEqual(len(inactive_inventories), 1)
        self.assertEqual(active_inventories[0]["status"], "active")
        self.assertEqual(inactive_inventories[0]["status"], "inactive")

    def test_get_inventory_by_product(self):
        """Test de récupération des stocks par produit."""
        # Création de stocks pour différents produits
        self.inventory_manager.create_inventory({
            **self.inventory_data,
            "product": {
                "id": "PRD-001",
                "name": "Smartphone XYZ"
            }
        })
        self.inventory_manager.create_inventory({
            **self.inventory_data,
            "reference": "INV-002",
            "product": {
                "id": "PRD-002",
                "name": "Smartphone ABC"
            }
        })
        
        # Récupération des stocks par produit
        product1_inventories = self.inventory_manager.get_inventories_by_product("PRD-001")
        product2_inventories = self.inventory_manager.get_inventories_by_product("PRD-002")
        
        # Vérification
        self.assertEqual(len(product1_inventories), 1)
        self.assertEqual(len(product2_inventories), 1)
        self.assertEqual(product1_inventories[0]["product"]["id"], "PRD-001")
        self.assertEqual(product2_inventories[0]["product"]["id"], "PRD-002")

    def test_validate_inventory(self):
        """Test de validation de stock."""
        # Création d'un stock valide
        inventory_obj = self.inventory_manager.create_inventory(self.inventory_data)
        
        # Validation du stock
        is_valid = self.inventory_manager.validate_inventory(inventory_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_inventory_summary(self):
        """Test de récupération du résumé de stock."""
        # Création du stock
        inventory_obj = self.inventory_manager.create_inventory(self.inventory_data)
        
        # Récupération du résumé
        summary = self.inventory_manager.get_inventory_summary(inventory_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("product" in summary)
        self.assertTrue("stock" in summary)
        self.assertTrue("location" in summary)
        self.assertTrue("pricing" in summary)
        self.assertTrue("supplier" in summary)

    def test_invalid_inventory_type(self):
        """Test avec un type de stock invalide."""
        with self.assertRaises(ValidationError):
            self.inventory_manager.create_inventory({
                **self.inventory_data,
                "type": "invalid_type"
            })

    def test_invalid_inventory_status(self):
        """Test avec un statut de stock invalide."""
        with self.assertRaises(ValidationError):
            self.inventory_manager.create_inventory({
                **self.inventory_data,
                "status": "invalid_status"
            })

    def test_invalid_inventory_dir(self):
        """Test avec un répertoire de stocks invalide."""
        with self.assertRaises(ValidationError):
            InventoryManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 