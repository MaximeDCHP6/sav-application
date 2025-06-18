import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.refunds import RefundManager
from alder_sav.utils.exceptions import ValidationError

class TestRefundManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de remboursements."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.refunds_dir = Path(self.temp_dir) / "refunds"
        self.refunds_dir.mkdir()
        
        # Initialisation du gestionnaire de remboursements
        self.refund_manager = RefundManager(self.refunds_dir)
        
        # Données de test
        self.refund_data = {
            "reference": "REF-001",
            "type": "return",
            "status": "pending",
            "amount": Decimal("999.99"),
            "currency": "EUR",
            "payment": {
                "id": "PAY-001",
                "reference": "PAY-001",
                "date": (datetime.now() - timedelta(days=5)).isoformat(),
                "method": "credit_card",
                "transaction_id": "TRX123456789"
            },
            "order": {
                "id": "ORD-001",
                "reference": "ORD-001",
                "date": (datetime.now() - timedelta(days=10)).isoformat()
            },
            "return": {
                "id": "RET-001",
                "reference": "RET-001",
                "date": (datetime.now() - timedelta(days=3)).isoformat()
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
            "transaction": {
                "id": None,
                "status": "pending",
                "created_at": None,
                "updated_at": None,
                "error": None
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Remboursement pour retour",
                "tags": ["nouveau", "standard"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_refund(self):
        """Test de création de remboursement."""
        # Création du remboursement
        refund_obj = self.refund_manager.create_refund(self.refund_data)
        
        # Vérification
        self.assertEqual(refund_obj["reference"], "REF-001")
        self.assertEqual(refund_obj["type"], "return")
        self.assertEqual(refund_obj["status"], "pending")
        self.assertEqual(refund_obj["amount"], Decimal("999.99"))
        self.assertEqual(refund_obj["currency"], "EUR")
        self.assertEqual(len(refund_obj["items"]), 1)
        self.assertTrue("id" in refund_obj)
        self.assertTrue("creation_date" in refund_obj)

    def test_get_refund(self):
        """Test de récupération de remboursement."""
        # Création du remboursement
        refund_obj = self.refund_manager.create_refund(self.refund_data)
        
        # Récupération du remboursement
        retrieved_refund = self.refund_manager.get_refund(refund_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_refund["reference"], "REF-001")
        self.assertEqual(retrieved_refund["client"]["name"], "Jean Dupont")
        self.assertEqual(retrieved_refund["amount"], Decimal("999.99"))
        self.assertEqual(retrieved_refund["payment"]["transaction_id"], "TRX123456789")

    def test_update_refund(self):
        """Test de mise à jour de remboursement."""
        # Création du remboursement
        refund_obj = self.refund_manager.create_refund(self.refund_data)
        
        # Mise à jour du remboursement
        updated_data = {
            "status": "completed",
            "transaction": {
                "id": "TRX987654321",
                "status": "succeeded",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "error": None
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_refund = self.refund_manager.update_refund(refund_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_refund["status"], "completed")
        self.assertEqual(updated_refund["transaction"]["id"], "TRX987654321")
        self.assertEqual(updated_refund["transaction"]["status"], "succeeded")

    def test_delete_refund(self):
        """Test de suppression de remboursement."""
        # Création du remboursement
        refund_obj = self.refund_manager.create_refund(self.refund_data)
        
        # Suppression du remboursement
        self.refund_manager.delete_refund(refund_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.refund_manager.get_refund(refund_obj["id"])

    def test_get_refund_by_type(self):
        """Test de récupération des remboursements par type."""
        # Création de remboursements de différents types
        self.refund_manager.create_refund({
            **self.refund_data,
            "type": "return"
        })
        self.refund_manager.create_refund({
            **self.refund_data,
            "reference": "REF-002",
            "type": "cancellation"
        })
        
        # Récupération des remboursements par type
        return_refunds = self.refund_manager.get_refunds_by_type("return")
        cancellation_refunds = self.refund_manager.get_refunds_by_type("cancellation")
        
        # Vérification
        self.assertEqual(len(return_refunds), 1)
        self.assertEqual(len(cancellation_refunds), 1)
        self.assertEqual(return_refunds[0]["type"], "return")
        self.assertEqual(cancellation_refunds[0]["type"], "cancellation")

    def test_get_refund_by_status(self):
        """Test de récupération des remboursements par statut."""
        # Création de remboursements avec différents statuts
        self.refund_manager.create_refund({
            **self.refund_data,
            "status": "pending"
        })
        self.refund_manager.create_refund({
            **self.refund_data,
            "reference": "REF-002",
            "status": "completed"
        })
        
        # Récupération des remboursements par statut
        pending_refunds = self.refund_manager.get_refunds_by_status("pending")
        completed_refunds = self.refund_manager.get_refunds_by_status("completed")
        
        # Vérification
        self.assertEqual(len(pending_refunds), 1)
        self.assertEqual(len(completed_refunds), 1)
        self.assertEqual(pending_refunds[0]["status"], "pending")
        self.assertEqual(completed_refunds[0]["status"], "completed")

    def test_get_refund_by_client(self):
        """Test de récupération des remboursements par client."""
        # Création de remboursements pour différents clients
        self.refund_manager.create_refund({
            **self.refund_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.refund_manager.create_refund({
            **self.refund_data,
            "reference": "REF-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des remboursements par client
        client1_refunds = self.refund_manager.get_refunds_by_client("CLI-001")
        client2_refunds = self.refund_manager.get_refunds_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_refunds), 1)
        self.assertEqual(len(client2_refunds), 1)
        self.assertEqual(client1_refunds[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_refunds[0]["client"]["id"], "CLI-002")

    def test_validate_refund(self):
        """Test de validation de remboursement."""
        # Création d'un remboursement valide
        refund_obj = self.refund_manager.create_refund(self.refund_data)
        
        # Validation du remboursement
        is_valid = self.refund_manager.validate_refund(refund_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_refund_summary(self):
        """Test de récupération du résumé de remboursement."""
        # Création du remboursement
        refund_obj = self.refund_manager.create_refund(self.refund_data)
        
        # Récupération du résumé
        summary = self.refund_manager.get_refund_summary(refund_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("amount" in summary)
        self.assertTrue("currency" in summary)
        self.assertTrue("payment" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("items" in summary)
        self.assertTrue("transaction" in summary)

    def test_invalid_refund_type(self):
        """Test avec un type de remboursement invalide."""
        with self.assertRaises(ValidationError):
            self.refund_manager.create_refund({
                **self.refund_data,
                "type": "invalid_type"
            })

    def test_invalid_refund_status(self):
        """Test avec un statut de remboursement invalide."""
        with self.assertRaises(ValidationError):
            self.refund_manager.create_refund({
                **self.refund_data,
                "status": "invalid_status"
            })

    def test_invalid_refund_dir(self):
        """Test avec un répertoire de remboursements invalide."""
        with self.assertRaises(ValidationError):
            RefundManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 