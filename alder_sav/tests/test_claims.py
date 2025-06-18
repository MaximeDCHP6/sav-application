import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.claims import ClaimManager
from alder_sav.utils.exceptions import ValidationError

class TestClaimManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de réclamations."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.claims_dir = Path(self.temp_dir) / "claims"
        self.claims_dir.mkdir()
        
        # Initialisation du gestionnaire de réclamations
        self.claim_manager = ClaimManager(self.claims_dir)
        
        # Données de test
        self.claim_data = {
            "reference": "CLA-001",
            "type": "warranty",
            "status": "pending",
            "device": {
                "id": "DEV-001",
                "type": "smartphone",
                "brand": "Apple",
                "model": "iPhone 13",
                "serial_number": "SN123456789"
            },
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "contact": {
                    "email": "jean.dupont@example.com",
                    "phone": "+33123456789"
                }
            },
            "warranty": {
                "id": "WAR-001",
                "type": "manufacturer",
                "status": "active",
                "coverage": {
                    "type": "standard",
                    "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end_date": (datetime.now() + timedelta(days=335)).isoformat()
                }
            },
            "issue": {
                "description": "Écran qui ne répond plus au toucher",
                "symptoms": ["écran noir", "tactile non fonctionnel"],
                "occurrence_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "priority": "high",
                "category": "hardware"
            },
            "diagnosis": {
                "technician": {
                    "id": "TECH-001",
                    "name": "Pierre Martin"
                },
                "date": datetime.now().isoformat(),
                "findings": "Écran LCD endommagé",
                "recommendation": "Remplacement de l'écran",
                "estimated_cost": Decimal("199.99"),
                "estimated_time": 48
            },
            "resolution": {
                "status": "pending",
                "action": None,
                "cost": None,
                "completion_date": None,
                "notes": None
            },
            "documents": [
                {
                    "type": "photo",
                    "description": "Photo de l'écran cassé",
                    "url": "https://example.com/photos/ecran-casse.jpg",
                    "upload_date": datetime.now().isoformat()
                }
            ],
            "history": [
                {
                    "date": datetime.now().isoformat(),
                    "status": "pending",
                    "notes": "Réclamation créée"
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Réclamation urgente",
                "tags": ["écran", "hardware", "urgent"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_claim(self):
        """Test de création de réclamation."""
        # Création de la réclamation
        claim_obj = self.claim_manager.create_claim(self.claim_data)
        
        # Vérification
        self.assertEqual(claim_obj["reference"], "CLA-001")
        self.assertEqual(claim_obj["type"], "warranty")
        self.assertEqual(claim_obj["status"], "pending")
        self.assertEqual(claim_obj["device"]["model"], "iPhone 13")
        self.assertEqual(claim_obj["issue"]["priority"], "high")
        self.assertTrue("id" in claim_obj)
        self.assertTrue("creation_date" in claim_obj)

    def test_get_claim(self):
        """Test de récupération de réclamation."""
        # Création de la réclamation
        claim_obj = self.claim_manager.create_claim(self.claim_data)
        
        # Récupération de la réclamation
        retrieved_claim = self.claim_manager.get_claim(claim_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_claim["reference"], "CLA-001")
        self.assertEqual(retrieved_claim["warranty"]["type"], "manufacturer")
        self.assertEqual(retrieved_claim["diagnosis"]["estimated_cost"], Decimal("199.99"))
        self.assertEqual(len(retrieved_claim["documents"]), 1)

    def test_update_claim(self):
        """Test de mise à jour de réclamation."""
        # Création de la réclamation
        claim_obj = self.claim_manager.create_claim(self.claim_data)
        
        # Mise à jour de la réclamation
        updated_data = {
            "status": "in_progress",
            "diagnosis": {
                "findings": "Écran LCD et tactile endommagés",
                "estimated_cost": Decimal("249.99")
            },
            "resolution": {
                "status": "approved",
                "action": "replace_screen",
                "cost": Decimal("249.99"),
                "completion_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "notes": "Remplacement de l'écran approuvé"
            },
            "history": [
                {
                    "date": datetime.now().isoformat(),
                    "status": "in_progress",
                    "notes": "Réparation en cours"
                }
            ],
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_claim = self.claim_manager.update_claim(claim_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_claim["status"], "in_progress")
        self.assertEqual(updated_claim["diagnosis"]["estimated_cost"], Decimal("249.99"))
        self.assertEqual(updated_claim["resolution"]["action"], "replace_screen")
        self.assertTrue(updated_claim["resolution"]["completion_date"] is not None)

    def test_delete_claim(self):
        """Test de suppression de réclamation."""
        # Création de la réclamation
        claim_obj = self.claim_manager.create_claim(self.claim_data)
        
        # Suppression de la réclamation
        self.claim_manager.delete_claim(claim_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.claim_manager.get_claim(claim_obj["id"])

    def test_get_claim_by_type(self):
        """Test de récupération des réclamations par type."""
        # Création de réclamations de différents types
        self.claim_manager.create_claim({
            **self.claim_data,
            "type": "warranty"
        })
        self.claim_manager.create_claim({
            **self.claim_data,
            "reference": "CLA-002",
            "type": "repair"
        })
        
        # Récupération des réclamations par type
        warranty_claims = self.claim_manager.get_claims_by_type("warranty")
        repair_claims = self.claim_manager.get_claims_by_type("repair")
        
        # Vérification
        self.assertEqual(len(warranty_claims), 1)
        self.assertEqual(len(repair_claims), 1)
        self.assertEqual(warranty_claims[0]["type"], "warranty")
        self.assertEqual(repair_claims[0]["type"], "repair")

    def test_get_claim_by_status(self):
        """Test de récupération des réclamations par statut."""
        # Création de réclamations avec différents statuts
        self.claim_manager.create_claim({
            **self.claim_data,
            "status": "pending"
        })
        self.claim_manager.create_claim({
            **self.claim_data,
            "reference": "CLA-002",
            "status": "in_progress"
        })
        
        # Récupération des réclamations par statut
        pending_claims = self.claim_manager.get_claims_by_status("pending")
        in_progress_claims = self.claim_manager.get_claims_by_status("in_progress")
        
        # Vérification
        self.assertEqual(len(pending_claims), 1)
        self.assertEqual(len(in_progress_claims), 1)
        self.assertEqual(pending_claims[0]["status"], "pending")
        self.assertEqual(in_progress_claims[0]["status"], "in_progress")

    def test_get_claim_by_client(self):
        """Test de récupération des réclamations par client."""
        # Création de réclamations pour différents clients
        self.claim_manager.create_claim({
            **self.claim_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.claim_manager.create_claim({
            **self.claim_data,
            "reference": "CLA-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des réclamations par client
        client1_claims = self.claim_manager.get_claims_by_client("CLI-001")
        client2_claims = self.claim_manager.get_claims_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_claims), 1)
        self.assertEqual(len(client2_claims), 1)
        self.assertEqual(client1_claims[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_claims[0]["client"]["id"], "CLI-002")

    def test_validate_claim(self):
        """Test de validation de réclamation."""
        # Création d'une réclamation valide
        claim_obj = self.claim_manager.create_claim(self.claim_data)
        
        # Validation de la réclamation
        is_valid = self.claim_manager.validate_claim(claim_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_claim_summary(self):
        """Test de récupération du résumé de réclamation."""
        # Création de la réclamation
        claim_obj = self.claim_manager.create_claim(self.claim_data)
        
        # Récupération du résumé
        summary = self.claim_manager.get_claim_summary(claim_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("device" in summary)
        self.assertTrue("client" in summary)
        self.assertTrue("warranty" in summary)
        self.assertTrue("issue" in summary)
        self.assertTrue("diagnosis" in summary)
        self.assertTrue("resolution" in summary)
        self.assertTrue("documents" in summary)
        self.assertTrue("history" in summary)

    def test_invalid_claim_type(self):
        """Test avec un type de réclamation invalide."""
        with self.assertRaises(ValidationError):
            self.claim_manager.create_claim({
                **self.claim_data,
                "type": "invalid_type"
            })

    def test_invalid_claim_status(self):
        """Test avec un statut de réclamation invalide."""
        with self.assertRaises(ValidationError):
            self.claim_manager.create_claim({
                **self.claim_data,
                "status": "invalid_status"
            })

    def test_invalid_claim_dir(self):
        """Test avec un répertoire de réclamations invalide."""
        with self.assertRaises(ValidationError):
            ClaimManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 