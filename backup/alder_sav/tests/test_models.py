import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import tempfile
import shutil

from alder_sav.database.models import (
    Base, Client, FRP, Product, Document, Supplier, Carrier, User, Role, Permission,
    Backup, Archive, Notification, Statistics, Export, Import, Log, Setting
)
from alder_sav.utils.exceptions import ValidationError

class TestModels(unittest.TestCase):
    """Tests unitaires pour les modèles de données."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Création d'une base de données temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """Nettoyage après les tests."""
        self.session.close()
        shutil.rmtree(self.temp_dir)

    def test_client_creation(self):
        """Test de création d'un client."""
        client = Client(
            name="Test Client",
            type="particulier",
            status="actif",
            email="test@example.com",
            phone="0123456789",
            address="123 Test Street",
            postal_code="75000",
            city="Paris",
            country="France",
            siret="12345678901234",
            vat_number="FR12345678901",
            notes="Test notes"
        )
        self.session.add(client)
        self.session.commit()

        # Vérification
        saved_client = self.session.query(Client).first()
        self.assertEqual(saved_client.name, "Test Client")
        self.assertEqual(saved_client.type, "particulier")
        self.assertEqual(saved_client.status, "actif")
        self.assertEqual(saved_client.email, "test@example.com")
        self.assertEqual(saved_client.phone, "0123456789")
        self.assertEqual(saved_client.address, "123 Test Street")
        self.assertEqual(saved_client.postal_code, "75000")
        self.assertEqual(saved_client.city, "Paris")
        self.assertEqual(saved_client.country, "France")
        self.assertEqual(saved_client.siret, "12345678901234")
        self.assertEqual(saved_client.vat_number, "FR12345678901")
        self.assertEqual(saved_client.notes, "Test notes")

    def test_frp_creation(self):
        """Test de création d'une FRP."""
        # Création du client
        client = Client(name="Test Client")
        self.session.add(client)
        self.session.commit()

        # Création de la FRP
        frp = FRP(
            number="FRP-2024-001",
            client_id=client.id,
            type="retour",
            status="en_cours",
            priority="normale",
            creation_date=datetime.now(),
            processing_date=datetime.now(),
            resolution_date=datetime.now(),
            notes="Test notes"
        )
        self.session.add(frp)
        self.session.commit()

        # Vérification
        saved_frp = self.session.query(FRP).first()
        self.assertEqual(saved_frp.number, "FRP-2024-001")
        self.assertEqual(saved_frp.client_id, client.id)
        self.assertEqual(saved_frp.type, "retour")
        self.assertEqual(saved_frp.status, "en_cours")
        self.assertEqual(saved_frp.priority, "normale")
        self.assertIsNotNone(saved_frp.creation_date)
        self.assertIsNotNone(saved_frp.processing_date)
        self.assertIsNotNone(saved_frp.resolution_date)
        self.assertEqual(saved_frp.notes, "Test notes")

    def test_product_creation(self):
        """Test de création d'un produit."""
        # Création du client et de la FRP
        client = Client(name="Test Client")
        self.session.add(client)
        self.session.commit()

        frp = FRP(number="FRP-2024-001", client_id=client.id)
        self.session.add(frp)
        self.session.commit()

        # Création du produit
        product = Product(
            frp_id=frp.id,
            name="Test Product",
            reference="REF-001",
            quantity=1,
            unit_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
            condition="neuf",
            notes="Test notes"
        )
        self.session.add(product)
        self.session.commit()

        # Vérification
        saved_product = self.session.query(Product).first()
        self.assertEqual(saved_product.frp_id, frp.id)
        self.assertEqual(saved_product.name, "Test Product")
        self.assertEqual(saved_product.reference, "REF-001")
        self.assertEqual(saved_product.quantity, 1)
        self.assertEqual(saved_product.unit_price, Decimal("100.00"))
        self.assertEqual(saved_product.total_price, Decimal("100.00"))
        self.assertEqual(saved_product.condition, "neuf")
        self.assertEqual(saved_product.notes, "Test notes")

    def test_document_creation(self):
        """Test de création d'un document."""
        # Création du client et de la FRP
        client = Client(name="Test Client")
        self.session.add(client)
        self.session.commit()

        frp = FRP(number="FRP-2024-001", client_id=client.id)
        self.session.add(frp)
        self.session.commit()

        # Création du document
        document = Document(
            frp_id=frp.id,
            name="Test Document",
            type="facture",
            path="/path/to/document.pdf",
            size=1024,
            mime_type="application/pdf",
            upload_date=datetime.now(),
            notes="Test notes"
        )
        self.session.add(document)
        self.session.commit()

        # Vérification
        saved_document = self.session.query(Document).first()
        self.assertEqual(saved_document.frp_id, frp.id)
        self.assertEqual(saved_document.name, "Test Document")
        self.assertEqual(saved_document.type, "facture")
        self.assertEqual(saved_document.path, "/path/to/document.pdf")
        self.assertEqual(saved_document.size, 1024)
        self.assertEqual(saved_document.mime_type, "application/pdf")
        self.assertIsNotNone(saved_document.upload_date)
        self.assertEqual(saved_document.notes, "Test notes")

    def test_supplier_creation(self):
        """Test de création d'un fournisseur."""
        supplier = Supplier(
            name="Test Supplier",
            status="actif",
            email="test@example.com",
            phone="0123456789",
            address="123 Test Street",
            postal_code="75000",
            city="Paris",
            country="France",
            siret="12345678901234",
            vat_number="FR12345678901",
            notes="Test notes"
        )
        self.session.add(supplier)
        self.session.commit()

        # Vérification
        saved_supplier = self.session.query(Supplier).first()
        self.assertEqual(saved_supplier.name, "Test Supplier")
        self.assertEqual(saved_supplier.status, "actif")
        self.assertEqual(saved_supplier.email, "test@example.com")
        self.assertEqual(saved_supplier.phone, "0123456789")
        self.assertEqual(saved_supplier.address, "123 Test Street")
        self.assertEqual(saved_supplier.postal_code, "75000")
        self.assertEqual(saved_supplier.city, "Paris")
        self.assertEqual(saved_supplier.country, "France")
        self.assertEqual(saved_supplier.siret, "12345678901234")
        self.assertEqual(saved_supplier.vat_number, "FR12345678901")
        self.assertEqual(saved_supplier.notes, "Test notes")

    def test_carrier_creation(self):
        """Test de création d'un transporteur."""
        carrier = Carrier(
            name="Test Carrier",
            status="actif",
            email="test@example.com",
            phone="0123456789",
            address="123 Test Street",
            postal_code="75000",
            city="Paris",
            country="France",
            siret="12345678901234",
            vat_number="FR12345678901",
            notes="Test notes"
        )
        self.session.add(carrier)
        self.session.commit()

        # Vérification
        saved_carrier = self.session.query(Carrier).first()
        self.assertEqual(saved_carrier.name, "Test Carrier")
        self.assertEqual(saved_carrier.status, "actif")
        self.assertEqual(saved_carrier.email, "test@example.com")
        self.assertEqual(saved_carrier.phone, "0123456789")
        self.assertEqual(saved_carrier.address, "123 Test Street")
        self.assertEqual(saved_carrier.postal_code, "75000")
        self.assertEqual(saved_carrier.city, "Paris")
        self.assertEqual(saved_carrier.country, "France")
        self.assertEqual(saved_carrier.siret, "12345678901234")
        self.assertEqual(saved_carrier.vat_number, "FR12345678901")
        self.assertEqual(saved_carrier.notes, "Test notes")

    def test_user_creation(self):
        """Test de création d'un utilisateur."""
        # Création du rôle
        role = Role(name="admin", description="Administrateur")
        self.session.add(role)
        self.session.commit()

        # Création de l'utilisateur
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password",
            salt="salt",
            role_id=role.id,
            status="actif",
            last_login=datetime.now(),
            notes="Test notes"
        )
        self.session.add(user)
        self.session.commit()

        # Vérification
        saved_user = self.session.query(User).first()
        self.assertEqual(saved_user.username, "test_user")
        self.assertEqual(saved_user.email, "test@example.com")
        self.assertEqual(saved_user.password_hash, "hashed_password")
        self.assertEqual(saved_user.salt, "salt")
        self.assertEqual(saved_user.role_id, role.id)
        self.assertEqual(saved_user.status, "actif")
        self.assertIsNotNone(saved_user.last_login)
        self.assertEqual(saved_user.notes, "Test notes")

    def test_permission_creation(self):
        """Test de création d'une permission."""
        permission = Permission(
            name="test_permission",
            description="Test permission",
            module="test_module",
            action="test_action"
        )
        self.session.add(permission)
        self.session.commit()

        # Vérification
        saved_permission = self.session.query(Permission).first()
        self.assertEqual(saved_permission.name, "test_permission")
        self.assertEqual(saved_permission.description, "Test permission")
        self.assertEqual(saved_permission.module, "test_module")
        self.assertEqual(saved_permission.action, "test_action")

    def test_backup_creation(self):
        """Test de création d'une sauvegarde."""
        backup = Backup(
            filename="test_backup.db",
            path="/path/to/backup.db",
            size=1024,
            creation_date=datetime.now(),
            type="automatique",
            status="termine",
            notes="Test notes"
        )
        self.session.add(backup)
        self.session.commit()

        # Vérification
        saved_backup = self.session.query(Backup).first()
        self.assertEqual(saved_backup.filename, "test_backup.db")
        self.assertEqual(saved_backup.path, "/path/to/backup.db")
        self.assertEqual(saved_backup.size, 1024)
        self.assertIsNotNone(saved_backup.creation_date)
        self.assertEqual(saved_backup.type, "automatique")
        self.assertEqual(saved_backup.status, "termine")
        self.assertEqual(saved_backup.notes, "Test notes")

    def test_archive_creation(self):
        """Test de création d'une archive."""
        archive = Archive(
            filename="test_archive.zip",
            path="/path/to/archive.zip",
            size=1024,
            creation_date=datetime.now(),
            type="mensuelle",
            status="termine",
            notes="Test notes"
        )
        self.session.add(archive)
        self.session.commit()

        # Vérification
        saved_archive = self.session.query(Archive).first()
        self.assertEqual(saved_archive.filename, "test_archive.zip")
        self.assertEqual(saved_archive.path, "/path/to/archive.zip")
        self.assertEqual(saved_archive.size, 1024)
        self.assertIsNotNone(saved_archive.creation_date)
        self.assertEqual(saved_archive.type, "mensuelle")
        self.assertEqual(saved_archive.status, "termine")
        self.assertEqual(saved_archive.notes, "Test notes")

    def test_notification_creation(self):
        """Test de création d'une notification."""
        notification = Notification(
            type="email",
            recipient="test@example.com",
            subject="Test Subject",
            content="Test Content",
            status="envoyee",
            sent_date=datetime.now(),
            notes="Test notes"
        )
        self.session.add(notification)
        self.session.commit()

        # Vérification
        saved_notification = self.session.query(Notification).first()
        self.assertEqual(saved_notification.type, "email")
        self.assertEqual(saved_notification.recipient, "test@example.com")
        self.assertEqual(saved_notification.subject, "Test Subject")
        self.assertEqual(saved_notification.content, "Test Content")
        self.assertEqual(saved_notification.status, "envoyee")
        self.assertIsNotNone(saved_notification.sent_date)
        self.assertEqual(saved_notification.notes, "Test notes")

    def test_statistics_creation(self):
        """Test de création d'une statistique."""
        statistics = Statistics(
            type="frp",
            period="jour",
            data={"total": 10, "en_cours": 5, "termine": 5},
            creation_date=datetime.now(),
            notes="Test notes"
        )
        self.session.add(statistics)
        self.session.commit()

        # Vérification
        saved_statistics = self.session.query(Statistics).first()
        self.assertEqual(saved_statistics.type, "frp")
        self.assertEqual(saved_statistics.period, "jour")
        self.assertEqual(saved_statistics.data, {"total": 10, "en_cours": 5, "termine": 5})
        self.assertIsNotNone(saved_statistics.creation_date)
        self.assertEqual(saved_statistics.notes, "Test notes")

    def test_export_creation(self):
        """Test de création d'un export."""
        export = Export(
            filename="test_export.xlsx",
            path="/path/to/export.xlsx",
            size=1024,
            creation_date=datetime.now(),
            type="frp",
            format="xlsx",
            status="termine",
            notes="Test notes"
        )
        self.session.add(export)
        self.session.commit()

        # Vérification
        saved_export = self.session.query(Export).first()
        self.assertEqual(saved_export.filename, "test_export.xlsx")
        self.assertEqual(saved_export.path, "/path/to/export.xlsx")
        self.assertEqual(saved_export.size, 1024)
        self.assertIsNotNone(saved_export.creation_date)
        self.assertEqual(saved_export.type, "frp")
        self.assertEqual(saved_export.format, "xlsx")
        self.assertEqual(saved_export.status, "termine")
        self.assertEqual(saved_export.notes, "Test notes")

    def test_import_creation(self):
        """Test de création d'un import."""
        import_data = Import(
            filename="test_import.xlsx",
            path="/path/to/import.xlsx",
            size=1024,
            creation_date=datetime.now(),
            type="frp",
            format="xlsx",
            status="termine",
            notes="Test notes"
        )
        self.session.add(import_data)
        self.session.commit()

        # Vérification
        saved_import = self.session.query(Import).first()
        self.assertEqual(saved_import.filename, "test_import.xlsx")
        self.assertEqual(saved_import.path, "/path/to/import.xlsx")
        self.assertEqual(saved_import.size, 1024)
        self.assertIsNotNone(saved_import.creation_date)
        self.assertEqual(saved_import.type, "frp")
        self.assertEqual(saved_import.format, "xlsx")
        self.assertEqual(saved_import.status, "termine")
        self.assertEqual(saved_import.notes, "Test notes")

    def test_log_creation(self):
        """Test de création d'un log."""
        log = Log(
            level="info",
            message="Test message",
            timestamp=datetime.now(),
            module="test_module",
            function="test_function",
            line=1,
            notes="Test notes"
        )
        self.session.add(log)
        self.session.commit()

        # Vérification
        saved_log = self.session.query(Log).first()
        self.assertEqual(saved_log.level, "info")
        self.assertEqual(saved_log.message, "Test message")
        self.assertIsNotNone(saved_log.timestamp)
        self.assertEqual(saved_log.module, "test_module")
        self.assertEqual(saved_log.function, "test_function")
        self.assertEqual(saved_log.line, 1)
        self.assertEqual(saved_log.notes, "Test notes")

    def test_setting_creation(self):
        """Test de création d'un paramètre."""
        setting = Setting(
            key="test_key",
            value="test_value",
            type="string",
            description="Test setting",
            module="test_module",
            notes="Test notes"
        )
        self.session.add(setting)
        self.session.commit()

        # Vérification
        saved_setting = self.session.query(Setting).first()
        self.assertEqual(saved_setting.key, "test_key")
        self.assertEqual(saved_setting.value, "test_value")
        self.assertEqual(saved_setting.type, "string")
        self.assertEqual(saved_setting.description, "Test setting")
        self.assertEqual(saved_setting.module, "test_module")
        self.assertEqual(saved_setting.notes, "Test notes")

if __name__ == '__main__':
    unittest.main() 