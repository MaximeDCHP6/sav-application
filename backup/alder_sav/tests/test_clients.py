import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.clients import ClientManager
from alder_sav.utils.exceptions import ValidationError

class TestClientManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de clients."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.clients_dir = Path(self.temp_dir) / "clients"
        self.clients_dir.mkdir()
        
        # Initialisation du gestionnaire de clients
        self.client_manager = ClientManager(self.clients_dir)
        
        # Données de test
        self.client_data = {
            "reference": "CLI-001",
            "type": "individual",
            "status": "active",
            "personal_info": {
                "first_name": "Jean",
                "last_name": "Dupont",
                "email": "jean.dupont@example.com",
                "phone": "+33123456789",
                "mobile": "+33612345678",
                "birth_date": "1980-01-01",
                "gender": "male"
            },
            "address": {
                "street": "123 Rue de la Paix",
                "city": "Paris",
                "postal_code": "75001",
                "country": "France"
            },
            "billing": {
                "payment_method": "credit_card",
                "currency": "EUR",
                "payment_terms": 30,
                "credit_limit": Decimal("1000.00"),
                "tax_exempt": False,
                "tax_id": "FR12345678901"
            },
            "orders": [
                {
                    "id": "ORD-001",
                    "date": datetime.now().isoformat(),
                    "status": "completed",
                    "total": Decimal("599.99")
                }
            ],
            "devices": [
                {
                    "id": "DEV-001",
                    "type": "smartphone",
                    "brand": "Apple",
                    "model": "iPhone 13",
                    "serial_number": "SN123456789",
                    "purchase_date": "2023-01-01",
                    "warranty_end": "2024-01-01"
                }
            ],
            "preferences": {
                "language": "fr",
                "communication": {
                    "email": True,
                    "sms": True,
                    "phone": False
                },
                "notifications": {
                    "order_updates": True,
                    "promotions": False,
                    "newsletter": True
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Client fidèle",
                "tags": ["premium", "tech_savvy"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_client(self):
        """Test de création de client."""
        # Création du client
        client_obj = self.client_manager.create_client(self.client_data)
        
        # Vérification
        self.assertEqual(client_obj["reference"], "CLI-001")
        self.assertEqual(client_obj["type"], "individual")
        self.assertEqual(client_obj["status"], "active")
        self.assertEqual(client_obj["personal_info"]["first_name"], "Jean")
        self.assertEqual(len(client_obj["orders"]), 1)
        self.assertTrue("id" in client_obj)
        self.assertTrue("creation_date" in client_obj)

    def test_get_client(self):
        """Test de récupération de client."""
        # Création du client
        client_obj = self.client_manager.create_client(self.client_data)
        
        # Récupération du client
        retrieved_client = self.client_manager.get_client(client_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_client["reference"], "CLI-001")
        self.assertEqual(retrieved_client["personal_info"]["first_name"], "Jean")
        self.assertEqual(retrieved_client["billing"]["currency"], "EUR")
        self.assertEqual(len(retrieved_client["devices"]), 1)

    def test_update_client(self):
        """Test de mise à jour de client."""
        # Création du client
        client_obj = self.client_manager.create_client(self.client_data)
        
        # Mise à jour du client
        updated_data = {
            "status": "inactive",
            "personal_info": {
                "email": "jean.dupont.new@example.com",
                "phone": "+33987654321"
            },
            "preferences": {
                "notifications": {
                    "promotions": True
                }
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_client = self.client_manager.update_client(client_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_client["status"], "inactive")
        self.assertEqual(updated_client["personal_info"]["email"], "jean.dupont.new@example.com")
        self.assertEqual(updated_client["preferences"]["notifications"]["promotions"], True)

    def test_delete_client(self):
        """Test de suppression de client."""
        # Création du client
        client_obj = self.client_manager.create_client(self.client_data)
        
        # Suppression du client
        self.client_manager.delete_client(client_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.client_manager.get_client(client_obj["id"])

    def test_get_client_by_type(self):
        """Test de récupération des clients par type."""
        # Création de clients de différents types
        self.client_manager.create_client({
            **self.client_data,
            "type": "individual"
        })
        self.client_manager.create_client({
            **self.client_data,
            "reference": "CLI-002",
            "type": "business"
        })
        
        # Récupération des clients par type
        individual_clients = self.client_manager.get_clients_by_type("individual")
        business_clients = self.client_manager.get_clients_by_type("business")
        
        # Vérification
        self.assertEqual(len(individual_clients), 1)
        self.assertEqual(len(business_clients), 1)
        self.assertEqual(individual_clients[0]["type"], "individual")
        self.assertEqual(business_clients[0]["type"], "business")

    def test_get_client_by_status(self):
        """Test de récupération des clients par statut."""
        # Création de clients avec différents statuts
        self.client_manager.create_client({
            **self.client_data,
            "status": "active"
        })
        self.client_manager.create_client({
            **self.client_data,
            "reference": "CLI-002",
            "status": "inactive"
        })
        
        # Récupération des clients par statut
        active_clients = self.client_manager.get_clients_by_status("active")
        inactive_clients = self.client_manager.get_clients_by_status("inactive")
        
        # Vérification
        self.assertEqual(len(active_clients), 1)
        self.assertEqual(len(inactive_clients), 1)
        self.assertEqual(active_clients[0]["status"], "active")
        self.assertEqual(inactive_clients[0]["status"], "inactive")

    def test_get_client_by_device(self):
        """Test de récupération des clients par appareil."""
        # Création de clients avec différents appareils
        self.client_manager.create_client({
            **self.client_data,
            "devices": [
                {
                    "id": "DEV-001",
                    "type": "smartphone",
                    "brand": "Apple"
                }
            ]
        })
        self.client_manager.create_client({
            **self.client_data,
            "reference": "CLI-002",
            "devices": [
                {
                    "id": "DEV-002",
                    "type": "tablet",
                    "brand": "Samsung"
                }
            ]
        })
        
        # Récupération des clients par appareil
        smartphone_clients = self.client_manager.get_clients_by_device("DEV-001")
        tablet_clients = self.client_manager.get_clients_by_device("DEV-002")
        
        # Vérification
        self.assertEqual(len(smartphone_clients), 1)
        self.assertEqual(len(tablet_clients), 1)
        self.assertEqual(smartphone_clients[0]["devices"][0]["id"], "DEV-001")
        self.assertEqual(tablet_clients[0]["devices"][0]["id"], "DEV-002")

    def test_validate_client(self):
        """Test de validation de client."""
        # Création d'un client valide
        client_obj = self.client_manager.create_client(self.client_data)
        
        # Validation du client
        is_valid = self.client_manager.validate_client(client_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_client_summary(self):
        """Test de récupération du résumé de client."""
        # Création du client
        client_obj = self.client_manager.create_client(self.client_data)
        
        # Récupération du résumé
        summary = self.client_manager.get_client_summary(client_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("personal_info" in summary)
        self.assertTrue("address" in summary)
        self.assertTrue("billing" in summary)
        self.assertTrue("orders" in summary)
        self.assertTrue("devices" in summary)
        self.assertTrue("preferences" in summary)

    def test_invalid_client_type(self):
        """Test avec un type de client invalide."""
        with self.assertRaises(ValidationError):
            self.client_manager.create_client({
                **self.client_data,
                "type": "invalid_type"
            })

    def test_invalid_client_status(self):
        """Test avec un statut de client invalide."""
        with self.assertRaises(ValidationError):
            self.client_manager.create_client({
                **self.client_data,
                "status": "invalid_status"
            })

    def test_invalid_client_dir(self):
        """Test avec un répertoire de clients invalide."""
        with self.assertRaises(ValidationError):
            ClientManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 