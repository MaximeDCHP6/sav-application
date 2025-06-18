import unittest
from datetime import datetime
from alder_sav.models.statistics import StatisticsManager
from alder_sav.models.clients import ClientManager
from alder_sav.models.devices import DeviceManager
from alder_sav.models.documents import DocumentManager
from alder_sav.models.notifications import NotificationManager
from alder_sav.models.reports import ReportManager

class TestE2EStatisticsFlow(unittest.TestCase):
    """Tests end-to-end pour le flux complet des statistiques."""

    def setUp(self):
        self.statistics_manager = StatisticsManager()
        self.client_manager = ClientManager()
        self.device_manager = DeviceManager()
        self.document_manager = DocumentManager()
        self.notification_manager = NotificationManager()
        self.report_manager = ReportManager()

    def test_complete_statistics_flow(self):
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

        # 3. Créer des statistiques
        statistics = self.statistics_manager.create_statistics({
            "type": "repair_metrics",
            "period": {
                "start": datetime.now().isoformat(),
                "end": datetime.now().isoformat()
            },
            "metrics": {
                "repairs": {
                    "total": 100,
                    "completed": 90,
                    "pending": 10,
                    "average_time": 2.5,
                    "success_rate": 0.9
                },
                "warranties": {
                    "total": 50,
                    "active": 45,
                    "expired": 5,
                    "coverage_rate": 0.9
                },
                "clients": {
                    "total": 200,
                    "active": 180,
                    "new": 20,
                    "satisfaction_rate": 0.85
                },
                "financials": {
                    "total_revenue": 15000.00,
                    "average_repair_cost": 150.00,
                    "profit_margin": 0.3
                }
            },
            "trends": {
                "repairs": {
                    "daily": [10, 12, 15, 8, 11],
                    "weekly": [50, 55, 60, 45, 50],
                    "monthly": [200, 220, 240, 210, 230]
                },
                "revenue": {
                    "daily": [1000, 1200, 1500, 800, 1100],
                    "weekly": [5000, 5500, 6000, 4500, 5000],
                    "monthly": [20000, 22000, 24000, 21000, 23000]
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "system",
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
        self.assertIsNotNone(statistics["id"])
        self.assertEqual(statistics["type"], "repair_metrics")
        self.assertEqual(statistics["metrics"]["repairs"]["total"], 100)

        # 5. Vérifier la notification de création
        notifications = self.notification_manager.get_notifications_by_statistics(statistics["id"])
        self.assertTrue(any(n["type"] == "statistics_created" for n in notifications))

        # 6. Vérifier le document de création
        documents = self.document_manager.get_documents_by_statistics(statistics["id"])
        self.assertTrue(any(d["type"] == "statistics_report" for d in documents))

        # 7. Mettre à jour les statistiques
        updated = self.statistics_manager.update_statistics(statistics["id"], {
            "metrics": {
                "repairs": {
                    "total": 110,
                    "completed": 100,
                    "pending": 10,
                    "average_time": 2.3,
                    "success_rate": 0.91
                },
                "warranties": {
                    "total": 55,
                    "active": 50,
                    "expired": 5,
                    "coverage_rate": 0.91
                },
                "clients": {
                    "total": 210,
                    "active": 190,
                    "new": 20,
                    "satisfaction_rate": 0.86
                },
                "financials": {
                    "total_revenue": 16500.00,
                    "average_repair_cost": 150.00,
                    "profit_margin": 0.31
                }
            },
            "trends": {
                "repairs": {
                    "daily": [11, 13, 16, 9, 12],
                    "weekly": [55, 60, 65, 50, 55],
                    "monthly": [220, 240, 260, 230, 250]
                },
                "revenue": {
                    "daily": [1100, 1300, 1600, 900, 1200],
                    "weekly": [5500, 6000, 6500, 5000, 5500],
                    "monthly": [22000, 24000, 26000, 23000, 25000]
                }
            }
        })

        # 8. Vérifier la mise à jour
        self.assertEqual(updated["metrics"]["repairs"]["total"], 110)
        self.assertEqual(updated["metrics"]["repairs"]["success_rate"], 0.91)

        # 9. Vérifier la notification de mise à jour
        notifications = self.notification_manager.get_notifications_by_statistics(statistics["id"])
        self.assertTrue(any(n["type"] == "statistics_updated" for n in notifications))

        # 10. Vérifier le document de mise à jour
        documents = self.document_manager.get_documents_by_statistics(statistics["id"])
        self.assertTrue(any(d["type"] == "statistics_update" for d in documents))

        # 11. Générer un rapport basé sur les statistiques
        report = self.report_manager.create_report({
            "type": "statistics_summary",
            "status": "completed",
            "content": {
                "summary": "Résumé des statistiques",
                "details": updated["metrics"],
                "charts": {
                    "repair_trends": "https://aldersav.com/charts/repair-trends.png",
                    "revenue_trends": "https://aldersav.com/charts/revenue-trends.png"
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "author": "System",
                "version": "1.0"
            }
        })

        # 12. Vérifier le rapport
        self.assertEqual(report["type"], "statistics_summary")
        self.assertEqual(report["status"], "completed")

        # 13. Vérifier la notification du rapport
        notifications = self.notification_manager.get_notifications_by_report(report["id"])
        self.assertTrue(any(n["type"] == "report_created" for n in notifications))

        # 14. Vérifier le document du rapport
        documents = self.document_manager.get_documents_by_report(report["id"])
        self.assertTrue(any(d["type"] == "report_final" for d in documents))

if __name__ == '__main__':
    unittest.main() 