import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alder_sav.database.base import Base
from alder_sav.managers.repair_manager import RepairManager
from alder_sav.managers.client_manager import ClientManager
from alder_sav.managers.user_manager import UserManager
from alder_sav.managers.notification_manager import NotificationManager
from alder_sav.utils.exceptions import (
    RepairError, ClientError, UserError, NotificationError
)

class TestWorkflow(unittest.TestCase):
    """Tests d'intégration des workflows principaux"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer une base de données de test en mémoire
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialiser les gestionnaires
        self.repair_manager = RepairManager(self.session)
        self.client_manager = ClientManager(self.session)
        self.user_manager = UserManager(self.session)
        self.notification_manager = NotificationManager(self.session)
        
        # Créer un utilisateur de test
        self.technician = self.user_manager.create_user(
            username="tech_test",
            password="password123",
            email="tech@test.com",
            role_id=1,
            first_name="Tech",
            last_name="Test"
        )
        
        # Créer un client de test
        self.client = self.client_manager.create_client({
            'name': 'Client Test',
            'email': 'client@test.com',
            'phone': '0123456789',
            'address': '123 Test Street'
        })
    
    def tearDown(self):
        """Nettoyage après les tests"""
        self.session.close()
        Base.metadata.drop_all(self.engine)
    
    def test_repair_workflow(self):
        """Test du workflow complet d'une réparation"""
        # 1. Création de la réparation
        repair = self.repair_manager.create_repair({
            'client_id': self.client.id,
            'device_id': 1,
            'type': 'warranty',
            'priority': 'medium',
            'description': 'Test repair workflow',
            'estimated_cost': 100.0,
            'estimated_completion_date': (datetime.now() + timedelta(days=7)).isoformat()
        })
        
        self.assertIsNotNone(repair.id)
        self.assertEqual(repair.status, 'pending')
        
        # 2. Attribution à un technicien
        repair = self.repair_manager.update_repair(repair.id, {
            'technician_id': self.technician.id,
            'status': 'in_progress',
            'diagnosis': 'Test diagnosis'
        })
        
        self.assertEqual(repair.technician_id, self.technician.id)
        self.assertEqual(repair.status, 'in_progress')
        
        # 3. Ajout de pièces
        repair_part = self.repair_manager.add_repair_part(
            repair.id,
            part_id=1,
            quantity=2,
            unit_price=50.0
        )
        
        self.assertEqual(repair_part.repair_id, repair.id)
        self.assertEqual(repair_part.total_price, 100.0)
        
        # 4. Ajout de notes
        note = self.repair_manager.add_repair_note(
            repair.id,
            author_id=self.technician.id,
            content='Test note'
        )
        
        self.assertEqual(note.repair_id, repair.id)
        self.assertEqual(note.author_id, self.technician.id)
        
        # 5. Finalisation de la réparation
        repair = self.repair_manager.complete_repair(
            repair.id,
            solution='Test solution',
            actual_cost=150.0
        )
        
        self.assertEqual(repair.status, 'completed')
        self.assertEqual(repair.actual_cost, 150.0)
        self.assertIsNotNone(repair.completion_date)
    
    def test_client_workflow(self):
        """Test du workflow complet d'un client"""
        # 1. Création du client
        client = self.client_manager.create_client({
            'name': 'New Client',
            'email': 'new@client.com',
            'phone': '9876543210',
            'address': '456 New Street'
        })
        
        self.assertIsNotNone(client.id)
        
        # 2. Ajout d'un appareil
        device = self.client_manager.add_device(
            client.id,
            brand='Test Brand',
            model='Test Model',
            serial_number='TEST123',
            purchase_date=datetime.now().isoformat()
        )
        
        self.assertEqual(device.client_id, client.id)
        
        # 3. Mise à jour des informations
        client = self.client_manager.update_client(client.id, {
            'phone': '1112223333',
            'notes': 'Test notes'
        })
        
        self.assertEqual(client.phone, '1112223333')
        self.assertEqual(client.notes, 'Test notes')
        
        # 4. Vérification des statistiques
        stats = self.client_manager.get_client_statistics(client.id)
        
        self.assertEqual(stats['device_count'], 1)
        self.assertEqual(stats['repair_count'], 0)
    
    def test_notification_workflow(self):
        """Test du workflow complet des notifications"""
        # 1. Création d'un template
        template = self.notification_manager.create_notification_template(
            name='Test Template',
            type='repair_status',
            subject='Test Subject',
            content='Test Content: {{ repair_id }}',
            variables=['repair_id']
        )
        
        self.assertIsNotNone(template.id)
        
        # 2. Création d'une notification
        notification = self.notification_manager.create_notification(
            recipient_id=self.client.id,
            type='repair_status',
            content='Test notification',
            data={'repair_id': 1}
        )
        
        self.assertIsNotNone(notification.id)
        self.assertEqual(notification.status, 'pending')
        
        # 3. Envoi de la notification
        self.notification_manager.send_notification(notification.id)
        
        notification = self.notification_manager.get_notification(notification.id)
        self.assertEqual(notification.status, 'sent')
        self.assertIsNotNone(notification.sent_at)
    
    def test_user_workflow(self):
        """Test du workflow complet d'un utilisateur"""
        # 1. Création d'un rôle
        role = self.user_manager.create_role(
            name='Test Role',
            description='Test role description',
            permissions=['view_repairs', 'edit_repairs']
        )
        
        self.assertIsNotNone(role.id)
        
        # 2. Création d'un utilisateur
        user = self.user_manager.create_user(
            username='test_user',
            password='password123',
            email='user@test.com',
            role_id=role.id,
            first_name='Test',
            last_name='User'
        )
        
        self.assertIsNotNone(user.id)
        
        # 3. Vérification des permissions
        self.assertTrue(
            self.user_manager.check_permission(user.id, 'view_repairs')
        )
        self.assertTrue(
            self.user_manager.check_permission(user.id, 'edit_repairs')
        )
        self.assertFalse(
            self.user_manager.check_permission(user.id, 'delete_repairs')
        )
        
        # 4. Changement de mot de passe
        self.user_manager.change_password(
            user.id,
            'password123',
            'newpassword123'
        )
        
        # 5. Authentification
        authenticated_user = self.user_manager.authenticate(
            'test_user',
            'newpassword123'
        )
        
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.id, user.id)

if __name__ == '__main__':
    unittest.main() 