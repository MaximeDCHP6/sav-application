import unittest
from datetime import datetime
from alder_sav.models.repairs import RepairManager
from alder_sav.models.warranties import WarrantyManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestIntegrationRepairs(unittest.TestCase):
    """Tests d'intégration pour la gestion des réparations."""

    def setUp(self):
        self.repair_manager = RepairManager()
        self.warranty_manager = WarrantyManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_create_repair_with_warranty(self):
        # Créer un client
        client = self.client_manager.create_client({
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+33612345678"
        })

        # Créer un appareil
        device = self.device_manager.create_device({
            "model": "iPhone 13",
            "serial_number": "SN1234567890",
            "client_id": client["id"]
        })

        # Créer une garantie
        warranty = self.warranty_manager.create_warranty({
            "type": "standard",
            "status": "active",
            "device_id": device["id"],
            "client_id": client["id"],
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).isoformat()
        })

        # Créer une réparation
        repair = self.repair_manager.create_repair({
            "type": "screen",
            "status": "pending",
            "device_id": device["id"],
            "client_id": client["id"],
            "warranty_id": warranty["id"],
            "description": "Écran cassé",
            "estimated_cost": 199.99
        })

        # Vérifier la création
        self.assertIsNotNone(repair["id"])
        self.assertEqual(repair["type"], "screen")
        self.assertEqual(repair["status"], "pending")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_repair(repair["id"])
        self.assertTrue(any(n["type"] == "repair_created" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_repair(repair["id"])
        self.assertTrue(any(d["type"] == "repair_form" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_repair(repair["id"])
        self.assertTrue(any(r["type"] == "repair_summary" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_repair(repair["id"])
        self.assertTrue(any(s["type"] == "repair_metrics" for s in stats))

    def test_update_repair_status(self):
        # Créer une réparation
        repair = self.repair_manager.create_repair({
            "type": "screen",
            "status": "pending",
            "device_id": "DEV-001",
            "client_id": "CLT-001",
            "description": "Écran cassé",
            "estimated_cost": 199.99
        })

        # Mettre à jour le statut
        updated = self.repair_manager.update_repair(repair["id"], {"status": "in_progress"})
        self.assertEqual(updated["status"], "in_progress")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_repair(repair["id"])
        self.assertTrue(any(n["type"] == "repair_status_updated" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_repair(repair["id"])
        self.assertTrue(any(d["type"] == "repair_status_update" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_repair(repair["id"])
        self.assertTrue(any(r["type"] == "repair_status_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_repair(repair["id"])
        self.assertTrue(any(s["type"] == "repair_status_metrics" for s in stats))

    def test_cancel_repair(self):
        # Créer une réparation
        repair = self.repair_manager.create_repair({
            "type": "screen",
            "status": "pending",
            "device_id": "DEV-001",
            "client_id": "CLT-001",
            "description": "Écran cassé",
            "estimated_cost": 199.99
        })

        # Annuler la réparation
        cancelled = self.repair_manager.cancel_repair(repair["id"])
        self.assertEqual(cancelled["status"], "cancelled")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_repair(repair["id"])
        self.assertTrue(any(n["type"] == "repair_cancelled" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_repair(repair["id"])
        self.assertTrue(any(d["type"] == "repair_cancellation" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_repair(repair["id"])
        self.assertTrue(any(r["type"] == "repair_cancellation_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_repair(repair["id"])
        self.assertTrue(any(s["type"] == "repair_cancellation_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 