from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from database.models import Client

class ClientWidget(QWidget):
    """Widget de gestion des clients"""
    
    # Signaux
    client_created = pyqtSignal(Client)
    client_updated = pyqtSignal(Client)
    client_deleted = pyqtSignal(int)  # ID du client
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_client = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialisation de l'interface"""
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        # Numéro compte
        account_layout = QVBoxLayout()
        account_layout.addWidget(QLabel("Numéro compte:"))
        self.account_number = QLineEdit()
        account_layout.addWidget(self.account_number)
        header_layout.addLayout(account_layout)
        
        # Date création
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Date création:"))
        self.creation_date = QLineEdit()
        self.creation_date.setReadOnly(True)
        self.creation_date.setText(datetime.now().strftime("%d/%m/%Y"))
        date_layout.addWidget(self.creation_date)
        header_layout.addLayout(date_layout)
        
        layout.addWidget(header)
        
        # Informations client
        info_group = QWidget()
        info_layout = QVBoxLayout(info_group)
        info_layout.addWidget(QLabel("Informations client"))
        
        # Nom
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nom:"))
        self.name = QLineEdit()
        name_layout.addWidget(self.name)
        info_layout.addLayout(name_layout)
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email = QLineEdit()
        email_layout.addWidget(self.email)
        info_layout.addLayout(email_layout)
        
        # Téléphone
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Téléphone:"))
        self.phone = QLineEdit()
        phone_layout.addWidget(self.phone)
        info_layout.addLayout(phone_layout)
        
        # Adresse
        address_layout = QVBoxLayout()
        address_layout.addWidget(QLabel("Adresse:"))
        self.address = QTextEdit()
        self.address.setMaximumHeight(100)
        address_layout.addWidget(self.address)
        info_layout.addLayout(address_layout)
        
        # Immatriculation
        registration_layout = QHBoxLayout()
        registration_layout.addWidget(QLabel("Immatriculation:"))
        self.registration = QLineEdit()
        registration_layout.addWidget(self.registration)
        info_layout.addLayout(registration_layout)
        
        layout.addWidget(info_group)
        
        # Notes
        notes_group = QWidget()
        notes_layout = QVBoxLayout(notes_group)
        notes_layout.addWidget(QLabel("Notes"))
        
        self.notes = QTextEdit()
        notes_layout.addWidget(self.notes)
        
        layout.addWidget(notes_group)
        
        # FRP associés
        frp_group = QWidget()
        frp_layout = QVBoxLayout(frp_group)
        frp_layout.addWidget(QLabel("FRP associés"))
        
        self.frp_table = QTableWidget()
        self.frp_table.setColumnCount(4)
        self.frp_table.setHorizontalHeaderLabels([
            "Numéro", "Date", "Statut", "Type"
        ])
        frp_layout.addWidget(self.frp_table)
        
        layout.addWidget(frp_group)
        
        # Boutons d'action
        action_buttons = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self._save_client)
        action_buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self._cancel)
        action_buttons.addWidget(cancel_btn)
        
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self._delete_client)
        action_buttons.addWidget(delete_btn)
        
        layout.addLayout(action_buttons)
    
    def _save_client(self):
        """Sauvegarde du client"""
        # Validation des données
        if not self._validate_data():
            return
        
        # Création ou mise à jour du client
        if self.current_client is None:
            self.current_client = Client()
        
        # Mise à jour des données
        self._update_client_data()
        
        # Émission du signal approprié
        if self.current_client.id is None:
            self.client_created.emit(self.current_client)
        else:
            self.client_updated.emit(self.current_client)
        
        QMessageBox.information(
            self,
            "Succès",
            "Client enregistré avec succès"
        )
    
    def _validate_data(self):
        """Validation des données du client"""
        if not self.account_number.text():
            QMessageBox.warning(
                self,
                "Erreur",
                "Le numéro de compte est requis"
            )
            return False
        
        if not self.name.text():
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom du client est requis"
            )
            return False
        
        return True
    
    def _update_client_data(self):
        """Mise à jour des données du client"""
        self.current_client.numero_compte = self.account_number.text()
        self.current_client.nom = self.name.text()
        self.current_client.email = self.email.text()
        self.current_client.telephone = self.phone.text()
        self.current_client.adresse = self.address.toPlainText()
        self.current_client.immatriculation = self.registration.text()
        self.current_client.notes = self.notes.toPlainText()
        
        if self.current_client.id is None:
            self.current_client.created_at = datetime.now()
        self.current_client.updated_at = datetime.now()
    
    def _cancel(self):
        """Annulation des modifications"""
        if self.current_client is not None:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Voulez-vous vraiment annuler les modifications ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.clear()
    
    def _delete_client(self):
        """Suppression du client"""
        if self.current_client is None:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer ce client ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.client_deleted.emit(self.current_client.id)
            self.clear()
    
    def clear(self):
        """Réinitialisation du formulaire"""
        self.current_client = None
        self.account_number.clear()
        self.name.clear()
        self.email.clear()
        self.phone.clear()
        self.address.clear()
        self.registration.clear()
        self.notes.clear()
        self.frp_table.setRowCount(0)
        self.creation_date.setText(datetime.now().strftime("%d/%m/%Y"))
    
    def load_client(self, client):
        """Chargement d'un client existant"""
        self.clear()
        self.current_client = client
        
        # Remplissage des champs
        self.account_number.setText(client.numero_compte)
        self.name.setText(client.nom)
        self.email.setText(client.email)
        self.phone.setText(client.telephone)
        self.address.setText(client.adresse)
        self.registration.setText(client.immatriculation)
        self.notes.setText(client.notes)
        self.creation_date.setText(client.created_at.strftime("%d/%m/%Y"))
        
        # Chargement des FRP associés
        for frp in client.frps:
            row = self.frp_table.rowCount()
            self.frp_table.insertRow(row)
            self.frp_table.setItem(row, 0, QTableWidgetItem(frp.numero))
            self.frp_table.setItem(
                row, 1,
                QTableWidgetItem(frp.date_creation.strftime("%d/%m/%Y"))
            )
            self.frp_table.setItem(row, 2, QTableWidgetItem(frp.statut))
            self.frp_table.setItem(row, 3, QTableWidgetItem(frp.type_motif)) 