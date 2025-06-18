import unittest
from alder_sav.utils.emails import (
    send_email,
    validate_email,
    format_email,
    get_email_template,
    list_email_templates
)

class TestEmailManager(unittest.TestCase):
    """Tests unitaires pour la gestion des emails."""

    def test_validate_email(self):
        self.assertTrue(validate_email("test@example.com"))
        self.assertFalse(validate_email("invalid-email"))

    def test_format_email(self):
        self.assertEqual(format_email("Jean.Dupont@Example.com"), "jean.dupont@example.com")
        self.assertEqual(format_email("Jean.Dupont@Example.com", domain="aldersav.com"), "jean.dupont@aldersav.com")

    def test_send_email(self):
        result = send_email(to="test@example.com", subject="Test", body="Ceci est un test.")
        self.assertTrue(result)

    def test_get_email_template(self):
        template = get_email_template("repair_status")
        self.assertIn("subject", template)
        self.assertIn("body", template)

    def test_list_email_templates(self):
        templates = list_email_templates()
        self.assertTrue(isinstance(templates, list))
        self.assertTrue(any("repair_status" in t["name"] for t in templates))

if __name__ == '__main__':
    unittest.main() 