import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
import json
from decimal import Decimal

from alder_sav.utils.documents import DocumentManager
from alder_sav.utils.exceptions import ValidationError

class TestDocumentManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de documents."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.documents_dir = Path(self.temp_dir) / "documents"
        self.documents_dir.mkdir()
        
        # Initialisation du gestionnaire de documents
        self.document_manager = DocumentManager(self.documents_dir)
        
        # Données de test
        self.document_data = {
            "reference": "DOC-001",
            "type": "invoice",
            "status": "active",
            "category": "financial",
            "title": "Facture #12345",
            "description": "Facture pour réparation iPhone 13",
            "content": {
                "format": "pdf",
                "size": 1024,
                "pages": 1,
                "url": "https://example.com/documents/invoice-12345.pdf"
            },
            "metadata": {
                "author": {
                    "id": "USER-001",
                    "name": "Pierre Martin",
                    "role": "technician"
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0",
                "language": "fr",
                "tags": ["facture", "réparation", "iPhone"]
            },
            "permissions": {
                "read": ["admin", "technician", "client"],
                "write": ["admin"],
                "delete": ["admin"]
            },
            "related_entities": [
                {
                    "type": "repair",
                    "id": "REP-001",
                    "reference": "REP-001"
                },
                {
                    "type": "client",
                    "id": "CLI-001",
                    "reference": "CLI-001"
                }
            ],
            "history": [
                {
                    "date": datetime.now().isoformat(),
                    "action": "created",
                    "user": {
                        "id": "USER-001",
                        "name": "Pierre Martin"
                    },
                    "notes": "Document créé"
                }
            ]
        }

    def tearDown(self):
        """Nettoyage après les tests."""
        shutil.rmtree(self.temp_dir)

    def test_create_document(self):
        """Test de création de document."""
        # Création du document
        document_obj = self.document_manager.create_document(self.document_data)
        
        # Vérification
        self.assertEqual(document_obj["reference"], "DOC-001")
        self.assertEqual(document_obj["type"], "invoice")
        self.assertEqual(document_obj["status"], "active")
        self.assertEqual(document_obj["category"], "financial")
        self.assertEqual(document_obj["title"], "Facture #12345")
        self.assertTrue("id" in document_obj)
        self.assertTrue("creation_date" in document_obj)

    def test_get_document(self):
        """Test de récupération de document."""
        # Création du document
        document_obj = self.document_manager.create_document(self.document_data)
        
        # Récupération du document
        retrieved_document = self.document_manager.get_document(document_obj["id"])
        
        # Vérification
        self.assertEqual(retrieved_document["reference"], "DOC-001")
        self.assertEqual(retrieved_document["content"]["format"], "pdf")
        self.assertEqual(retrieved_document["metadata"]["language"], "fr")
        self.assertEqual(len(retrieved_document["related_entities"]), 2)

    def test_update_document(self):
        """Test de mise à jour de document."""
        # Création du document
        document_obj = self.document_manager.create_document(self.document_data)
        
        # Mise à jour du document
        updated_data = {
            "status": "archived",
            "content": {
                "format": "pdf",
                "size": 2048,
                "pages": 2,
                "url": "https://example.com/documents/invoice-12345-v2.pdf"
            },
            "metadata": {
                "updated_at": datetime.now().isoformat(),
                "version": "2.0"
            },
            "history": [
                {
                    "date": datetime.now().isoformat(),
                    "action": "updated",
                    "user": {
                        "id": "USER-001",
                        "name": "Pierre Martin"
                    },
                    "notes": "Document mis à jour"
                }
            ]
        }
        updated_document = self.document_manager.update_document(document_obj["id"], updated_data)
        
        # Vérification
        self.assertEqual(updated_document["status"], "archived")
        self.assertEqual(updated_document["content"]["size"], 2048)
        self.assertEqual(updated_document["metadata"]["version"], "2.0")
        self.assertEqual(len(updated_document["history"]), 2)

    def test_delete_document(self):
        """Test de suppression de document."""
        # Création du document
        document_obj = self.document_manager.create_document(self.document_data)
        
        # Suppression du document
        self.document_manager.delete_document(document_obj["id"])
        
        # Vérification
        with self.assertRaises(ValidationError):
            self.document_manager.get_document(document_obj["id"])

    def test_get_document_by_type(self):
        """Test de récupération des documents par type."""
        # Création de documents de différents types
        self.document_manager.create_document({
            **self.document_data,
            "type": "invoice"
        })
        self.document_manager.create_document({
            **self.document_data,
            "reference": "DOC-002",
            "type": "report"
        })
        
        # Récupération des documents par type
        invoice_documents = self.document_manager.get_documents_by_type("invoice")
        report_documents = self.document_manager.get_documents_by_type("report")
        
        # Vérification
        self.assertEqual(len(invoice_documents), 1)
        self.assertEqual(len(report_documents), 1)
        self.assertEqual(invoice_documents[0]["type"], "invoice")
        self.assertEqual(report_documents[0]["type"], "report")

    def test_get_document_by_status(self):
        """Test de récupération des documents par statut."""
        # Création de documents avec différents statuts
        self.document_manager.create_document({
            **self.document_data,
            "status": "active"
        })
        self.document_manager.create_document({
            **self.document_data,
            "reference": "DOC-002",
            "status": "archived"
        })
        
        # Récupération des documents par statut
        active_documents = self.document_manager.get_documents_by_status("active")
        archived_documents = self.document_manager.get_documents_by_status("archived")
        
        # Vérification
        self.assertEqual(len(active_documents), 1)
        self.assertEqual(len(archived_documents), 1)
        self.assertEqual(active_documents[0]["status"], "active")
        self.assertEqual(archived_documents[0]["status"], "archived")

    def test_get_document_by_category(self):
        """Test de récupération des documents par catégorie."""
        # Création de documents de différentes catégories
        self.document_manager.create_document({
            **self.document_data,
            "category": "financial"
        })
        self.document_manager.create_document({
            **self.document_data,
            "reference": "DOC-002",
            "category": "technical"
        })
        
        # Récupération des documents par catégorie
        financial_documents = self.document_manager.get_documents_by_category("financial")
        technical_documents = self.document_manager.get_documents_by_category("technical")
        
        # Vérification
        self.assertEqual(len(financial_documents), 1)
        self.assertEqual(len(technical_documents), 1)
        self.assertEqual(financial_documents[0]["category"], "financial")
        self.assertEqual(technical_documents[0]["category"], "technical")

    def test_validate_document(self):
        """Test de validation de document."""
        # Création d'un document valide
        document_obj = self.document_manager.create_document(self.document_data)
        
        # Validation du document
        is_valid = self.document_manager.validate_document(document_obj["id"])
        
        # Vérification
        self.assertTrue(is_valid)

    def test_get_document_summary(self):
        """Test de récupération du résumé de document."""
        # Création du document
        document_obj = self.document_manager.create_document(self.document_data)
        
        # Récupération du résumé
        summary = self.document_manager.get_document_summary(document_obj["id"])
        
        # Vérification
        self.assertTrue("reference" in summary)
        self.assertTrue("type" in summary)
        self.assertTrue("status" in summary)
        self.assertTrue("category" in summary)
        self.assertTrue("title" in summary)
        self.assertTrue("content" in summary)
        self.assertTrue("metadata" in summary)
        self.assertTrue("permissions" in summary)
        self.assertTrue("related_entities" in summary)
        self.assertTrue("history" in summary)

    def test_invalid_document_type(self):
        """Test avec un type de document invalide."""
        with self.assertRaises(ValidationError):
            self.document_manager.create_document({
                **self.document_data,
                "type": "invalid_type"
            })

    def test_invalid_document_status(self):
        """Test avec un statut de document invalide."""
        with self.assertRaises(ValidationError):
            self.document_manager.create_document({
                **self.document_data,
                "status": "invalid_status"
            })

    def test_invalid_document_dir(self):
        """Test avec un répertoire de documents invalide."""
        with self.assertRaises(ValidationError):
            DocumentManager(Path("invalid_path"))

if __name__ == '__main__':
    unittest.main() 