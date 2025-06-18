import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from alder_sav.models.claims import ClaimManager
from alder_sav.models.warranties import WarrantyManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.reports import ReportManager
from alder_sav.models.statistics import StatisticsManager

class TestE2EClaimFlow(unittest.TestCase):
    """Tests end-to-end pour le flux complet d'une réclamation."""

    def setUp(self):
        self.claim_manager = ClaimManager()
        self.warranty_manager = WarrantyManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.notification_manager = NotificationManager()
        self.document_manager = DocumentManager()
        self.report_manager = ReportManager()
        self.statistics_manager = StatisticsManager()

    def test_complete_claim_flow(self):
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

        # 4. Créer une réclamation
        claim = self.claim_manager.create_claim({
            "type": "warranty",
            "status": "pending",
            "device_id": device["id"],
            "client_id": client["id"],
            "warranty_id": warranty["id"],
            "description": "Écran LCD endommagé",
            "diagnosis": "Écran LCD endommagé",
            "resolution": "Remplacement de l'écran",
            "estimated_cost": Decimal("199.99")
        })

        # 5. Vérifier la création
        self.assertIsNotNone(claim["id"])
        self.assertEqual(claim["type"], "warranty")
        self.assertEqual(claim["status"], "pending")

        # 6. Vérifier la notification de création
        notifications = self.notification_manager.get_notifications_by_claim(claim["id"])
        self.assertTrue(any(n["type"] == "claim_created" for n in notifications))

        # 7. Vérifier le document de création
        documents = self.document_manager.get_documents_by_claim(claim["id"])
        self.assertTrue(any(d["type"] == "claim_form" for d in documents))

        # 8. Mettre à jour le statut de la réclamation
        updated = self.claim_manager.update_claim(claim["id"], {
            "status": "in_review",
            "reviewer": "John Doe",
            "review_date": datetime.now().isoformat(),
            "review_notes": "En attente de validation"
        })

        # 9. Vérifier la mise à jour
        self.assertEqual(updated["status"], "in_review")
        self.assertEqual(updated["reviewer"], "John Doe")

        # 10. Vérifier la notification de mise à jour
        notifications = self.notification_manager.get_notifications_by_claim(claim["id"])
        self.assertTrue(any(n["type"] == "claim_status_updated" for n in notifications))

        # 11. Vérifier le document de mise à jour
        documents = self.document_manager.get_documents_by_claim(claim["id"])
        self.assertTrue(any(d["type"] == "claim_status_update" for d in documents))

        # 12. Finaliser la réclamation
        completed = self.claim_manager.update_claim(claim["id"], {
            "status": "approved",
            "approval_date": datetime.now().isoformat(),
            "approved_by": "John Doe",
            "approved_amount": Decimal("199.99"),
            "payment_status": "pending"
        })

        # 13. Vérifier la finalisation
        self.assertEqual(completed["status"], "approved")
        self.assertEqual(completed["approved_amount"], Decimal("199.99"))
        self.assertEqual(completed["payment_status"], "pending")

        # 14. Vérifier la notification de finalisation
        notifications = self.notification_manager.get_notifications_by_claim(claim["id"])
        self.assertTrue(any(n["type"] == "claim_approved" for n in notifications))

        # 15. Vérifier le document de finalisation
        documents = self.document_manager.get_documents_by_claim(claim["id"])
        self.assertTrue(any(d["type"] == "claim_approval" for d in documents))

        # 16. Vérifier le rapport final
        reports = self.report_manager.get_reports_by_claim(claim["id"])
        self.assertTrue(any(r["type"] == "claim_summary" for r in reports))

        # 17. Vérifier les statistiques
        stats = self.statistics_manager.get_statistics_by_claim(claim["id"])
        self.assertTrue(any(s["type"] == "claim_metrics" for s in stats))

if __name__ == '__main__':
    unittest.main() 