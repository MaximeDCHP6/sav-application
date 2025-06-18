import unittest
from datetime import datetime, timedelta
from alder_sav.models.warranties import WarrantyManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestE2EWarrantyFlow(unittest.TestCase):
    """Tests end-to-end pour le flux complet d'une garantie."""

    def setUp(self):
        self.warranty_manager = WarrantyManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_complete_warranty_flow(self):
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
            "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "coverage": {
                "parts": True,
                "labor": True,
                "accidental_damage": False
            },
            "terms": {
                "duration": "12 months",
                "renewable": True,
                "transferable": False
            }
        })

        # 4. Vérifier la création
        self.assertIsNotNone(warranty["id"])
        self.assertEqual(warranty["type"], "standard")
        self.assertEqual(warranty["status"], "active")

        # 5. Vérifier la notification de création
        notifications = self.notification_manager.get_notifications_by_warranty(warranty["id"])
        self.assertTrue(any(n["type"] == "warranty_created" for n in notifications))

        # 6. Vérifier le document de création
        documents = self.document_manager.get_documents_by_warranty(warranty["id"])
        self.assertTrue(any(d["type"] == "warranty_contract" for d in documents))

        # 7. Mettre à jour le statut de la garantie
        updated = self.warranty_manager.update_warranty(warranty["id"], {
            "status": "in_use",
            "usage_count": 1,
            "last_used": datetime.now().isoformat()
        })

        # 8. Vérifier la mise à jour
        self.assertEqual(updated["status"], "in_use")
        self.assertEqual(updated["usage_count"], 1)

        # 9. Vérifier la notification de mise à jour
        notifications = self.notification_manager.get_notifications_by_warranty(warranty["id"])
        self.assertTrue(any(n["type"] == "warranty_status_updated" for n in notifications))

        # 10. Vérifier le document de mise à jour
        documents = self.document_manager.get_documents_by_warranty(warranty["id"])
        self.assertTrue(any(d["type"] == "warranty_status_update" for d in documents))

        # 11. Finaliser la garantie
        completed = self.warranty_manager.update_warranty(warranty["id"], {
            "status": "expired",
            "end_date": datetime.now().isoformat(),
            "final_usage_count": 1
        })

        # 12. Vérifier la finalisation
        self.assertEqual(completed["status"], "expired")
        self.assertEqual(completed["final_usage_count"], 1)

        # 13. Vérifier la notification de finalisation
        notifications = self.notification_manager.get_notifications_by_warranty(warranty["id"])
        self.assertTrue(any(n["type"] == "warranty_expired" for n in notifications))

        # 14. Vérifier le document de finalisation
        documents = self.document_manager.get_documents_by_warranty(warranty["id"])
        self.assertTrue(any(d["type"] == "warranty_expiration" for d in documents))

        # 15. Vérifier le rapport final
        reports = self.report_manager.get_reports_by_warranty(warranty["id"])
        self.assertTrue(any(r["type"] == "warranty_summary" for r in reports))

        # 16. Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_warranty(warranty["id"])
        self.assertTrue(any(s["type"] == "warranty_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 