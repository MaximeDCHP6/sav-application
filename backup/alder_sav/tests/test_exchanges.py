import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.exchanges import ExchangeManager
from alder_sav.utils.exceptions import ValidationError

class TestExchangeManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire d'échanges."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.exchanges_dir = Path(self.temp_dir) / "exchanges"
        self.exchanges_dir.mkdir()
        
        # Initialisation du gestionnaire d'échanges
        self.exchange_manager = ExchangeManager(self.exchanges_dir)
        
        # Données de test
        self.exchange_data = {
            "reference": "EXC-001",
            "type": "standard",
            "status": "pending",
            "order": {
                "id": "ORD-001",
                "reference": "ORD-001",
                "date": (datetime.now() - timedelta(days=10)).isoformat()
            },
            "return": {
                "id": "RET-001",
                "reference": "RET-001",
                "date": (datetime.now() - timedelta(days=5)).isoformat()
            },
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "email": "jean.dupont@example.com",
                "phone": "+33123456789"
            },
            "old_items": [
                {
                    "product_id": "PRD-001",
                    "name": "Smartphone XYZ",
                    "quantity": 1,
                    "unit_price": Decimal("999.99"),
                    "reason": "Produit défectueux",
                    "condition": "used",
                    "notes": "L'écran ne s'allume pas"
                }
            ],
            "new_items": [
                {
                    "product_id": "PRD-002",
                    "name": "Smartphone ABC",
                    "quantity": 1,
                    "unit_price": Decimal("1099.99"),
                    "notes": "Remplacement du produit défectueux"
                }
            ],
            "shipping": {
                "return": {
                    "method": "standard",
                    "address": {
                        "street": "123 Avenue des Champs-Élysées",
                        "city": "Paris",
                        "postal_code": "75008",
                        "country": "France"
                    },
                    "tracking_number": None,
                    "return_label": None,
                    "estimated_arrival": None
                },
                "delivery": {
                    "method": "standard",
                    "address": {
                        "street": "123 Avenue des Champs-Élysées",
                        "city": "Paris",
                        "postal_code": "75008",
                        "country": "France"
                    },
                    "tracking_number": None,
                    "estimated_delivery": None
                }
            },
            "payment": {
                "status": "pending",
                "amount": Decimal("100.00"),
                "method": "credit_card",
                "transaction_id": None,
                "payment_date": None
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Échange standard",
                "tags": ["nouveau", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_exchange(self):
        """Test de création d'échange."""
        # Création de l'échange
        exchange_obj = self.exchange_manager.create_exchange(self.exchange_data)
        
        # Vérification
        self.assertEqual(exchange_obj["reference"], "EXC-001")
        self.assertEqual(exchange_obj["type"], "standard")
        self.assertEqual(exchange_obj["status"], "pending")
        self.assertEqual(len(exchange_obj["old_items"]), 1)
        self.assertEqual(len(exchange_obj["new_items"]), 1)
        self.assertTrue("id" in exchange_obj)
        self.assertTrue("creation_date" in exchange_obj)

    def test_get_exchange(self):
        """Test de récupération d'échange."""
        # Création de l'échange
        exchange_obj = self.exchange_manager.create_exchange(self.exchange_data)
        
        # Récupération de l'échange
        retrieved_exchange = self.exchange_manager.get_exchange(exchange_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_exchange["reference"], "EXC-001")
        self.assertEqual(retrieved_exchange["client"]["name"], "Jean Dupont")
        self.assertEqual(retrieved_exchange["payment"]["amount"], Decimal("100.00"))

    def test_update_exchange(self):
        """Test de mise à jour d'échange."""
        # Création de l'échange
        exchange_obj = self.exchange_manager.create_exchange(self.exchange_data)
        
        # Mise à jour de l'échange
        updated_data = {
            "status": "processing",
            "shipping": {
                "return": {
                    "tracking_number": "TRK123456789",
                    "return_label": "https://example.com/labels/return-label.pdf",
                    "estimated_arrival": (datetime.now() + timedelta(days=3)).isoformat()
                },
                "delivery": {
                    "tracking_number": "TRK987654321",
                    "estimated_delivery": (datetime.now() + timedelta(days=5)).isoformat()
                }
            },
            "payment": {
                "status": "completed",
                "transaction_id": "TRX123456789",
                "payment_date": datetime.now().isoformat()
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_exchange = self.exchange_manager.update_exchange(exchange_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_exchange["status"], "processing")
        self.assertEqual(updated_exchange["shipping"]["return"]["tracking_number"], "TRK123456789")
        self.assertEqual(updated_exchange["shipping"]["delivery"]["tracking_number"], "TRK987654321")
        self.assertEqual(updated_exchange["payment"]["status"], "completed")
        self.assertEqual(updated_exchange["payment"]["transaction_id"], "TRX123456789")

    def test_delete_exchange(self):
        """Test de suppression d'échange."""
        # Création de l'échange
        exchange_obj = self.exchange_manager.create_exchange(self.exchange_data)
        
        # Suppression de l'échange
        self.exchange_manager.delete_exchange(exchange_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.exchange_manager.get_exchange(exchange_obj["id"])

    def test_get_exchange_by_type(self):
        """Test de récupération des échanges par type."""
        # Création d'échanges de différents types
        self.exchange_manager.create_exchange({
            **self.exchange_data,
            "type": "standard"
        })
        self.exchange_manager.create_exchange({
            **self.exchange_data,
            "reference": "EXC-002",
            "type": "express"
        })
        
        # Récupération des échanges par type
        standard_exchanges = self.exchange_manager.get_exchanges_by_type("standard")
        express_exchanges = self.exchange_manager.get_exchanges_by_type("express")
        
        # Vérification
        self.assertEqual(len(standard_exchanges), 1)
        self.assertEqual(len(express_exchanges), 1)
        self.assertEqual(standard_exchanges[0]["type"], "standard")
        self.assertEqual(express_exchanges[0]["type"], "express")

    def test_get_exchange_by_status(self):
        """Test de récupération des échanges par statut."""
        # Création d'échanges avec différents statuts
        self.exchange_manager.create_exchange({
            **self.exchange_data,
            "status": "pending"
        })
        self.exchange_manager.create_exchange({
            **self.exchange_data,
            "reference": "EXC-002",
            "status": "processing"
        })
        
        # Récupération des échanges par statut
        pending_exchanges = self.exchange_manager.get_exchanges_by_status("pending")
        processing_exchanges = self.exchange_manager.get_exchanges_by_status("processing")
        
        # Vérification
        self.assertEqual(len(pending_exchanges), 1)
        self.assertEqual(len(processing_exchanges), 1)
        self.assertEqual(pending_exchanges[0]["status"], "pending")
        self.assertEqual(processing_exchanges[0]["status"], "processing")

    def test_get_exchange_by_client(self):
        """Test de récupération des échanges par client."""
        # Création d'échanges pour différents clients
        self.exchange_manager.create_exchange({
            **self.exchange_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.exchange_manager.create_exchange({
            **self.exchange_data,
            "reference": "EXC-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des échanges par client
        client1_exchanges = self.exchange_manager.get_exchanges_by_client("CLI-001")
        client2_exchanges = self.exchange_manager.get_exchanges_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_exchanges), 1)
        self.assertEqual(len(client2_exchanges), 1)
        self.assertEqual(client1_exchanges[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_exchanges[0]["client"]["id"], "CLI-002")

    def test_validate_exchange(self):
        """Test de validation d'échange."""
        # Création d'un échange valide
        exchange_obj = self.exchange_manager.create_exchange(self.exchange_data)
        
        # Validation de l'échange
        is_valid = self.exchange_manager.validate_exchange(exchange_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_exchange_summary(self):
        """Test de récupération du résumé d'échange."""
        # Création de l'échange
        exchange_obj = self.exchange_manager.create_exchange(self.exchange_data)
        
        # Récupération du résumé
        summary = self.exchange_manager.get_exchange_summary(exchange_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("old_items" in summary)
        self.assertTrue("new_items" in summary)
        self.assertTrue("payment" in summary)

    def test_invalid_exchange_type(self):
        """Test avec un type d'échange invalide."""
        with self.assertRaises(ValidationError):
            self.exchange_manager.create_exchange({
                **self.exchange_data,
                "type": "invalid_type"
            })

    def test_invalid_exchange_status(self):
        """Test avec un statut d'échange invalide."""
        with self.assertRaises(ValidationError):
            self.exchange_manager.create_exchange({
                **self.exchange_data,
                "status": "invalid_status"
            })

    def test_invalid_exchange_dir(self):
        """Test avec un répertoire d'échanges invalide."""
        with self.assertRaises(ValidationError):
            ExchangeManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 