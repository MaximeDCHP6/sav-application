import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.interventions import InterventionManager
from alder_sav.utils.exceptions import ValidationError

class TestInterventionManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire d'interventions."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.intervention_dir = Path(self.temp_dir) / "interventions"
        self.intervention_dir.mkdir()
        
        # Initialisation du gestionnaire d'interventions
        self.intervention_manager = InterventionManager(self.intervention_dir)
        
        # Données de test
        self.client_data = {
            "id": "CLI-001",
            "name": "Test Client",
            "type": "particulier",
            "email": "test@example.com",
            "phone": "0123456789"
        }
        
        self.intervention_data = {
            "client": self.client_data,
            "type": "reparation",
            "status": "en_cours",
            "product": {
                "name": "Product 1",
                "reference": "REF-001",
                "serial_number": "SN-001",
                "warranty": {
                    "type": "constructeur",
                    "status": "active",
                    "end_date": (datetime.now() + timedelta(days=180)).isoformat()
                }
            },
            "description": "Le produit ne démarre plus",
            "diagnostic": {
                "date": datetime.now().isoformat(),
                "findings": "Problème de carte mère",
                "estimated_cost": Decimal("150.00"),
                "estimated_duration": 3
            },
            "technician": {
                "id": "TECH-001",
                "name": "John Doe",
                "specialty": "electronique"
            },
            "schedule": {
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "priority": "moyenne"
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_intervention(self):
        """Test de création d'une intervention."""
        # Création de l'intervention
        intervention = self.intervention_manager.create_intervention(self.intervention_data)
        
        # Vérification
        self.assertEqual(intervention["client"]["name"], "Test Client")
        self.assertEqual(intervention["type"], "reparation")
        self.assertEqual(intervention["status"], "en_cours")
        self.assertEqual(intervention["product"]["name"], "Product 1")
        self.assertTrue("id" in intervention)
        self.assertTrue("creation_date" in intervention)
        self.assertTrue("number" in intervention)

    def test_get_intervention(self):
        """Test de récupération d'une intervention."""
        # Création de l'intervention
        intervention = self.intervention_manager.create_intervention(self.intervention_data)
        
        # Récupération de l'intervention
        retrieved_intervention = self.intervention_manager.get_intervention(intervention["id"])
        
        # Vérification
        self.assertEqual(retrieved_intervention["client"]["name"], "Test Client")
        self.assertEqual(retrieved_intervention["type"], "reparation")
        self.assertEqual(retrieved_intervention["status"], "en_cours")

    def test_update_intervention(self):
        """Test de mise à jour d'une intervention."""
        # Création de l'intervention
        intervention = self.intervention_manager.create_intervention(self.intervention_data)
        
        # Mise à jour de l'intervention
        updated_data = {
            "status": "terminee",
            "diagnostic": {
                "date": datetime.now().isoformat(),
                "findings": "Carte mère remplacée",
                "actual_cost": Decimal("180.00"),
                "actual_duration": 2,
                "notes": "Intervention terminée avec succès"
            }
        }
        updated_intervention = self.intervention_manager.update_intervention(intervention["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_intervention["status"], "terminee")
        self.assertEqual(updated_intervention["diagnostic"]["actual_cost"], Decimal("180.00"))
        self.assertEqual(updated_intervention["diagnostic"]["actual_duration"], 2)

    def test_delete_intervention(self):
        """Test de suppression d'une intervention."""
        # Création de l'intervention
        intervention = self.intervention_manager.create_intervention(self.intervention_data)
        
        # Suppression de l'intervention
        self.intervention_manager.delete_intervention(intervention["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.intervention_manager.get_intervention(intervention["id"])

    def test_get_intervention_by_status(self):
        """Test de récupération des interventions par statut."""
        # Création d'interventions avec différents statuts
        self.intervention_manager.create_intervention(self.intervention_data)
        self.intervention_manager.create_intervention({
            **self.intervention_data,
            "status": "terminee"
        })
        
        # Récupération des interventions par statut
        en_cours = self.intervention_manager.get_intervention_by_status("en_cours")
        terminees = self.intervention_manager.get_intervention_by_status("terminee")
        
        # Vérification
        self.assertEqual(len(en_cours), 1)
        self.assertEqual(len(terminees), 1)
        self.assertEqual(en_cours[0]["status"], "en_cours")
        self.assertEqual(terminees[0]["status"], "terminee")

    def test_get_intervention_by_type(self):
        """Test de récupération des interventions par type."""
        # Création d'interventions de différents types
        self.intervention_manager.create_intervention({
            **self.intervention_data,
            "type": "reparation"
        })
        self.intervention_manager.create_intervention({
            **self.intervention_data,
            "type": "maintenance"
        })
        self.intervention_manager.create_intervention({
            **self.intervention_data,
            "type": "reparation"
        })
        
        # Récupération des interventions par type
        reparations = self.intervention_manager.get_intervention_by_type("reparation")
        maintenances = self.intervention_manager.get_intervention_by_type("maintenance")
        
        # Vérification
        self.assertEqual(len(reparations), 2)
        self.assertEqual(len(maintenances), 1)
        self.assertEqual(reparations[0]["type"], "reparation")
        self.assertEqual(maintenances[0]["type"], "maintenance")

    def test_get_intervention_by_client(self):
        """Test de récupération des interventions par client."""
        # Création d'interventions pour différents clients
        client2 = {
            **self.client_data,
            "id": "CLI-002",
            "name": "Client 2"
        }
        self.intervention_manager.create_intervention(self.intervention_data)
        self.intervention_manager.create_intervention({
            **self.intervention_data,
            "client": client2
        })
        self.intervention_manager.create_intervention(self.intervention_data)
        
        # Récupération des interventions par client
        client1_interventions = self.intervention_manager.get_intervention_by_client("CLI-001")
        client2_interventions = self.intervention_manager.get_intervention_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_interventions), 2)
        self.assertEqual(len(client2_interventions), 1)
        self.assertEqual(client1_interventions[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_interventions[0]["client"]["id"], "CLI-002")

    def test_get_intervention_by_date_range(self):
        """Test de récupération des interventions par plage de dates."""
        # Création d'interventions sur plusieurs jours
        intervention_list = []
        for i in range(3):
            intervention = self.intervention_manager.create_intervention(self.intervention_data)
            intervention["creation_date"] = (datetime.now() - timedelta(days=i)).isoformat()
            intervention_list.append(intervention)
        
        # Récupération des interventions par plage de dates
        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        date_range_interventions = self.intervention_manager.get_intervention_by_date_range(
            start_date,
            end_date
        )
        
        # Vérification
        self.assertEqual(len(date_range_interventions), 2)
        self.assertEqual(date_range_interventions[0]["id"], intervention_list[0]["id"])
        self.assertEqual(date_range_interventions[1]["id"], intervention_list[1]["id"])

    def test_validate_intervention(self):
        """Test de validation d'une intervention."""
        # Création d'une intervention valide
        intervention = self.intervention_manager.create_intervention(self.intervention_data)
        
        # Validation de l'intervention
        is_valid = self.intervention_manager.validate_intervention(intervention["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_intervention_stats(self):
        """Test de récupération des statistiques d'une intervention."""
        # Création de l'intervention
        intervention = self.intervention_manager.create_intervention(self.intervention_data)
        
        # Récupération des statistiques
        stats = self.intervention_manager.get_intervention_stats(intervention["id"])
        
        # Vérification
        self.assertTrue("type" in stats)
        self.assertTrue("status" in stats)
        self.assertTrue("diagnostic" in stats)
        self.assertTrue("schedule" in stats)
        self.assertTrue("technician" in stats)

    def test_invalid_intervention_type(self):
        """Test avec un type d'intervention invalide."""
        with self.assertRaises(ValidationError):
            self.intervention_manager.create_intervention({
                **self.intervention_data,
                "type": "invalid_type"
            })

    def test_invalid_intervention_status(self):
        """Test avec un statut d'intervention invalide."""
        with self.assertRaises(ValidationError):
            self.intervention_manager.create_intervention({
                **self.intervention_data,
                "status": "invalid_status"
            })

    def test_invalid_intervention_dir(self):
        """Test avec un répertoire d'interventions invalide."""
        with self.assertRaises(ValidationError):
            InterventionManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 