import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.export import ExportManager
from alder_sav.utils.exceptions import ValidationError

class TestExportManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire d'exports."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.export_dir = Path(self.temp_dir) / "exports"
        self.export_dir.mkdir()
        
        # Initialisation du gestionnaire d'exports
        self.export_manager = ExportManager(self.export_dir)
        
        # Données de test
        self.export_data = {
            "type": "intervention",
            "format": "xlsx",
            "filters": {
                "status": ["termine", "en_cours"],
                "date_range": {
                    "start": datetime.now().isoformat(),
                    "end": (datetime.now() + timedelta(days=30)).isoformat()
                },
                "technician": "TECH-001"
            },
            "columns": [
                "id",
                "date",
                "client",
                "technician",
                "status",
                "duration",
                "cost"
            ],
            "options": {
                "include_header": True,
                "include_summary": True,
                "group_by": ["technician", "status"],
                "sort_by": ["date", "client"]
            },
            "metadata": {
                "created_by": "system",
                "created_at": datetime.now().isoformat(),
                "description": "Export des interventions du mois"
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_export(self):
        """Test de création d'un export."""
        # Création de l'export
        export = self.export_manager.create_export(self.export_data)
        
        # Vérification
        self.assertEqual(export["type"], "intervention")
        self.assertEqual(export["format"], "xlsx")
        self.assertEqual(len(export["columns"]), 7)
        self.assertTrue("id" in export)
        self.assertTrue("creation_date" in export)

    def test_get_export(self):
        """Test de récupération d'un export."""
        # Création de l'export
        export = self.export_manager.create_export(self.export_data)
        
        # Récupération de l'export
        retrieved_export = self.export_manager.get_export(export["id"])
        
        # Vérification
        self.assertEqual(retrieved_export["type"], "intervention")
        self.assertEqual(retrieved_export["format"], "xlsx")
        self.assertEqual(len(retrieved_export["columns"]), 7)

    def test_update_export(self):
        """Test de mise à jour d'un export."""
        # Création de l'export
        export = self.export_manager.create_export(self.export_data)
        
        # Mise à jour de l'export
        updated_data = {
            "filters": {
                "status": ["termine"],
                "date_range": {
                    "start": datetime.now().isoformat(),
                    "end": (datetime.now() + timedelta(days=15)).isoformat()
                }
            },
            "columns": [
                "id",
                "date",
                "client",
                "status",
                "cost"
            ],
            "options": {
                "include_header": True,
                "include_summary": False,
                "group_by": ["status"],
                "sort_by": ["date"]
            }
        }
        updated_export = self.export_manager.update_export(export["id"], updated_data)
        
        # Vérification
        self.assertEqual(len(updated_export["filters"]["status"]), 1)
        self.assertEqual(len(updated_export["columns"]), 5)
        self.assertEqual(len(updated_export["options"]["group_by"]), 1)

    def test_delete_export(self):
        """Test de suppression d'un export."""
        # Création de l'export
        export = self.export_manager.create_export(self.export_data)
        
        # Suppression de l'export
        self.export_manager.delete_export(export["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.export_manager.get_export(export["id"])

    def test_get_export_by_type(self):
        """Test de récupération des exports par type."""
        # Création d'exports de différents types
        self.export_manager.create_export({
            **self.export_data,
            "type": "intervention"
        })
        self.export_manager.create_export({
            **self.export_data,
            "type": "retour"
        })
        
        # Récupération des exports par type
        intervention_exports = self.export_manager.get_export_by_type("intervention")
        retour_exports = self.export_manager.get_export_by_type("retour")
        
        # Vérification
        self.assertEqual(len(intervention_exports), 1)
        self.assertEqual(len(retour_exports), 1)
        self.assertEqual(intervention_exports[0]["type"], "intervention")
        self.assertEqual(retour_exports[0]["type"], "retour")

    def test_get_export_by_format(self):
        """Test de récupération des exports par format."""
        # Création d'exports de différents formats
        self.export_manager.create_export({
            **self.export_data,
            "format": "xlsx"
        })
        self.export_manager.create_export({
            **self.export_data,
            "format": "csv"
        })
        
        # Récupération des exports par format
        xlsx_exports = self.export_manager.get_export_by_format("xlsx")
        csv_exports = self.export_manager.get_export_by_format("csv")
        
        # Vérification
        self.assertEqual(len(xlsx_exports), 1)
        self.assertEqual(len(csv_exports), 1)
        self.assertEqual(xlsx_exports[0]["format"], "xlsx")
        self.assertEqual(csv_exports[0]["format"], "csv")

    def test_get_export_by_date_range(self):
        """Test de récupération des exports par période."""
        # Création d'exports pour différentes périodes
        now = datetime.now()
        self.export_manager.create_export({
            **self.export_data,
            "filters": {
                **self.export_data["filters"],
                "date_range": {
                    "start": now.isoformat(),
                    "end": (now + timedelta(days=30)).isoformat()
                }
            }
        })
        self.export_manager.create_export({
            **self.export_data,
            "filters": {
                **self.export_data["filters"],
                "date_range": {
                    "start": (now + timedelta(days=31)).isoformat(),
                    "end": (now + timedelta(days=60)).isoformat()
                }
            }
        })
        
        # Récupération des exports par période
        current_period_exports = self.export_manager.get_export_by_date_range(
            now,
            now + timedelta(days=30)
        )
        next_period_exports = self.export_manager.get_export_by_date_range(
            now + timedelta(days=31),
            now + timedelta(days=60)
        )
        
        # Vérification
        self.assertEqual(len(current_period_exports), 1)
        self.assertEqual(len(next_period_exports), 1)

    def test_validate_export(self):
        """Test de validation d'un export."""
        # Création d'un export valide
        export = self.export_manager.create_export(self.export_data)
        
        # Validation de l'export
        is_valid = self.export_manager.validate_export(export["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_export_summary(self):
        """Test de récupération du résumé d'un export."""
        # Création d'un export
        export = self.export_manager.create_export(self.export_data)
        
        # Récupération du résumé
        summary = self.export_manager.get_export_summary(export["id"])
        
        # Vérification
        self.assertTrue("type" in summary)
        self.assertTrue("format" in summary)
        self.assertTrue("filters" in summary)
        self.assertTrue("columns" in summary)
        self.assertTrue("options" in summary)
        self.assertTrue("metadata" in summary)

    def test_invalid_export_type(self):
        """Test avec un type d'export invalide."""
        with self.assertRaises(ValidationError):
            self.export_manager.create_export({
                **self.export_data,
                "type": "invalid_type"
            })

    def test_invalid_export_format(self):
        """Test avec un format d'export invalide."""
        with self.assertRaises(ValidationError):
            self.export_manager.create_export({
                **self.export_data,
                "format": "invalid_format"
            })

    def test_invalid_export_dir(self):
        """Test avec un répertoire d'exports invalide."""
        with self.assertRaises(ValidationError):
            ExportManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 