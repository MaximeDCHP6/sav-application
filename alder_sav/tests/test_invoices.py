import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.invoices import InvoiceManager
from alder_sav.utils.exceptions import ValidationError

class TestInvoiceManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de factures."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.invoice_dir = Path(self.temp_dir) / "invoices"
        self.invoice_dir.mkdir()
        
        # Initialisation du gestionnaire de factures
        self.invoice_manager = InvoiceManager(self.invoice_dir)
        
        # Données de test
        self.invoice_data = {
            "number": "FAC-2024-001",
            "type": "vente",
            "status": "en_attente",
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "email": "jean.dupont@example.com",
                "address": {
                    "street": "123 rue de la Paix",
                    "city": "Paris",
                    "postal_code": "75001",
                    "country": "France"
                }
            },
            "items": [
                {
                    "product": {
                        "id": "PROD-001",
                        "name": "Ordinateur portable",
                        "reference": "LAP-001"
                    },
                    "quantity": 1,
                    "unit_price": Decimal("999.99"),
                    "vat_rate": Decimal("20.00"),
                    "discount": Decimal("0.00")
                }
            ],
            "payment": {
                "method": "carte",
                "status": "en_attente",
                "due_date": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "shipping": {
                "method": "standard",
                "cost": Decimal("9.99"),
                "tracking_number": "TRK-001"
            },
            "totals": {
                "subtotal": Decimal("999.99"),
                "vat": Decimal("200.00"),
                "shipping": Decimal("9.99"),
                "discount": Decimal("0.00"),
                "total": Decimal("1209.98")
            },
            "notes": "Facture pour la vente d'un ordinateur portable"
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_invoice(self):
        """Test de création d'une facture."""
        # Création de la facture
        invoice = self.invoice_manager.create_invoice(self.invoice_data)
        
        # Vérification
        self.assertEqual(invoice["number"], "FAC-2024-001")
        self.assertEqual(invoice["type"], "vente")
        self.assertEqual(invoice["status"], "en_attente")
        self.assertEqual(invoice["client"]["name"], "Jean Dupont")
        self.assertEqual(len(invoice["items"]), 1)
        self.assertEqual(invoice["totals"]["total"], Decimal("1209.98"))
        self.assertTrue("id" in invoice)
        self.assertTrue("creation_date" in invoice)

    def test_get_invoice(self):
        """Test de récupération d'une facture."""
        # Création de la facture
        invoice = self.invoice_manager.create_invoice(self.invoice_data)
        
        # Récupération de la facture
        retrieved_invoice = self.invoice_manager.get_invoice(invoice["id"])
        
        # Vérification
        self.assertEqual(retrieved_invoice["number"], "FAC-2024-001")
        self.assertEqual(retrieved_invoice["type"], "vente")
        self.assertEqual(retrieved_invoice["client"]["name"], "Jean Dupont")

    def test_update_invoice(self):
        """Test de mise à jour d'une facture."""
        # Création de la facture
        invoice = self.invoice_manager.create_invoice(self.invoice_data)
        
        # Mise à jour de la facture
        updated_data = {
            "status": "payee",
            "payment": {
                "status": "complete",
                "payment_date": datetime.now().isoformat()
            }
        }
        updated_invoice = self.invoice_manager.update_invoice(invoice["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_invoice["status"], "payee")
        self.assertEqual(updated_invoice["payment"]["status"], "complete")
        self.assertTrue("payment_date" in updated_invoice["payment"])

    def test_delete_invoice(self):
        """Test de suppression d'une facture."""
        # Création de la facture
        invoice = self.invoice_manager.create_invoice(self.invoice_data)
        
        # Suppression de la facture
        self.invoice_manager.delete_invoice(invoice["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.invoice_manager.get_invoice(invoice["id"])

    def test_get_invoice_by_status(self):
        """Test de récupération des factures par statut."""
        # Création de factures avec différents statuts
        self.invoice_manager.create_invoice(self.invoice_data)
        self.invoice_manager.create_invoice({
            **self.invoice_data,
            "number": "FAC-2024-002",
            "status": "payee"
        })
        
        # Récupération des factures par statut
        en_attente = self.invoice_manager.get_invoice_by_status("en_attente")
        payees = self.invoice_manager.get_invoice_by_status("payee")
        
        # Vérification
        self.assertEqual(len(en_attente), 1)
        self.assertEqual(len(payees), 1)
        self.assertEqual(en_attente[0]["status"], "en_attente")
        self.assertEqual(payees[0]["status"], "payee")

    def test_get_invoice_by_type(self):
        """Test de récupération des factures par type."""
        # Création de factures de différents types
        self.invoice_manager.create_invoice({
            **self.invoice_data,
            "type": "vente"
        })
        self.invoice_manager.create_invoice({
            **self.invoice_data,
            "number": "FAC-2024-002",
            "type": "achat"
        })
        
        # Récupération des factures par type
        ventes = self.invoice_manager.get_invoice_by_type("vente")
        achats = self.invoice_manager.get_invoice_by_type("achat")
        
        # Vérification
        self.assertEqual(len(ventes), 1)
        self.assertEqual(len(achats), 1)
        self.assertEqual(ventes[0]["type"], "vente")
        self.assertEqual(achats[0]["type"], "achat")

    def test_get_invoice_by_client(self):
        """Test de récupération des factures par client."""
        # Création de factures pour différents clients
        self.invoice_manager.create_invoice(self.invoice_data)
        self.invoice_manager.create_invoice({
            **self.invoice_data,
            "number": "FAC-2024-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin",
                "email": "marie.martin@example.com",
                "address": {
                    "street": "456 avenue des Champs-Élysées",
                    "city": "Paris",
                    "postal_code": "75008",
                    "country": "France"
                }
            }
        })
        
        # Récupération des factures par client
        jean_invoices = self.invoice_manager.get_invoice_by_client("CLI-001")
        marie_invoices = self.invoice_manager.get_invoice_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(jean_invoices), 1)
        self.assertEqual(len(marie_invoices), 1)
        self.assertEqual(jean_invoices[0]["client"]["name"], "Jean Dupont")
        self.assertEqual(marie_invoices[0]["client"]["name"], "Marie Martin")

    def test_get_invoice_by_date_range(self):
        """Test de récupération des factures par plage de dates."""
        # Création de factures à différentes dates
        self.invoice_manager.create_invoice(self.invoice_data)
        self.invoice_manager.create_invoice({
            **self.invoice_data,
            "number": "FAC-2024-002",
            "creation_date": (datetime.now() + timedelta(days=1)).isoformat()
        })
        
        # Récupération des factures par plage de dates
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        today_invoices = self.invoice_manager.get_invoice_by_date_range(today, today)
        tomorrow_invoices = self.invoice_manager.get_invoice_by_date_range(tomorrow, tomorrow)
        
        # Vérification
        self.assertEqual(len(today_invoices), 1)
        self.assertEqual(len(tomorrow_invoices), 1)
        self.assertEqual(today_invoices[0]["number"], "FAC-2024-001")
        self.assertEqual(tomorrow_invoices[0]["number"], "FAC-2024-002")

    def test_validate_invoice(self):
        """Test de validation d'une facture."""
        # Création d'une facture valide
        invoice = self.invoice_manager.create_invoice(self.invoice_data)
        
        # Validation de la facture
        is_valid = self.invoice_manager.validate_invoice(invoice["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_invoice_stats(self):
        """Test de récupération des statistiques d'une facture."""
        # Création de la facture
        invoice = self.invoice_manager.create_invoice(self.invoice_data)
        
        # Récupération des statistiques
        stats = self.invoice_manager.get_invoice_stats(invoice["id"])
        
        # Vérification
        self.assertTrue("type" in stats)
        self.assertTrue("status" in stats)
        self.assertTrue("totals" in stats)
        self.assertTrue("payment" in stats)
        self.assertTrue("shipping" in stats)

    def test_invalid_invoice_type(self):
        """Test avec un type de facture invalide."""
        with self.assertRaises(ValidationError):
            self.invoice_manager.create_invoice({
                **self.invoice_data,
                "type": "invalid_type"
            })

    def test_invalid_invoice_status(self):
        """Test avec un statut de facture invalide."""
        with self.assertRaises(ValidationError):
            self.invoice_manager.create_invoice({
                **self.invoice_data,
                "status": "invalid_status"
            })

    def test_invalid_invoice_dir(self):
        """Test avec un répertoire de factures invalide."""
        with self.assertRaises(ValidationError):
            InvoiceManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 