import unittest
from alder_sav.utils.sys_notifications import (
    send_push_notification,
    send_websocket_notification,
    validate_notification_payload,
    get_notification_channel,
    list_notification_channels
)

class TestSysNotificationManager(unittest.TestCase):
    """Tests unitaires pour la gestion des notifications système avancées."""

    def test_validate_notification_payload(self):
        payload = {"title": "Test", "message": "Ceci est un test."}
        self.assertTrue(validate_notification_payload(payload))
        self.assertFalse(validate_notification_payload({"title": "Test"}))

    def test_send_push_notification(self):
        result = send_push_notification(user_id="USR-001", title="Test", message="Ceci est un test.")
        self.assertTrue(result)

    def test_send_websocket_notification(self):
        result = send_websocket_notification(channel="repairs", data={"status": "updated"})
        self.assertTrue(result)

    def test_get_notification_channel(self):
        channel = get_notification_channel("repairs")
        self.assertIn("name", channel)
        self.assertIn("type", channel)

    def test_list_notification_channels(self):
        channels = list_notification_channels()
        self.assertTrue(isinstance(channels, list))
        self.assertTrue(any("repairs" in c["name"] for c in channels))

if __name__ == '__main__':
    unittest.main() 