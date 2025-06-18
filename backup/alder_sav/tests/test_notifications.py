import unittest
import time
from datetime import datetime, timedelta
from decimal import Decimal
from alder_sav.utils.notifications import NotificationManager
from alder_sav.utils.exceptions import NotificationError

class TestNotificationManager(unittest.TestCase):
    """Tests pour le gestionnaire de notifications."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.notification_manager = NotificationManager()

    def test_create_notification(self):
        """Test de création de notification."""
        # Créer une notification
        notification = self.notification_manager.create_notification(
            type="email",
            recipient="user@example.com",
            subject="Test Notification",
            content="This is a test notification",
            priority="high"
        )
        
        # Vérifier la notification
        self.assertIsNotNone(notification["id"])
        self.assertEqual(notification["type"], "email")
        self.assertEqual(notification["recipient"], "user@example.com")
        self.assertEqual(notification["subject"], "Test Notification")
        self.assertEqual(notification["content"], "This is a test notification")
        self.assertEqual(notification["priority"], "high")
        self.assertEqual(notification["status"], "pending")

    def test_get_notification(self):
        """Test de récupération de notification."""
        # Créer une notification
        notification = self.notification_manager.create_notification(
            type="email",
            recipient="user@example.com",
            subject="Test Notification",
            content="This is a test notification"
        )
        
        # Récupérer la notification
        retrieved_notification = self.notification_manager.get_notification(notification["id"])
        
        # Vérifier la récupération
        self.assertEqual(retrieved_notification, notification)

    def test_update_notification(self):
        """Test de mise à jour de notification."""
        # Créer une notification
        notification = self.notification_manager.create_notification(
            type="email",
            recipient="user@example.com",
            subject="Test Notification",
            content="This is a test notification"
        )
        
        # Mettre à jour la notification
        updated_notification = self.notification_manager.update_notification(
            notification["id"],
            status="sent",
            sent_at=datetime.now().isoformat()
        )
        
        # Vérifier la mise à jour
        self.assertEqual(updated_notification["status"], "sent")
        self.assertIsNotNone(updated_notification["sent_at"])

    def test_delete_notification(self):
        """Test de suppression de notification."""
        # Créer une notification
        notification = self.notification_manager.create_notification(
            type="email",
            recipient="user@example.com",
            subject="Test Notification",
            content="This is a test notification"
        )
        
        # Supprimer la notification
        self.notification_manager.delete_notification(notification["id"])
        
        # Vérifier la suppression
        with self.assertRaises(NotificationError):
            self.notification_manager.get_notification(notification["id"])

    def test_get_notifications_by_type(self):
        """Test de récupération des notifications par type."""
        # Créer des notifications de différents types
        self.notification_manager.create_notification(
            type="email",
            recipient="user1@example.com",
            subject="Email Notification",
            content="This is an email notification"
        )
        self.notification_manager.create_notification(
            type="sms",
            recipient="+1234567890",
            subject="SMS Notification",
            content="This is an SMS notification"
        )
        
        # Récupérer les notifications par type
        email_notifications = self.notification_manager.get_notifications_by_type("email")
        sms_notifications = self.notification_manager.get_notifications_by_type("sms")
        
        # Vérifier les résultats
        self.assertEqual(len(email_notifications), 1)
        self.assertEqual(len(sms_notifications), 1)
        self.assertEqual(email_notifications[0]["type"], "email")
        self.assertEqual(sms_notifications[0]["type"], "sms")

    def test_get_notifications_by_status(self):
        """Test de récupération des notifications par statut."""
        # Créer des notifications avec différents statuts
        notification1 = self.notification_manager.create_notification(
            type="email",
            recipient="user1@example.com",
            subject="Pending Notification",
            content="This is a pending notification"
        )
        notification2 = self.notification_manager.create_notification(
            type="email",
            recipient="user2@example.com",
            subject="Sent Notification",
            content="This is a sent notification"
        )
        
        # Mettre à jour le statut de la deuxième notification
        self.notification_manager.update_notification(
            notification2["id"],
            status="sent",
            sent_at=datetime.now().isoformat()
        )
        
        # Récupérer les notifications par statut
        pending_notifications = self.notification_manager.get_notifications_by_status("pending")
        sent_notifications = self.notification_manager.get_notifications_by_status("sent")
        
        # Vérifier les résultats
        self.assertEqual(len(pending_notifications), 1)
        self.assertEqual(len(sent_notifications), 1)
        self.assertEqual(pending_notifications[0]["status"], "pending")
        self.assertEqual(sent_notifications[0]["status"], "sent")

    def test_get_notifications_by_recipient(self):
        """Test de récupération des notifications par destinataire."""
        # Créer des notifications pour différents destinataires
        self.notification_manager.create_notification(
            type="email",
            recipient="user1@example.com",
            subject="Notification 1",
            content="This is notification 1"
        )
        self.notification_manager.create_notification(
            type="email",
            recipient="user1@example.com",
            subject="Notification 2",
            content="This is notification 2"
        )
        
        # Récupérer les notifications par destinataire
        recipient_notifications = self.notification_manager.get_notifications_by_recipient("user1@example.com")
        
        # Vérifier les résultats
        self.assertEqual(len(recipient_notifications), 2)
        self.assertTrue(all(n["recipient"] == "user1@example.com" for n in recipient_notifications))

    def test_send_notification(self):
        """Test d'envoi de notification."""
        # Créer une notification
        notification = self.notification_manager.create_notification(
            type="email",
            recipient="user@example.com",
            subject="Test Notification",
            content="This is a test notification"
        )
        
        # Envoyer la notification
        sent_notification = self.notification_manager.send_notification(notification["id"])
        
        # Vérifier l'envoi
        self.assertEqual(sent_notification["status"], "sent")
        self.assertIsNotNone(sent_notification["sent_at"])

    def test_send_bulk_notifications(self):
        """Test d'envoi en masse de notifications."""
        # Créer plusieurs notifications
        notifications = []
        for i in range(3):
            notification = self.notification_manager.create_notification(
                type="email",
                recipient=f"user{i}@example.com",
                subject=f"Bulk Notification {i}",
                content=f"This is bulk notification {i}"
            )
            notifications.append(notification)
        
        # Envoyer les notifications en masse
        results = self.notification_manager.send_bulk_notifications([n["id"] for n in notifications])
        
        # Vérifier les résultats
        self.assertEqual(results["success"], 3)
        self.assertEqual(results["failed"], 0)

    def test_schedule_notification(self):
        """Test de planification de notification."""
        # Créer une notification
        notification = self.notification_manager.create_notification(
            type="email",
            recipient="user@example.com",
            subject="Scheduled Notification",
            content="This is a scheduled notification"
        )
        
        # Planifier la notification
        scheduled_time = (datetime.now() + timedelta(minutes=5)).isoformat()
        scheduled_notification = self.notification_manager.schedule_notification(
            notification["id"],
            scheduled_time
        )
        
        # Vérifier la planification
        self.assertEqual(scheduled_notification["status"], "scheduled")
        self.assertEqual(scheduled_notification["scheduled_time"], scheduled_time)

    def test_cancel_notification(self):
        """Test d'annulation de notification."""
        # Créer et planifier une notification
        notification = self.notification_manager.create_notification(
            type="email",
            recipient="user@example.com",
            subject="Scheduled Notification",
            content="This is a scheduled notification"
        )
        scheduled_time = (datetime.now() + timedelta(minutes=5)).isoformat()
        self.notification_manager.schedule_notification(notification["id"], scheduled_time)
        
        # Annuler la notification
        cancelled_notification = self.notification_manager.cancel_notification(notification["id"])
        
        # Vérifier l'annulation
        self.assertEqual(cancelled_notification["status"], "cancelled")

    def test_get_notification_templates(self):
        """Test de récupération des templates de notification."""
        # Créer un template
        template = self.notification_manager.create_notification_template(
            name="welcome_email",
            subject="Welcome to Our Service",
            content="Welcome, {{name}}! Thank you for joining our service."
        )
        
        # Récupérer les templates
        templates = self.notification_manager.get_notification_templates()
        
        # Vérifier les résultats
        self.assertTrue(any(t["name"] == "welcome_email" for t in templates))

    def test_create_notification_template(self):
        """Test de création de template de notification."""
        # Créer un template
        template = self.notification_manager.create_notification_template(
            name="welcome_email",
            subject="Welcome to Our Service",
            content="Welcome, {{name}}! Thank you for joining our service."
        )
        
        # Vérifier le template
        self.assertIsNotNone(template["id"])
        self.assertEqual(template["name"], "welcome_email")
        self.assertEqual(template["subject"], "Welcome to Our Service")
        self.assertEqual(template["content"], "Welcome, {{name}}! Thank you for joining our service.")

    def test_update_notification_template(self):
        """Test de mise à jour de template de notification."""
        # Créer un template
        template = self.notification_manager.create_notification_template(
            name="welcome_email",
            subject="Welcome to Our Service",
            content="Welcome, {{name}}! Thank you for joining our service."
        )
        
        # Mettre à jour le template
        updated_template = self.notification_manager.update_notification_template(
            template["id"],
            subject="Welcome to Our Amazing Service",
            content="Welcome, {{name}}! We're excited to have you on board."
        )
        
        # Vérifier la mise à jour
        self.assertEqual(updated_template["subject"], "Welcome to Our Amazing Service")
        self.assertEqual(updated_template["content"], "Welcome, {{name}}! We're excited to have you on board.")

    def test_delete_notification_template(self):
        """Test de suppression de template de notification."""
        # Créer un template
        template = self.notification_manager.create_notification_template(
            name="welcome_email",
            subject="Welcome to Our Service",
            content="Welcome, {{name}}! Thank you for joining our service."
        )
        
        # Supprimer le template
        self.notification_manager.delete_notification_template(template["id"])
        
        # Vérifier la suppression
        templates = self.notification_manager.get_notification_templates()
        self.assertFalse(any(t["id"] == template["id"] for t in templates))

if __name__ == '__main__':
    unittest.main() 