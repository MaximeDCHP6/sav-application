import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.validation import ValidationManager
from alder_sav.utils.exceptions import ValidationError

class TestValidationManager(unittest.TestCase):
    """Tests pour le gestionnaire de validation."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.validation_manager = ValidationManager()

    def test_create_validation(self):
        """Test de création d'une validation."""
        validation = self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {
                "required_fields": ["client_id", "device_id", "description"],
                "field_types": {
                    "client_id": "string",
                    "device_id": "string",
                    "description": "string",
                    "cost": "decimal",
                    "estimated_time": "integer"
                },
                "constraints": {
                    "cost": {
                        "min": 0,
                        "max": 10000
                    },
                    "estimated_time": {
                        "min": 1,
                        "max": 365
                    }
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        })

        self.assertIsNotNone(validation["id"])
        self.assertEqual(validation["type"], "repair")
        self.assertEqual(validation["status"], "active")
        self.assertIn("client_id", validation["rules"]["required_fields"])

    def test_get_validation(self):
        """Test de récupération d'une validation."""
        # Créer une validation
        validation = self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {
                "required_fields": ["client_id", "device_id"]
            }
        })

        # Récupérer la validation
        retrieved = self.validation_manager.get_validation(validation["id"])
        self.assertEqual(retrieved["id"], validation["id"])
        self.assertEqual(retrieved["type"], "repair")

    def test_update_validation(self):
        """Test de mise à jour d'une validation."""
        # Créer une validation
        validation = self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {
                "required_fields": ["client_id"]
            }
        })

        # Mettre à jour la validation
        updated = self.validation_manager.update_validation(validation["id"], {
            "rules": {
                "required_fields": ["client_id", "device_id", "description"]
            }
        })

        self.assertEqual(len(updated["rules"]["required_fields"]), 3)
        self.assertIn("description", updated["rules"]["required_fields"])

    def test_delete_validation(self):
        """Test de suppression d'une validation."""
        # Créer une validation
        validation = self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {
                "required_fields": ["client_id"]
            }
        })

        # Supprimer la validation
        self.validation_manager.delete_validation(validation["id"])

        # Vérifier que la validation n'existe plus
        with self.assertRaises(ValidationError):
            self.validation_manager.get_validation(validation["id"])

    def test_validate_data(self):
        """Test de validation des données."""
        # Créer une validation
        validation = self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {
                "required_fields": ["client_id", "device_id", "description"],
                "field_types": {
                    "client_id": "string",
                    "device_id": "string",
                    "description": "string",
                    "cost": "decimal"
                },
                "constraints": {
                    "cost": {
                        "min": 0,
                        "max": 10000
                    }
                }
            }
        })

        # Données valides
        valid_data = {
            "client_id": "CLI-001",
            "device_id": "DEV-001",
            "description": "Réparation écran",
            "cost": Decimal("500.00")
        }
        self.assertTrue(self.validation_manager.validate_data(validation["id"], valid_data))

        # Données invalides
        invalid_data = {
            "client_id": "CLI-001",
            "device_id": "DEV-001"
            # description manquante
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_data(validation["id"], invalid_data)

    def test_get_validation_by_type(self):
        """Test de récupération des validations par type."""
        # Créer plusieurs validations
        self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {"required_fields": ["client_id"]}
        })
        self.validation_manager.create_validation({
            "type": "warranty",
            "status": "active",
            "rules": {"required_fields": ["device_id"]}
        })

        # Récupérer les validations de type repair
        repair_validations = self.validation_manager.get_validations_by_type("repair")
        self.assertEqual(len(repair_validations), 1)
        self.assertEqual(repair_validations[0]["type"], "repair")

    def test_get_validation_by_status(self):
        """Test de récupération des validations par statut."""
        # Créer plusieurs validations
        self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {"required_fields": ["client_id"]}
        })
        self.validation_manager.create_validation({
            "type": "repair",
            "status": "inactive",
            "rules": {"required_fields": ["client_id"]}
        })

        # Récupérer les validations actives
        active_validations = self.validation_manager.get_validations_by_status("active")
        self.assertEqual(len(active_validations), 1)
        self.assertEqual(active_validations[0]["status"], "active")

    def test_validate_complex_data(self):
        """Test de validation de données complexes."""
        # Créer une validation pour des données complexes
        validation = self.validation_manager.create_validation({
            "type": "repair",
            "status": "active",
            "rules": {
                "required_fields": ["client_id", "device_id", "description", "parts"],
                "field_types": {
                    "client_id": "string",
                    "device_id": "string",
                    "description": "string",
                    "parts": "array",
                    "cost": "decimal"
                },
                "array_rules": {
                    "parts": {
                        "required_fields": ["part_id", "quantity"],
                        "field_types": {
                            "part_id": "string",
                            "quantity": "integer"
                        },
                        "constraints": {
                            "quantity": {
                                "min": 1
                            }
                        }
                    }
                }
            }
        })

        # Données valides
        valid_data = {
            "client_id": "CLI-001",
            "device_id": "DEV-001",
            "description": "Réparation écran",
            "parts": [
                {
                    "part_id": "PART-001",
                    "quantity": 2
                },
                {
                    "part_id": "PART-002",
                    "quantity": 1
                }
            ],
            "cost": Decimal("500.00")
        }
        self.assertTrue(self.validation_manager.validate_data(validation["id"], valid_data))

        # Données invalides
        invalid_data = {
            "client_id": "CLI-001",
            "device_id": "DEV-001",
            "description": "Réparation écran",
            "parts": [
                {
                    "part_id": "PART-001",
                    "quantity": 0  # Quantité invalide
                }
            ]
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_data(validation["id"], invalid_data)

    def test_validate_required_fields(self):
        """Test de validation des champs requis."""
        # Schéma avec champs requis
        schema = {
            "name": {"type": "string", "required": True},
            "email": {"type": "string", "required": True},
            "age": {"type": "integer", "required": False}
        }

        # Données valides
        valid_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        self.assertTrue(self.validation_manager.validate_required_fields(valid_data, schema))

        # Données invalides (champ requis manquant)
        invalid_data = {
            "name": "John Doe"
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_required_fields(invalid_data, schema)

    def test_validate_field_types(self):
        """Test de validation des types de champs."""
        # Schéma avec différents types
        schema = {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "height": {"type": "number"},
            "is_active": {"type": "boolean"},
            "birth_date": {"type": "datetime"},
            "scores": {"type": "array"},
            "address": {"type": "object"}
        }

        # Données valides
        valid_data = {
            "name": "John Doe",
            "age": 30,
            "height": 1.75,
            "is_active": True,
            "birth_date": datetime.now().isoformat(),
            "scores": [1, 2, 3],
            "address": {"street": "123 Main St"}
        }
        self.assertTrue(self.validation_manager.validate_field_types(valid_data, schema))

        # Données invalides (type incorrect)
        invalid_data = {
            "name": 123,  # Devrait être une chaîne
            "age": "30"   # Devrait être un entier
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_field_types(invalid_data, schema)

    def test_validate_string_constraints(self):
        """Test de validation des contraintes sur les chaînes."""
        # Schéma avec contraintes sur les chaînes
        schema = {
            "name": {
                "type": "string",
                "min_length": 2,
                "max_length": 50,
                "pattern": "^[a-zA-Z ]+$"
            },
            "email": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            }
        }

        # Données valides
        valid_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        self.assertTrue(self.validation_manager.validate_string_constraints(valid_data, schema))

        # Données invalides
        invalid_data = {
            "name": "J",  # Trop court
            "email": "invalid-email"  # Format invalide
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_string_constraints(invalid_data, schema)

    def test_validate_number_constraints(self):
        """Test de validation des contraintes sur les nombres."""
        # Schéma avec contraintes sur les nombres
        schema = {
            "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 120
            },
            "price": {
                "type": "number",
                "minimum": 0,
                "maximum": 1000,
                "multiple_of": 0.01
            }
        }

        # Données valides
        valid_data = {
            "age": 30,
            "price": 99.99
        }
        self.assertTrue(self.validation_manager.validate_number_constraints(valid_data, schema))

        # Données invalides
        invalid_data = {
            "age": 150,  # Trop grand
            "price": -10  # Négatif
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_number_constraints(invalid_data, schema)

    def test_validate_array_constraints(self):
        """Test de validation des contraintes sur les tableaux."""
        # Schéma avec contraintes sur les tableaux
        schema = {
            "scores": {
                "type": "array",
                "min_items": 1,
                "max_items": 5,
                "items": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                }
            }
        }

        # Données valides
        valid_data = {
            "scores": [85, 90, 95]
        }
        self.assertTrue(self.validation_manager.validate_array_constraints(valid_data, schema))

        # Données invalides
        invalid_data = {
            "scores": [150, -10]  # Valeurs hors limites
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_array_constraints(invalid_data, schema)

    def test_validate_object_constraints(self):
        """Test de validation des contraintes sur les objets."""
        # Schéma avec contraintes sur les objets
        schema = {
            "address": {
                "type": "object",
                "required": ["street", "city"],
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip": {"type": "string", "pattern": "^\\d{5}$"}
                }
            }
        }

        # Données valides
        valid_data = {
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001"
            }
        }
        self.assertTrue(self.validation_manager.validate_object_constraints(valid_data, schema))

        # Données invalides
        invalid_data = {
            "address": {
                "street": "123 Main St"
                # Manque 'city'
            }
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_object_constraints(invalid_data, schema)

    def test_validate_custom_rules(self):
        """Test de validation avec des règles personnalisées."""
        # Règle personnalisée pour vérifier la date de naissance
        def validate_birth_date(value):
            birth_date = datetime.fromisoformat(value)
            age = (datetime.now() - birth_date).days / 365
            if age < 18:
                raise ValidationError("L'âge doit être d'au moins 18 ans")
            return True

        # Schéma avec règle personnalisée
        schema = {
            "birth_date": {
                "type": "datetime",
                "custom": validate_birth_date
            }
        }

        # Données valides
        valid_data = {
            "birth_date": (datetime.now().replace(year=datetime.now().year - 20)).isoformat()
        }
        self.assertTrue(self.validation_manager.validate_custom_rules(valid_data, schema))

        # Données invalides
        invalid_data = {
            "birth_date": (datetime.now().replace(year=datetime.now().year - 10)).isoformat()
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_custom_rules(invalid_data, schema)

    def test_validate_conditional_rules(self):
        """Test de validation avec des règles conditionnelles."""
        # Schéma avec règles conditionnelles
        schema = {
            "type": {"type": "string", "enum": ["individual", "company"]},
            "name": {"type": "string"},
            "company_name": {
                "type": "string",
                "required_if": {"type": "company"}
            },
            "tax_id": {
                "type": "string",
                "required_if": {"type": "company"}
            }
        }

        # Données valides pour un individu
        valid_individual = {
            "type": "individual",
            "name": "John Doe"
        }
        self.assertTrue(self.validation_manager.validate_conditional_rules(valid_individual, schema))

        # Données valides pour une entreprise
        valid_company = {
            "type": "company",
            "name": "John Doe",
            "company_name": "ACME Corp",
            "tax_id": "123456789"
        }
        self.assertTrue(self.validation_manager.validate_conditional_rules(valid_company, schema))

        # Données invalides (entreprise sans nom)
        invalid_company = {
            "type": "company",
            "name": "John Doe",
            "tax_id": "123456789"
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_conditional_rules(invalid_company, schema)

    def test_validate_dependencies(self):
        """Test de validation des dépendances entre champs."""
        # Schéma avec dépendances
        schema = {
            "payment_method": {"type": "string", "enum": ["credit_card", "bank_transfer"]},
            "credit_card": {
                "type": "object",
                "required_if": {"payment_method": "credit_card"},
                "properties": {
                    "number": {"type": "string"},
                    "expiry": {"type": "string"},
                    "cvv": {"type": "string"}
                }
            },
            "bank_account": {
                "type": "object",
                "required_if": {"payment_method": "bank_transfer"},
                "properties": {
                    "account_number": {"type": "string"},
                    "routing_number": {"type": "string"}
                }
            }
        }

        # Données valides pour carte de crédit
        valid_credit_card = {
            "payment_method": "credit_card",
            "credit_card": {
                "number": "4111111111111111",
                "expiry": "12/25",
                "cvv": "123"
            }
        }
        self.assertTrue(self.validation_manager.validate_dependencies(valid_credit_card, schema))

        # Données valides pour virement bancaire
        valid_bank_transfer = {
            "payment_method": "bank_transfer",
            "bank_account": {
                "account_number": "123456789",
                "routing_number": "987654321"
            }
        }
        self.assertTrue(self.validation_manager.validate_dependencies(valid_bank_transfer, schema))

        # Données invalides (carte de crédit sans numéro)
        invalid_credit_card = {
            "payment_method": "credit_card",
            "credit_card": {
                "expiry": "12/25",
                "cvv": "123"
            }
        }
        with self.assertRaises(ValidationError):
            self.validation_manager.validate_dependencies(invalid_credit_card, schema)

if __name__ == '__main__':
    unittest.main() 