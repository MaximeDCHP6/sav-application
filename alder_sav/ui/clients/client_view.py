from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from alder_sav.managers.client_manager import ClientManager
from alder_sav.utils.exceptions import ClientError

class ClientView(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.client_manager = ClientManager(session)
        self._init_ui()
        self._load_clients()
    
    def _init_ui(self):
        """Initialisation de l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        
        # Boutons d'action
        new_btn = QPushButton("Nouveau client")
        new_btn.setIcon(QIcon("resources/icons/new.png"))
        new_btn.clicked.connect(self._create_new_client)
        toolbar.addWidget(new_btn)
        
        edit_btn = QPushButton("Modifier")
        edit_btn.setIcon(QIcon("resources/icons/edit.png"))
        edit_btn.clicked.connect(self._edit_client)
        toolbar.addWidget(edit_btn)
        
        delete_btn = QPushButton("Supprimer")
        delete_btn.setIcon(QIcon("resources/icons/delete.png"))
        delete_btn.clicked.connect(self._delete_client)
        toolbar.addWidget(delete_btn)
        
        toolbar.addStretch()
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un client...")
        self.search_input.textChanged.connect(self._apply_filters)
        toolbar.addWidget(self.search_input)
        
        layout.addLayout(toolbar)
        
        # Table des clients
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels([
            "ID", "Nom", "Email", "Téléphone", "Adresse", "Date création"
        ])
        self.clients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.clients_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.clients_table.itemSelectionChanged.connect(self._show_client_details)
        layout.addWidget(self.clients_table)
        
        # Onglets de détails
        self.details_tabs = QTabWidget()
        
        # Onglet Informations
        info_tab = QWidget()
        info_layout = QFormLayout(info_tab)
        
        self.name_info = QLabel()
        self.email_info = QLabel()
        self.phone_info = QLabel()
        self.address_info = QLabel()
        self.notes_info = QTextEdit()
        self.notes_info.setReadOnly(True)
        
        info_layout.addRow("Nom:", self.name_info)
        info_layout.addRow("Email:", self.email_info)
        info_layout.addRow("Téléphone:", self.phone_info)
        info_layout.addRow("Adresse:", self.address_info)
        info_layout.addRow("Notes:", self.notes_info)
        
        self.details_tabs.addTab(info_tab, "Informations")
        
        # Onglet Appareils
        devices_tab = QWidget()
        devices_layout = QVBoxLayout(devices_tab)
        
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(5)
        self.devices_table.setHorizontalHeaderLabels([
            "ID", "Marque", "Modèle", "Numéro de série", "Date d'achat"
        ])
        devices_layout.addWidget(self.devices_table)
        
        self.details_tabs.addTab(devices_tab, "Appareils")
        
        # Onglet Réparations
        repairs_tab = QWidget()
        repairs_layout = QVBoxLayout(repairs_tab)
        
        self.repairs_table = QTableWidget()
        self.repairs_table.setColumnCount(6)
        self.repairs_table.setHorizontalHeaderLabels([
            "ID", "Type", "Statut", "Date création", "Date fin", "Coût"
        ])
        repairs_layout.addWidget(self.repairs_table)
        
        self.details_tabs.addTab(repairs_tab, "Réparations")
        
        layout.addWidget(self.details_tabs)
    
    def _load_clients(self):
        """Chargement des clients dans la table"""
        try:
            clients = self.client_manager.get_all_clients()
            self.clients_table.setRowCount(len(clients))
            
            for row, client in enumerate(clients):
                self.clients_table.setItem(row, 0, QTableWidgetItem(str(client.id)))
                self.clients_table.setItem(row, 1, QTableWidgetItem(client.name))
                self.clients_table.setItem(row, 2, QTableWidgetItem(client.email))
                self.clients_table.setItem(row, 3, QTableWidgetItem(client.phone))
                self.clients_table.setItem(row, 4, QTableWidgetItem(client.address))
                self.clients_table.setItem(row, 5, QTableWidgetItem(
                    client.created_at.strftime("%d/%m/%Y")
                ))
        
        except ClientError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des clients: {str(e)}")
    
    def _show_client_details(self):
        """Affichage des détails du client sélectionné"""
        selected_rows = self.clients_table.selectedItems()
        if not selected_rows:
            return
        
        client_id = int(self.clients_table.item(selected_rows[0].row(), 0).text())
        try:
            client = self.client_manager.get_client(client_id)
            
            # Mise à jour des informations
            self.name_info.setText(client.name)
            self.email_info.setText(client.email)
            self.phone_info.setText(client.phone)
            self.address_info.setText(client.address)
            self.notes_info.setText(client.notes or "Aucune note")
            
            # Mise à jour des appareils
            self.devices_table.setRowCount(len(client.devices))
            for row, device in enumerate(client.devices):
                self.devices_table.setItem(row, 0, QTableWidgetItem(str(device.id)))
                self.devices_table.setItem(row, 1, QTableWidgetItem(device.brand))
                self.devices_table.setItem(row, 2, QTableWidgetItem(device.model))
                self.devices_table.setItem(row, 3, QTableWidgetItem(device.serial_number))
                self.devices_table.setItem(row, 4, QTableWidgetItem(
                    device.purchase_date.strftime("%d/%m/%Y")
                ))
            
            # Mise à jour des réparations
            self.repairs_table.setRowCount(len(client.repairs))
            for row, repair in enumerate(client.repairs):
                self.repairs_table.setItem(row, 0, QTableWidgetItem(str(repair.id)))
                self.repairs_table.setItem(row, 1, QTableWidgetItem(repair.type))
                self.repairs_table.setItem(row, 2, QTableWidgetItem(repair.status))
                self.repairs_table.setItem(row, 3, QTableWidgetItem(
                    repair.created_at.strftime("%d/%m/%Y")
                ))
                self.repairs_table.setItem(row, 4, QTableWidgetItem(
                    repair.completion_date.strftime("%d/%m/%Y") if repair.completion_date else "-"
                ))
                self.repairs_table.setItem(row, 5, QTableWidgetItem(
                    f"{repair.actual_cost:.2f} €" if repair.actual_cost else "-"
                ))
        
        except ClientError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des détails: {str(e)}")
    
    def _create_new_client(self):
        """Création d'un nouveau client"""
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                client_data = dialog.get_client_data()
                self.client_manager.create_client(client_data)
                self._load_clients()
                QMessageBox.information(self, "Succès", "Client créé avec succès")
            except ClientError as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")
    
    def _edit_client(self):
        """Modification d'un client existant"""
        selected_rows = self.clients_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un client")
            return
        
        client_id = int(self.clients_table.item(selected_rows[0].row(), 0).text())
        try:
            client = self.client_manager.get_client(client_id)
            dialog = ClientDialog(self, client)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                client_data = dialog.get_client_data()
                self.client_manager.update_client(client_id, client_data)
                self._load_clients()
                self._show_client_details()
                QMessageBox.information(self, "Succès", "Client mis à jour avec succès")
        except ClientError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification: {str(e)}")
    
    def _delete_client(self):
        """Suppression d'un client"""
        selected_rows = self.clients_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un client")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer ce client ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            client_id = int(self.clients_table.item(selected_rows[0].row(), 0).text())
            try:
                self.client_manager.delete_client(client_id)
                self._load_clients()
                QMessageBox.information(self, "Succès", "Client supprimé avec succès")
            except ClientError as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def _apply_filters(self):
        """Application des filtres sur la liste des clients"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.clients_table.rowCount()):
            show_row = False
            for col in range(self.clients_table.columnCount()):
                item = self.clients_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.clients_table.setRowHidden(row, not show_row)

class ClientDialog(QDialog):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.client = client
        self._init_ui()
        if client:
            self._load_client_data()
    
    def _init_ui(self):
        """Initialisation de l'interface utilisateur"""
        self.setWindowTitle("Client")
        layout = QFormLayout(self)
        
        # Champs
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        
        # Ajout des champs au layout
        layout.addRow("Nom:", self.name_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Téléphone:", self.phone_edit)
        layout.addRow("Adresse:", self.address_edit)
        layout.addRow("Notes:", self.notes_edit)
        
        # Boutons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
    
    def _load_client_data(self):
        """Chargement des données du client existant"""
        self.name_edit.setText(self.client.name)
        self.email_edit.setText(self.client.email)
        self.phone_edit.setText(self.client.phone)
        self.address_edit.setText(self.client.address)
        self.notes_edit.setText(self.client.notes)
    
    def get_client_data(self):
        """Récupération des données du formulaire"""
        return {
            'name': self.name_edit.text(),
            'email': self.email_edit.text(),
            'phone': self.phone_edit.text(),
            'address': self.address_edit.text(),
            'notes': self.notes_edit.toPlainText()
        } 