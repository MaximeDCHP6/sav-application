import unittest
from alder_sav.utils.imports import (
    import_data,
    validate_import_file,
    map_import_fields,
    get_import_template,
    list_import_templates
)

class TestImportManager(unittest.TestCase):
    """Tests unitaires pour la gestion des imports avancés."""

    def test_validate_import_file(self):
        self.assertTrue(validate_import_file("clients.csv"))
        self.assertFalse(validate_import_file("invalid.txt"))

    def test_map_import_fields(self):
        mapping = map_import_fields(["Nom", "Prénom", "Email"], ["last_name", "first_name", "email"])
        self.assertEqual(mapping["Nom"], "last_name")
        self.assertEqual(mapping["Prénom"], "first_name")

    def test_import_data(self):
        data = [
            {"Nom": "Dupont", "Prénom": "Jean", "Email": "jean.dupont@example.com"}
        ]
        mapping = {"Nom": "last_name", "Prénom": "first_name", "Email": "email"}
        result = import_data(data, mapping)
        self.assertTrue(result)

    def test_get_import_template(self):
        template = get_import_template("clients")
        self.assertIn("fields", template)
        self.assertIn("example", template)

    def test_list_import_templates(self):
        templates = list_import_templates()
        self.assertTrue(isinstance(templates, list))
        self.assertTrue(any("clients" in t["name"] for t in templates))

if __name__ == '__main__':
    unittest.main() 