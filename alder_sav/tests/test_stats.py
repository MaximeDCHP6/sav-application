import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.stats import StatsManager
from alder_sav.utils.exceptions import ValidationError

class TestStatsManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de statistiques."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.stats_dir = Path(self.temp_dir) / "stats"
        self.stats_dir.mkdir()
        
        # Initialisation du gestionnaire de statistiques
        self.stats_manager = StatsManager(self.stats_dir)
        
        # Données de test
        self.stats_data = {
            "type": "intervention",
            "category": "maintenance",
            "period": {
                "start": datetime.now().isoformat(),
                "end": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "metrics": {
                "total": 10,
                "completed": 8,
                "in_progress": 2,
                "cancelled": 0,
                "average_duration": 2.5,
                "success_rate": 0.8
            },
            "details": {
                "by_status": {
                    "completed": 8,
                    "in_progress": 2,
                    "cancelled": 0
                },
                "by_type": {
                    "preventive": 6,
                    "corrective": 4
                },
                "by_technician": {
                    "TECH-001": 5,
                    "TECH-002": 5
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "system"
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_stats(self):
        """Test de création de statistiques."""
        # Création des statistiques
        stats = self.stats_manager.create_stats(self.stats_data)
        
        # Vérification
        self.assertEqual(stats["type"], "intervention")
        self.assertEqual(stats["category"], "maintenance")
        self.assertEqual(stats["metrics"]["total"], 10)
        self.assertTrue("id" in stats)
        self.assertTrue("creation_date" in stats)

    def test_get_stats(self):
        """Test de récupération de statistiques."""
        # Création des statistiques
        stats = self.stats_manager.create_stats(self.stats_data)
        
        # Récupération des statistiques
        retrieved_stats = self.stats_manager.get_stats(stats["id"])
        
        # Vérification
        self.assertEqual(retrieved_stats["type"], "intervention")
        self.assertEqual(retrieved_stats["category"], "maintenance")
        self.assertEqual(retrieved_stats["metrics"]["total"], 10)

    def test_update_stats(self):
        """Test de mise à jour de statistiques."""
        # Création des statistiques
        stats = self.stats_manager.create_stats(self.stats_data)
        
        # Mise à jour des statistiques
        updated_data = {
            "metrics": {
                "total": 12,
                "completed": 10,
                "in_progress": 2,
                "cancelled": 0,
                "average_duration": 2.3,
                "success_rate": 0.83
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_stats = self.stats_manager.update_stats(stats["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_stats["metrics"]["total"], 12)
        self.assertEqual(updated_stats["metrics"]["completed"], 10)
        self.assertEqual(updated_stats["metrics"]["success_rate"], 0.83)

    def test_delete_stats(self):
        """Test de suppression de statistiques."""
        # Création des statistiques
        stats = self.stats_manager.create_stats(self.stats_data)
        
        # Suppression des statistiques
        self.stats_manager.delete_stats(stats["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.stats_manager.get_stats(stats["id"])

    def test_get_stats_by_type(self):
        """Test de récupération des statistiques par type."""
        # Création de statistiques de différents types
        self.stats_manager.create_stats({
            **self.stats_data,
            "type": "intervention"
        })
        self.stats_manager.create_stats({
            **self.stats_data,
            "type": "retour"
        })
        
        # Récupération des statistiques par type
        intervention_stats = self.stats_manager.get_stats_by_type("intervention")
        retour_stats = self.stats_manager.get_stats_by_type("retour")
        
        # Vérification
        self.assertEqual(len(intervention_stats), 1)
        self.assertEqual(len(retour_stats), 1)
        self.assertEqual(intervention_stats[0]["type"], "intervention")
        self.assertEqual(retour_stats[0]["type"], "retour")

    def test_get_stats_by_category(self):
        """Test de récupération des statistiques par catégorie."""
        # Création de statistiques de différentes catégories
        self.stats_manager.create_stats({
            **self.stats_data,
            "category": "maintenance"
        })
        self.stats_manager.create_stats({
            **self.stats_data,
            "category": "reparation"
        })
        
        # Récupération des statistiques par catégorie
        maintenance_stats = self.stats_manager.get_stats_by_category("maintenance")
        reparation_stats = self.stats_manager.get_stats_by_category("reparation")
        
        # Vérification
        self.assertEqual(len(maintenance_stats), 1)
        self.assertEqual(len(reparation_stats), 1)
        self.assertEqual(maintenance_stats[0]["category"], "maintenance")
        self.assertEqual(reparation_stats[0]["category"], "reparation")

    def test_get_stats_by_period(self):
        """Test de récupération des statistiques par période."""
        # Création de statistiques pour différentes périodes
        now = datetime.now()
        self.stats_manager.create_stats({
            **self.stats_data,
            "period": {
                "start": now.isoformat(),
                "end": (now + timedelta(days=30)).isoformat()
            }
        })
        self.stats_manager.create_stats({
            **self.stats_data,
            "period": {
                "start": (now + timedelta(days=31)).isoformat(),
                "end": (now + timedelta(days=60)).isoformat()
            }
        })
        
        # Récupération des statistiques par période
        current_period_stats = self.stats_manager.get_stats_by_period(
            now,
            now + timedelta(days=30)
        )
        next_period_stats = self.stats_manager.get_stats_by_period(
            now + timedelta(days=31),
            now + timedelta(days=60)
        )
        
        # Vérification
        self.assertEqual(len(current_period_stats), 1)
        self.assertEqual(len(next_period_stats), 1)

    def test_validate_stats(self):
        """Test de validation de statistiques."""
        # Création de statistiques valides
        stats = self.stats_manager.create_stats(self.stats_data)
        
        # Validation des statistiques
        is_valid = self.stats_manager.validate_stats(stats["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_stats_summary(self):
        """Test de récupération du résumé des statistiques."""
        # Création de statistiques
        stats = self.stats_manager.create_stats(self.stats_data)
        
        # Récupération du résumé
        summary = self.stats_manager.get_stats_summary(stats["id"])
        
        # Vérification
        self.assertTrue("type" in summary)
        self.assertTrue("category" in summary)
        self.assertTrue("period" in summary)
        self.assertTrue("metrics" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_stats_type(self):
        """Test avec un type de statistiques invalide."""
        with self.assertRaises(ValidationError):
            self.stats_manager.create_stats({
                **self.stats_data,
                "type": "invalid_type"
            })

    def test_invalid_stats_category(self):
        """Test avec une catégorie de statistiques invalide."""
        with self.assertRaises(ValidationError):
            self.stats_manager.create_stats({
                **self.stats_data,
                "category": "invalid_category"
            })

    def test_invalid_stats_dir(self):
        """Test avec un répertoire de statistiques invalide."""
        with self.assertRaises(ValidationError):
            StatsManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 