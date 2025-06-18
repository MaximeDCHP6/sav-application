import unittest
from datetime import datetime, timedelta
from alder_sav.models.warranties import WarrantyManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestIntegrationWarranties(unittest.TestCase):
    """Tests d'intégration pour la gestion des garanties."""

    def setUp(self):
        self.warranty_manager = WarrantyManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_create_warranty(self):
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

        # Vérifier la création
        self.assertIsNotNone(warranty["id"])
        self.assertEqual(warranty["type"], "standard")
        self.assertEqual(warranty["status"], "active")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_warranty(warranty["id"])
        self.assertTrue(any(n["type"] == "warranty_created" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_warranty(warranty["id"])
        self.assertTrue(any(d["type"] == "warranty_contract" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_warranty(warranty["id"])
        self.assertTrue(any(r["type"] == "warranty_summary" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_warranty(warranty["id"])
        self.assertTrue(any(s["type"] == "warranty_metrics" for s in stats))

    def test_update_warranty_status(self):
        # Créer une garantie
        warranty = self.warranty_manager.create_warranty({
            "type": "standard",
            "status": "active",
            "device_id": "DEV-001",
            "client_id": "CLT-001",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).isoformat()
        })

        # Mettre à jour le statut
        updated = self.warranty_manager.update_warranty(warranty["id"], {"status": "expired"})
        self.assertEqual(updated["status"], "expired")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_warranty(warranty["id"])
        self.assertTrue(any(n["type"] == "warranty_status_updated" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_warranty(warranty["id"])
        self.assertTrue(any(d["type"] == "warranty_status_update" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_warranty(warranty["id"])
        self.assertTrue(any(r["type"] == "warranty_status_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_warranty(warranty["id"])
        self.assertTrue(any(s["type"] == "warranty_status_metrics" for s in stats))

    def test_cancel_warranty(self):
        # Créer une garantie
        warranty = self.warranty_manager.create_warranty({
            "type": "standard",
            "status": "active",
            "device_id": "DEV-001",
            "client_id": "CLT-001",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).isoformat()
        })

        # Annuler la garantie
        cancelled = self.warranty_manager.cancel_warranty(warranty["id"])
        self.assertEqual(cancelled["status"], "cancelled")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_warranty(warranty["id"])
        self.assertTrue(any(n["type"] == "warranty_cancelled" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_warranty(warranty["id"])
        self.assertTrue(any(d["type"] == "warranty_cancellation" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_warranty(warranty["id"])
        self.assertTrue(any(r["type"] == "warranty_cancellation_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_warranty(warranty["id"])
        self.assertTrue(any(s["type"] == "warranty_cancellation_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 