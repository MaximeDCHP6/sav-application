import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.suppliers import SupplierManager
from alder_sav.utils.exceptions import ValidationError

class TestSupplierManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de fournisseurs."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.suppliers_dir = Path(self.temp_dir) / "suppliers"
        self.suppliers_dir.mkdir()
        
        # Initialisation du gestionnaire de fournisseurs
        self.supplier_manager = SupplierManager(self.suppliers_dir)
        
        # Données de test
        self.supplier_data = {
            "reference": "SUP-001",
            "type": "manufacturer",
            "status": "active",
            "name": "TechSupplier",
            "legal_name": "TechSupplier SAS",
            "siret": "12345678901234",
            "vat_number": "FR12345678901",
            "contact": {
                "name": "Jean Martin",
                "position": "Responsable Commercial",
                "email": "jean.martin@techsupplier.com",
                "phone": "+33123456789",
                "mobile": "+33612345678"
            },
            "address": {
                "street": "123 Rue de la Tech",
                "city": "Paris",
                "postal_code": "75001",
                "country": "France"
            },
            "banking": {
                "iban": "FR7630006000011234567890189",
                "bic": "BNPAFRPP",
                "bank_name": "BNP Paribas",
                "account_holder": "TechSupplier SAS"
            },
            "products": [
                {
                    "id": "PRD-001",
                    "name": "Smartphone XYZ",
                    "sku": "SP-XYZ-001",
                    "category": "electronics",
                    "brand": "TechBrand",
                    "model": "XYZ-2023"
                }
            ],
            "pricing": {
                "currency": "EUR",
                "payment_terms": 30,
                "minimum_order": Decimal("1000.00"),
                "discounts": [
                    {
                        "threshold": Decimal("5000.00"),
                        "percentage": 5
                    },
                    {
                        "threshold": Decimal("10000.00"),
                        "percentage": 10
                    }
                ]
            },
            "delivery": {
                "lead_time": 7,
                "methods": [
                    {
                        "type": "standard",
                        "carrier": "colissimo",
                        "cost": Decimal("10.00")
                    },
                    {
                        "type": "express",
                        "carrier": "chronopost",
                        "cost": Decimal("20.00")
                    }
                ]
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Fournisseur principal",
                "tags": ["nouveau", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_supplier(self):
        """Test de création de fournisseur."""
        # Création du fournisseur
        supplier_obj = self.supplier_manager.create_supplier(self.supplier_data)
        
        # Vérification
        self.assertEqual(supplier_obj["reference"], "SUP-001")
        self.assertEqual(supplier_obj["type"], "manufacturer")
        self.assertEqual(supplier_obj["status"], "active")
        self.assertEqual(supplier_obj["name"], "TechSupplier")
        self.assertEqual(len(supplier_obj["products"]), 1)
        self.assertTrue("id" in supplier_obj)
        self.assertTrue("creation_date" in supplier_obj)

    def test_get_supplier(self):
        """Test de récupération de fournisseur."""
        # Création du fournisseur
        supplier_obj = self.supplier_manager.create_supplier(self.supplier_data)
        
        # Récupération du fournisseur
        retrieved_supplier = self.supplier_manager.get_supplier(supplier_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_supplier["reference"], "SUP-001")
        self.assertEqual(retrieved_supplier["name"], "TechSupplier")
        self.assertEqual(retrieved_supplier["contact"]["name"], "Jean Martin")
        self.assertEqual(retrieved_supplier["pricing"]["currency"], "EUR")

    def test_update_supplier(self):
        """Test de mise à jour de fournisseur."""
        # Création du fournisseur
        supplier_obj = self.supplier_manager.create_supplier(self.supplier_data)
        
        # Mise à jour du fournisseur
        updated_data = {
            "status": "inactive",
            "contact": {
                "name": "Marie Dupont",
                "position": "Directrice Commerciale",
                "email": "marie.dupont@techsupplier.com",
                "phone": "+33123456789",
                "mobile": "+33612345678"
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_supplier = self.supplier_manager.update_supplier(supplier_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_supplier["status"], "inactive")
        self.assertEqual(updated_supplier["contact"]["name"], "Marie Dupont")
        self.assertEqual(updated_supplier["contact"]["position"], "Directrice Commerciale")

    def test_delete_supplier(self):
        """Test de suppression de fournisseur."""
        # Création du fournisseur
        supplier_obj = self.supplier_manager.create_supplier(self.supplier_data)
        
        # Suppression du fournisseur
        self.supplier_manager.delete_supplier(supplier_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.supplier_manager.get_supplier(supplier_obj["id"])

    def test_get_supplier_by_type(self):
        """Test de récupération des fournisseurs par type."""
        # Création de fournisseurs de différents types
        self.supplier_manager.create_supplier({
            **self.supplier_data,
            "type": "manufacturer"
        })
        self.supplier_manager.create_supplier({
            **self.supplier_data,
            "reference": "SUP-002",
            "type": "distributor"
        })
        
        # Récupération des fournisseurs par type
        manufacturer_suppliers = self.supplier_manager.get_suppliers_by_type("manufacturer")
        distributor_suppliers = self.supplier_manager.get_suppliers_by_type("distributor")
        
        # Vérification
        self.assertEqual(len(manufacturer_suppliers), 1)
        self.assertEqual(len(distributor_suppliers), 1)
        self.assertEqual(manufacturer_suppliers[0]["type"], "manufacturer")
        self.assertEqual(distributor_suppliers[0]["type"], "distributor")

    def test_get_supplier_by_status(self):
        """Test de récupération des fournisseurs par statut."""
        # Création de fournisseurs avec différents statuts
        self.supplier_manager.create_supplier({
            **self.supplier_data,
            "status": "active"
        })
        self.supplier_manager.create_supplier({
            **self.supplier_data,
            "reference": "SUP-002",
            "status": "inactive"
        })
        
        # Récupération des fournisseurs par statut
        active_suppliers = self.supplier_manager.get_suppliers_by_status("active")
        inactive_suppliers = self.supplier_manager.get_suppliers_by_status("inactive")
        
        # Vérification
        self.assertEqual(len(active_suppliers), 1)
        self.assertEqual(len(inactive_suppliers), 1)
        self.assertEqual(active_suppliers[0]["status"], "active")
        self.assertEqual(inactive_suppliers[0]["status"], "inactive")

    def test_get_supplier_by_product(self):
        """Test de récupération des fournisseurs par produit."""
        # Création de fournisseurs pour différents produits
        self.supplier_manager.create_supplier({
            **self.supplier_data,
            "products": [
                {
                    "id": "PRD-001",
                    "name": "Smartphone XYZ"
                }
            ]
        })
        self.supplier_manager.create_supplier({
            **self.supplier_data,
            "reference": "SUP-002",
            "products": [
                {
                    "id": "PRD-002",
                    "name": "Smartphone ABC"
                }
            ]
        })
        
        # Récupération des fournisseurs par produit
        product1_suppliers = self.supplier_manager.get_suppliers_by_product("PRD-001")
        product2_suppliers = self.supplier_manager.get_suppliers_by_product("PRD-002")
        
        # Vérification
        self.assertEqual(len(product1_suppliers), 1)
        self.assertEqual(len(product2_suppliers), 1)
        self.assertEqual(product1_suppliers[0]["products"][0]["id"], "PRD-001")
        self.assertEqual(product2_suppliers[0]["products"][0]["id"], "PRD-002")

    def test_validate_supplier(self):
        """Test de validation de fournisseur."""
        # Création d'un fournisseur valide
        supplier_obj = self.supplier_manager.create_supplier(self.supplier_data)
        
        # Validation du fournisseur
        is_valid = self.supplier_manager.validate_supplier(supplier_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_supplier_summary(self):
        """Test de récupération du résumé de fournisseur."""
        # Création du fournisseur
        supplier_obj = self.supplier_manager.create_supplier(self.supplier_data)
        
        # Récupération du résumé
        summary = self.supplier_manager.get_supplier_summary(supplier_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("name" in summary)
        self.assertTrue("contact" in summary)
        self.assertTrue("address" in summary)
        self.assertTrue("products" in summary)
        self.assertTrue("pricing" in summary)
        self.assertTrue("delivery" in summary)

    def test_invalid_supplier_type(self):
        """Test avec un type de fournisseur invalide."""
        with self.assertRaises(ValidationError):
            self.supplier_manager.create_supplier({
                **self.supplier_data,
                "type": "invalid_type"
            })

    def test_invalid_supplier_status(self):
        """Test avec un statut de fournisseur invalide."""
        with self.assertRaises(ValidationError):
            self.supplier_manager.create_supplier({
                **self.supplier_data,
                "status": "invalid_status"
            })

    def test_invalid_supplier_dir(self):
        """Test avec un répertoire de fournisseurs invalide."""
        with self.assertRaises(ValidationError):
            SupplierManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 