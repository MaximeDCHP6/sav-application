import unittest
from datetime import datetime
from decimal import Decimal
from alder_sav.utils.error_handling import ErrorHandler
from alder_sav.utils.exceptions import (
    ValidationError,
    DatabaseError,
    NetworkError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    CacheError,
    NotificationError,
    ReportError,
    StatisticsError
)

class TestErrorHandler(unittest.TestCase):
    """Tests pour le gestionnaire d'erreurs."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.error_handler = ErrorHandler()

    def test_handle_validation_error(self):
        """Test de gestion des erreurs de validation."""
        # Test avec une erreur de validation
        error = ValidationError("Champ requis manquant")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "validation_error")
        self.assertEqual(result["message"], "Champ requis manquant")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_database_error(self):
        """Test de gestion des erreurs de base de données."""
        # Test avec une erreur de base de données
        error = DatabaseError("Erreur de connexion à la base de données")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "database_error")
        self.assertEqual(result["message"], "Erreur de connexion à la base de données")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_network_error(self):
        """Test de gestion des erreurs réseau."""
        # Test avec une erreur réseau
        error = NetworkError("Timeout de connexion")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "network_error")
        self.assertEqual(result["message"], "Timeout de connexion")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_authentication_error(self):
        """Test de gestion des erreurs d'authentification."""
        # Test avec une erreur d'authentification
        error = AuthenticationError("Identifiants invalides")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "authentication_error")
        self.assertEqual(result["message"], "Identifiants invalides")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_authorization_error(self):
        """Test de gestion des erreurs d'autorisation."""
        # Test avec une erreur d'autorisation
        error = AuthorizationError("Accès non autorisé")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "authorization_error")
        self.assertEqual(result["message"], "Accès non autorisé")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_configuration_error(self):
        """Test de gestion des erreurs de configuration."""
        # Test avec une erreur de configuration
        error = ConfigurationError("Configuration manquante")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "configuration_error")
        self.assertEqual(result["message"], "Configuration manquante")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_cache_error(self):
        """Test de gestion des erreurs de cache."""
        # Test avec une erreur de cache
        error = CacheError("Erreur de mise en cache")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "cache_error")
        self.assertEqual(result["message"], "Erreur de mise en cache")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_notification_error(self):
        """Test de gestion des erreurs de notification."""
        # Test avec une erreur de notification
        error = NotificationError("Échec d'envoi de notification")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "notification_error")
        self.assertEqual(result["message"], "Échec d'envoi de notification")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_report_error(self):
        """Test de gestion des erreurs de rapport."""
        # Test avec une erreur de rapport
        error = ReportError("Erreur de génération de rapport")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "report_error")
        self.assertEqual(result["message"], "Erreur de génération de rapport")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_statistics_error(self):
        """Test de gestion des erreurs de statistiques."""
        # Test avec une erreur de statistiques
        error = StatisticsError("Erreur de calcul de statistiques")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "statistics_error")
        self.assertEqual(result["message"], "Erreur de calcul de statistiques")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_handle_unknown_error(self):
        """Test de gestion des erreurs inconnues."""
        # Test avec une erreur inconnue
        error = Exception("Erreur inconnue")
        result = self.error_handler.handle_error(error)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["type"], "unknown_error")
        self.assertEqual(result["message"], "Erreur inconnue")
        self.assertIn("timestamp", result)
        self.assertIn("traceback", result)

    def test_error_logging(self):
        """Test de journalisation des erreurs."""
        # Test de journalisation d'une erreur
        error = ValidationError("Test d'erreur")
        self.error_handler.handle_error(error)
        
        # Vérifier que l'erreur a été journalisée
        logs = self.error_handler.get_error_logs()
        self.assertTrue(any(log["type"] == "validation_error" for log in logs))

    def test_error_filtering(self):
        """Test de filtrage des erreurs."""
        # Ajouter plusieurs erreurs
        errors = [
            ValidationError("Erreur 1"),
            DatabaseError("Erreur 2"),
            NetworkError("Erreur 3")
        ]
        
        for error in errors:
            self.error_handler.handle_error(error)
        
        # Filtrer par type d'erreur
        validation_errors = self.error_handler.get_error_logs(error_type="validation_error")
        self.assertEqual(len(validation_errors), 1)
        self.assertEqual(validation_errors[0]["type"], "validation_error")

    def test_error_aggregation(self):
        """Test d'agrégation des erreurs."""
        # Ajouter plusieurs erreurs du même type
        for _ in range(3):
            self.error_handler.handle_error(ValidationError("Erreur répétée"))
        
        # Vérifier l'agrégation
        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["validation_error"], 3)

    def test_error_recovery(self):
        """Test de récupération après erreur."""
        # Simuler une erreur récupérable
        error = DatabaseError("Erreur temporaire")
        result = self.error_handler.handle_error(error, recoverable=True)
        
        self.assertEqual(result["status"], "error")
        self.assertTrue(result["recoverable"])
        self.assertIn("recovery_attempts", result)

    def test_error_notification(self):
        """Test de notification des erreurs."""
        # Simuler une erreur critique
        error = DatabaseError("Erreur critique")
        result = self.error_handler.handle_error(error, critical=True)
        
        self.assertEqual(result["status"], "error")
        self.assertTrue(result["critical"])
        self.assertIn("notified", result)

if __name__ == '__main__':
    unittest.main() 