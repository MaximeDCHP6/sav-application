import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.orders import OrderManager
from alder_sav.utils.exceptions import ValidationError

class TestOrderManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de commandes."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.orders_dir = Path(self.temp_dir) / "orders"
        self.orders_dir.mkdir()
        
        # Initialisation du gestionnaire de commandes
        self.order_manager = OrderManager(self.orders_dir)
        
        # Données de test
        self.order_data = {
            "reference": "ORD-001",
            "type": "standard",
            "status": "pending",
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "email": "jean.dupont@example.com",
                "phone": "+33123456789"
            },
            "items": [
                {
                    "product_id": "PRD-001",
                    "name": "Smartphone XYZ",
                    "quantity": 1,
                    "unit_price": Decimal("999.99"),
                    "tax_rate": Decimal("20.00"),
                    "total": Decimal("1199.99")
                },
                {
                    "product_id": "PRD-002",
                    "name": "Coque de Protection",
                    "quantity": 2,
                    "unit_price": Decimal("19.99"),
                    "tax_rate": Decimal("20.00"),
                    "total": Decimal("47.98")
                }
            ],
            "shipping": {
                "method": "standard",
                "address": {
                    "street": "123 Avenue des Champs-Élysées",
                    "city": "Paris",
                    "postal_code": "75008",
                    "country": "France"
                },
                "cost": Decimal("9.99"),
                "tracking_number": None,
                "estimated_delivery": (datetime.now() + timedelta(days=5)).isoformat()
            },
            "payment": {
                "method": "credit_card",
                "status": "pending",
                "amount": Decimal("1257.96"),
                "currency": "EUR",
                "transaction_id": None,
                "payment_date": None
            },
            "totals": {
                "subtotal": Decimal("1039.97"),
                "tax": Decimal("207.99"),
                "shipping": Decimal("9.99"),
                "total": Decimal("1257.96")
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Commande standard",
                "tags": ["nouvelle", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_order(self):
        """Test de création de commande."""
        # Création de la commande
        order_obj = self.order_manager.create_order(self.order_data)
        
        # Vérification
        self.assertEqual(order_obj["reference"], "ORD-001")
        self.assertEqual(order_obj["type"], "standard")
        self.assertEqual(order_obj["status"], "pending")
        self.assertEqual(len(order_obj["items"]), 2)
        self.assertTrue("id" in order_obj)
        self.assertTrue("creation_date" in order_obj)

    def test_get_order(self):
        """Test de récupération de commande."""
        # Création de la commande
        order_obj = self.order_manager.create_order(self.order_data)
        
        # Récupération de la commande
        retrieved_order = self.order_manager.get_order(order_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_order["reference"], "ORD-001")
        self.assertEqual(retrieved_order["client"]["name"], "Jean Dupont")
        self.assertEqual(retrieved_order["totals"]["total"], Decimal("1257.96"))

    def test_update_order(self):
        """Test de mise à jour de commande."""
        # Création de la commande
        order_obj = self.order_manager.create_order(self.order_data)
        
        # Mise à jour de la commande
        updated_data = {
            "status": "processing",
            "shipping": {
                "tracking_number": "TRK123456789",
                "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat()
            },
            "payment": {
                "status": "completed",
                "transaction_id": "TRX987654321",
                "payment_date": datetime.now().isoformat()
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_order = self.order_manager.update_order(order_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_order["status"], "processing")
        self.assertEqual(updated_order["shipping"]["tracking_number"], "TRK123456789")
        self.assertEqual(updated_order["payment"]["status"], "completed")
        self.assertEqual(updated_order["payment"]["transaction_id"], "TRX987654321")

    def test_delete_order(self):
        """Test de suppression de commande."""
        # Création de la commande
        order_obj = self.order_manager.create_order(self.order_data)
        
        # Suppression de la commande
        self.order_manager.delete_order(order_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.order_manager.get_order(order_obj["id"])

    def test_get_order_by_type(self):
        """Test de récupération des commandes par type."""
        # Création de commandes de différents types
        self.order_manager.create_order({
            **self.order_data,
            "type": "standard"
        })
        self.order_manager.create_order({
            **self.order_data,
            "reference": "ORD-002",
            "type": "express"
        })
        
        # Récupération des commandes par type
        standard_orders = self.order_manager.get_orders_by_type("standard")
        express_orders = self.order_manager.get_orders_by_type("express")
        
        # Vérification
        self.assertEqual(len(standard_orders), 1)
        self.assertEqual(len(express_orders), 1)
        self.assertEqual(standard_orders[0]["type"], "standard")
        self.assertEqual(express_orders[0]["type"], "express")

    def test_get_order_by_status(self):
        """Test de récupération des commandes par statut."""
        # Création de commandes avec différents statuts
        self.order_manager.create_order({
            **self.order_data,
            "status": "pending"
        })
        self.order_manager.create_order({
            **self.order_data,
            "reference": "ORD-002",
            "status": "processing"
        })
        
        # Récupération des commandes par statut
        pending_orders = self.order_manager.get_orders_by_status("pending")
        processing_orders = self.order_manager.get_orders_by_status("processing")
        
        # Vérification
        self.assertEqual(len(pending_orders), 1)
        self.assertEqual(len(processing_orders), 1)
        self.assertEqual(pending_orders[0]["status"], "pending")
        self.assertEqual(processing_orders[0]["status"], "processing")

    def test_get_order_by_client(self):
        """Test de récupération des commandes par client."""
        # Création de commandes pour différents clients
        self.order_manager.create_order({
            **self.order_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.order_manager.create_order({
            **self.order_data,
            "reference": "ORD-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des commandes par client
        client1_orders = self.order_manager.get_orders_by_client("CLI-001")
        client2_orders = self.order_manager.get_orders_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_orders), 1)
        self.assertEqual(len(client2_orders), 1)
        self.assertEqual(client1_orders[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_orders[0]["client"]["id"], "CLI-002")

    def test_validate_order(self):
        """Test de validation de commande."""
        # Création d'une commande valide
        order_obj = self.order_manager.create_order(self.order_data)
        
        # Validation de la commande
        is_valid = self.order_manager.validate_order(order_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_order_summary(self):
        """Test de récupération du résumé de commande."""
        # Création de la commande
        order_obj = self.order_manager.create_order(self.order_data)
        
        # Récupération du résumé
        summary = self.order_manager.get_order_summary(order_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("items" in summary)
        self.assertTrue("totals" in summary)

    def test_invalid_order_type(self):
        """Test avec un type de commande invalide."""
        with self.assertRaises(ValidationError):
            self.order_manager.create_order({
                **self.order_data,
                "type": "invalid_type"
            })

    def test_invalid_order_status(self):
        """Test avec un statut de commande invalide."""
        with self.assertRaises(ValidationError):
            self.order_manager.create_order({
                **self.order_data,
                "status": "invalid_status"
            })

    def test_invalid_order_dir(self):
        """Test avec un répertoire de commandes invalide."""
        with self.assertRaises(ValidationError):
            OrderManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 