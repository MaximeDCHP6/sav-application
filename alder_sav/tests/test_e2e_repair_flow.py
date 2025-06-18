import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from alder_sav.models.repairs import RepairManager
from alder_sav.models.warranties import WarrantyManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestE2ERepairFlow(unittest.TestCase):
    """Tests end-to-end pour le flux complet d'une réparation."""

    def setUp(self):
        self.repair_manager = RepairManager()
        self.warranty_manager = WarrantyManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_complete_repair_flow(self):
        # 1. Créer un client
        client = self.client_manager.create_client({
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+33612345678"
        })

        # 2. Créer un appareil
        device = self.device_manager.create_device({
            "model": "iPhone 13",
            "serial_number": "SN1234567890",
            "client_id": client["id"]
        })

        # 3. Créer une garantie
        warranty = self.warranty_manager.create_warranty({
            "type": "standard",
            "status": "active",
            "device_id": device["id"],
            "client_id": client["id"],
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).isoformat()
        })

        # 4. Créer une réparation
        repair = self.repair_manager.create_repair({
            "type": "screen",
            "status": "pending",
            "device_id": device["id"],
            "client_id": client["id"],
            "warranty_id": warranty["id"],
            "description": "Écran cassé",
            "estimated_cost": Decimal("199.99")
        })

        # 5. Vérifier la création
        self.assertIsNotNone(repair["id"])
        self.assertEqual(repair["type"], "screen")
        self.assertEqual(repair["status"], "pending")

        # 6. Vérifier la notification de création
        notifications = self.notification_manager.get_notifications_by_repair(repair["id"])
        self.assertTrue(any(n["type"] == "repair_created" for n in notifications))

        # 7. Vérifier le document de création
        documents = self.document_manager.get_documents_by_repair(repair["id"])
        self.assertTrue(any(d["type"] == "repair_form" for d in documents))

        # 8. Mettre à jour le statut de la réparation
        updated = self.repair_manager.update_repair(repair["id"], {
            "status": "in_progress",
            "diagnosis": "Écran LCD endommagé",
            "estimated_completion": (datetime.now() + timedelta(days=2)).isoformat()
        })

        # 9. Vérifier la mise à jour
        self.assertEqual(updated["status"], "in_progress")
        self.assertEqual(updated["diagnosis"], "Écran LCD endommagé")

        # 10. Vérifier la notification de mise à jour
        notifications = self.notification_manager.get_notifications_by_repair(repair["id"])
        self.assertTrue(any(n["type"] == "repair_status_updated" for n in notifications))

        # 11. Vérifier le document de mise à jour
        documents = self.document_manager.get_documents_by_repair(repair["id"])
        self.assertTrue(any(d["type"] == "repair_status_update" for d in documents))

        # 12. Finaliser la réparation
        completed = self.repair_manager.update_repair(repair["id"], {
            "status": "completed",
            "resolution": "Écran LCD remplacé",
            "actual_cost": Decimal("199.99"),
            "completion_date": datetime.now().isoformat()
        })

        # 13. Vérifier la finalisation
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["resolution"], "Écran LCD remplacé")
        self.assertEqual(completed["actual_cost"], Decimal("199.99"))

        # 14. Vérifier la notification de finalisation
        notifications = self.notification_manager.get_notifications_by_repair(repair["id"])
        self.assertTrue(any(n["type"] == "repair_completed" for n in notifications))

        # 15. Vérifier le document de finalisation
        documents = self.document_manager.get_documents_by_repair(repair["id"])
        self.assertTrue(any(d["type"] == "repair_completion" for d in documents))

        # 16. Vérifier le rapport final
        reports = self.report_manager.get_reports_by_repair(repair["id"])
        self.assertTrue(any(r["type"] == "repair_summary" for r in reports))

        # 17. Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_repair(repair["id"])
        self.assertTrue(any(s["type"] == "repair_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 