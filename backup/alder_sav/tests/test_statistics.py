import unittest
import time
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.statistics import StatisticsManager
from alder_sav.utils.exceptions import ValidationError, StatisticsError

class TestStatisticsManager(unittest.TestCase):
    """Tests pour le gestionnaire de statistiques."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.statistics_manager = StatisticsManager()

    def test_create_statistics(self):
        """Test de création de statistiques."""
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={
                "total_repairs": 100,
                "completed_repairs": 80,
                "pending_repairs": 20,
                "average_repair_time": 2.5
            }
        )
        
        # Vérifier les statistiques
        self.assertIsNotNone(statistics["id"])
        self.assertEqual(statistics["type"], "repair_statistics")
        self.assertEqual(statistics["data"]["total_repairs"], 100)
        self.assertEqual(statistics["data"]["completed_repairs"], 80)
        self.assertEqual(statistics["data"]["pending_repairs"], 20)
        self.assertEqual(statistics["data"]["average_repair_time"], 2.5)

    def test_get_statistics(self):
        """Test de récupération de statistiques."""
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        
        # Récupérer les statistiques
        retrieved_statistics = self.statistics_manager.get_statistics(statistics["id"])
        
        # Vérifier la récupération
        self.assertEqual(retrieved_statistics, statistics)

    def test_update_statistics(self):
        """Test de mise à jour de statistiques."""
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        
        # Mettre à jour les statistiques
        updated_statistics = self.statistics_manager.update_statistics(
            statistics["id"],
            data={"total_repairs": 150}
        )
        
        # Vérifier la mise à jour
        self.assertEqual(updated_statistics["data"]["total_repairs"], 150)

    def test_delete_statistics(self):
        """Test de suppression de statistiques."""
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        
        # Supprimer les statistiques
        self.statistics_manager.delete_statistics(statistics["id"])
        
        # Vérifier la suppression
        with self.assertRaises(StatisticsError):
            self.statistics_manager.get_statistics(statistics["id"])

    def test_get_statistics_by_type(self):
        """Test de récupération des statistiques par type."""
        # Créer des statistiques de différents types
        self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        self.statistics_manager.create_statistics(
            type="warranty_statistics",
            data={"total_warranties": 50}
        )
        
        # Récupérer les statistiques par type
        repair_statistics = self.statistics_manager.get_statistics_by_type("repair_statistics")
        warranty_statistics = self.statistics_manager.get_statistics_by_type("warranty_statistics")
        
        # Vérifier les résultats
        self.assertEqual(len(repair_statistics), 1)
        self.assertEqual(len(warranty_statistics), 1)
        self.assertEqual(repair_statistics[0]["type"], "repair_statistics")
        self.assertEqual(warranty_statistics[0]["type"], "warranty_statistics")

    def test_get_statistics_by_date_range(self):
        """Test de récupération des statistiques par plage de dates."""
        # Créer des statistiques à différentes dates
        self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100},
            created_at=(datetime.now() - timedelta(days=5)).isoformat()
        )
        self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 200},
            created_at=datetime.now().isoformat()
        )
        
        # Récupérer les statistiques par plage de dates
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = (datetime.now() - timedelta(days=3)).isoformat()
        date_range_statistics = self.statistics_manager.get_statistics_by_date_range(start_date, end_date)
        
        # Vérifier les résultats
        self.assertEqual(len(date_range_statistics), 1)
        self.assertEqual(date_range_statistics[0]["data"]["total_repairs"], 100)

    def test_aggregate_statistics(self):
        """Test d'agrégation de statistiques."""
        # Créer des statistiques
        self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 200}
        )
        
        # Agréger les statistiques
        aggregated_statistics = self.statistics_manager.aggregate_statistics("repair_statistics")
        
        # Vérifier l'agrégation
        self.assertEqual(aggregated_statistics["total_repairs"], 300)

    def test_generate_statistics_report(self):
        """Test de génération de rapport de statistiques."""
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        
        # Générer un rapport
        report = self.statistics_manager.generate_statistics_report(statistics["id"])
        
        # Vérifier le rapport
        self.assertIsNotNone(report["content"])
        self.assertEqual(report["type"], "statistics_report")

    def test_export_statistics(self):
        """Test d'export de statistiques."""
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        
        # Exporter les statistiques
        exported_statistics = self.statistics_manager.export_statistics(statistics["id"], format="csv")
        
        # Vérifier l'export
        self.assertIsNotNone(exported_statistics["content"])
        self.assertEqual(exported_statistics["format"], "csv")

    def test_schedule_statistics(self):
        """Test de planification de statistiques."""
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        
        # Planifier les statistiques
        scheduled_time = (datetime.now() + timedelta(days=1)).isoformat()
        scheduled_statistics = self.statistics_manager.schedule_statistics(
            statistics["id"],
            scheduled_time,
            frequency="daily"
        )
        
        # Vérifier la planification
        self.assertEqual(scheduled_statistics["status"], "scheduled")
        self.assertEqual(scheduled_statistics["scheduled_time"], scheduled_time)
        self.assertEqual(scheduled_statistics["frequency"], "daily")

    def test_cancel_scheduled_statistics(self):
        """Test d'annulation de statistiques planifiées."""
        # Créer et planifier des statistiques
        statistics = self.statistics_manager.create_statistics(
            type="repair_statistics",
            data={"total_repairs": 100}
        )
        scheduled_time = (datetime.now() + timedelta(days=1)).isoformat()
        self.statistics_manager.schedule_statistics(statistics["id"], scheduled_time)
        
        # Annuler les statistiques
        cancelled_statistics = self.statistics_manager.cancel_scheduled_statistics(statistics["id"])
        
        # Vérifier l'annulation
        self.assertEqual(cancelled_statistics["status"], "cancelled")

if __name__ == '__main__':
    unittest.main() 