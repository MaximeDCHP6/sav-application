import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.exceptions import (
    AlderSAVError,
    ValidationError,
    NotFoundError,
    DuplicateError,
    PermissionError,
    AuthenticationError,
    AuthorizationError,
    BusinessError,
    SystemError,
    DatabaseError,
    NetworkError,
    TimeoutError,
    ConfigurationError,
    ResourceError,
    StateError,
    FormatError,
    DependencyError,
    IntegrationError,
    SecurityError,
    DataError,
    LogicError,
    BusinessLogicError,
    ExternalServiceError,
    NotificationError,
    ReportError,
    StatisticsError
)

class TestExceptions(unittest.TestCase):
    """Tests pour le système de gestion des erreurs."""

    def test_base_exception(self):
        """Test de l'exception de base."""
        error = AlderSAVError("Une erreur est survenue")
        self.assertEqual(str(error), "Une erreur est survenue")
        self.assertIsNone(error.code)
        self.assertIsNone(error.details)

        error = AlderSAVError("Une erreur est survenue", code="ERR001", details={"cause": "test"})
        self.assertEqual(error.code, "ERR001")
        self.assertEqual(error.details, {"cause": "test"})

    def test_validation_error(self):
        """Test des erreurs de validation."""
        error = ValidationError("Données invalides")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "VALIDATION_ERROR")

        error = ValidationError("Données invalides", details={"field": "email", "reason": "format invalide"})
        self.assertEqual(error.details["field"], "email")
        self.assertEqual(error.details["reason"], "format invalide")

    def test_configuration_error(self):
        """Test des erreurs de configuration."""
        error = ConfigurationError("Configuration invalide")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "CONFIGURATION_ERROR")

        error = ConfigurationError("Configuration invalide", details={"file": "config.json", "line": 10})
        self.assertEqual(error.details["file"], "config.json")
        self.assertEqual(error.details["line"], 10)

    def test_database_error(self):
        """Test des erreurs de base de données."""
        error = DatabaseError("Erreur de connexion")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "DATABASE_ERROR")

        error = DatabaseError("Erreur de connexion", details={
            "operation": "insert",
            "table": "users",
            "sql": "INSERT INTO users..."
        })
        self.assertEqual(error.details["operation"], "insert")
        self.assertEqual(error.details["table"], "users")

    def test_authentication_error(self):
        """Test des erreurs d'authentification."""
        error = AuthenticationError("Identifiants invalides")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "AUTHENTICATION_ERROR")

        error = AuthenticationError("Identifiants invalides", details={
            "username": "john",
            "attempts": 3
        })
        self.assertEqual(error.details["username"], "john")
        self.assertEqual(error.details["attempts"], 3)

    def test_authorization_error(self):
        """Test des erreurs d'autorisation."""
        error = AuthorizationError("Accès non autorisé")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "AUTHORIZATION_ERROR")

        error = AuthorizationError("Accès non autorisé", details={
            "user": "john",
            "resource": "admin_panel",
            "required_role": "admin"
        })
        self.assertEqual(error.details["user"], "john")
        self.assertEqual(error.details["resource"], "admin_panel")

    def test_not_found_error(self):
        """Test des erreurs de ressource non trouvée."""
        error = NotFoundError("Utilisateur non trouvé")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "NOT_FOUND_ERROR")

        error = NotFoundError("Utilisateur non trouvé", details={
            "resource_type": "user",
            "resource_id": "123"
        })
        self.assertEqual(error.details["resource_type"], "user")
        self.assertEqual(error.details["resource_id"], "123")

    def test_duplicate_error(self):
        """Test des erreurs de doublon."""
        error = DuplicateError("Email déjà utilisé")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "DUPLICATE_ERROR")

        error = DuplicateError("Email déjà utilisé", details={
            "field": "email",
            "value": "john@example.com"
        })
        self.assertEqual(error.details["field"], "email")
        self.assertEqual(error.details["value"], "john@example.com")

    def test_business_logic_error(self):
        """Test des erreurs de logique métier."""
        error = BusinessLogicError("Opération impossible")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "BUSINESS_LOGIC_ERROR")

        error = BusinessLogicError("Opération impossible", details={
            "operation": "delete_user",
            "reason": "user_has_active_orders"
        })
        self.assertEqual(error.details["operation"], "delete_user")
        self.assertEqual(error.details["reason"], "user_has_active_orders")

    def test_external_service_error(self):
        """Test des erreurs de service externe."""
        error = ExternalServiceError("Service indisponible")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "EXTERNAL_SERVICE_ERROR")

        error = ExternalServiceError("Service indisponible", details={
            "service": "payment_gateway",
            "status_code": 503,
            "response": "Service Unavailable"
        })
        self.assertEqual(error.details["service"], "payment_gateway")
        self.assertEqual(error.details["status_code"], 503)

    def test_notification_error(self):
        """Test des erreurs de notification."""
        error = NotificationError("Échec de l'envoi")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "NOTIFICATION_ERROR")

        error = NotificationError("Échec de l'envoi", details={
            "type": "email",
            "recipient": "john@example.com",
            "reason": "invalid_address"
        })
        self.assertEqual(error.details["type"], "email")
        self.assertEqual(error.details["recipient"], "john@example.com")

    def test_report_error(self):
        """Test des erreurs de rapport."""
        error = ReportError("Échec de génération")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "REPORT_ERROR")

        error = ReportError("Échec de génération", details={
            "report_type": "sales_summary",
            "period": "2024-01",
            "reason": "missing_data"
        })
        self.assertEqual(error.details["report_type"], "sales_summary")
        self.assertEqual(error.details["period"], "2024-01")

    def test_statistics_error(self):
        """Test des erreurs de statistiques."""
        error = StatisticsError("Échec du calcul")
        self.assertIsInstance(error, AlderSAVError)
        self.assertEqual(error.code, "STATISTICS_ERROR")

        error = StatisticsError("Échec du calcul", details={
            "metric": "average_order_value",
            "period": "2024-01",
            "reason": "insufficient_data"
        })
        self.assertEqual(error.details["metric"], "average_order_value")
        self.assertEqual(error.details["period"], "2024-01")

    def test_error_inheritance(self):
        """Test de l'héritage des erreurs."""
        errors = [
            ValidationError("test"),
            ConfigurationError("test"),
            DatabaseError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            NotFoundError("test"),
            DuplicateError("test"),
            BusinessLogicError("test"),
            ExternalServiceError("test"),
            NotificationError("test"),
            ReportError("test"),
            StatisticsError("test")
        ]

        for error in errors:
            self.assertIsInstance(error, AlderSAVError)

    def test_error_details_serialization(self):
        """Test de la sérialisation des détails d'erreur."""
        details = {
            "string": "test",
            "integer": 123,
            "float": 123.45,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "datetime": datetime.now(),
            "decimal": Decimal("123.45")
        }

        error = AlderSAVError("Test", details=details)
        serialized = error.to_dict()

        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized["message"], "Test")
        self.assertEqual(serialized["code"], None)
        self.assertIn("details", serialized)

    def test_error_chaining(self):
        """Test de l'enchaînement des erreurs."""
        try:
            try:
                raise DatabaseError("Erreur de base de données")
            except DatabaseError as e:
                raise BusinessLogicError("Opération impossible") from e
        except BusinessLogicError as e:
            self.assertIsNotNone(e.__cause__)
            self.assertIsInstance(e.__cause__, DatabaseError)

if __name__ == '__main__':
    unittest.main() 