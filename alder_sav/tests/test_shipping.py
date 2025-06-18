import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.shipping import ShippingManager
from alder_sav.utils.exceptions import ValidationError

class TestShippingManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de livraisons."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.shipping_dir = Path(self.temp_dir) / "shipping"
        self.shipping_dir.mkdir()
        
        # Initialisation du gestionnaire de livraisons
        self.shipping_manager = ShippingManager(self.shipping_dir)
        
        # Données de test
        self.shipping_data = {
            "reference": "SHP-001",
            "type": "delivery",
            "status": "pending",
            "order": {
                "id": "ORD-001",
                "reference": "ORD-001",
                "date": (datetime.now() - timedelta(days=1)).isoformat()
            },
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "email": "jean.dupont@example.com",
                "phone": "+33123456789"
            },
            "address": {
                "street": "123 Avenue des Champs-Élysées",
                "city": "Paris",
                "postal_code": "75008",
                "country": "France"
            },
            "method": {
                "type": "standard",
                "carrier": "colissimo",
                "service": "home_delivery",
                "tracking_number": None,
                "label_url": None,
                "estimated_delivery": None
            },
            "items": [
                {
                    "product_id": "PRD-001",
                    "name": "Smartphone XYZ",
                    "quantity": 1,
                    "weight": 0.5,
                    "dimensions": {
                        "length": 15,
                        "width": 8,
                        "height": 1,
                        "unit": "cm"
                    }
                }
            ],
            "costs": {
                "shipping": Decimal("5.99"),
                "insurance": Decimal("2.99"),
                "total": Decimal("8.98"),
                "currency": "EUR"
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Livraison standard",
                "tags": ["nouveau", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_shipping(self):
        """Test de création de livraison."""
        # Création de la livraison
        shipping_obj = self.shipping_manager.create_shipping(self.shipping_data)
        
        # Vérification
        self.assertEqual(shipping_obj["reference"], "SHP-001")
        self.assertEqual(shipping_obj["type"], "delivery")
        self.assertEqual(shipping_obj["status"], "pending")
        self.assertEqual(len(shipping_obj["items"]), 1)
        self.assertEqual(shipping_obj["costs"]["total"], Decimal("8.98"))
        self.assertTrue("id" in shipping_obj)
        self.assertTrue("creation_date" in shipping_obj)

    def test_get_shipping(self):
        """Test de récupération de livraison."""
        # Création de la livraison
        shipping_obj = self.shipping_manager.create_shipping(self.shipping_data)
        
        # Récupération de la livraison
        retrieved_shipping = self.shipping_manager.get_shipping(shipping_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_shipping["reference"], "SHP-001")
        self.assertEqual(retrieved_shipping["client"]["name"], "Jean Dupont")
        self.assertEqual(retrieved_shipping["method"]["type"], "standard")
        self.assertEqual(retrieved_shipping["costs"]["total"], Decimal("8.98"))

    def test_update_shipping(self):
        """Test de mise à jour de livraison."""
        # Création de la livraison
        shipping_obj = self.shipping_manager.create_shipping(self.shipping_data)
        
        # Mise à jour de la livraison
        updated_data = {
            "status": "in_transit",
            "method": {
                "tracking_number": "TRK123456789",
                "label_url": "https://example.com/labels/shipping-label.pdf",
                "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat()
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_shipping = self.shipping_manager.update_shipping(shipping_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_shipping["status"], "in_transit")
        self.assertEqual(updated_shipping["method"]["tracking_number"], "TRK123456789")
        self.assertEqual(updated_shipping["method"]["label_url"], "https://example.com/labels/shipping-label.pdf")

    def test_delete_shipping(self):
        """Test de suppression de livraison."""
        # Création de la livraison
        shipping_obj = self.shipping_manager.create_shipping(self.shipping_data)
        
        # Suppression de la livraison
        self.shipping_manager.delete_shipping(shipping_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.shipping_manager.get_shipping(shipping_obj["id"])

    def test_get_shipping_by_type(self):
        """Test de récupération des livraisons par type."""
        # Création de livraisons de différents types
        self.shipping_manager.create_shipping({
            **self.shipping_data,
            "type": "delivery"
        })
        self.shipping_manager.create_shipping({
            **self.shipping_data,
            "reference": "SHP-002",
            "type": "return"
        })
        
        # Récupération des livraisons par type
        delivery_shippings = self.shipping_manager.get_shippings_by_type("delivery")
        return_shippings = self.shipping_manager.get_shippings_by_type("return")
        
        # Vérification
        self.assertEqual(len(delivery_shippings), 1)
        self.assertEqual(len(return_shippings), 1)
        self.assertEqual(delivery_shippings[0]["type"], "delivery")
        self.assertEqual(return_shippings[0]["type"], "return")

    def test_get_shipping_by_status(self):
        """Test de récupération des livraisons par statut."""
        # Création de livraisons avec différents statuts
        self.shipping_manager.create_shipping({
            **self.shipping_data,
            "status": "pending"
        })
        self.shipping_manager.create_shipping({
            **self.shipping_data,
            "reference": "SHP-002",
            "status": "in_transit"
        })
        
        # Récupération des livraisons par statut
        pending_shippings = self.shipping_manager.get_shippings_by_status("pending")
        in_transit_shippings = self.shipping_manager.get_shippings_by_status("in_transit")
        
        # Vérification
        self.assertEqual(len(pending_shippings), 1)
        self.assertEqual(len(in_transit_shippings), 1)
        self.assertEqual(pending_shippings[0]["status"], "pending")
        self.assertEqual(in_transit_shippings[0]["status"], "in_transit")

    def test_get_shipping_by_client(self):
        """Test de récupération des livraisons par client."""
        # Création de livraisons pour différents clients
        self.shipping_manager.create_shipping({
            **self.shipping_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.shipping_manager.create_shipping({
            **self.shipping_data,
            "reference": "SHP-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des livraisons par client
        client1_shippings = self.shipping_manager.get_shippings_by_client("CLI-001")
        client2_shippings = self.shipping_manager.get_shippings_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_shippings), 1)
        self.assertEqual(len(client2_shippings), 1)
        self.assertEqual(client1_shippings[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_shippings[0]["client"]["id"], "CLI-002")

    def test_validate_shipping(self):
        """Test de validation de livraison."""
        # Création d'une livraison valide
        shipping_obj = self.shipping_manager.create_shipping(self.shipping_data)
        
        # Validation de la livraison
        is_valid = self.shipping_manager.validate_shipping(shipping_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_shipping_summary(self):
        """Test de récupération du résumé de livraison."""
        # Création de la livraison
        shipping_obj = self.shipping_manager.create_shipping(self.shipping_data)
        
        # Récupération du résumé
        summary = self.shipping_manager.get_shipping_summary(shipping_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("address" in summary)
        self.assertTrue("method" in summary)
        self.assertTrue("items" in summary)
        self.assertTrue("costs" in summary)

    def test_invalid_shipping_type(self):
        """Test avec un type de livraison invalide."""
        with self.assertRaises(ValidationError):
            self.shipping_manager.create_shipping({
                **self.shipping_data,
                "type": "invalid_type"
            })

    def test_invalid_shipping_status(self):
        """Test avec un statut de livraison invalide."""
        with self.assertRaises(ValidationError):
            self.shipping_manager.create_shipping({
                **self.shipping_data,
                "status": "invalid_status"
            })

    def test_invalid_shipping_dir(self):
        """Test avec un répertoire de livraisons invalide."""
        with self.assertRaises(ValidationError):
            ShippingManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 