import unittest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.products import ProductManager
from alder_sav.utils.exceptions import ValidationError

class TestProductManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de produits."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.products_dir = Path(self.temp_dir) / "products"
        self.products_dir.mkdir()
        
        # Initialisation du gestionnaire de produits
        self.product_manager = ProductManager(self.products_dir)
        
        # Données de test
        self.product_data = {
            "reference": "PRD-001",
            "type": "physical",
            "status": "active",
            "name": "Smartphone XYZ",
            "description": "Un smartphone haut de gamme avec les dernières fonctionnalités",
            "brand": "TechBrand",
            "category": "electronics",
            "subcategory": "smartphones",
            "sku": "TB-SM-001",
            "barcode": "123456789012",
            "price": {
                "base": Decimal("999.99"),
                "tax_rate": Decimal("20.00"),
                "currency": "EUR"
            },
            "stock": {
                "quantity": 100,
                "min_quantity": 10,
                "max_quantity": 1000,
                "location": "A-01-02"
            },
            "specifications": {
                "color": "Noir",
                "storage": "256GB",
                "ram": "8GB",
                "screen": "6.5 pouces",
                "battery": "4500mAh",
                "processor": "Octa-core 2.5GHz"
            },
            "warranty": {
                "duration": 24,
                "type": "standard",
                "conditions": "Couverture des défauts de fabrication"
            },
            "shipping": {
                "weight": 0.2,
                "dimensions": {
                    "length": 15,
                    "width": 7,
                    "height": 1
                },
                "package_type": "box"
            },
            "images": [
                {
                    "url": "https://example.com/images/smartphone-xyz-1.jpg",
                    "type": "main",
                    "alt": "Smartphone XYZ - Vue principale"
                },
                {
                    "url": "https://example.com/images/smartphone-xyz-2.jpg",
                    "type": "gallery",
                    "alt": "Smartphone XYZ - Vue latérale"
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "tags": ["smartphone", "tech", "nouveau"],
                "rating": 4.5,
                "reviews_count": 0
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_product(self):
        """Test de création de produit."""
        # Création du produit
        product_obj = self.product_manager.create_product(self.product_data)
        
        # Vérification
        self.assertEqual(product_obj["reference"], "PRD-001")
        self.assertEqual(product_obj["type"], "physical")
        self.assertEqual(product_obj["status"], "active")
        self.assertEqual(product_obj["name"], "Smartphone XYZ")
        self.assertTrue("id" in product_obj)
        self.assertTrue("creation_date" in product_obj)

    def test_get_product(self):
        """Test de récupération de produit."""
        # Création du produit
        product_obj = self.product_manager.create_product(self.product_data)
        
        # Récupération du produit
        retrieved_product = self.product_manager.get_product(product_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_product["reference"], "PRD-001")
        self.assertEqual(retrieved_product["brand"], "TechBrand")
        self.assertEqual(retrieved_product["price"]["base"], Decimal("999.99"))

    def test_update_product(self):
        """Test de mise à jour de produit."""
        # Création du produit
        product_obj = self.product_manager.create_product(self.product_data)
        
        # Mise à jour du produit
        updated_data = {
            "price": {
                "base": Decimal("899.99")
            },
            "stock": {
                "quantity": 150
            },
            "specifications": {
                "color": "Bleu"
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_product = self.product_manager.update_product(product_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_product["price"]["base"], Decimal("899.99"))
        self.assertEqual(updated_product["stock"]["quantity"], 150)
        self.assertEqual(updated_product["specifications"]["color"], "Bleu")

    def test_delete_product(self):
        """Test de suppression de produit."""
        # Création du produit
        product_obj = self.product_manager.create_product(self.product_data)
        
        # Suppression du produit
        self.product_manager.delete_product(product_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.product_manager.get_product(product_obj["id"])

    def test_get_product_by_type(self):
        """Test de récupération des produits par type."""
        # Création de produits de différents types
        self.product_manager.create_product({
            **self.product_data,
            "type": "physical"
        })
        self.product_manager.create_product({
            **self.product_data,
            "reference": "PRD-002",
            "name": "Service Premium",
            "type": "service"
        })
        
        # Récupération des produits par type
        physical_products = self.product_manager.get_products_by_type("physical")
        service_products = self.product_manager.get_products_by_type("service")
        
        # Vérification
        self.assertEqual(len(physical_products), 1)
        self.assertEqual(len(service_products), 1)
        self.assertEqual(physical_products[0]["type"], "physical")
        self.assertEqual(service_products[0]["type"], "service")

    def test_get_product_by_status(self):
        """Test de récupération des produits par statut."""
        # Création de produits avec différents statuts
        self.product_manager.create_product({
            **self.product_data,
            "status": "active"
        })
        self.product_manager.create_product({
            **self.product_data,
            "reference": "PRD-002",
            "name": "Produit Inactif",
            "status": "inactive"
        })
        
        # Récupération des produits par statut
        active_products = self.product_manager.get_products_by_status("active")
        inactive_products = self.product_manager.get_products_by_status("inactive")
        
        # Vérification
        self.assertEqual(len(active_products), 1)
        self.assertEqual(len(inactive_products), 1)
        self.assertEqual(active_products[0]["status"], "active")
        self.assertEqual(inactive_products[0]["status"], "inactive")

    def test_get_product_by_category(self):
        """Test de récupération des produits par catégorie."""
        # Création de produits de différentes catégories
        self.product_manager.create_product({
            **self.product_data,
            "category": "electronics"
        })
        self.product_manager.create_product({
            **self.product_data,
            "reference": "PRD-002",
            "name": "T-shirt Premium",
            "category": "clothing"
        })
        
        # Récupération des produits par catégorie
        electronics_products = self.product_manager.get_products_by_category("electronics")
        clothing_products = self.product_manager.get_products_by_category("clothing")
        
        # Vérification
        self.assertEqual(len(electronics_products), 1)
        self.assertEqual(len(clothing_products), 1)
        self.assertEqual(electronics_products[0]["category"], "electronics")
        self.assertEqual(clothing_products[0]["category"], "clothing")

    def test_validate_product(self):
        """Test de validation de produit."""
        # Création d'un produit valide
        product_obj = self.product_manager.create_product(self.product_data)
        
        # Validation du produit
        is_valid = self.product_manager.validate_product(product_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_product_summary(self):
        """Test de récupération du résumé de produit."""
        # Création du produit
        product_obj = self.product_manager.create_product(self.product_data)
        
        # Récupération du résumé
        summary = self.product_manager.get_product_summary(product_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("name" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("price" in summary)
        self.assertTrue("stock" in summary)

    def test_invalid_product_type(self):
        """Test avec un type de produit invalide."""
        with self.assertRaises(ValidationError):
            self.product_manager.create_product({
                **self.product_data,
                "type": "invalid_type"
            })

    def test_invalid_product_status(self):
        """Test avec un statut de produit invalide."""
        with self.assertRaises(ValidationError):
            self.product_manager.create_product({
                **self.product_data,
                "status": "invalid_status"
            })

    def test_invalid_product_dir(self):
        """Test avec un répertoire de produits invalide."""
        with self.assertRaises(ValidationError):
            ProductManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 