import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.payments import PaymentManager
from alder_sav.utils.exceptions import ValidationError

class TestPaymentManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de paiements."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.payment_dir = Path(self.temp_dir) / "payments"
        self.payment_dir.mkdir()
        
        # Initialisation du gestionnaire de paiements
        self.payment_manager = PaymentManager(self.payment_dir)
        
        # Données de test
        self.payment_data = {
            "reference": "PAY-001",
            "type": "vente",
            "status": "en_attente",
            "order": {
                "id": "CMD-001",
                "reference": "CMD-001",
                "total": Decimal("240.00")
            },
            "client": {
                "id": "CLI-001",
                "name": "Client Test",
                "contact": "contact@client.com"
            },
            "amount": {
                "total": Decimal("240.00"),
                "currency": "EUR",
                "tax_amount": Decimal("40.00"),
                "shipping_amount": Decimal("10.00")
            },
            "method": {
                "type": "carte",
                "details": {
                    "card_type": "visa",
                    "last_four": "1234",
                    "expiry_date": "12/25"
                }
            },
            "schedule": {
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "installments": 1,
                "current_installment": 1
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Paiement test pour les développements"
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_payment(self):
        """Test de création d'un paiement."""
        # Création du paiement
        payment = self.payment_manager.create_payment(self.payment_data)
        
        # Vérification
        self.assertEqual(payment["reference"], "PAY-001")
        self.assertEqual(payment["type"], "vente")
        self.assertEqual(payment["status"], "en_attente")
        self.assertTrue("id" in payment)
        self.assertTrue("creation_date" in payment)

    def test_get_payment(self):
        """Test de récupération d'un paiement."""
        # Création du paiement
        payment = self.payment_manager.create_payment(self.payment_data)
        
        # Récupération du paiement
        retrieved_payment = self.payment_manager.get_payment(payment["id"])
        
        # Vérification
        self.assertEqual(retrieved_payment["reference"], "PAY-001")
        self.assertEqual(retrieved_payment["type"], "vente")
        self.assertEqual(retrieved_payment["client"]["name"], "Client Test")

    def test_update_payment(self):
        """Test de mise à jour d'un paiement."""
        # Création du paiement
        payment = self.payment_manager.create_payment(self.payment_data)
        
        # Mise à jour du paiement
        updated_data = {
            "status": "paye",
            "method": {
                "type": "carte",
                "details": {
                    "transaction_id": "TRANS-001",
                    "authorization_code": "AUTH-001"
                }
            }
        }
        updated_payment = self.payment_manager.update_payment(payment["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_payment["status"], "paye")
        self.assertEqual(updated_payment["method"]["details"]["transaction_id"], "TRANS-001")

    def test_delete_payment(self):
        """Test de suppression d'un paiement."""
        # Création du paiement
        payment = self.payment_manager.create_payment(self.payment_data)
        
        # Suppression du paiement
        self.payment_manager.delete_payment(payment["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.payment_manager.get_payment(payment["id"])

    def test_get_payment_by_type(self):
        """Test de récupération des paiements par type."""
        # Création de paiements de différents types
        self.payment_manager.create_payment({
            **self.payment_data,
            "type": "vente"
        })
        self.payment_manager.create_payment({
            **self.payment_data,
            "reference": "PAY-002",
            "type": "remboursement"
        })
        
        # Récupération des paiements par type
        vente_payments = self.payment_manager.get_payment_by_type("vente")
        remboursement_payments = self.payment_manager.get_payment_by_type("remboursement")
        
        # Vérification
        self.assertEqual(len(vente_payments), 1)
        self.assertEqual(len(remboursement_payments), 1)
        self.assertEqual(vente_payments[0]["type"], "vente")
        self.assertEqual(remboursement_payments[0]["type"], "remboursement")

    def test_get_payment_by_status(self):
        """Test de récupération des paiements par statut."""
        # Création de paiements avec différents statuts
        self.payment_manager.create_payment({
            **self.payment_data,
            "status": "en_attente"
        })
        self.payment_manager.create_payment({
            **self.payment_data,
            "reference": "PAY-002",
            "status": "paye"
        })
        
        # Récupération des paiements par statut
        en_attente_payments = self.payment_manager.get_payment_by_status("en_attente")
        paye_payments = self.payment_manager.get_payment_by_status("paye")
        
        # Vérification
        self.assertEqual(len(en_attente_payments), 1)
        self.assertEqual(len(paye_payments), 1)
        self.assertEqual(en_attente_payments[0]["status"], "en_attente")
        self.assertEqual(paye_payments[0]["status"], "paye")

    def test_get_payment_by_client(self):
        """Test de récupération des paiements par client."""
        # Création de paiements pour différents clients
        self.payment_manager.create_payment({
            **self.payment_data,
            "client": {
                "id": "CLI-001",
                "name": "Client A"
            }
        })
        self.payment_manager.create_payment({
            **self.payment_data,
            "reference": "PAY-002",
            "client": {
                "id": "CLI-002",
                "name": "Client B"
            }
        })
        
        # Récupération des paiements par client
        client_a_payments = self.payment_manager.get_payment_by_client("CLI-001")
        client_b_payments = self.payment_manager.get_payment_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client_a_payments), 1)
        self.assertEqual(len(client_b_payments), 1)
        self.assertEqual(client_a_payments[0]["client"]["id"], "CLI-001")
        self.assertEqual(client_b_payments[0]["client"]["id"], "CLI-002")

    def test_validate_payment(self):
        """Test de validation d'un paiement."""
        # Création d'un paiement valide
        payment = self.payment_manager.create_payment(self.payment_data)
        
        # Validation du paiement
        is_valid = self.payment_manager.validate_payment(payment["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_payment_summary(self):
        """Test de récupération du résumé d'un paiement."""
        # Création d'un paiement
        payment = self.payment_manager.create_payment(self.payment_data)
        
        # Récupération du résumé
        summary = self.payment_manager.get_payment_summary(payment["id"])
        
        # Vérification
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("order" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("amount" in summary)
        self.assertTrue("method" in summary)
        self.assertTrue("schedule" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_payment_type(self):
        """Test avec un type de paiement invalide."""
        with self.assertRaises(ValidationError):
            self.payment_manager.create_payment({
                **self.payment_data,
                "type": "invalid_type"
            })

    def test_invalid_payment_status(self):
        """Test avec un statut de paiement invalide."""
        with self.assertRaises(ValidationError):
            self.payment_manager.create_payment({
                **self.payment_data,
                "status": "invalid_status"
            })

    def test_invalid_payment_dir(self):
        """Test avec un répertoire de paiements invalide."""
        with self.assertRaises(ValidationError):
            PaymentManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 