import unittest
from datetime import datetime
from alder_sav.models.claims import ClaimManager
from alder_sav.models.warranties import WarrantyManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestIntegrationClaims(unittest.TestCase):
    """Tests d'intégration pour la gestion des réclamations."""

    def setUp(self):
        self.claim_manager = ClaimManager()
        self.warranty_manager = WarrantyManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_create_claim(self):
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

        # Créer une réclamation
        claim = self.claim_manager.create_claim({
            "type": "warranty",
            "status": "pending",
            "device_id": device["id"],
            "client_id": client["id"],
            "warranty_id": warranty["id"],
            "description": "Écran LCD endommagé",
            "diagnosis": "Écran LCD endommagé",
            "resolution": "Remplacement de l'écran",
            "estimated_cost": 199.99
        })

        # Vérifier la création
        self.assertIsNotNone(claim["id"])
        self.assertEqual(claim["type"], "warranty")
        self.assertEqual(claim["status"], "pending")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_claim(claim["id"])
        self.assertTrue(any(n["type"] == "claim_created" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_claim(claim["id"])
        self.assertTrue(any(d["type"] == "claim_form" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_claim(claim["id"])
        self.assertTrue(any(r["type"] == "claim_summary" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_claim(claim["id"])
        self.assertTrue(any(s["type"] == "claim_metrics" for s in stats))

    def test_update_claim_status(self):
        # Créer une réclamation
        claim = self.claim_manager.create_claim({
            "type": "warranty",
            "status": "pending",
            "device_id": "DEV-001",
            "client_id": "CLT-001",
            "description": "Écran LCD endommagé",
            "diagnosis": "Écran LCD endommagé",
            "resolution": "Remplacement de l'écran",
            "estimated_cost": 199.99
        })

        # Mettre à jour le statut
        updated = self.claim_manager.update_claim(claim["id"], {"status": "in_progress"})
        self.assertEqual(updated["status"], "in_progress")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_claim(claim["id"])
        self.assertTrue(any(n["type"] == "claim_status_updated" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_claim(claim["id"])
        self.assertTrue(any(d["type"] == "claim_status_update" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_claim(claim["id"])
        self.assertTrue(any(r["type"] == "claim_status_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_claim(claim["id"])
        self.assertTrue(any(s["type"] == "claim_status_metrics" for s in stats))

    def test_cancel_claim(self):
        # Créer une réclamation
        claim = self.claim_manager.create_claim({
            "type": "warranty",
            "status": "pending",
            "device_id": "DEV-001",
            "client_id": "CLT-001",
            "description": "Écran LCD endommagé",
            "diagnosis": "Écran LCD endommagé",
            "resolution": "Remplacement de l'écran",
            "estimated_cost": 199.99
        })

        # Annuler la réclamation
        cancelled = self.claim_manager.cancel_claim(claim["id"])
        self.assertEqual(cancelled["status"], "cancelled")

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_claim(claim["id"])
        self.assertTrue(any(n["type"] == "claim_cancelled" for n in notifications))

        # Vérifier le document
        documents = self.document_manager.get_documents_by_claim(claim["id"])
        self.assertTrue(any(d["type"] == "claim_cancellation" for d in documents))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_claim(claim["id"])
        self.assertTrue(any(r["type"] == "claim_cancellation_report" for r in reports))

        # Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_claim(claim["id"])
        self.assertTrue(any(s["type"] == "claim_cancellation_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 