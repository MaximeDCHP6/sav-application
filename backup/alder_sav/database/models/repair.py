from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from alder_sav.database.base import Base

class Repair(Base):
    """Modèle pour les réparations."""
    
    __tablename__ = 'repairs'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    technician_id = Column(Integer, ForeignKey('technicians.id'))
    
    status = Column(Enum('pending', 'in_progress', 'completed', 'cancelled', name='repair_status'), default='pending')
    type = Column(Enum('warranty', 'paid', 'diagnostic', name='repair_type'), nullable=False)
    priority = Column(Enum('low', 'medium', 'high', 'urgent', name='repair_priority'), default='medium')
    
    description = Column(String(1000))
    diagnosis = Column(String(1000))
    solution = Column(String(1000))
    
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    estimated_completion_date = Column(DateTime)
    completion_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    client = relationship("Client", back_populates="repairs")
    device = relationship("Device", back_populates="repairs")
    technician = relationship("Technician", back_populates="repairs")
    parts = relationship("RepairPart", back_populates="repair")
    documents = relationship("Document", back_populates="repair")
    notes = relationship("RepairNote", back_populates="repair")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'device_id': self.device_id,
            'technician_id': self.technician_id,
            'status': self.status,
            'type': self.type,
            'priority': self.priority,
            'description': self.description,
            'diagnosis': self.diagnosis,
            'solution': self.solution,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'estimated_completion_date': self.estimated_completion_date.isoformat() if self.estimated_completion_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RepairPart(Base):
    """Modèle pour les pièces utilisées dans les réparations."""
    
    __tablename__ = 'repair_parts'
    
    id = Column(Integer, primary_key=True)
    repair_id = Column(Integer, ForeignKey('repairs.id'), nullable=False)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)
    total_price = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    repair = relationship("Repair", back_populates="parts")
    part = relationship("Part")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'repair_id': self.repair_id,
            'part_id': self.part_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RepairNote(Base):
    """Modèle pour les notes sur les réparations."""
    
    __tablename__ = 'repair_notes'
    
    id = Column(Integer, primary_key=True)
    repair_id = Column(Integer, ForeignKey('repairs.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String(1000), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    repair = relationship("Repair", back_populates="notes")
    author = relationship("User")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'repair_id': self.repair_id,
            'author_id': self.author_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 