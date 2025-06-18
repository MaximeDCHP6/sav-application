import unittest
from datetime import datetime
from alder_sav.models.documents import DocumentManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestIntegrationDocuments(unittest.TestCase):
    """Tests d'intégration pour la gestion des documents."""

    def setUp(self):
        self.document_manager = DocumentManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_create_document(self):
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

        # Créer un document
        document = self.document_manager.create_document({
            "type": "invoice",
            "status": "active",
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

        # Vérifier la création
        self.assertIsNotNone(document["id"])
        self.assertEqual(document["type"], "invoice")
        self.assertEqual(document["status"], "active")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_document(document["id"])
        self.assertTrue(any(n["type"] == "document_created" for n in notifications))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_document(document["id"])
        self.assertTrue(any(r["type"] == "document_summary" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_document(document["id"])
        self.assertTrue(any(s["type"] == "document_metrics" for s in stats))

    def test_update_document_status(self):
        # Créer un document
        document = self.document_manager.create_document({
            "type": "invoice",
            "status": "active",
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
            }
        })

        # Mettre à jour le statut
        updated = self.document_manager.update_document(document["id"], {"status": "archived"})
        self.assertEqual(updated["status"], "archived")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_document(document["id"])
        self.assertTrue(any(n["type"] == "document_status_updated" for n in notifications))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_document(document["id"])
        self.assertTrue(any(r["type"] == "document_status_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_document(document["id"])
        self.assertTrue(any(s["type"] == "document_status_metrics" for s in stats))

    def test_delete_document(self):
        # Créer un document
        document = self.document_manager.create_document({
            "type": "invoice",
            "status": "active",
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
            }
        })

        # Supprimer le document
        self.document_manager.delete_document(document["id"])

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_document(document["id"])
        self.assertTrue(any(n["type"] == "document_deleted" for n in notifications))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_document(document["id"])
        self.assertTrue(any(r["type"] == "document_deletion_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_document(document["id"])
        self.assertTrue(any(s["type"] == "document_deletion_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 