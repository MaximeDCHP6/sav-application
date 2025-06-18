import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import tempfile
import shutil
import os
import json

from alder_sav.utils.helpers import (
    generate_id, generate_password, hash_password, verify_password,
    format_date, parse_date, format_number, parse_number,
    format_currency, parse_currency,
    validate_email, validate_phone, validate_postal_code,
    validate_siret, validate_siren, validate_vat,
    validate_iban, validate_bic, validate_url,
    validate_ip, validate_mac, validate_hex_color,
    validate_file_extension, validate_file_size, validate_file_type,
    validate_json, validate_xml, validate_yaml,
    validate_csv, validate_ini, validate_toml,
    validate_html, validate_markdown, validate_regex,
    validate_date_range, validate_number_range,
    validate_string_length, validate_list_length,
    validate_dict_keys, validate_dict_values,
    validate_enum
)
from alder_sav.utils.exceptions import ValidationError, FormatError
from alder_sav.utils.utils import (
    generate_reference,
    format_phone,
    parse_phone,
    format_email,
    format_address,
    validate_address,
    format_name,
    validate_name,
    format_postal_code,
    validate_postal_code,
    format_country,
    validate_country,
    format_imei,
    validate_imei,
    format_serial_number,
    validate_serial_number,
    format_mac_address,
    validate_mac_address,
    format_ip_address,
    validate_ip_address,
    format_url,
    validate_url,
    format_password,
    validate_password,
    format_username,
    validate_username,
    format_role,
    validate_role,
    format_permission,
    validate_permission,
    format_status,
    validate_status,
    format_type,
    validate_type,
    format_category,
    validate_category,
    format_tag,
    validate_tag,
    format_version,
    validate_version,
    format_uuid,
    validate_uuid,
    format_hash,
    validate_hash,
    format_token,
    validate_token,
    format_signature,
    validate_signature,
    format_certificate,
    validate_certificate,
    format_key,
    validate_key,
    format_secret,
    validate_secret,
    format_credential,
    validate_credential,
    format_identity,
    validate_identity,
    format_authorization,
    validate_authorization,
    format_authentication,
    validate_authentication,
    format_session,
    validate_session,
    format_cookie,
    validate_cookie,
    format_header,
    validate_header,
    format_parameter,
    validate_parameter,
    format_query,
    validate_query,
    format_path,
    validate_path,
    format_method,
    validate_method,
    format_protocol,
    validate_protocol,
    format_port,
    validate_port,
    format_host,
    validate_host,
    format_domain,
    validate_domain,
    format_subdomain,
    validate_subdomain,
    format_tld,
    validate_tld,
    format_dns,
    validate_dns,
    format_mx,
    validate_mx,
    format_spf,
    validate_spf,
    format_dkim,
    validate_dkim,
    format_dmarc,
    validate_dmarc,
    format_ssl,
    validate_ssl,
    format_tls,
    validate_tls,
    format_cert,
    validate_cert,
    format_csr,
    validate_csr,
    format_crl,
    validate_crl,
    format_ocsp,
    validate_ocsp,
    format_ca,
    validate_ca,
    format_ra,
    validate_ra,
    format_va,
    validate_va,
    format_pa,
    validate_pa,
    format_ta,
    validate_ta,
    format_ea,
    validate_ea,
    format_ma,
    validate_ma,
    format_sa,
    validate_sa,
    format_ia,
    validate_ia,
    format_oa,
    validate_oa,
    format_ua,
    validate_ua,
    format_ga,
    validate_ga,
    format_ha,
    validate_ha,
    format_ja,
    validate_ja,
    format_ka,
    validate_ka,
    format_la,
    validate_la,
    format_ma,
    validate_ma,
    format_na,
    validate_na,
    format_oa,
    validate_oa,
    format_pa,
    validate_pa,
    format_qa,
    validate_qa,
    format_ra,
    validate_ra,
    format_sa,
    validate_sa,
    format_ta,
    validate_ta,
    format_ua,
    validate_ua,
    format_va,
    validate_va,
    format_wa,
    validate_wa,
    format_xa,
    validate_xa,
    format_ya,
    validate_ya,
    format_za,
    validate_za
)

class TestHelpers(unittest.TestCase):
    """Tests unitaires pour les fonctions d'aide."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_generate_id(self):
        """Test de génération d'identifiant."""
        # Test sans préfixe
        id1 = generate_id()
        self.assertIsInstance(id1, str)
        self.assertEqual(len(id1), 32)

        # Test avec préfixe
        id2 = generate_id("TEST-")
        self.assertIsInstance(id2, str)
        self.assertTrue(id2.startswith("TEST-"))
        self.assertEqual(len(id2), 37)

    def test_generate_password(self):
        """Test de génération de mot de passe."""
        # Test longueur par défaut
        password1 = generate_password()
        self.assertIsInstance(password1, str)
        self.assertEqual(len(password1), 12)

        # Test longueur personnalisée
        password2 = generate_password(16)
        self.assertIsInstance(password2, str)
        self.assertEqual(len(password2), 16)

    def test_hash_password(self):
        """Test de hachage de mot de passe."""
        password = "test_password"
        
        # Test sans sel
        hashed1, salt1 = hash_password(password)
        self.assertIsInstance(hashed1, str)
        self.assertIsInstance(salt1, str)
        self.assertEqual(len(hashed1), 64)
        self.assertEqual(len(salt1), 64)

        # Test avec sel
        salt2 = "test_salt"
        hashed2, salt2 = hash_password(password, salt2)
        self.assertIsInstance(hashed2, str)
        self.assertIsInstance(salt2, str)
        self.assertEqual(len(hashed2), 64)
        self.assertEqual(salt2, "test_salt")

    def test_verify_password(self):
        """Test de vérification de mot de passe."""
        password = "test_password"
        hashed, salt = hash_password(password)
        
        # Test mot de passe correct
        self.assertTrue(verify_password(password, hashed, salt))
        
        # Test mot de passe incorrect
        self.assertFalse(verify_password("wrong_password", hashed, salt))

    def test_format_date(self):
        """Test de formatage de date."""
        date = datetime(2024, 1, 1)
        
        # Test format par défaut
        self.assertEqual(format_date(date), "01/01/2024")
        
        # Test format personnalisé
        self.assertEqual(format_date(date, "%Y-%m-%d"), "2024-01-01")
        
        # Test avec chaîne
        self.assertEqual(format_date("2024-01-01"), "01/01/2024")
        
        # Test date invalide
        with self.assertRaises(FormatError):
            format_date("invalid_date")

    def test_parse_date(self):
        """Test de parsing de date."""
        # Test format par défaut
        date1 = parse_date("01/01/2024")
        self.assertIsInstance(date1, datetime)
        self.assertEqual(date1.year, 2024)
        self.assertEqual(date1.month, 1)
        self.assertEqual(date1.day, 1)
        
        # Test format personnalisé
        date2 = parse_date("2024-01-01", "%Y-%m-%d")
        self.assertIsInstance(date2, datetime)
        self.assertEqual(date2.year, 2024)
        self.assertEqual(date2.month, 1)
        self.assertEqual(date2.day, 1)
        
        # Test date invalide
        with self.assertRaises(FormatError):
            parse_date("invalid_date")

    def test_format_number(self):
        """Test de formatage de nombre."""
        # Test nombre entier
        self.assertEqual(format_number(100), "100.00")
        
        # Test nombre décimal
        self.assertEqual(format_number(100.5), "100.50")
        
        # Test format personnalisé
        self.assertEqual(format_number(100.5, "%.1f"), "100.5")
        
        # Test nombre invalide
        with self.assertRaises(FormatError):
            format_number("invalid_number")

    def test_parse_number(self):
        """Test de parsing de nombre."""
        # Test nombre entier
        self.assertEqual(parse_number("100"), Decimal("100"))
        
        # Test nombre décimal avec point
        self.assertEqual(parse_number("100.5"), Decimal("100.5"))
        
        # Test nombre décimal avec virgule
        self.assertEqual(parse_number("100,5"), Decimal("100.5"))
        
        # Test nombre invalide
        with self.assertRaises(FormatError):
            parse_number("invalid_number")

    def test_format_currency(self):
        """Test de formatage de montant."""
        # Test montant entier
        self.assertEqual(format_currency(100), "100.00 €")
        
        # Test montant décimal
        self.assertEqual(format_currency(100.5), "100.50 €")
        
        # Test devise personnalisée
        self.assertEqual(format_currency(100.5, "$"), "100.50 $")
        
        # Test montant invalide
        with self.assertRaises(FormatError):
            format_currency("invalid_amount")

    def test_parse_currency(self):
        """Test de parsing de montant."""
        # Test montant entier
        self.assertEqual(parse_currency("100 €"), Decimal("100"))
        
        # Test montant décimal
        self.assertEqual(parse_currency("100.50 €"), Decimal("100.50"))
        
        # Test montant invalide
        with self.assertRaises(FormatError):
            parse_currency("invalid_amount")

    def test_validate_email(self):
        """Test de validation d'email."""
        # Test email valide
        self.assertTrue(validate_email("test@example.com"))
        
        # Test email invalide
        self.assertFalse(validate_email("invalid_email"))

    def test_validate_phone(self):
        """Test de validation de numéro de téléphone."""
        # Test numéro valide
        self.assertTrue(validate_phone("0123456789"))
        
        # Test numéro invalide
        self.assertFalse(validate_phone("invalid_phone"))

    def test_validate_postal_code(self):
        """Test de validation de code postal."""
        # Test code valide
        self.assertTrue(validate_postal_code("75000"))
        
        # Test code invalide
        self.assertFalse(validate_postal_code("invalid_code"))

    def test_validate_siret(self):
        """Test de validation de numéro SIRET."""
        # Test numéro valide
        self.assertTrue(validate_siret("12345678901234"))
        
        # Test numéro invalide
        self.assertFalse(validate_siret("invalid_siret"))

    def test_validate_siren(self):
        """Test de validation de numéro SIREN."""
        # Test numéro valide
        self.assertTrue(validate_siren("123456789"))
        
        # Test numéro invalide
        self.assertFalse(validate_siren("invalid_siren"))

    def test_validate_vat(self):
        """Test de validation de numéro de TVA."""
        # Test numéro valide
        self.assertTrue(validate_vat("FR12345678901"))
        
        # Test numéro invalide
        self.assertFalse(validate_vat("invalid_vat"))

    def test_validate_iban(self):
        """Test de validation de numéro IBAN."""
        # Test numéro valide
        self.assertTrue(validate_iban("FR7630006000011234567890189"))
        
        # Test numéro invalide
        self.assertFalse(validate_iban("invalid_iban"))

    def test_validate_bic(self):
        """Test de validation de code BIC."""
        # Test code valide
        self.assertTrue(validate_bic("BNPAFRPP"))
        
        # Test code invalide
        self.assertFalse(validate_bic("invalid_bic"))

    def test_validate_url(self):
        """Test de validation d'URL."""
        # Test URL valide
        self.assertTrue(validate_url("https://example.com"))
        
        # Test URL invalide
        self.assertFalse(validate_url("invalid_url"))

    def test_validate_ip(self):
        """Test de validation d'adresse IP."""
        # Test IP valide
        self.assertTrue(validate_ip("192.168.1.1"))
        
        # Test IP invalide
        self.assertFalse(validate_ip("invalid_ip"))

    def test_validate_mac(self):
        """Test de validation d'adresse MAC."""
        # Test MAC valide
        self.assertTrue(validate_mac("00:11:22:33:44:55"))
        
        # Test MAC invalide
        self.assertFalse(validate_mac("invalid_mac"))

    def test_validate_hex_color(self):
        """Test de validation de couleur hexadécimale."""
        # Test couleur valide
        self.assertTrue(validate_hex_color("#FF0000"))
        
        # Test couleur invalide
        self.assertFalse(validate_hex_color("invalid_color"))

    def test_validate_file_extension(self):
        """Test de validation d'extension de fichier."""
        # Test extension valide
        self.assertTrue(validate_file_extension("test.pdf", [".pdf", ".doc"]))
        
        # Test extension invalide
        self.assertFalse(validate_file_extension("test.txt", [".pdf", ".doc"]))

    def test_validate_file_size(self):
        """Test de validation de taille de fichier."""
        # Création d'un fichier temporaire
        temp_file = os.path.join(self.temp_dir, "test.txt")
        with open(temp_file, "w") as f:
            f.write("test")
        
        # Test taille valide
        self.assertTrue(validate_file_size(temp_file, 1024))
        
        # Test taille invalide
        self.assertFalse(validate_file_size(temp_file, 1))

    def test_validate_file_type(self):
        """Test de validation de type de fichier."""
        # Création d'un fichier temporaire
        temp_file = os.path.join(self.temp_dir, "test.txt")
        with open(temp_file, "w") as f:
            f.write("test")
        
        # Test type valide
        self.assertTrue(validate_file_type(temp_file, ["text/plain"]))
        
        # Test type invalide
        self.assertFalse(validate_file_type(temp_file, ["application/pdf"]))

    def test_validate_json(self):
        """Test de validation de JSON."""
        # Test JSON valide
        self.assertTrue(validate_json('{"key": "value"}'))
        
        # Test JSON invalide
        self.assertFalse(validate_json('invalid_json'))

    def test_validate_xml(self):
        """Test de validation de XML."""
        # Test XML valide
        self.assertTrue(validate_xml("<root><item>value</item></root>"))
        
        # Test XML invalide
        self.assertFalse(validate_xml("invalid_xml"))

    def test_validate_yaml(self):
        """Test de validation de YAML."""
        # Test YAML valide
        self.assertTrue(validate_yaml("key: value"))
        
        # Test YAML invalide
        self.assertFalse(validate_yaml("invalid_yaml"))

    def test_validate_csv(self):
        """Test de validation de CSV."""
        # Test CSV valide
        self.assertTrue(validate_csv("value1,value2,value3"))
        
        # Test CSV invalide
        self.assertFalse(validate_csv("invalid_csv"))

    def test_validate_ini(self):
        """Test de validation de INI."""
        # Test INI valide
        self.assertTrue(validate_ini("[section]\nkey=value"))
        
        # Test INI invalide
        self.assertFalse(validate_ini("invalid_ini"))

    def test_validate_toml(self):
        """Test de validation de TOML."""
        # Test TOML valide
        self.assertTrue(validate_toml('key = "value"'))
        
        # Test TOML invalide
        self.assertFalse(validate_toml("invalid_toml"))

    def test_validate_html(self):
        """Test de validation de HTML."""
        # Test HTML valide
        self.assertTrue(validate_html("<html><body>test</body></html>"))
        
        # Test HTML invalide
        self.assertFalse(validate_html("invalid_html"))

    def test_validate_markdown(self):
        """Test de validation de Markdown."""
        # Test Markdown valide
        self.assertTrue(validate_markdown("# Title"))
        
        # Test Markdown invalide
        self.assertFalse(validate_markdown("invalid_markdown"))

    def test_validate_regex(self):
        """Test de validation d'expression régulière."""
        # Test regex valide
        self.assertTrue(validate_regex(r"\d+"))
        
        # Test regex invalide
        self.assertFalse(validate_regex("invalid_regex"))

    def test_validate_date_range(self):
        """Test de validation de plage de dates."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        
        # Test plage valide
        self.assertTrue(validate_date_range(start_date, end_date))
        
        # Test plage invalide
        self.assertFalse(validate_date_range(end_date, start_date))

    def test_validate_number_range(self):
        """Test de validation de plage de nombres."""
        # Test plage valide
        self.assertTrue(validate_number_range(5, 1, 10))
        
        # Test plage invalide
        self.assertFalse(validate_number_range(15, 1, 10))

    def test_validate_string_length(self):
        """Test de validation de longueur de chaîne."""
        # Test longueur valide
        self.assertTrue(validate_string_length("test", 1, 10))
        
        # Test longueur invalide
        self.assertFalse(validate_string_length("test", 5, 10))

    def test_validate_list_length(self):
        """Test de validation de longueur de liste."""
        # Test longueur valide
        self.assertTrue(validate_list_length([1, 2, 3], 1, 10))
        
        # Test longueur invalide
        self.assertFalse(validate_list_length([1, 2, 3], 5, 10))

    def test_validate_dict_keys(self):
        """Test de validation de clés de dictionnaire."""
        data = {"key1": "value1", "key2": "value2"}
        
        # Test clés valides
        self.assertTrue(validate_dict_keys(data, ["key1"], ["key2"]))
        
        # Test clés invalides
        self.assertFalse(validate_dict_keys(data, ["key3"]))

    def test_validate_dict_values(self):
        """Test de validation de valeurs de dictionnaire."""
        data = {"key1": "value1", "key2": 2}
        value_types = {"key1": str, "key2": int}
        
        # Test valeurs valides
        self.assertTrue(validate_dict_values(data, value_types))
        
        # Test valeurs invalides
        self.assertFalse(validate_dict_values({"key1": 1}, value_types))

    def test_validate_enum(self):
        """Test de validation d'énumération."""
        # Test valeur valide
        self.assertTrue(validate_enum("value1", ["value1", "value2"]))
        
        # Test valeur invalide
        self.assertFalse(validate_enum("value3", ["value1", "value2"]))

class TestUtils(unittest.TestCase):
    """Tests pour les fonctions utilitaires."""

    def test_generate_reference(self):
        """Test de la génération de références."""
        # Test avec préfixe
        ref = generate_reference("TEST")
        self.assertTrue(ref.startswith("TEST-"))
        self.assertEqual(len(ref), 9)  # TEST-XXXX

        # Test sans préfixe
        ref = generate_reference()
        self.assertEqual(len(ref), 4)  # XXXX

        # Test avec longueur personnalisée
        ref = generate_reference("TEST", length=6)
        self.assertTrue(ref.startswith("TEST-"))
        self.assertEqual(len(ref), 11)  # TEST-XXXXXX

    def test_format_date(self):
        """Test du formatage des dates."""
        date = datetime(2024, 3, 15, 14, 30, 0)

        # Test format par défaut
        self.assertEqual(format_date(date), "15/03/2024")

        # Test format personnalisé
        self.assertEqual(format_date(date, format="%Y-%m-%d"), "2024-03-15")

        # Test avec locale
        self.assertEqual(format_date(date, locale="fr_FR"), "15/03/2024")
        self.assertEqual(format_date(date, locale="en_US"), "03/15/2024")

        # Test avec fuseau horaire
        self.assertEqual(format_date(date, timezone="timezone.utc"), "15/03/2024")
        self.assertEqual(format_date(date, timezone="Europe/Paris"), "15/03/2024")

    def test_parse_date(self):
        """Test du parsing des dates."""
        # Test format par défaut
        date = parse_date("15/03/2024")
        self.assertEqual(date.year, 2024)
        self.assertEqual(date.month, 3)
        self.assertEqual(date.day, 15)

        # Test format personnalisé
        date = parse_date("2024-03-15", format="%Y-%m-%d")
        self.assertEqual(date.year, 2024)
        self.assertEqual(date.month, 3)
        self.assertEqual(date.day, 15)

        # Test avec locale
        date = parse_date("15/03/2024", locale="fr_FR")
        self.assertEqual(date.year, 2024)
        self.assertEqual(date.month, 3)
        self.assertEqual(date.day, 15)

        # Test avec fuseau horaire
        date = parse_date("15/03/2024", timezone="timezone.utc")
        self.assertEqual(date.year, 2024)
        self.assertEqual(date.month, 3)
        self.assertEqual(date.day, 15)

    def test_format_currency(self):
        """Test du formatage des montants."""
        amount = Decimal("1500.50")

        # Test format par défaut
        self.assertEqual(format_currency(amount), "1 500,50 €")

        # Test avec devise
        self.assertEqual(format_currency(amount, currency="USD"), "$1,500.50")
        self.assertEqual(format_currency(amount, currency="GBP"), "£1,500.50")

        # Test avec locale
        self.assertEqual(format_currency(amount, locale="fr_FR"), "1 500,50 €")
        self.assertEqual(format_currency(amount, locale="en_US"), "$1,500.50")

        # Test avec précision
        self.assertEqual(format_currency(amount, precision=0), "1 501 €")
        self.assertEqual(format_currency(amount, precision=3), "1 500,500 €")

    def test_parse_currency(self):
        """Test du parsing des montants."""
        # Test format par défaut
        amount = parse_currency("1 500,50 €")
        self.assertEqual(amount, Decimal("1500.50"))

        # Test avec devise
        amount = parse_currency("$1,500.50", currency="USD")
        self.assertEqual(amount, Decimal("1500.50"))

        # Test avec locale
        amount = parse_currency("1 500,50 €", locale="fr_FR")
        self.assertEqual(amount, Decimal("1500.50"))

        # Test avec précision
        amount = parse_currency("1 500,500 €", precision=3)
        self.assertEqual(amount, Decimal("1500.500"))

    def test_format_phone(self):
        """Test du formatage des numéros de téléphone."""
        # Test format par défaut
        self.assertEqual(format_phone("0612345678"), "+33 6 12 34 56 78")

        # Test avec pays
        self.assertEqual(format_phone("0612345678", country="FR"), "+33 6 12 34 56 78")
        self.assertEqual(format_phone("0612345678", country="US"), "+1 6 12 34 56 78")

        # Test avec format
        self.assertEqual(format_phone("0612345678", format="international"), "+33 6 12 34 56 78")
        self.assertEqual(format_phone("0612345678", format="national"), "06 12 34 56 78")

    def test_parse_phone(self):
        """Test du parsing des numéros de téléphone."""
        # Test format par défaut
        self.assertEqual(parse_phone("+33 6 12 34 56 78"), "0612345678")

        # Test avec pays
        self.assertEqual(parse_phone("+33 6 12 34 56 78", country="FR"), "0612345678")
        self.assertEqual(parse_phone("+1 6 12 34 56 78", country="US"), "0612345678")

        # Test avec format
        self.assertEqual(parse_phone("06 12 34 56 78", format="national"), "0612345678")

    def test_format_email(self):
        """Test du formatage des adresses email."""
        # Test format par défaut
        self.assertEqual(format_email("john.doe@example.com"), "john.doe@example.com")

        # Test avec format
        self.assertEqual(format_email("John.Doe@Example.com", format="lowercase"), "john.doe@example.com")
        self.assertEqual(format_email("john.doe@example.com", format="uppercase"), "JOHN.DOE@EXAMPLE.COM")

    def test_validate_email(self):
        """Test de la validation des adresses email."""
        # Test adresse valide
        self.assertTrue(validate_email("john.doe@example.com"))

        # Test adresse invalide
        self.assertFalse(validate_email("john.doe@"))
        self.assertFalse(validate_email("john.doe"))
        self.assertFalse(validate_email("@example.com"))

    def test_format_address(self):
        """Test du formatage des adresses."""
        address = {
            "street": "123 rue de la Paix",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France"
        }

        # Test format par défaut
        formatted = format_address(address)
        self.assertIn("123 rue de la Paix", formatted)
        self.assertIn("75001 Paris", formatted)
        self.assertIn("France", formatted)

        # Test avec format
        formatted = format_address(address, format="single_line")
        self.assertIn("123 rue de la Paix, 75001 Paris, France", formatted)

        # Test avec locale
        formatted = format_address(address, locale="fr_FR")
        self.assertIn("123 rue de la Paix", formatted)
        self.assertIn("75001 Paris", formatted)
        self.assertIn("France", formatted)

    def test_validate_address(self):
        """Test de la validation des adresses."""
        # Test adresse valide
        valid_address = {
            "street": "123 rue de la Paix",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France"
        }
        self.assertTrue(validate_address(valid_address))

        # Test adresse invalide
        invalid_address = {
            "street": "",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France"
        }
        self.assertFalse(validate_address(invalid_address))

if __name__ == '__main__':
    unittest.main() 