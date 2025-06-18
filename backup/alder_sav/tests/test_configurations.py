import unittest
import os
import json
from datetime import datetime
from decimal import Decimal
from alder_sav.utils.configuration import ConfigurationManager
from alder_sav.utils.exceptions import ConfigurationError

class TestConfigurationManager(unittest.TestCase):
    """Tests pour le gestionnaire de configuration."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.config_manager = ConfigurationManager()
        self.test_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "test_db",
                "user": "test_user",
                "password": "test_password"
            },
            "api": {
                "base_url": "http://api.example.com",
                "timeout": 30,
                "retry_attempts": 3
            },
            "logging": {
                "level": "INFO",
                "file": "app.log",
                "max_size": 10485760,
                "backup_count": 5
            }
        }

    def test_load_configuration(self):
        """Test de chargement de la configuration."""
        # Charger la configuration
        self.config_manager.load_configuration(self.test_config)
        
        # Vérifier que la configuration a été chargée
        config = self.config_manager.get_configuration()
        self.assertEqual(config["database"]["host"], "localhost")
        self.assertEqual(config["api"]["timeout"], 30)
        self.assertEqual(config["logging"]["level"], "INFO")

    def test_validate_configuration(self):
        """Test de validation de la configuration."""
        # Configuration valide
        self.assertTrue(self.config_manager.validate_configuration(self.test_config))
        
        # Configuration invalide (champ requis manquant)
        invalid_config = self.test_config.copy()
        del invalid_config["database"]["host"]
        
        with self.assertRaises(ConfigurationError):
            self.config_manager.validate_configuration(invalid_config)

    def test_get_configuration_value(self):
        """Test de récupération d'une valeur de configuration."""
        # Charger la configuration
        self.config_manager.load_configuration(self.test_config)
        
        # Récupérer une valeur
        db_host = self.config_manager.get_configuration_value("database.host")
        self.assertEqual(db_host, "localhost")
        
        # Récupérer une valeur imbriquée
        api_timeout = self.config_manager.get_configuration_value("api.timeout")
        self.assertEqual(api_timeout, 30)

    def test_set_configuration_value(self):
        """Test de modification d'une valeur de configuration."""
        # Charger la configuration
        self.config_manager.load_configuration(self.test_config)
        
        # Modifier une valeur
        self.config_manager.set_configuration_value("database.host", "new_host")
        self.assertEqual(
            self.config_manager.get_configuration_value("database.host"),
            "new_host"
        )

    def test_environment_specific_configuration(self):
        """Test de configuration spécifique à l'environnement."""
        # Configurations pour différents environnements
        env_configs = {
            "development": {
                "database": {"host": "localhost"},
                "api": {"base_url": "http://dev-api.example.com"}
            },
            "production": {
                "database": {"host": "prod-db.example.com"},
                "api": {"base_url": "https://api.example.com"}
            }
        }
        
        # Charger la configuration de développement
        self.config_manager.load_environment_configuration(env_configs, "development")
        dev_config = self.config_manager.get_configuration()
        self.assertEqual(dev_config["database"]["host"], "localhost")
        
        # Charger la configuration de production
        self.config_manager.load_environment_configuration(env_configs, "production")
        prod_config = self.config_manager.get_configuration()
        self.assertEqual(prod_config["database"]["host"], "prod-db.example.com")

    def test_secret_management(self):
        """Test de gestion des secrets."""
        # Secrets à gérer
        secrets = {
            "database": {
                "password": "secret_password",
                "api_key": "secret_api_key"
            }
        }
        
        # Charger les secrets
        self.config_manager.load_secrets(secrets)
        
        # Vérifier que les secrets sont masqués
        config = self.config_manager.get_configuration()
        self.assertEqual(config["database"]["password"], "********")
        self.assertEqual(config["database"]["api_key"], "********")

    def test_configuration_export(self):
        """Test d'export de la configuration."""
        # Charger la configuration
        self.config_manager.load_configuration(self.test_config)
        
        # Exporter la configuration
        exported_config = self.config_manager.export_configuration()
        self.assertEqual(exported_config, self.test_config)

    def test_configuration_import(self):
        """Test d'import de la configuration."""
        # Configuration à importer
        import_config = {
            "new_section": {
                "key": "value"
            }
        }
        
        # Importer la configuration
        self.config_manager.import_configuration(import_config)
        
        # Vérifier l'import
        config = self.config_manager.get_configuration()
        self.assertEqual(config["new_section"]["key"], "value")

    def test_configuration_validation_rules(self):
        """Test des règles de validation de configuration."""
        # Règles de validation
        validation_rules = {
            "database": {
                "host": {"type": "string", "required": True},
                "port": {"type": "integer", "min": 1, "max": 65535}
            }
        }
        
        # Configuration valide
        valid_config = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        self.assertTrue(
            self.config_manager.validate_configuration_with_rules(
                valid_config,
                validation_rules
            )
        )
        
        # Configuration invalide
        invalid_config = {
            "database": {
                "host": "localhost",
                "port": 70000  # Port invalide
            }
        }
        with self.assertRaises(ConfigurationError):
            self.config_manager.validate_configuration_with_rules(
                invalid_config,
                validation_rules
            )

    def test_configuration_defaults(self):
        """Test des valeurs par défaut de configuration."""
        # Valeurs par défaut
        defaults = {
            "database": {
                "port": 5432,
                "timeout": 30
            }
        }
        
        # Configuration partielle
        partial_config = {
            "database": {
                "host": "localhost"
            }
        }
        
        # Charger la configuration avec les valeurs par défaut
        self.config_manager.load_configuration_with_defaults(partial_config, defaults)
        
        # Vérifier les valeurs par défaut
        config = self.config_manager.get_configuration()
        self.assertEqual(config["database"]["port"], 5432)
        self.assertEqual(config["database"]["timeout"], 30)

    def test_configuration_override(self):
        """Test de surcharge de configuration."""
        # Configuration de base
        base_config = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Surcharge
        override_config = {
            "database": {
                "host": "new_host"
            }
        }
        
        # Appliquer la surcharge
        self.config_manager.load_configuration_with_override(base_config, override_config)
        
        # Vérifier la surcharge
        config = self.config_manager.get_configuration()
        self.assertEqual(config["database"]["host"], "new_host")
        self.assertEqual(config["database"]["port"], 5432)

if __name__ == '__main__':
    unittest.main() 