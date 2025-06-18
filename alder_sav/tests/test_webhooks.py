import unittest
from alder_sav.utils.webhooks import (
    send_webhook,
    validate_webhook_payload,
    get_webhook_config,
    list_webhook_configs
)

class TestWebhookManager(unittest.TestCase):
    """Tests unitaires pour la gestion des webhooks et intégrations externes."""

    def test_validate_webhook_payload(self):
        payload = {"event": "repair_created", "data": {"id": "REP-001"}}
        self.assertTrue(validate_webhook_payload(payload))
        self.assertFalse(validate_webhook_payload({"event": "repair_created"}))

    def test_send_webhook(self):
        result = send_webhook(url="https://webhook.site/test", payload={"event": "repair_created", "data": {"id": "REP-001"}})
        self.assertTrue(result)

    def test_get_webhook_config(self):
        config = get_webhook_config("repair_created")
        self.assertIn("url", config)
        self.assertIn("event", config)

    def test_list_webhook_configs(self):
        configs = list_webhook_configs()
        self.assertTrue(isinstance(configs, list))
        self.assertTrue(any("repair_created" in c["event"] for c in configs))

if __name__ == '__main__':
    unittest.main() 