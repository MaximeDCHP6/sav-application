from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from alder_sav.database.models.repair import Repair, RepairPart, RepairNote
from alder_sav.utils.exceptions import RepairError
from alder_sav.utils.notifications import NotificationManager
from alder_sav.utils.documents import DocumentManager

class RepairManager:
    """Gestionnaire des réparations."""
    
    def __init__(self, db_session: Session):
        """Initialise le gestionnaire de réparations."""
        self.db = db_session
        self.notification_manager = NotificationManager()
        self.document_manager = DocumentManager()
    
    def create_repair(self, data: Dict[str, Any]) -> Repair:
        """Crée une nouvelle réparation."""
        try:
            repair = Repair(
                client_id=data['client_id'],
                device_id=data['device_id'],
                type=data['type'],
                priority=data.get('priority', 'medium'),
                description=data.get('description'),
                estimated_cost=data.get('estimated_cost'),
                estimated_completion_date=data.get('estimated_completion_date')
            )
            
            self.db.add(repair)
            self.db.commit()
            self.db.refresh(repair)
            
            # Créer une notification
            self.notification_manager.create_notification(
                type='email',
                recipient=repair.client.email,
                subject='Nouvelle réparation créée',
                content=f'Une nouvelle réparation a été créée pour votre appareil. ID: {repair.id}'
            )
            
            # Créer un document
            self.document_manager.create_document(
                type='repair_order',
                title=f'Ordre de réparation #{repair.id}',
                content=repair.to_dict(),
                related_entity={
                    'type': 'repair',
                    'id': repair.id
                }
            )
            
            return repair
            
        except Exception as e:
            self.db.rollback()
            raise RepairError(f"Erreur lors de la création de la réparation: {str(e)}")
    
    def get_repair(self, repair_id: int) -> Repair:
        """Récupère une réparation par son ID."""
        repair = self.db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise RepairError(f"Réparation non trouvée: {repair_id}")
        return repair
    
    def update_repair(self, repair_id: int, data: Dict[str, Any]) -> Repair:
        """Met à jour une réparation."""
        try:
            repair = self.get_repair(repair_id)
            
            for key, value in data.items():
                if hasattr(repair, key):
                    setattr(repair, key, value)
            
            repair.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(repair)
            
            # Créer une notification si le statut a changé
            if 'status' in data:
                self.notification_manager.create_notification(
                    type='email',
                    recipient=repair.client.email,
                    subject='Mise à jour de la réparation',
                    content=f'Le statut de votre réparation a été mis à jour: {data["status"]}'
                )
            
            return repair
            
        except Exception as e:
            self.db.rollback()
            raise RepairError(f"Erreur lors de la mise à jour de la réparation: {str(e)}")
    
    def delete_repair(self, repair_id: int) -> None:
        """Supprime une réparation."""
        try:
            repair = self.get_repair(repair_id)
            self.db.delete(repair)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise RepairError(f"Erreur lors de la suppression de la réparation: {str(e)}")
    
    def get_repairs_by_status(self, status: str) -> List[Repair]:
        """Récupère les réparations par statut."""
        return self.db.query(Repair).filter(Repair.status == status).all()
    
    def get_repairs_by_client(self, client_id: int) -> List[Repair]:
        """Récupère les réparations d'un client."""
        return self.db.query(Repair).filter(Repair.client_id == client_id).all()
    
    def get_repairs_by_technician(self, technician_id: int) -> List[Repair]:
        """Récupère les réparations d'un technicien."""
        return self.db.query(Repair).filter(Repair.technician_id == technician_id).all()
    
    def add_repair_part(self, repair_id: int, part_id: int, quantity: int, unit_price: float) -> RepairPart:
        """Ajoute une pièce à une réparation."""
        try:
            repair = self.get_repair(repair_id)
            
            repair_part = RepairPart(
                repair_id=repair_id,
                part_id=part_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=quantity * unit_price
            )
            
            self.db.add(repair_part)
            self.db.commit()
            self.db.refresh(repair_part)
            
            return repair_part
            
        except Exception as e:
            self.db.rollback()
            raise RepairError(f"Erreur lors de l'ajout de la pièce: {str(e)}")
    
    def add_repair_note(self, repair_id: int, author_id: int, content: str) -> RepairNote:
        """Ajoute une note à une réparation."""
        try:
            repair = self.get_repair(repair_id)
            
            note = RepairNote(
                repair_id=repair_id,
                author_id=author_id,
                content=content
            )
            
            self.db.add(note)
            self.db.commit()
            self.db.refresh(note)
            
            return note
            
        except Exception as e:
            self.db.rollback()
            raise RepairError(f"Erreur lors de l'ajout de la note: {str(e)}")
    
    def complete_repair(self, repair_id: int, solution: str, actual_cost: float) -> Repair:
        """Finalise une réparation."""
        try:
            repair = self.get_repair(repair_id)
            
            repair.status = 'completed'
            repair.solution = solution
            repair.actual_cost = actual_cost
            repair.completion_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(repair)
            
            # Créer une notification
            self.notification_manager.create_notification(
                type='email',
                recipient=repair.client.email,
                subject='Réparation terminée',
                content=f'Votre réparation a été terminée. Coût final: {actual_cost}€'
            )
            
            # Créer un document
            self.document_manager.create_document(
                type='repair_completion',
                title=f'Rapport de réparation #{repair.id}',
                content=repair.to_dict(),
                related_entity={
                    'type': 'repair',
                    'id': repair.id
                }
            )
            
            return repair
            
        except Exception as e:
            self.db.rollback()
            raise RepairError(f"Erreur lors de la finalisation de la réparation: {str(e)}")
    
    def cancel_repair(self, repair_id: int, reason: str) -> Repair:
        """Annule une réparation."""
        try:
            repair = self.get_repair(repair_id)
            
            repair.status = 'cancelled'
            repair.solution = f"Annulée: {reason}"
            
            self.db.commit()
            self.db.refresh(repair)
            
            # Créer une notification
            self.notification_manager.create_notification(
                type='email',
                recipient=repair.client.email,
                subject='Réparation annulée',
                content=f'Votre réparation a été annulée. Raison: {reason}'
            )
            
            return repair
            
        except Exception as e:
            self.db.rollback()
            raise RepairError(f"Erreur lors de l'annulation de la réparation: {str(e)}")
    
    def get_repair_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques des réparations."""
        try:
            total_repairs = self.db.query(Repair).count()
            completed_repairs = self.db.query(Repair).filter(Repair.status == 'completed').count()
            pending_repairs = self.db.query(Repair).filter(Repair.status == 'pending').count()
            in_progress_repairs = self.db.query(Repair).filter(Repair.status == 'in_progress').count()
            cancelled_repairs = self.db.query(Repair).filter(Repair.status == 'cancelled').count()
            
            total_cost = self.db.query(Repair).filter(Repair.status == 'completed').with_entities(
                func.sum(Repair.actual_cost)
            ).scalar() or 0
            
            return {
                'total_repairs': total_repairs,
                'completed_repairs': completed_repairs,
                'pending_repairs': pending_repairs,
                'in_progress_repairs': in_progress_repairs,
                'cancelled_repairs': cancelled_repairs,
                'total_cost': total_cost,
                'average_cost': total_cost / completed_repairs if completed_repairs > 0 else 0
            }
            
        except Exception as e:
            raise RepairError(f"Erreur lors de la récupération des statistiques: {str(e)}") 