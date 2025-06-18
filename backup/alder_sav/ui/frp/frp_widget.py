from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from config.settings import FRP_CONFIG
from database.models import FRP, FRPProduit, Document

class FRPWidget(QWidget):
    """Widget de gestion des FRP"""
    
    # Signaux
    frp_created = pyqtSignal(FRP)
    frp_updated = pyqtSignal(FRP)
    frp_deleted = pyqtSignal(int)  # ID du FRP
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frp = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialisation de l'interface"""
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        # Numéro FRP
        frp_number_layout = QVBoxLayout()
        frp_number_layout.addWidget(QLabel("Numéro FRP:"))
        self.frp_number = QLineEdit()
        self.frp_number.setReadOnly(True)
        frp_number_layout.addWidget(self.frp_number)
        header_layout.addLayout(frp_number_layout)
        
        # Date
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date = QLineEdit()
        self.date.setReadOnly(True)
        self.date.setText(datetime.now().strftime("%d/%m/%Y"))
        date_layout.addWidget(self.date)
        header_layout.addLayout(date_layout)
        
        layout.addWidget(header)
        
        # Informations client
        client_group = QWidget()
        client_layout = QVBoxLayout(client_group)
        client_layout.addWidget(QLabel("Informations client"))
        
        # Numéro compte
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("Numéro compte:"))
        self.account_number = QLineEdit()
        account_layout.addWidget(self.account_number)
        client_layout.addLayout(account_layout)
        
        # Nom client
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nom client:"))
        self.client_name = QLineEdit()
        name_layout.addWidget(self.client_name)
        client_layout.addLayout(name_layout)
        
        layout.addWidget(client_group)
        
        # Produits
        products_group = QWidget()
        products_layout = QVBoxLayout(products_group)
        products_layout.addWidget(QLabel("Produits"))
        
        # Table des produits
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "Référence", "Quantité", "N° BL", "N° Lot",
            "Date achat", "Prix"
        ])
        products_layout.addWidget(self.products_table)
        
        # Boutons produits
        products_buttons = QHBoxLayout()
        add_product_btn = QPushButton("Ajouter produit")
        add_product_btn.clicked.connect(self._add_product)
        products_buttons.addWidget(add_product_btn)
        
        remove_product_btn = QPushButton("Supprimer produit")
        remove_product_btn.clicked.connect(self._remove_product)
        products_buttons.addWidget(remove_product_btn)
        
        products_layout.addLayout(products_buttons)
        layout.addWidget(products_group)
        
        # Motif
        reason_group = QWidget()
        reason_layout = QVBoxLayout(reason_group)
        reason_layout.addWidget(QLabel("Motif du retour"))
        
        # Type de motif
        reason_type_layout = QHBoxLayout()
        reason_type_layout.addWidget(QLabel("Type:"))
        self.reason_type = QComboBox()
        self.reason_type.addItems([
            "ERREUR ALDER",
            "RETARD",
            "ERREUR CLIENT",
            "AUTRE"
        ])
        reason_type_layout.addWidget(self.reason_type)
        reason_layout.addLayout(reason_type_layout)
        
        # Description
        description_layout = QVBoxLayout()
        description_layout.addWidget(QLabel("Description:"))
        self.description = QTextEdit()
        description_layout.addWidget(self.description)
        reason_layout.addLayout(description_layout)
        
        layout.addWidget(reason_group)
        
        # Documents
        documents_group = QWidget()
        documents_layout = QVBoxLayout(documents_group)
        documents_layout.addWidget(QLabel("Documents"))
        
        # Liste des documents
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(3)
        self.documents_table.setHorizontalHeaderLabels([
            "Type", "Date", "Description"
        ])
        documents_layout.addWidget(self.documents_table)
        
        # Boutons documents
        documents_buttons = QHBoxLayout()
        add_document_btn = QPushButton("Ajouter document")
        add_document_btn.clicked.connect(self._add_document)
        documents_buttons.addWidget(add_document_btn)
        
        remove_document_btn = QPushButton("Supprimer document")
        remove_document_btn.clicked.connect(self._remove_document)
        documents_buttons.addWidget(remove_document_btn)
        
        documents_layout.addLayout(documents_buttons)
        layout.addWidget(documents_group)
        
        # Boutons d'action
        action_buttons = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self._save_frp)
        action_buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self._cancel)
        action_buttons.addWidget(cancel_btn)
        
        layout.addLayout(action_buttons)
    
    def _add_product(self):
        """Ajout d'un produit"""
        row = self.products_table.rowCount()
        self.products_table.insertRow(row)
        
        # Ajout des widgets pour chaque colonne
        self.products_table.setItem(row, 0, QTableWidgetItem(""))  # Référence
        self.products_table.setItem(row, 1, QTableWidgetItem("1"))  # Quantité
        self.products_table.setItem(row, 2, QTableWidgetItem(""))  # N° BL
        self.products_table.setItem(row, 3, QTableWidgetItem(""))  # N° Lot
        self.products_table.setItem(row, 4, QTableWidgetItem(""))  # Date achat
        self.products_table.setItem(row, 5, QTableWidgetItem("0.00"))  # Prix
    
    def _remove_product(self):
        """Suppression d'un produit"""
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            self.products_table.removeRow(current_row)
    
    def _add_document(self):
        """Ajout d'un document"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un document",
            "",
            "Tous les fichiers (*.*)"
        )
        
        if file_path:
            row = self.documents_table.rowCount()
            self.documents_table.insertRow(row)
            
            # Ajout des informations du document
            self.documents_table.setItem(row, 0, QTableWidgetItem("Document"))
            self.documents_table.setItem(
                row, 1,
                QTableWidgetItem(datetime.now().strftime("%d/%m/%Y"))
            )
            self.documents_table.setItem(row, 2, QTableWidgetItem(file_path))
    
    def _remove_document(self):
        """Suppression d'un document"""
        current_row = self.documents_table.currentRow()
        if current_row >= 0:
            self.documents_table.removeRow(current_row)
    
    def _save_frp(self):
        """Sauvegarde du FRP"""
        # Validation des données
        if not self._validate_data():
            return
        
        # Création ou mise à jour du FRP
        if self.current_frp is None:
            self.current_frp = FRP()
        
        # Mise à jour des données
        self._update_frp_data()
        
        # Émission du signal approprié
        if self.current_frp.id is None:
            self.frp_created.emit(self.current_frp)
        else:
            self.frp_updated.emit(self.current_frp)
        
        QMessageBox.information(
            self,
            "Succès",
            "FRP enregistré avec succès"
        )
    
    def _validate_data(self):
        """Validation des données du FRP"""
        if not self.account_number.text():
            QMessageBox.warning(
                self,
                "Erreur",
                "Le numéro de compte est requis"
            )
            return False
        
        if not self.client_name.text():
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom du client est requis"
            )
            return False
        
        if self.products_table.rowCount() == 0:
            QMessageBox.warning(
                self,
                "Erreur",
                "Au moins un produit est requis"
            )
            return False
        
        return True
    
    def _update_frp_data(self):
        """Mise à jour des données du FRP"""
        # Mise à jour des informations de base
        self.current_frp.numero = self.frp_number.text()
        self.current_frp.date_creation = datetime.now()
        self.current_frp.type_motif = self.reason_type.currentText()
        self.current_frp.description = self.description.toPlainText()
        
        # Mise à jour des produits
        self.current_frp.produits = []
        for row in range(self.products_table.rowCount()):
            produit = FRPProduit()
            produit.reference = self.products_table.item(row, 0).text()
            produit.quantite = int(self.products_table.item(row, 1).text())
            produit.numero_bl = self.products_table.item(row, 2).text()
            produit.numero_lot = self.products_table.item(row, 3).text()
            produit.date_achat = datetime.strptime(
                self.products_table.item(row, 4).text(),
                "%d/%m/%Y"
            )
            produit.prix = float(self.products_table.item(row, 5).text())
            self.current_frp.produits.append(produit)
        
        # Mise à jour des documents
        self.current_frp.documents = []
        for row in range(self.documents_table.rowCount()):
            document = Document()
            document.type = self.documents_table.item(row, 0).text()
            document.chemin_fichier = self.documents_table.item(row, 2).text()
            document.date_creation = datetime.strptime(
                self.documents_table.item(row, 1).text(),
                "%d/%m/%Y"
            )
            self.current_frp.documents.append(document)
    
    def _cancel(self):
        """Annulation des modifications"""
        if self.current_frp is not None:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Voulez-vous vraiment annuler les modifications ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.clear()
    
    def clear(self):
        """Réinitialisation du formulaire"""
        self.current_frp = None
        self.frp_number.clear()
        self.account_number.clear()
        self.client_name.clear()
        self.products_table.setRowCount(0)
        self.documents_table.setRowCount(0)
        self.description.clear()
        self.reason_type.setCurrentIndex(0)
    
    def load_frp(self, frp):
        """Chargement d'un FRP existant"""
        self.clear()
        self.current_frp = frp
        
        # Remplissage des champs
        self.frp_number.setText(frp.numero)
        self.account_number.setText(str(frp.client_id))
        self.client_name.setText(frp.client.nom)
        self.reason_type.setCurrentText(frp.type_motif)
        self.description.setText(frp.description)
        
        # Chargement des produits
        for produit in frp.produits:
            row = self.products_table.rowCount()
            self.products_table.insertRow(row)
            self.products_table.setItem(row, 0, QTableWidgetItem(produit.reference))
            self.products_table.setItem(row, 1, QTableWidgetItem(str(produit.quantite)))
            self.products_table.setItem(row, 2, QTableWidgetItem(produit.numero_bl))
            self.products_table.setItem(row, 3, QTableWidgetItem(produit.numero_lot))
            self.products_table.setItem(
                row, 4,
                QTableWidgetItem(produit.date_achat.strftime("%d/%m/%Y"))
            )
            self.products_table.setItem(row, 5, QTableWidgetItem(str(produit.prix)))
        
        # Chargement des documents
        for document in frp.documents:
            row = self.documents_table.rowCount()
            self.documents_table.insertRow(row)
            self.documents_table.setItem(row, 0, QTableWidgetItem(document.type))
            self.documents_table.setItem(
                row, 1,
                QTableWidgetItem(document.date_creation.strftime("%d/%m/%Y"))
            )
            self.documents_table.setItem(row, 2, QTableWidgetItem(document.chemin_fichier)) 