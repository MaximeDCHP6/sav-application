import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.frp import FRPManager
from alder_sav.utils.exceptions import ValidationError

class TestFRPManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de FRP."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.frp_dir = Path(self.temp_dir) / "frp"
        self.frp_dir.mkdir()
        
        # Initialisation du gestionnaire de FRP
        self.frp_manager = FRPManager(self.frp_dir)
        
        # Données de test
        self.client_data = {
            "id": "CLI-001",
            "name": "Test Client",
            "type": "particulier",
            "email": "test@example.com",
            "phone": "0123456789"
        }
        
        self.frp_data = {
            "client": self.client_data,
            "type": "retour",
            "status": "en_cours",
            "products": [
                {
                    "name": "Product 1",
                    "reference": "REF-001",
                    "quantity": 1,
                    "unit_price": Decimal("100.00"),
                    "total_price": Decimal("100.00")
                },
                {
                    "name": "Product 2",
                    "reference": "REF-002",
                    "quantity": 2,
                    "unit_price": Decimal("50.00"),
                    "total_price": Decimal("100.00")
                }
            ],
            "documents": [
                {
                    "name": "Document 1",
                    "type": "facture",
                    "path": "/path/to/doc1.pdf"
                },
                {
                    "name": "Document 2",
                    "type": "bon_livraison",
                    "path": "/path/to/doc2.pdf"
                }
            ]
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_frp(self):
        """Test de création d'une FRP."""
        # Création de la FRP
        frp = self.frp_manager.create_frp(self.frp_data)
        
        # Vérification
        self.assertEqual(frp["client"]["name"], "Test Client")
        self.assertEqual(frp["type"], "retour")
        self.assertEqual(frp["status"], "en_cours")
        self.assertEqual(len(frp["products"]), 2)
        self.assertEqual(len(frp["documents"]), 2)
        self.assertTrue("id" in frp)
        self.assertTrue("creation_date" in frp)
        self.assertTrue("number" in frp)

    def test_get_frp(self):
        """Test de récupération d'une FRP."""
        # Création de la FRP
        frp = self.frp_manager.create_frp(self.frp_data)
        
        # Récupération de la FRP
        retrieved_frp = self.frp_manager.get_frp(frp["id"])
        
        # Vérification
        self.assertEqual(retrieved_frp["client"]["name"], "Test Client")
        self.assertEqual(retrieved_frp["type"], "retour")
        self.assertEqual(retrieved_frp["status"], "en_cours")

    def test_update_frp(self):
        """Test de mise à jour d'une FRP."""
        # Création de la FRP
        frp = self.frp_manager.create_frp(self.frp_data)
        
        # Mise à jour de la FRP
        updated_data = {
            "status": "termine",
            "products": [
                {
                    "name": "Product 1",
                    "reference": "REF-001",
                    "quantity": 2,
                    "unit_price": Decimal("100.00"),
                    "total_price": Decimal("200.00")
                }
            ]
        }
        updated_frp = self.frp_manager.update_frp(frp["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_frp["status"], "termine")
        self.assertEqual(len(updated_frp["products"]), 1)
        self.assertEqual(updated_frp["products"][0]["quantity"], 2)
        self.assertEqual(updated_frp["products"][0]["total_price"], Decimal("200.00"))

    def test_delete_frp(self):
        """Test de suppression d'une FRP."""
        # Création de la FRP
        frp = self.frp_manager.create_frp(self.frp_data)
        
        # Suppression de la FRP
        self.frp_manager.delete_frp(frp["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.frp_manager.get_frp(frp["id"])

    def test_get_frp_by_status(self):
        """Test de récupération des FRP par statut."""
        # Création de FRP avec différents statuts
        frp1 = self.frp_manager.create_frp(self.frp_data)
        frp2 = self.frp_manager.create_frp({
            **self.frp_data,
            "status": "termine"
        })
        
        # Récupération des FRP par statut
        en_cours = self.frp_manager.get_frp_by_status("en_cours")
        terminees = self.frp_manager.get_frp_by_status("termine")
        
        # Vérification
        self.assertEqual(len(en_cours), 1)
        self.assertEqual(len(terminees), 1)
        self.assertEqual(en_cours[0]["status"], "en_cours")
        self.assertEqual(terminees[0]["status"], "termine")

    def test_get_frp_by_type(self):
        """Test de récupération des FRP par type."""
        # Création de FRP de différents types
        self.frp_manager.create_frp({
            **self.frp_data,
            "type": "retour"
        })
        self.frp_manager.create_frp({
            **self.frp_data,
            "type": "echange"
        })
        self.frp_manager.create_frp({
            **self.frp_data,
            "type": "retour"
        })
        
        # Récupération des FRP par type
        retours = self.frp_manager.get_frp_by_type("retour")
        echanges = self.frp_manager.get_frp_by_type("echange")
        
        # Vérification
        self.assertEqual(len(retours), 2)
        self.assertEqual(len(echanges), 1)
        self.assertEqual(retours[0]["type"], "retour")
        self.assertEqual(echanges[0]["type"], "echange")

    def test_get_frp_by_client(self):
        """Test de récupération des FRP par client."""
        # Création de FRP pour différents clients
        client2 = {
            **self.client_data,
            "id": "CLI-002",
            "name": "Client 2"
        }
        self.frp_manager.create_frp(self.frp_data)
        self.frp_manager.create_frp({
            **self.frp_data,
            "client": client2
        })
        self.frp_manager.create_frp(self.frp_data)
        
        # Récupération des FRP par client
        client1_frp = self.frp_manager.get_frp_by_client("CLI-001")
        client2_frp = self.frp_manager.get_frp_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_frp), 2)
        self.assertEqual(len(client2_frp), 1)
        self.assertEqual(client1_frp[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_frp[0]["client"]["id"], "CLI-002")

    def test_get_frp_by_date_range(self):
        """Test de récupération des FRP par plage de dates."""
        # Création de FRP sur plusieurs jours
        frp_list = []
        for i in range(3):
            frp = self.frp_manager.create_frp(self.frp_data)
            frp["creation_date"] = (datetime.now() - timedelta(days=i)).isoformat()
            frp_list.append(frp)
        
        # Récupération des FRP par plage de dates
        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        date_range_frp = self.frp_manager.get_frp_by_date_range(
            start_date,
            end_date
        )
        
        # Vérification
        self.assertEqual(len(date_range_frp), 2)
        self.assertEqual(date_range_frp[0]["id"], frp_list[0]["id"])
        self.assertEqual(date_range_frp[1]["id"], frp_list[1]["id"])

    def test_validate_frp(self):
        """Test de validation d'une FRP."""
        # Création d'une FRP valide
        frp = self.frp_manager.create_frp(self.frp_data)
        
        # Validation de la FRP
        is_valid = self.frp_manager.validate_frp(frp["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_frp_stats(self):
        """Test de récupération des statistiques d'une FRP."""
        # Création de la FRP
        frp = self.frp_manager.create_frp(self.frp_data)
        
        # Récupération des statistiques
        stats = self.frp_manager.get_frp_stats(frp["id"])
        
        # Vérification
        self.assertTrue("total_products" in stats)
        self.assertTrue("total_value" in stats)
        self.assertTrue("documents_count" in stats)
        self.assertTrue("creation_date" in stats)

    def test_invalid_frp_type(self):
        """Test avec un type de FRP invalide."""
        with self.assertRaises(ValidationError):
            self.frp_manager.create_frp({
                **self.frp_data,
                "type": "invalid_type"
            })

    def test_invalid_frp_status(self):
        """Test avec un statut de FRP invalide."""
        with self.assertRaises(ValidationError):
            self.frp_manager.create_frp({
                **self.frp_data,
                "status": "invalid_status"
            })

    def test_invalid_frp_dir(self):
        """Test avec un répertoire de FRP invalide."""
        with self.assertRaises(ValidationError):
            FRPManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 