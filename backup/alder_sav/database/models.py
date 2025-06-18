from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    GESTIONNAIRE = "gestionnaire"
    TECHNICIEN = "technicien"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)

class Client(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    numero_compte = Column(String(50), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    email = Column(String(100))
    telephone = Column(String(20))
    adresse = Column(Text)
    immatriculation = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    frps = relationship("FRP", back_populates="client")

class FRP(Base):
    __tablename__ = 'frps'
    
    id = Column(Integer, primary_key=True)
    numero = Column(String(20), unique=True, nullable=False)  # Format: FRP25-0001
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    date_creation = Column(DateTime, default=datetime.now)
    date_modification = Column(DateTime, onupdate=datetime.now)
    statut = Column(String(50))  # En cours, Validé, Refusé, etc.
    type_motif = Column(String(50))  # ERREUR ALDER, RETARD, ERREUR CLIENT, etc.
    description = Column(Text)
    validation_requise = Column(Boolean, default=True)
    valide_par = Column(Integer, ForeignKey('users.id'))
    date_validation = Column(DateTime)
    
    client = relationship("Client", back_populates="frps")
    produits = relationship("FRPProduit", back_populates="frp")
    documents = relationship("Document", back_populates="frp")

class FRPProduit(Base):
    __tablename__ = 'frp_produits'
    
    id = Column(Integer, primary_key=True)
    frp_id = Column(Integer, ForeignKey('frps.id'), nullable=False)
    reference = Column(String(50), nullable=False)
    quantite = Column(Integer, nullable=False)
    numero_bl = Column(String(50))
    numero_lot = Column(String(50))
    date_achat = Column(DateTime)
    prix = Column(Float)
    
    frp = relationship("FRP", back_populates="produits")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    frp_id = Column(Integer, ForeignKey('frps.id'))
    type = Column(String(50))  # FRP, Photo, Vidéo, etc.
    chemin_fichier = Column(String(255), nullable=False)
    date_creation = Column(DateTime, default=datetime.now)
    description = Column(Text)
    
    frp = relationship("FRP", back_populates="documents")

class Statistique(Base):
    __tablename__ = 'statistiques'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type = Column(String(50), nullable=False)  # FRP, Client, etc.
    valeur = Column(Float, nullable=False)
    description = Column(Text)

class Backup(Base):
    __tablename__ = 'backups'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    chemin_fichier = Column(String(255), nullable=False)
    taille = Column(Integer)  # Taille en octets
    statut = Column(String(50))  # Succès, Échec, etc.
    description = Column(Text)

# Création de la base de données
def init_db():
    engine = create_engine('sqlite:///alder_sav.db')
    Base.metadata.create_all(engine)
    return engine 