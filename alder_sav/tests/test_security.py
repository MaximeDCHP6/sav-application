import unittest
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from alder_sav.utils.security import SecurityManager
from alder_sav.utils.exceptions import SecurityError

class TestSecurityManager(unittest.TestCase):
    """Tests pour le gestionnaire de sécurité."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.security_manager = SecurityManager()

    def test_password_hashing(self):
        """Test du hachage des mots de passe."""
        # Mot de passe à hacher
        password = "secure_password123"
        
        # Hacher le mot de passe
        hashed_password = self.security_manager.hash_password(password)
        
        # Vérifier le hachage
        self.assertNotEqual(hashed_password, password)
        self.assertTrue(self.security_manager.verify_password(password, hashed_password))
        self.assertFalse(self.security_manager.verify_password("wrong_password", hashed_password))

    def test_token_generation(self):
        """Test de la génération de tokens."""
        # Générer un token
        token = self.security_manager.generate_token()
        
        # Vérifier le token
        self.assertIsNotNone(token)
        self.assertTrue(self.security_manager.verify_token(token))

    def test_token_expiration(self):
        """Test de l'expiration des tokens."""
        # Générer un token avec expiration
        token = self.security_manager.generate_token(ttl=1)  # 1 seconde
        
        # Vérifier que le token est valide
        self.assertTrue(self.security_manager.verify_token(token))
        
        # Attendre l'expiration
        time.sleep(2)
        
        # Vérifier que le token a expiré
        self.assertFalse(self.security_manager.verify_token(token))

    def test_encryption(self):
        """Test du chiffrement."""
        # Données à chiffrer
        sensitive_data = "sensitive information"
        
        # Chiffrer les données
        encrypted_data = self.security_manager.encrypt(sensitive_data)
        
        # Vérifier le chiffrement
        self.assertNotEqual(encrypted_data, sensitive_data)
        self.assertEqual(self.security_manager.decrypt(encrypted_data), sensitive_data)

    def test_key_generation(self):
        """Test de la génération de clés."""
        # Générer une paire de clés
        public_key, private_key = self.security_manager.generate_key_pair()
        
        # Vérifier les clés
        self.assertIsNotNone(public_key)
        self.assertIsNotNone(private_key)

    def test_digital_signature(self):
        """Test des signatures numériques."""
        # Données à signer
        data = "important document"
        
        # Générer une signature
        signature = self.security_manager.sign(data)
        
        # Vérifier la signature
        self.assertTrue(self.security_manager.verify_signature(data, signature))

    def test_certificate_management(self):
        """Test de la gestion des certificats."""
        # Générer un certificat
        certificate = self.security_manager.generate_certificate()
        
        # Vérifier le certificat
        self.assertIsNotNone(certificate)
        self.assertTrue(self.security_manager.verify_certificate(certificate))

    def test_csrf_protection(self):
        """Test de la protection CSRF."""
        # Générer un token CSRF
        csrf_token = self.security_manager.generate_csrf_token()
        
        # Vérifier le token
        self.assertIsNotNone(csrf_token)
        self.assertTrue(self.security_manager.verify_csrf_token(csrf_token))

    def test_input_validation(self):
        """Test de la validation des entrées."""
        # Données à valider
        user_input = {
            "username": "john_doe",
            "email": "john@example.com",
            "age": "25"
        }
        
        # Schéma de validation
        schema = {
            "username": {"type": "string", "pattern": "^[a-zA-Z0-9_]+$"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 18}
        }
        
        # Valider les données
        self.assertTrue(self.security_manager.validate_input(user_input, schema))

    def test_sql_injection_prevention(self):
        """Test de la prévention des injections SQL."""
        # Requête SQL avec injection
        malicious_input = "'; DROP TABLE users; --"
        
        # Nettoyer l'entrée
        cleaned_input = self.security_manager.sanitize_sql_input(malicious_input)
        
        # Vérifier le nettoyage
        self.assertNotEqual(cleaned_input, malicious_input)
        self.assertNotIn("DROP TABLE", cleaned_input)

    def test_xss_prevention(self):
        """Test de la prévention XSS."""
        # Données avec XSS
        malicious_input = "<script>alert('XSS')</script>"
        
        # Nettoyer l'entrée
        cleaned_input = self.security_manager.sanitize_html_input(malicious_input)
        
        # Vérifier le nettoyage
        self.assertNotEqual(cleaned_input, malicious_input)
        self.assertNotIn("<script>", cleaned_input)

    def test_rate_limiting(self):
        """Test de la limitation de taux."""
        # Configurer la limitation
        self.security_manager.configure_rate_limit(
            max_requests=3,
            time_window=1  # 1 seconde
        )
        
        # Effectuer des requêtes
        for _ in range(3):
            self.assertTrue(self.security_manager.check_rate_limit("user1"))
        
        # Vérifier la limitation
        self.assertFalse(self.security_manager.check_rate_limit("user1"))

    def test_audit_logging(self):
        """Test de la journalisation d'audit."""
        # Enregistrer une action
        self.security_manager.log_audit(
            user_id=123,
            action="login",
            details={"ip": "192.168.1.1"}
        )
        
        # Vérifier la journalisation
        logs = self.security_manager.get_audit_logs()
        self.assertTrue(any(
            log["user_id"] == 123 and
            log["action"] == "login" and
            log["details"]["ip"] == "192.168.1.1"
            for log in logs
        ))

    def test_password_policy(self):
        """Test de la politique de mots de passe."""
        # Configurer la politique
        self.security_manager.configure_password_policy(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )
        
        # Vérifier un mot de passe valide
        valid_password = "SecurePass123!"
        self.assertTrue(self.security_manager.validate_password_policy(valid_password))
        
        # Vérifier un mot de passe invalide
        invalid_password = "weak"
        self.assertFalse(self.security_manager.validate_password_policy(invalid_password))

    def test_session_management(self):
        """Test de la gestion des sessions."""
        # Créer une session
        session_id = self.security_manager.create_session(user_id=123)
        
        # Vérifier la session
        self.assertTrue(self.security_manager.validate_session(session_id))
        
        # Invalider la session
        self.security_manager.invalidate_session(session_id)
        self.assertFalse(self.security_manager.validate_session(session_id))

if __name__ == '__main__':
    unittest.main() 