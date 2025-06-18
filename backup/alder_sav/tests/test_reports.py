import unittest
import time
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.reports import ReportManager
from alder_sav.utils.exceptions import ValidationError, ReportError

class TestReportManager(unittest.TestCase):
    """Tests pour le gestionnaire de rapports."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.report_manager = ReportManager()

    def test_create_report(self):
        """Test de création de rapport."""
        # Créer un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100, "completed_repairs": 80, "pending_repairs": 20}
        )
        
        # Vérifier le rapport
        self.assertIsNotNone(report["id"])
        self.assertEqual(report["type"], "repair_summary")
        self.assertEqual(report["title"], "Monthly Repair Summary")
        self.assertEqual(report["description"], "Summary of repairs for the current month")
        self.assertEqual(report["data"]["total_repairs"], 100)
        self.assertEqual(report["status"], "draft")

    def test_get_report(self):
        """Test de récupération de rapport."""
        # Créer un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100}
        )
        
        # Récupérer le rapport
        retrieved_report = self.report_manager.get_report(report["id"])
        
        # Vérifier la récupération
        self.assertEqual(retrieved_report, report)

    def test_update_report(self):
        """Test de mise à jour de rapport."""
        # Créer un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100}
        )
        
        # Mettre à jour le rapport
        updated_report = self.report_manager.update_report(
            report["id"],
            title="Updated Monthly Repair Summary",
            data={"total_repairs": 150}
        )
        
        # Vérifier la mise à jour
        self.assertEqual(updated_report["title"], "Updated Monthly Repair Summary")
        self.assertEqual(updated_report["data"]["total_repairs"], 150)

    def test_delete_report(self):
        """Test de suppression de rapport."""
        # Créer un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100}
        )
        
        # Supprimer le rapport
        self.report_manager.delete_report(report["id"])
        
        # Vérifier la suppression
        with self.assertRaises(ReportError):
            self.report_manager.get_report(report["id"])

    def test_get_reports_by_type(self):
        """Test de récupération des rapports par type."""
        # Créer des rapports de différents types
        self.report_manager.create_report(
            type="repair_summary",
            title="Repair Summary",
            description="Summary of repairs",
            data={"total_repairs": 100}
        )
        self.report_manager.create_report(
            type="warranty_summary",
            title="Warranty Summary",
            description="Summary of warranties",
            data={"total_warranties": 50}
        )
        
        # Récupérer les rapports par type
        repair_reports = self.report_manager.get_reports_by_type("repair_summary")
        warranty_reports = self.report_manager.get_reports_by_type("warranty_summary")
        
        # Vérifier les résultats
        self.assertEqual(len(repair_reports), 1)
        self.assertEqual(len(warranty_reports), 1)
        self.assertEqual(repair_reports[0]["type"], "repair_summary")
        self.assertEqual(warranty_reports[0]["type"], "warranty_summary")

    def test_get_reports_by_status(self):
        """Test de récupération des rapports par statut."""
        # Créer des rapports avec différents statuts
        report1 = self.report_manager.create_report(
            type="repair_summary",
            title="Draft Report",
            description="This is a draft report",
            data={"total_repairs": 100}
        )
        report2 = self.report_manager.create_report(
            type="repair_summary",
            title="Published Report",
            description="This is a published report",
            data={"total_repairs": 200}
        )
        
        # Mettre à jour le statut du deuxième rapport
        self.report_manager.update_report(
            report2["id"],
            status="published"
        )
        
        # Récupérer les rapports par statut
        draft_reports = self.report_manager.get_reports_by_status("draft")
        published_reports = self.report_manager.get_reports_by_status("published")
        
        # Vérifier les résultats
        self.assertEqual(len(draft_reports), 1)
        self.assertEqual(len(published_reports), 1)
        self.assertEqual(draft_reports[0]["status"], "draft")
        self.assertEqual(published_reports[0]["status"], "published")

    def test_get_reports_by_date_range(self):
        """Test de récupération des rapports par plage de dates."""
        # Créer des rapports à différentes dates
        self.report_manager.create_report(
            type="repair_summary",
            title="Report 1",
            description="This is report 1",
            data={"total_repairs": 100},
            created_at=(datetime.now() - timedelta(days=5)).isoformat()
        )
        self.report_manager.create_report(
            type="repair_summary",
            title="Report 2",
            description="This is report 2",
            data={"total_repairs": 200},
            created_at=datetime.now().isoformat()
        )
        
        # Récupérer les rapports par plage de dates
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = (datetime.now() - timedelta(days=3)).isoformat()
        date_range_reports = self.report_manager.get_reports_by_date_range(start_date, end_date)
        
        # Vérifier les résultats
        self.assertEqual(len(date_range_reports), 1)
        self.assertEqual(date_range_reports[0]["title"], "Report 1")

    def test_generate_report(self):
        """Test de génération de rapport."""
        # Créer un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100}
        )
        
        # Générer le rapport
        generated_report = self.report_manager.generate_report(report["id"])
        
        # Vérifier la génération
        self.assertEqual(generated_report["status"], "generated")
        self.assertIsNotNone(generated_report["generated_at"])

    def test_export_report(self):
        """Test d'export de rapport."""
        # Créer un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100}
        )
        
        # Exporter le rapport
        exported_report = self.report_manager.export_report(report["id"], format="pdf")
        
        # Vérifier l'export
        self.assertIsNotNone(exported_report["content"])
        self.assertEqual(exported_report["format"], "pdf")

    def test_schedule_report(self):
        """Test de planification de rapport."""
        # Créer un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100}
        )
        
        # Planifier le rapport
        scheduled_time = (datetime.now() + timedelta(days=1)).isoformat()
        scheduled_report = self.report_manager.schedule_report(
            report["id"],
            scheduled_time,
            frequency="daily"
        )
        
        # Vérifier la planification
        self.assertEqual(scheduled_report["status"], "scheduled")
        self.assertEqual(scheduled_report["scheduled_time"], scheduled_time)
        self.assertEqual(scheduled_report["frequency"], "daily")

    def test_cancel_scheduled_report(self):
        """Test d'annulation de rapport planifié."""
        # Créer et planifier un rapport
        report = self.report_manager.create_report(
            type="repair_summary",
            title="Monthly Repair Summary",
            description="Summary of repairs for the current month",
            data={"total_repairs": 100}
        )
        scheduled_time = (datetime.now() + timedelta(days=1)).isoformat()
        self.report_manager.schedule_report(report["id"], scheduled_time)
        
        # Annuler le rapport
        cancelled_report = self.report_manager.cancel_scheduled_report(report["id"])
        
        # Vérifier l'annulation
        self.assertEqual(cancelled_report["status"], "cancelled")

    def test_get_report_templates(self):
        """Test de récupération des templates de rapport."""
        # Créer un template
        template = self.report_manager.create_report_template(
            name="repair_summary_template",
            type="repair_summary",
            format="pdf",
            template={
                "title": "{{title}}",
                "content": "Total Repairs: {{data.total_repairs}}"
            }
        )
        
        # Récupérer les templates
        templates = self.report_manager.get_report_templates()
        
        # Vérifier les résultats
        self.assertTrue(any(t["name"] == "repair_summary_template" for t in templates))

    def test_create_report_template(self):
        """Test de création de template de rapport."""
        # Créer un template
        template = self.report_manager.create_report_template(
            name="repair_summary_template",
            type="repair_summary",
            format="pdf",
            template={
                "title": "{{title}}",
                "content": "Total Repairs: {{data.total_repairs}}"
            }
        )
        
        # Vérifier le template
        self.assertIsNotNone(template["id"])
        self.assertEqual(template["name"], "repair_summary_template")
        self.assertEqual(template["type"], "repair_summary")
        self.assertEqual(template["format"], "pdf")

    def test_update_report_template(self):
        """Test de mise à jour de template de rapport."""
        # Créer un template
        template = self.report_manager.create_report_template(
            name="repair_summary_template",
            type="repair_summary",
            format="pdf",
            template={
                "title": "{{title}}",
                "content": "Total Repairs: {{data.total_repairs}}"
            }
        )
        
        # Mettre à jour le template
        updated_template = self.report_manager.update_report_template(
            template["id"],
            template={
                "title": "{{title}}",
                "content": "Total Repairs: {{data.total_repairs}}\nCompleted: {{data.completed_repairs}}"
            }
        )
        
        # Vérifier la mise à jour
        self.assertIn("Completed: {{data.completed_repairs}}", updated_template["template"]["content"])

    def test_delete_report_template(self):
        """Test de suppression de template de rapport."""
        # Créer un template
        template = self.report_manager.create_report_template(
            name="repair_summary_template",
            type="repair_summary",
            format="pdf",
            template={
                "title": "{{title}}",
                "content": "Total Repairs: {{data.total_repairs}}"
            }
        )
        
        # Supprimer le template
        self.report_manager.delete_report_template(template["id"])
        
        # Vérifier la suppression
        templates = self.report_manager.get_report_templates()
        self.assertFalse(any(t["id"] == template["id"] for t in templates))

if __name__ == '__main__':
    unittest.main() 