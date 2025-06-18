import unittest
from datetime import datetime
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestE2ENotificationFlow(unittest.TestCase):
    """Tests end-to-end pour le flux complet d'une notification."""

    def setUp(self):
        self.notification_manager = NotificationManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_complete_notification_flow(self):
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

        # 3. Créer une notification
        notification = self.notification_manager.create_notification({
            "type": "repair_status",
            "status": "pending",
            "priority": "high",
            "recipient": {
                "name": "Jean Dupont",
                "email": "jean.dupont@example.com"
            },
            "content": {
                "title": "Mise à jour de votre réparation",
                "message": "Votre iPhone 13 est en cours de réparation"
            },
            "delivery_channels": ["email", "sms"],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "system",
                "tags": ["repair", "status"]
            }
        })

        # 4. Vérifier la création
        self.assertIsNotNone(notification["id"])
        self.assertEqual(notification["type"], "repair_status")
        self.assertEqual(notification["status"], "pending")

        # 5. Vérifier le document de création
        documents = self.document_manager.get_documents_by_notification(notification["id"])
        self.assertTrue(any(d["type"] == "notification_log" for d in documents))

        # 6. Mettre à jour le statut de la notification
        updated = self.notification_manager.update_notification(notification["id"], {
            "status": "sending",
            "sending_date": datetime.now().isoformat(),
            "sending_attempts": 1
        })

        # 7. Vérifier la mise à jour
        self.assertEqual(updated["status"], "sending")
        self.assertEqual(updated["sending_attempts"], 1)

        # 8. Vérifier le document de mise à jour
        documents = self.document_manager.get_documents_by_notification(notification["id"])
        self.assertTrue(any(d["type"] == "notification_status_update" for d in documents))

        # 9. Finaliser la notification
        completed = self.notification_manager.update_notification(notification["id"], {
            "status": "sent",
            "sent_date": datetime.now().isoformat(),
            "delivery_status": {
                "email": "delivered",
                "sms": "delivered"
            }
        })

        # 10. Vérifier la finalisation
        self.assertEqual(completed["status"], "sent")
        self.assertEqual(completed["delivery_status"]["email"], "delivered")
        self.assertEqual(completed["delivery_status"]["sms"], "delivered")

        # 11. Vérifier le document de finalisation
        documents = self.document_manager.get_documents_by_notification(notification["id"])
        self.assertTrue(any(d["type"] == "notification_delivery" for d in documents))

        # 12. Vérifier le rapport final
        reports = self.report_manager.get_reports_by_notification(notification["id"])
        self.assertTrue(any(r["type"] == "notification_summary" for r in reports))

        # 13. Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_notification(notification["id"])
        self.assertTrue(any(s["type"] == "notification_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 