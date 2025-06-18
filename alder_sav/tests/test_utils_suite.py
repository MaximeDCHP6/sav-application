import unittest
from datetime import datetime
from decimal import Decimal
from alder_sav.utils.utils import (
    format_name, validate_name,
    format_postal_code, validate_postal_code,
    format_imei, validate_imei,
    format_serial_number, validate_serial_number,
    format_mac_address, validate_mac_address,
    format_ip_address, validate_ip_address,
    format_url, validate_url,
    format_password, validate_password,
    format_username, validate_username,
    format_role, validate_role,
    format_permission, validate_permission,
    format_status, validate_status,
    format_type, validate_type,
    format_category, validate_category,
    format_tag, validate_tag,
    format_version, validate_version,
    format_uuid, validate_uuid,
    format_hash, validate_hash,
    format_token, validate_token
)

class TestUtilsSuite(unittest.TestCase):
    """Tests complémentaires pour les utilitaires avancés."""

    def test_format_and_validate_name(self):
        self.assertEqual(format_name("jean dupont"), "Jean Dupont")
        self.assertTrue(validate_name("Jean Dupont"))
        self.assertFalse(validate_name("J"))

    def test_format_and_validate_postal_code(self):
        self.assertEqual(format_postal_code("75000"), "75000")
        self.assertTrue(validate_postal_code("75000"))
        self.assertFalse(validate_postal_code("123"))

    def test_format_and_validate_imei(self):
        self.assertEqual(format_imei("490154203237518"), "490154203237518")
        self.assertTrue(validate_imei("490154203237518"))
        self.assertFalse(validate_imei("12345678901234"))

    def test_format_and_validate_serial_number(self):
        self.assertEqual(format_serial_number("SN1234567890"), "SN1234567890")
        self.assertTrue(validate_serial_number("SN1234567890"))
        self.assertFalse(validate_serial_number("SN12"))

    def test_format_and_validate_mac_address(self):
        self.assertEqual(format_mac_address("00:1A:2B:3C:4D:5E"), "00:1A:2B:3C:4D:5E")
        self.assertTrue(validate_mac_address("00:1A:2B:3C:4D:5E"))
        self.assertFalse(validate_mac_address("00:1A:2B:3C:4D"))

    def test_format_and_validate_ip_address(self):
        self.assertEqual(format_ip_address("192.168.1.1"), "192.168.1.1")
        self.assertTrue(validate_ip_address("192.168.1.1"))
        self.assertFalse(validate_ip_address("999.999.999.999"))

    def test_format_and_validate_url(self):
        self.assertEqual(format_url("https://aldersav.com"), "https://aldersav.com")
        self.assertTrue(validate_url("https://aldersav.com"))
        self.assertFalse(validate_url("aldersav"))

    def test_format_and_validate_password(self):
        self.assertTrue(validate_password("Abcdef1!"))
        self.assertFalse(validate_password("abc"))

    def test_format_and_validate_username(self):
        self.assertEqual(format_username("Jean.Dupont"), "jean.dupont")
        self.assertTrue(validate_username("jean.dupont"))
        self.assertFalse(validate_username("j"))

    def test_format_and_validate_role(self):
        self.assertEqual(format_role("Technician"), "technician")
        self.assertTrue(validate_role("technician"))
        self.assertFalse(validate_role("unknown"))

    def test_format_and_validate_permission(self):
        self.assertEqual(format_permission("view_repairs"), "view_repairs")
        self.assertTrue(validate_permission("view_repairs"))
        self.assertFalse(validate_permission("invalid_permission"))

    def test_format_and_validate_status(self):
        self.assertEqual(format_status("Active"), "active")
        self.assertTrue(validate_status("active"))
        self.assertFalse(validate_status("unknown"))

    def test_format_and_validate_type(self):
        self.assertEqual(format_type("System"), "system")
        self.assertTrue(validate_type("system"))
        self.assertFalse(validate_type("invalid"))

    def test_format_and_validate_category(self):
        self.assertEqual(format_category("General"), "general")
        self.assertTrue(validate_category("general"))
        self.assertFalse(validate_category("invalid"))

    def test_format_and_validate_tag(self):
        self.assertEqual(format_tag("sav"), "sav")
        self.assertTrue(validate_tag("sav"))
        self.assertFalse(validate_tag("") )

    def test_format_and_validate_version(self):
        self.assertEqual(format_version("1.0.0"), "1.0.0")
        self.assertTrue(validate_version("1.0.0"))
        self.assertFalse(validate_version("1"))

    def test_format_and_validate_uuid(self):
        uuid = format_uuid("123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(uuid, "123e4567-e89b-12d3-a456-426614174000")
        self.assertTrue(validate_uuid(uuid))
        self.assertFalse(validate_uuid("invalid-uuid"))

    def test_format_and_validate_hash(self):
        hash_val = format_hash("abc123")
        self.assertEqual(hash_val, "abc123")
        self.assertTrue(validate_hash("abc123"))
        self.assertFalse(validate_hash(""))

    def test_format_and_validate_token(self):
        token = format_token("tok_123456")
        self.assertEqual(token, "tok_123456")
        self.assertTrue(validate_token("tok_123456"))
        self.assertFalse(validate_token(""))

if __name__ == '__main__':
    unittest.main() 