import unittest
from datetime import datetime
from alder_sav.models.reports import ReportManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.statistics import StatisticsManager

class TestIntegrationReports(unittest.TestCase):
    """Tests d'intégration pour la gestion des rapports."""

    def setUp(self):
        self.report_manager = ReportManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.document_manager = DocumentManager()
        self.notification_manager = NotificationManager()
        self.statistics_manager = StatisticsManager()

    def test_create_report(self):
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

        # Créer un rapport
        report = self.report_manager.create_report({
            "type": "repair_summary",
            "status": "completed",
            "content": {
                "summary": "Résumé des réparations",
                "details": {
                    "total_repairs": 100,
                    "completed_repairs": 90,
                    "pending_repairs": 10
                },
                "charts": {
                    "repair_status": "https://aldersav.com/charts/repair-status.png"
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "author": "System",
                "version": "1.0",
                "permissions": {
                    "read": ["admin", "manager"],
                    "write": ["admin"],
                    "delete": ["admin"]
                }
            },
            "history": [
                {
                    "action": "created",
                    "timestamp": datetime.now().isoformat(),
                    "user": "System"
                }
            ]
        })

        # Vérifier la création
        self.assertIsNotNone(report["id"])
        self.assertEqual(report["type"], "repair_summary")
        self.assertEqual(report["status"], "completed")

        # Vérifier le document
        documents = self.document_manager.get_documents_by_report(report["id"])
        self.assertTrue(any(d["type"] == "report_pdf" for d in documents))

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_report(report["id"])
        self.assertTrue(any(n["type"] == "report_created" for n in notifications))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_report(report["id"])
        self.assertTrue(any(s["type"] == "report_metrics" for s in stats))

    def test_update_report_status(self):
        # Créer un rapport
        report = self.report_manager.create_report({
            "type": "repair_summary",
            "status": "completed",
            "content": {
                "summary": "Résumé des réparations",
                "details": {
                    "total_repairs": 100,
                    "completed_repairs": 90,
                    "pending_repairs": 10
                },
                "charts": {
                    "repair_status": "https://aldersav.com/charts/repair-status.png"
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "author": "System",
                "version": "1.0",
                "permissions": {
                    "read": ["admin", "manager"],
                    "write": ["admin"],
                    "delete": ["admin"]
                }
            },
            "history": [
                {
                    "action": "created",
                    "timestamp": datetime.now().isoformat(),
                    "user": "System"
                }
            ]
        })

        # Mettre à jour le statut
        updated = self.report_manager.update_report(report["id"], {"status": "archived"})
        self.assertEqual(updated["status"], "archived")

        # Vérifier le document
        documents = self.document_manager.get_documents_by_report(report["id"])
        self.assertTrue(any(d["type"] == "report_status_update" for d in documents))

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_report(report["id"])
        self.assertTrue(any(n["type"] == "report_status_updated" for n in notifications))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_report(report["id"])
        self.assertTrue(any(s["type"] == "report_status_metrics" for s in stats))

    def test_delete_report(self):
        # Créer un rapport
        report = self.report_manager.create_report({
            "type": "repair_summary",
            "status": "completed",
            "content": {
                "summary": "Résumé des réparations",
                "details": {
                    "total_repairs": 100,
                    "completed_repairs": 90,
                    "pending_repairs": 10
                },
                "charts": {
                    "repair_status": "https://aldersav.com/charts/repair-status.png"
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "author": "System",
                "version": "1.0",
                "permissions": {
                    "read": ["admin", "manager"],
                    "write": ["admin"],
                    "delete": ["admin"]
                }
            },
            "history": [
                {
                    "action": "created",
                    "timestamp": datetime.now().isoformat(),
                    "user": "System"
                }
            ]
        })

        # Supprimer le rapport
        self.report_manager.delete_report(report["id"])

        # Vérifier le document
        documents = self.document_manager.get_documents_by_report(report["id"])
        self.assertTrue(any(d["type"] == "report_deletion" for d in documents))

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_report(report["id"])
        self.assertTrue(any(n["type"] == "report_deleted" for n in notifications))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_report(report["id"])
        self.assertTrue(any(s["type"] == "report_deletion_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 