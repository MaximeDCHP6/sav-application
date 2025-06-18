import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.returns import ReturnManager
from alder_sav.utils.exceptions import ValidationError

class TestReturnManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de retours."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.returns_dir = Path(self.temp_dir) / "returns"
        self.returns_dir.mkdir()
        
        # Initialisation du gestionnaire de retours
        self.return_manager = ReturnManager(self.returns_dir)
        
        # Données de test
        self.return_data = {
            "reference": "RET-001",
            "type": "standard",
            "status": "pending",
            "order": {
                "id": "ORD-001",
                "reference": "ORD-001",
                "date": (datetime.now() - timedelta(days=10)).isoformat()
            },
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
                    "reason": "Produit défectueux",
                    "condition": "used",
                    "notes": "L'écran ne s'allume pas"
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
                "tracking_number": None,
                "return_label": None,
                "estimated_arrival": None
            },
            "refund": {
                "status": "pending",
                "amount": Decimal("1199.99"),
                "method": "credit_card",
                "transaction_id": None,
                "refund_date": None
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Retour standard",
                "tags": ["nouveau", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_return(self):
        """Test de création de retour."""
        # Création du retour
        return_obj = self.return_manager.create_return(self.return_data)
        
        # Vérification
        self.assertEqual(return_obj["reference"], "RET-001")
        self.assertEqual(return_obj["type"], "standard")
        self.assertEqual(return_obj["status"], "pending")
        self.assertEqual(len(return_obj["items"]), 1)
        self.assertTrue("id" in return_obj)
        self.assertTrue("creation_date" in return_obj)

    def test_get_return(self):
        """Test de récupération de retour."""
        # Création du retour
        return_obj = self.return_manager.create_return(self.return_data)
        
        # Récupération du retour
        retrieved_return = self.return_manager.get_return(return_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_return["reference"], "RET-001")
        self.assertEqual(retrieved_return["client"]["name"], "Jean Dupont")
        self.assertEqual(retrieved_return["refund"]["amount"], Decimal("1199.99"))

    def test_update_return(self):
        """Test de mise à jour de retour."""
        # Création du retour
        return_obj = self.return_manager.create_return(self.return_data)
        
        # Mise à jour du retour
        updated_data = {
            "status": "processing",
            "shipping": {
                "tracking_number": "TRK123456789",
                "return_label": "https://example.com/labels/return-label.pdf",
                "estimated_arrival": (datetime.now() + timedelta(days=3)).isoformat()
            },
            "refund": {
                "status": "completed",
                "transaction_id": "TRX987654321",
                "refund_date": datetime.now().isoformat()
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_return = self.return_manager.update_return(return_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_return["status"], "processing")
        self.assertEqual(updated_return["shipping"]["tracking_number"], "TRK123456789")
        self.assertEqual(updated_return["refund"]["status"], "completed")
        self.assertEqual(updated_return["refund"]["transaction_id"], "TRX987654321")

    def test_delete_return(self):
        """Test de suppression de retour."""
        # Création du retour
        return_obj = self.return_manager.create_return(self.return_data)
        
        # Suppression du retour
        self.return_manager.delete_return(return_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.return_manager.get_return(return_obj["id"])

    def test_get_return_by_type(self):
        """Test de récupération des retours par type."""
        # Création de retours de différents types
        self.return_manager.create_return({
            **self.return_data,
            "type": "standard"
        })
        self.return_manager.create_return({
            **self.return_data,
            "reference": "RET-002",
            "type": "express"
        })
        
        # Récupération des retours par type
        standard_returns = self.return_manager.get_returns_by_type("standard")
        express_returns = self.return_manager.get_returns_by_type("express")
        
        # Vérification
        self.assertEqual(len(standard_returns), 1)
        self.assertEqual(len(express_returns), 1)
        self.assertEqual(standard_returns[0]["type"], "standard")
        self.assertEqual(express_returns[0]["type"], "express")

    def test_get_return_by_status(self):
        """Test de récupération des retours par statut."""
        # Création de retours avec différents statuts
        self.return_manager.create_return({
            **self.return_data,
            "status": "pending"
        })
        self.return_manager.create_return({
            **self.return_data,
            "reference": "RET-002",
            "status": "processing"
        })
        
        # Récupération des retours par statut
        pending_returns = self.return_manager.get_returns_by_status("pending")
        processing_returns = self.return_manager.get_returns_by_status("processing")
        
        # Vérification
        self.assertEqual(len(pending_returns), 1)
        self.assertEqual(len(processing_returns), 1)
        self.assertEqual(pending_returns[0]["status"], "pending")
        self.assertEqual(processing_returns[0]["status"], "processing")

    def test_get_return_by_client(self):
        """Test de récupération des retours par client."""
        # Création de retours pour différents clients
        self.return_manager.create_return({
            **self.return_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.return_manager.create_return({
            **self.return_data,
            "reference": "RET-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des retours par client
        client1_returns = self.return_manager.get_returns_by_client("CLI-001")
        client2_returns = self.return_manager.get_returns_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_returns), 1)
        self.assertEqual(len(client2_returns), 1)
        self.assertEqual(client1_returns[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_returns[0]["client"]["id"], "CLI-002")

    def test_validate_return(self):
        """Test de validation de retour."""
        # Création d'un retour valide
        return_obj = self.return_manager.create_return(self.return_data)
        
        # Validation du retour
        is_valid = self.return_manager.validate_return(return_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_return_summary(self):
        """Test de récupération du résumé de retour."""
        # Création du retour
        return_obj = self.return_manager.create_return(self.return_data)
        
        # Récupération du résumé
        summary = self.return_manager.get_return_summary(return_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("items" in summary)
        self.assertTrue("refund" in summary)

    def test_invalid_return_type(self):
        """Test avec un type de retour invalide."""
        with self.assertRaises(ValidationError):
            self.return_manager.create_return({
                **self.return_data,
                "type": "invalid_type"
            })

    def test_invalid_return_status(self):
        """Test avec un statut de retour invalide."""
        with self.assertRaises(ValidationError):
            self.return_manager.create_return({
                **self.return_data,
                "status": "invalid_status"
            })

    def test_invalid_return_dir(self):
        """Test avec un répertoire de retours invalide."""
        with self.assertRaises(ValidationError):
            ReturnManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 