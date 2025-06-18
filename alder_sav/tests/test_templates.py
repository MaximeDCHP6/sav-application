import unittest
from alder_sav.utils.templates import (
    render_template,
    validate_template,
    get_template,
    list_templates
)

class TestTemplateManager(unittest.TestCase):
    """Tests unitaires pour la gestion des templates."""

    def test_render_template(self):
        context = {"name": "Jean", "date": "2024-01-01"}
        result = render_template("welcome", context)
        self.assertIn("Jean", result)
        self.assertIn("2024-01-01", result)

    def test_validate_template(self):
        self.assertTrue(validate_template("welcome"))
        self.assertFalse(validate_template("invalid"))

    def test_get_template(self):
        template = get_template("welcome")
        self.assertIn("content", template)
        self.assertIn("name", template)

    def test_list_templates(self):
        templates = list_templates()
        self.assertTrue(isinstance(templates, list))
        self.assertTrue(any("welcome" in t["name"] for t in templates))

if __name__ == '__main__':
    unittest.main() 