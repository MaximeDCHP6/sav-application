import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from alder_sav.models.statistics import StatisticsManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.reports import ReportManager

class TestIntegrationStatistics(unittest.TestCase):
    """Tests d'intégration pour la gestion des statistiques."""

    def setUp(self):
        self.statistics_manager = StatisticsManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.document_manager = DocumentManager()
        self.notification_manager = NotificationManager()
        self.report_manager = ReportManager()

    def test_create_statistics(self):
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

        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics({
            "type": "repair_metrics",
            "period": {
                "start": datetime.now().isoformat(),
                "end": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "metrics": {
                "repairs": {
                    "total": 100,
                    "completed": 90,
                    "pending": 10,
                    "cancelled": 0
                },
                "warranties": {
                    "total": 50,
                    "active": 45,
                    "expired": 5
                },
                "clients": {
                    "total": 200,
                    "active": 180,
                    "inactive": 20
                },
                "financials": {
                    "total_revenue": Decimal("15000.00"),
                    "total_costs": Decimal("10000.00"),
                    "profit": Decimal("5000.00")
                }
            },
            "trends": {
                "repairs": {
                    "daily": [10, 15, 20, 25, 30],
                    "weekly": [100, 150, 200, 250, 300],
                    "monthly": [1000, 1500, 2000, 2500, 3000]
                },
                "revenue": {
                    "daily": [Decimal("1000.00"), Decimal("1500.00"), Decimal("2000.00")],
                    "weekly": [Decimal("10000.00"), Decimal("15000.00"), Decimal("20000.00")],
                    "monthly": [Decimal("100000.00"), Decimal("150000.00"), Decimal("200000.00")]
                }
            }
        })

        # Vérifier la création
        self.assertIsNotNone(statistics["id"])
        self.assertEqual(statistics["type"], "repair_metrics")

        # Vérifier le document
        documents = self.document_manager.get_documents_by_statistics(statistics["id"])
        self.assertTrue(any(d["type"] == "statistics_report" for d in documents))

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_statistics(statistics["id"])
        self.assertTrue(any(n["type"] == "statistics_updated" for n in notifications))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_statistics(statistics["id"])
        self.assertTrue(any(r["type"] == "statistics_summary" for r in reports))

    def test_update_statistics(self):
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics({
            "type": "repair_metrics",
            "period": {
                "start": datetime.now().isoformat(),
                "end": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "metrics": {
                "repairs": {
                    "total": 100,
                    "completed": 90,
                    "pending": 10,
                    "cancelled": 0
                }
            }
        })

        # Mettre à jour les statistiques
        updated = self.statistics_manager.update_statistics(statistics["id"], {
            "metrics": {
                "repairs": {
                    "total": 110,
                    "completed": 100,
                    "pending": 10,
                    "cancelled": 0
                }
            }
        })

        # Vérifier la mise à jour
        self.assertEqual(updated["metrics"]["repairs"]["total"], 110)
        self.assertEqual(updated["metrics"]["repairs"]["completed"], 100)

        # Vérifier le document
        documents = self.document_manager.get_documents_by_statistics(statistics["id"])
        self.assertTrue(any(d["type"] == "statistics_update" for d in documents))

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_statistics(statistics["id"])
        self.assertTrue(any(n["type"] == "statistics_updated" for n in notifications))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_statistics(statistics["id"])
        self.assertTrue(any(r["type"] == "statistics_update_report" for r in reports))

    def test_delete_statistics(self):
        # Créer des statistiques
        statistics = self.statistics_manager.create_statistics({
            "type": "repair_metrics",
            "period": {
                "start": datetime.now().isoformat(),
                "end": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "metrics": {
                "repairs": {
                    "total": 100,
                    "completed": 90,
                    "pending": 10,
                    "cancelled": 0
                }
            }
        })

        # Supprimer les statistiques
        self.statistics_manager.delete_statistics(statistics["id"])

        # Vérifier le document
        documents = self.document_manager.get_documents_by_statistics(statistics["id"])
        self.assertTrue(any(d["type"] == "statistics_deletion" for d in documents))

        # Vérifier la notification
        notifications = self.notification_manager.get_notifications_by_statistics(statistics["id"])
        self.assertTrue(any(n["type"] == "statistics_deleted" for n in notifications))

        # Vérifier le rapport
        reports = self.report_manager.get_reports_by_statistics(statistics["id"])
        self.assertTrue(any(r["type"] == "statistics_deletion_report" for r in reports))

if __name__ == '__main__':
    unittest.main() 