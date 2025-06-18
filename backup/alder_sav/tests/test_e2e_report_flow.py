import unittest
from datetime import datetime
from alder_sav.models.reports import ReportManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.statistics import StatisticsManager

class TestE2EReportFlow(unittest.TestCase):
    """Tests end-to-end pour le flux complet d'un rapport."""

    def setUp(self):
        self.report_manager = ReportManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.document_manager = DocumentManager()
        self.notification_manager = NotificationManager()
        self.statistics_manager = StatisticsManager()

    def test_complete_report_flow(self):
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

        # 3. Créer un rapport
        report = self.report_manager.create_report({
            "type": "repair_summary",
            "status": "draft",
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

        # 4. Vérifier la création
        self.assertIsNotNone(report["id"])
        self.assertEqual(report["type"], "repair_summary")
        self.assertEqual(report["status"], "draft")

        # 5. Vérifier la notification de création
        notifications = self.notification_manager.get_notifications_by_report(report["id"])
        self.assertTrue(any(n["type"] == "report_created" for n in notifications))

        # 6. Vérifier le document de création
        documents = self.document_manager.get_documents_by_report(report["id"])
        self.assertTrue(any(d["type"] == "report_draft" for d in documents))

        # 7. Mettre à jour le statut du rapport
        updated = self.report_manager.update_report(report["id"], {
            "status": "review",
            "reviewer": "John Doe",
            "review_date": datetime.now().isoformat(),
            "review_notes": "En attente de validation"
        })

        # 8. Vérifier la mise à jour
        self.assertEqual(updated["status"], "review")
        self.assertEqual(updated["reviewer"], "John Doe")

        # 9. Vérifier la notification de mise à jour
        notifications = self.notification_manager.get_notifications_by_report(report["id"])
        self.assertTrue(any(n["type"] == "report_status_updated" for n in notifications))

        # 10. Vérifier le document de mise à jour
        documents = self.document_manager.get_documents_by_report(report["id"])
        self.assertTrue(any(d["type"] == "report_review" for d in documents))

        # 11. Finaliser le rapport
        completed = self.report_manager.update_report(report["id"], {
            "status": "completed",
            "approval_date": datetime.now().isoformat(),
            "approved_by": "John Doe",
            "version": "1.1",
            "content": {
                "summary": "Résumé final des réparations",
                "details": {
                    "total_repairs": 100,
                    "completed_repairs": 95,
                    "pending_repairs": 5
                },
                "charts": {
                    "repair_status": "https://aldersav.com/charts/repair-status-final.png"
                }
            }
        })

        # 12. Vérifier la finalisation
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["version"], "1.1")

        # 13. Vérifier la notification de finalisation
        notifications = self.notification_manager.get_notifications_by_report(report["id"])
        self.assertTrue(any(n["type"] == "report_completed" for n in notifications))

        # 14. Vérifier le document de finalisation
        documents = self.document_manager.get_documents_by_report(report["id"])
        self.assertTrue(any(d["type"] == "report_final" for d in documents))

        # 15. Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_report(report["id"])
        self.assertTrue(any(s["type"] == "report_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 