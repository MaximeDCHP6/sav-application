import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alder_sav.database.base import Base
from alder_sav.managers.repair_manager import RepairManager
from alder_sav.utils.exceptions import RepairError

class TestRepairManager(unittest.TestCase):
    """Tests pour le gestionnaire de réparations."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        # Créer une base de données de test en mémoire
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialiser le gestionnaire de réparations
        self.repair_manager = RepairManager(self.session)
        
        # Créer des données de test
        self.test_repair_data = {
            'client_id': 1,
            'device_id': 1,
            'type': 'warranty',
            'priority': 'medium',
            'description': 'Test repair',
            'estimated_cost': 100.0,
            'estimated_completion_date': (datetime.now() + timedelta(days=7)).isoformat()
        }
    
    def tearDown(self):
        """Nettoyage après les tests."""
        self.session.close()
        Base.metadata.drop_all(self.engine)
    
    def test_create_repair(self):
        """Test de création d'une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        
        self.assertIsNotNone(repair.id)
        self.assertEqual(repair.client_id, self.test_repair_data['client_id'])
        self.assertEqual(repair.device_id, self.test_repair_data['device_id'])
        self.assertEqual(repair.type, self.test_repair_data['type'])
        self.assertEqual(repair.priority, self.test_repair_data['priority'])
        self.assertEqual(repair.description, self.test_repair_data['description'])
        self.assertEqual(repair.estimated_cost, self.test_repair_data['estimated_cost'])
        self.assertEqual(repair.status, 'pending')
    
    def test_get_repair(self):
        """Test de récupération d'une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        retrieved_repair = self.repair_manager.get_repair(repair.id)
        
        self.assertEqual(retrieved_repair, repair)
    
    def test_get_nonexistent_repair(self):
        """Test de récupération d'une réparation inexistante."""
        with self.assertRaises(RepairError):
            self.repair_manager.get_repair(999)
    
    def test_update_repair(self):
        """Test de mise à jour d'une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        
        update_data = {
            'status': 'in_progress',
            'technician_id': 1,
            'diagnosis': 'Test diagnosis'
        }
        
        updated_repair = self.repair_manager.update_repair(repair.id, update_data)
        
        self.assertEqual(updated_repair.status, update_data['status'])
        self.assertEqual(updated_repair.technician_id, update_data['technician_id'])
        self.assertEqual(updated_repair.diagnosis, update_data['diagnosis'])
    
    def test_delete_repair(self):
        """Test de suppression d'une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        self.repair_manager.delete_repair(repair.id)
        
        with self.assertRaises(RepairError):
            self.repair_manager.get_repair(repair.id)
    
    def test_get_repairs_by_status(self):
        """Test de récupération des réparations par statut."""
        # Créer des réparations avec différents statuts
        repair1 = self.repair_manager.create_repair(self.test_repair_data)
        repair2 = self.repair_manager.create_repair(self.test_repair_data)
        
        self.repair_manager.update_repair(repair1.id, {'status': 'in_progress'})
        self.repair_manager.update_repair(repair2.id, {'status': 'completed'})
        
        pending_repairs = self.repair_manager.get_repairs_by_status('pending')
        in_progress_repairs = self.repair_manager.get_repairs_by_status('in_progress')
        completed_repairs = self.repair_manager.get_repairs_by_status('completed')
        
        self.assertEqual(len(pending_repairs), 0)
        self.assertEqual(len(in_progress_repairs), 1)
        self.assertEqual(len(completed_repairs), 1)
    
    def test_get_repairs_by_client(self):
        """Test de récupération des réparations d'un client."""
        # Créer des réparations pour différents clients
        repair1 = self.repair_manager.create_repair(self.test_repair_data)
        repair2 = self.repair_manager.create_repair({
            **self.test_repair_data,
            'client_id': 2
        })
        
        client1_repairs = self.repair_manager.get_repairs_by_client(1)
        client2_repairs = self.repair_manager.get_repairs_by_client(2)
        
        self.assertEqual(len(client1_repairs), 1)
        self.assertEqual(len(client2_repairs), 1)
        self.assertEqual(client1_repairs[0].client_id, 1)
        self.assertEqual(client2_repairs[0].client_id, 2)
    
    def test_get_repairs_by_technician(self):
        """Test de récupération des réparations d'un technicien."""
        # Créer des réparations pour différents techniciens
        repair1 = self.repair_manager.create_repair(self.test_repair_data)
        repair2 = self.repair_manager.create_repair(self.test_repair_data)
        
        self.repair_manager.update_repair(repair1.id, {'technician_id': 1})
        self.repair_manager.update_repair(repair2.id, {'technician_id': 2})
        
        tech1_repairs = self.repair_manager.get_repairs_by_technician(1)
        tech2_repairs = self.repair_manager.get_repairs_by_technician(2)
        
        self.assertEqual(len(tech1_repairs), 1)
        self.assertEqual(len(tech2_repairs), 1)
        self.assertEqual(tech1_repairs[0].technician_id, 1)
        self.assertEqual(tech2_repairs[0].technician_id, 2)
    
    def test_add_repair_part(self):
        """Test d'ajout d'une pièce à une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        
        repair_part = self.repair_manager.add_repair_part(
            repair.id,
            part_id=1,
            quantity=2,
            unit_price=50.0
        )
        
        self.assertEqual(repair_part.repair_id, repair.id)
        self.assertEqual(repair_part.part_id, 1)
        self.assertEqual(repair_part.quantity, 2)
        self.assertEqual(repair_part.unit_price, 50.0)
        self.assertEqual(repair_part.total_price, 100.0)
    
    def test_add_repair_note(self):
        """Test d'ajout d'une note à une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        
        note = self.repair_manager.add_repair_note(
            repair.id,
            author_id=1,
            content='Test note'
        )
        
        self.assertEqual(note.repair_id, repair.id)
        self.assertEqual(note.author_id, 1)
        self.assertEqual(note.content, 'Test note')
    
    def test_complete_repair(self):
        """Test de finalisation d'une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        
        completed_repair = self.repair_manager.complete_repair(
            repair.id,
            solution='Test solution',
            actual_cost=150.0
        )
        
        self.assertEqual(completed_repair.status, 'completed')
        self.assertEqual(completed_repair.solution, 'Test solution')
        self.assertEqual(completed_repair.actual_cost, 150.0)
        self.assertIsNotNone(completed_repair.completion_date)
    
    def test_cancel_repair(self):
        """Test d'annulation d'une réparation."""
        repair = self.repair_manager.create_repair(self.test_repair_data)
        
        cancelled_repair = self.repair_manager.cancel_repair(
            repair.id,
            reason='Test cancellation'
        )
        
        self.assertEqual(cancelled_repair.status, 'cancelled')
        self.assertEqual(cancelled_repair.solution, 'Annulée: Test cancellation')
    
    def test_get_repair_statistics(self):
        """Test de récupération des statistiques des réparations."""
        # Créer des réparations avec différents statuts
        repair1 = self.repair_manager.create_repair(self.test_repair_data)
        repair2 = self.repair_manager.create_repair(self.test_repair_data)
        repair3 = self.repair_manager.create_repair(self.test_repair_data)
        
        self.repair_manager.update_repair(repair1.id, {'status': 'in_progress'})
        self.repair_manager.complete_repair(repair2.id, 'Solution 1', 100.0)
        self.repair_manager.complete_repair(repair3.id, 'Solution 2', 200.0)
        
        stats = self.repair_manager.get_repair_statistics()
        
        self.assertEqual(stats['total_repairs'], 3)
        self.assertEqual(stats['completed_repairs'], 2)
        self.assertEqual(stats['in_progress_repairs'], 1)
        self.assertEqual(stats['total_cost'], 300.0)
        self.assertEqual(stats['average_cost'], 150.0)

if __name__ == '__main__':
    unittest.main() 