import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.scheduler import SchedulerManager
from alder_sav.utils.exceptions import ValidationError

class TestSchedulerManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de tâches planifiées."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.scheduler_dir = Path(self.temp_dir) / "scheduler"
        self.scheduler_dir.mkdir()
        
        # Initialisation du gestionnaire de tâches planifiées
        self.scheduler_manager = SchedulerManager(self.scheduler_dir)
        
        # Données de test
        self.task_data = {
            "name": "Vérification du stock",
            "type": "maintenance",
            "category": "stock",
            "status": "planifiee",
            "schedule": {
                "frequency": "quotidien",
                "time": "08:00",
                "days": ["lundi", "mardi", "mercredi", "jeudi", "vendredi"],
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "action": {
                "type": "verification",
                "target": "stock",
                "parameters": {
                    "threshold": 5,
                    "notify": True
                }
            },
            "notification": {
                "recipients": [
                    {
                        "id": "USR-001",
                        "name": "Jean Dupont",
                        "email": "jean.dupont@example.com",
                        "role": "technicien"
                    }
                ],
                "template": "stock_check"
            },
            "metadata": {
                "created_by": "system",
                "last_run": None,
                "next_run": (datetime.now() + timedelta(days=1)).isoformat()
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_task(self):
        """Test de création d'une tâche planifiée."""
        # Création de la tâche
        task = self.scheduler_manager.create_task(self.task_data)
        
        # Vérification
        self.assertEqual(task["name"], "Vérification du stock")
        self.assertEqual(task["type"], "maintenance")
        self.assertEqual(task["category"], "stock")
        self.assertEqual(task["status"], "planifiee")
        self.assertEqual(task["schedule"]["frequency"], "quotidien")
        self.assertTrue("id" in task)
        self.assertTrue("creation_date" in task)

    def test_get_task(self):
        """Test de récupération d'une tâche planifiée."""
        # Création de la tâche
        task = self.scheduler_manager.create_task(self.task_data)
        
        # Récupération de la tâche
        retrieved_task = self.scheduler_manager.get_task(task["id"])
        
        # Vérification
        self.assertEqual(retrieved_task["name"], "Vérification du stock")
        self.assertEqual(retrieved_task["type"], "maintenance")
        self.assertEqual(retrieved_task["category"], "stock")

    def test_update_task(self):
        """Test de mise à jour d'une tâche planifiée."""
        # Création de la tâche
        task = self.scheduler_manager.create_task(self.task_data)
        
        # Mise à jour de la tâche
        updated_data = {
            "status": "en_cours",
            "schedule": {
                "time": "09:00",
                "days": ["lundi", "mercredi", "vendredi"]
            },
            "metadata": {
                "last_run": datetime.now().isoformat()
            }
        }
        updated_task = self.scheduler_manager.update_task(task["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_task["status"], "en_cours")
        self.assertEqual(updated_task["schedule"]["time"], "09:00")
        self.assertEqual(len(updated_task["schedule"]["days"]), 3)
        self.assertTrue("last_run" in updated_task["metadata"])

    def test_delete_task(self):
        """Test de suppression d'une tâche planifiée."""
        # Création de la tâche
        task = self.scheduler_manager.create_task(self.task_data)
        
        # Suppression de la tâche
        self.scheduler_manager.delete_task(task["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.scheduler_manager.get_task(task["id"])

    def test_get_task_by_type(self):
        """Test de récupération des tâches par type."""
        # Création de tâches de différents types
        self.scheduler_manager.create_task({
            **self.task_data,
            "type": "maintenance"
        })
        self.scheduler_manager.create_task({
            **self.task_data,
            "name": "Sauvegarde système",
            "type": "system"
        })
        
        # Récupération des tâches par type
        maintenance_tasks = self.scheduler_manager.get_task_by_type("maintenance")
        system_tasks = self.scheduler_manager.get_task_by_type("system")
        
        # Vérification
        self.assertEqual(len(maintenance_tasks), 1)
        self.assertEqual(len(system_tasks), 1)
        self.assertEqual(maintenance_tasks[0]["type"], "maintenance")
        self.assertEqual(system_tasks[0]["type"], "system")

    def test_get_task_by_category(self):
        """Test de récupération des tâches par catégorie."""
        # Création de tâches de différentes catégories
        self.scheduler_manager.create_task({
            **self.task_data,
            "category": "stock"
        })
        self.scheduler_manager.create_task({
            **self.task_data,
            "name": "Nettoyage base de données",
            "category": "system"
        })
        
        # Récupération des tâches par catégorie
        stock_tasks = self.scheduler_manager.get_task_by_category("stock")
        system_tasks = self.scheduler_manager.get_task_by_category("system")
        
        # Vérification
        self.assertEqual(len(stock_tasks), 1)
        self.assertEqual(len(system_tasks), 1)
        self.assertEqual(stock_tasks[0]["category"], "stock")
        self.assertEqual(system_tasks[0]["category"], "system")

    def test_get_task_by_status(self):
        """Test de récupération des tâches par statut."""
        # Création de tâches avec différents statuts
        self.scheduler_manager.create_task({
            **self.task_data,
            "status": "planifiee"
        })
        self.scheduler_manager.create_task({
            **self.task_data,
            "status": "en_cours"
        })
        
        # Récupération des tâches par statut
        planifiees = self.scheduler_manager.get_task_by_status("planifiee")
        en_cours = self.scheduler_manager.get_task_by_status("en_cours")
        
        # Vérification
        self.assertEqual(len(planifiees), 1)
        self.assertEqual(len(en_cours), 1)
        self.assertEqual(planifiees[0]["status"], "planifiee")
        self.assertEqual(en_cours[0]["status"], "en_cours")

    def test_get_task_by_frequency(self):
        """Test de récupération des tâches par fréquence."""
        # Création de tâches avec différentes fréquences
        self.scheduler_manager.create_task({
            **self.task_data,
            "schedule": {
                **self.task_data["schedule"],
                "frequency": "quotidien"
            }
        })
        self.scheduler_manager.create_task({
            **self.task_data,
            "schedule": {
                **self.task_data["schedule"],
                "frequency": "hebdomadaire"
            }
        })
        
        # Récupération des tâches par fréquence
        quotidiennes = self.scheduler_manager.get_task_by_frequency("quotidien")
        hebdomadaires = self.scheduler_manager.get_task_by_frequency("hebdomadaire")
        
        # Vérification
        self.assertEqual(len(quotidiennes), 1)
        self.assertEqual(len(hebdomadaires), 1)
        self.assertEqual(quotidiennes[0]["schedule"]["frequency"], "quotidien")
        self.assertEqual(hebdomadaires[0]["schedule"]["frequency"], "hebdomadaire")

    def test_validate_task(self):
        """Test de validation d'une tâche planifiée."""
        # Création d'une tâche valide
        task = self.scheduler_manager.create_task(self.task_data)
        
        # Validation de la tâche
        is_valid = self.scheduler_manager.validate_task(task["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_task_stats(self):
        """Test de récupération des statistiques d'une tâche planifiée."""
        # Création de la tâche
        task = self.scheduler_manager.create_task(self.task_data)
        
        # Récupération des statistiques
        stats = self.scheduler_manager.get_task_stats(task["id"])
        
        # Vérification
        self.assertTrue("type" in stats)
        self.assertTrue("category" in stats)
        self.assertTrue("schedule" in stats)
        self.assertTrue("action" in stats)
        self.assertTrue("metadata" in stats)

    def test_invalid_task_type(self):
        """Test avec un type de tâche invalide."""
        with self.assertRaises(ValidationError):
            self.scheduler_manager.create_task({
                **self.task_data,
                "type": "invalid_type"
            })

    def test_invalid_task_category(self):
        """Test avec une catégorie de tâche invalide."""
        with self.assertRaises(ValidationError):
            self.scheduler_manager.create_task({
                **self.task_data,
                "category": "invalid_category"
            })

    def test_invalid_task_dir(self):
        """Test avec un répertoire de tâches invalide."""
        with self.assertRaises(ValidationError):
            SchedulerManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 