import unittest
from datetime import datetime
from alder_sav.models.documents import DocumentManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestE2EDocumentFlow(unittest.TestCase):
    """Tests end-to-end pour le flux complet d'un document."""

    def setUp(self):
        self.document_manager = DocumentManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_complete_document_flow(self):
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

        # 3. Créer un document
        document = self.document_manager.create_document({
            "type": "invoice",
            "status": "draft",
            "category": "financial",
            "title": "Facture #12345",
            "content": {
                "url": "https://aldersav.com/documents/invoice-12345.pdf"
            },
            "metadata": {
                "author": "System",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0",
                "language": "fr",
                "tags": ["facture", "client"]
            },
            "related_entities": {
                "client_id": client["id"],
                "device_id": device["id"]
            }
        })

        # 4. Vérifier la création
        self.assertIsNotNone(document["id"])
        self.assertEqual(document["type"], "invoice")
        self.assertEqual(document["status"], "draft")

        # 5. Vérifier la notification de création
        notifications = self.notification_manager.get_notifications_by_document(document["id"])
        self.assertTrue(any(n["type"] == "document_created" for n in notifications))

        # 6. Mettre à jour le statut du document
        updated = self.document_manager.update_document(document["id"], {
            "status": "review",
            "reviewer": "John Doe",
            "review_date": datetime.now().isoformat(),
            "review_notes": "En attente de validation"
        })

        # 7. Vérifier la mise à jour
        self.assertEqual(updated["status"], "review")
        self.assertEqual(updated["reviewer"], "John Doe")

        # 8. Vérifier la notification de mise à jour
        notifications = self.notification_manager.get_notifications_by_document(document["id"])
        self.assertTrue(any(n["type"] == "document_status_updated" for n in notifications))

        # 9. Finaliser le document
        completed = self.document_manager.update_document(document["id"], {
            "status": "active",
            "approval_date": datetime.now().isoformat(),
            "approved_by": "John Doe",
            "version": "1.1",
            "content": {
                "url": "https://aldersav.com/documents/invoice-12345-v1.1.pdf"
            }
        })

        # 10. Vérifier la finalisation
        self.assertEqual(completed["status"], "active")
        self.assertEqual(completed["version"], "1.1")

        # 11. Vérifier la notification de finalisation
        notifications = self.notification_manager.get_notifications_by_document(document["id"])
        self.assertTrue(any(n["type"] == "document_activated" for n in notifications))

        # 12. Vérifier le rapport final
        reports = self.report_manager.get_reports_by_document(document["id"])
        self.assertTrue(any(r["type"] == "document_summary" for r in reports))

        # 13. Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_document(document["id"])
        self.assertTrue(any(s["type"] == "document_metrics" for s in stats))

        # 14. Archiver le document
        archived = self.document_manager.update_document(document["id"], {
            "status": "archived",
            "archive_date": datetime.now().isoformat(),
            "archived_by": "John Doe",
            "archive_reason": "Document obsolète"
        })

        # 15. Vérifier l'archivage
        self.assertEqual(archived["status"], "archived")
        self.assertEqual(archived["archived_by"], "John Doe")

        # 16. Vérifier la notification d'archivage
        notifications = self.notification_manager.get_notifications_by_document(document["id"])
        self.assertTrue(any(n["type"] == "document_archived" for n in notifications))

if __name__ == '__main__':
    unittest.main() 