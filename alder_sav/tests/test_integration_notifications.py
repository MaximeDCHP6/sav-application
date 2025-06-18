import unittest
from datetime import datetime
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestIntegrationNotifications(unittest.TestCase):
    """Tests d'intégration pour la gestion des notifications."""

    def setUp(self):
        self.notification_manager = NotificationManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_create_notification(self):
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

        # Créer une notification
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

        # Vérifier la création
        self.assertIsNotNone(notification["id"])
        self.assertEqual(notification["type"], "repair_status")
        self.assertEqual(notification["status"], "pending")

        # Vérifier le document
        documents = self.document_manager.get_documents_by_notification(notification["id"])
        self.assertTrue(any(d["type"] == "notification_log" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_notification(notification["id"])
        self.assertTrue(any(r["type"] == "notification_summary" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_notification(notification["id"])
        self.assertTrue(any(s["type"] == "notification_metrics" for s in stats))

    def test_update_notification_status(self):
        # Créer une notification
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

        # Mettre à jour le statut
        updated = self.notification_manager.update_notification(notification["id"], {"status": "sent"})
        self.assertEqual(updated["status"], "sent")

        # Vérifier le document
        documents = self.document_manager.get_documents_by_notification(notification["id"])
        self.assertTrue(any(d["type"] == "notification_status_update" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_notification(notification["id"])
        self.assertTrue(any(r["type"] == "notification_status_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_notification(notification["id"])
        self.assertTrue(any(s["type"] == "notification_status_metrics" for s in stats))

    def test_delete_notification(self):
        # Créer une notification
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

        # Supprimer la notification
        self.notification_manager.delete_notification(notification["id"])

        # Vérifier le document
        documents = self.document_manager.get_documents_by_notification(notification["id"])
        self.assertTrue(any(d["type"] == "notification_deletion" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_notification(notification["id"])
        self.assertTrue(any(r["type"] == "notification_deletion_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_notification(notification["id"])
        self.assertTrue(any(s["type"] == "notification_deletion_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 