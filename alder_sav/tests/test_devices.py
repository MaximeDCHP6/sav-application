import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.devices import DeviceManager
from alder_sav.utils.exceptions import ValidationError

class TestDeviceManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire d'appareils."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.devices_dir = Path(self.temp_dir) / "devices"
        self.devices_dir.mkdir()
        
        # Initialisation du gestionnaire d'appareils
        self.device_manager = DeviceManager(self.devices_dir)
        
        # Données de test
        self.device_data = {
            "reference": "DEV-001",
            "type": "smartphone",
            "status": "active",
            "brand": "Apple",
            "model": "iPhone 13",
            "serial_number": "SN123456789",
            "imei": "123456789012345",
            "specifications": {
                "color": "noir",
                "storage": "128GB",
                "ram": "4GB",
                "os_version": "iOS 15.0",
                "battery_health": 100,
                "screen_size": "6.1 pouces",
                "resolution": "2532x1170"
            },
            "purchase": {
                "date": "2023-01-01",
                "price": Decimal("899.99"),
                "currency": "EUR",
                "store": "Apple Store",
                "invoice_number": "INV-001"
            },
            "warranty": {
                "type": "standard",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "status": "active",
                "provider": "Apple",
                "coverage": ["hardware", "software", "battery"]
            },
            "repairs": [
                {
                    "id": "REP-001",
                    "date": datetime.now().isoformat(),
                    "type": "screen",
                    "status": "completed",
                    "cost": Decimal("199.99"),
                    "description": "Remplacement de l'écran"
                }
            ],
            "maintenance": {
                "last_check": datetime.now().isoformat(),
                "next_check": (datetime.now() + timedelta(days=180)).isoformat(),
                "battery_cycles": 50,
                "software_updates": [
                    {
                        "version": "15.1",
                        "date": "2023-02-01",
                        "status": "installed"
                    }
                ]
            },
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont",
                "contact": {
                    "email": "jean.dupont@example.com",
                    "phone": "+33123456789"
                }
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Appareil en bon état",
                "tags": ["premium", "new"]
            }
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_device(self):
        """Test de création d'appareil."""
        # Création de l'appareil
        device_obj = self.device_manager.create_device(self.device_data)
        
        # Vérification
        self.assertEqual(device_obj["reference"], "DEV-001")
        self.assertEqual(device_obj["type"], "smartphone")
        self.assertEqual(device_obj["status"], "active")
        self.assertEqual(device_obj["brand"], "Apple")
        self.assertEqual(len(device_obj["repairs"]), 1)
        self.assertTrue("id" in device_obj)
        self.assertTrue("creation_date" in device_obj)

    def test_get_device(self):
        """Test de récupération d'appareil."""
        # Création de l'appareil
        device_obj = self.device_manager.create_device(self.device_data)
        
        # Récupération de l'appareil
        retrieved_device = self.device_manager.get_device(device_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_device["reference"], "DEV-001")
        self.assertEqual(retrieved_device["model"], "iPhone 13")
        self.assertEqual(retrieved_device["specifications"]["storage"], "128GB")
        self.assertEqual(retrieved_device["warranty"]["status"], "active")

    def test_update_device(self):
        """Test de mise à jour d'appareil."""
        # Création de l'appareil
        device_obj = self.device_manager.create_device(self.device_data)
        
        # Mise à jour de l'appareil
        updated_data = {
            "status": "in_repair",
            "specifications": {
                "battery_health": 95,
                "os_version": "iOS 15.2"
            },
            "maintenance": {
                "battery_cycles": 75,
                "last_check": datetime.now().isoformat()
            },
            "metadata": {
                "updated_at": datetime.now().isoformat()
            }
        }
        updated_device = self.device_manager.update_device(device_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_device["status"], "in_repair")
        self.assertEqual(updated_device["specifications"]["battery_health"], 95)
        self.assertEqual(updated_device["maintenance"]["battery_cycles"], 75)

    def test_delete_device(self):
        """Test de suppression d'appareil."""
        # Création de l'appareil
        device_obj = self.device_manager.create_device(self.device_data)
        
        # Suppression de l'appareil
        self.device_manager.delete_device(device_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.device_manager.get_device(device_obj["id"])

    def test_get_device_by_type(self):
        """Test de récupération des appareils par type."""
        # Création d'appareils de différents types
        self.device_manager.create_device({
            **self.device_data,
            "type": "smartphone"
        })
        self.device_manager.create_device({
            **self.device_data,
            "reference": "DEV-002",
            "type": "tablet"
        })
        
        # Récupération des appareils par type
        smartphone_devices = self.device_manager.get_devices_by_type("smartphone")
        tablet_devices = self.device_manager.get_devices_by_type("tablet")
        
        # Vérification
        self.assertEqual(len(smartphone_devices), 1)
        self.assertEqual(len(tablet_devices), 1)
        self.assertEqual(smartphone_devices[0]["type"], "smartphone")
        self.assertEqual(tablet_devices[0]["type"], "tablet")

    def test_get_device_by_status(self):
        """Test de récupération des appareils par statut."""
        # Création d'appareils avec différents statuts
        self.device_manager.create_device({
            **self.device_data,
            "status": "active"
        })
        self.device_manager.create_device({
            **self.device_data,
            "reference": "DEV-002",
            "status": "in_repair"
        })
        
        # Récupération des appareils par statut
        active_devices = self.device_manager.get_devices_by_status("active")
        repair_devices = self.device_manager.get_devices_by_status("in_repair")
        
        # Vérification
        self.assertEqual(len(active_devices), 1)
        self.assertEqual(len(repair_devices), 1)
        self.assertEqual(active_devices[0]["status"], "active")
        self.assertEqual(repair_devices[0]["status"], "in_repair")

    def test_get_device_by_client(self):
        """Test de récupération des appareils par client."""
        # Création d'appareils pour différents clients
        self.device_manager.create_device({
            **self.device_data,
            "client": {
                "id": "CLI-001",
                "name": "Jean Dupont"
            }
        })
        self.device_manager.create_device({
            **self.device_data,
            "reference": "DEV-002",
            "client": {
                "id": "CLI-002",
                "name": "Marie Martin"
            }
        })
        
        # Récupération des appareils par client
        client1_devices = self.device_manager.get_devices_by_client("CLI-001")
        client2_devices = self.device_manager.get_devices_by_client("CLI-002")
        
        # Vérification
        self.assertEqual(len(client1_devices), 1)
        self.assertEqual(len(client2_devices), 1)
        self.assertEqual(client1_devices[0]["client"]["id"], "CLI-001")
        self.assertEqual(client2_devices[0]["client"]["id"], "CLI-002")

    def test_validate_device(self):
        """Test de validation d'appareil."""
        # Création d'un appareil valide
        device_obj = self.device_manager.create_device(self.device_data)
        
        # Validation de l'appareil
        is_valid = self.device_manager.validate_device(device_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_device_summary(self):
        """Test de récupération du résumé d'appareil."""
        # Création de l'appareil
        device_obj = self.device_manager.create_device(self.device_data)
        
        # Récupération du résumé
        summary = self.device_manager.get_device_summary(device_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("brand" in summary)
        self.assertTrue("model" in summary)
        self.assertTrue("specifications" in summary)
        self.assertTrue("warranty" in summary)
        self.assertTrue("repairs" in summary)
        self.assertTrue("maintenance" in summary)
        self.assertTrue("client" in summary)

    def test_invalid_device_type(self):
        """Test avec un type d'appareil invalide."""
        with self.assertRaises(ValidationError):
            self.device_manager.create_device({
                **self.device_data,
                "type": "invalid_type"
            })

    def test_invalid_device_status(self):
        """Test avec un statut d'appareil invalide."""
        with self.assertRaises(ValidationError):
            self.device_manager.create_device({
                **self.device_data,
                "status": "invalid_status"
            })

    def test_invalid_device_dir(self):
        """Test avec un répertoire d'appareils invalide."""
        with self.assertRaises(ValidationError):
            DeviceManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 