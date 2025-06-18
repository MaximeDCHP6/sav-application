from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
    QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
from datetime import datetime
from decimal import Decimal

from alder_sav.managers.repair_manager import RepairManager
from alder_sav.utils.exceptions import RepairError

class RepairView(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.repair_manager = RepairManager(session)
        self._init_ui()
        self._load_repairs()
    
    def _init_ui(self):
        """Initialisation de l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        
        # Boutons d'action
        new_btn = QPushButton("Nouvelle réparation")
        new_btn.setIcon(QIcon("resources/icons/new.png"))
        new_btn.clicked.connect(self._create_new_repair)
        toolbar.addWidget(new_btn)
        
        edit_btn = QPushButton("Modifier")
        edit_btn.setIcon(QIcon("resources/icons/edit.png"))
        edit_btn.clicked.connect(self._edit_repair)
        toolbar.addWidget(edit_btn)
        
        delete_btn = QPushButton("Supprimer")
        delete_btn.setIcon(QIcon("resources/icons/delete.png"))
        delete_btn.clicked.connect(self._delete_repair)
        toolbar.addWidget(delete_btn)
        
        toolbar.addStretch()
        
        # Filtres
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "En attente", "En cours", "Terminée", "Annulée"])
        self.status_filter.currentTextChanged.connect(self._apply_filters)
        toolbar.addWidget(QLabel("Statut:"))
        toolbar.addWidget(self.status_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self._apply_filters)
        toolbar.addWidget(self.search_input)
        
        layout.addLayout(toolbar)
        
        # Table des réparations
        self.repairs_table = QTableWidget()
        self.repairs_table.setColumnCount(8)
        self.repairs_table.setHorizontalHeaderLabels([
            "ID", "Client", "Appareil", "Type", "Statut",
            "Priorité", "Date création", "Coût estimé"
        ])
        self.repairs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.repairs_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.repairs_table.itemSelectionChanged.connect(self._show_repair_details)
        layout.addWidget(self.repairs_table)
        
        # Onglets de détails
        self.details_tabs = QTabWidget()
        
        # Onglet Informations
        info_tab = QWidget()
        info_layout = QFormLayout(info_tab)
        
        self.client_info = QLabel()
        self.device_info = QLabel()
        self.type_info = QLabel()
        self.status_info = QLabel()
        self.priority_info = QLabel()
        self.description_info = QTextEdit()
        self.description_info.setReadOnly(True)
        
        info_layout.addRow("Client:", self.client_info)
        info_layout.addRow("Appareil:", self.device_info)
        info_layout.addRow("Type:", self.type_info)
        info_layout.addRow("Statut:", self.status_info)
        info_layout.addRow("Priorité:", self.priority_info)
        info_layout.addRow("Description:", self.description_info)
        
        self.details_tabs.addTab(info_tab, "Informations")
        
        # Onglet Diagnostic
        diagnosis_tab = QWidget()
        diagnosis_layout = QVBoxLayout(diagnosis_tab)
        
        self.diagnosis_text = QTextEdit()
        self.diagnosis_text.setReadOnly(True)
        diagnosis_layout.addWidget(self.diagnosis_text)
        
        self.details_tabs.addTab(diagnosis_tab, "Diagnostic")
        
        # Onglet Pièces
        parts_tab = QWidget()
        parts_layout = QVBoxLayout(parts_tab)
        
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(5)
        self.parts_table.setHorizontalHeaderLabels([
            "ID", "Pièce", "Quantité", "Prix unitaire", "Total"
        ])
        parts_layout.addWidget(self.parts_table)
        
        self.details_tabs.addTab(parts_tab, "Pièces")
        
        # Onglet Notes
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        
        self.notes_table = QTableWidget()
        self.notes_table.setColumnCount(4)
        self.notes_table.setHorizontalHeaderLabels([
            "Date", "Auteur", "Contenu", "Type"
        ])
        notes_layout.addWidget(self.notes_table)
        
        self.details_tabs.addTab(notes_tab, "Notes")
        
        layout.addWidget(self.details_tabs)
    
    def _load_repairs(self):
        """Chargement des réparations dans la table"""
        try:
            repairs = self.repair_manager.get_all_repairs()
            self.repairs_table.setRowCount(len(repairs))
            
            for row, repair in enumerate(repairs):
                self.repairs_table.setItem(row, 0, QTableWidgetItem(str(repair.id)))
                self.repairs_table.setItem(row, 1, QTableWidgetItem(repair.client.name))
                self.repairs_table.setItem(row, 2, QTableWidgetItem(repair.device.model))
                self.repairs_table.setItem(row, 3, QTableWidgetItem(repair.type))
                self.repairs_table.setItem(row, 4, QTableWidgetItem(repair.status))
                self.repairs_table.setItem(row, 5, QTableWidgetItem(repair.priority))
                self.repairs_table.setItem(row, 6, QTableWidgetItem(
                    repair.created_at.strftime("%d/%m/%Y")
                ))
                self.repairs_table.setItem(row, 7, QTableWidgetItem(
                    f"{repair.estimated_cost:.2f} €"
                ))
        
        except RepairError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des réparations: {str(e)}")
    
    def _show_repair_details(self):
        """Affichage des détails de la réparation sélectionnée"""
        selected_rows = self.repairs_table.selectedItems()
        if not selected_rows:
            return
        
        repair_id = int(self.repairs_table.item(selected_rows[0].row(), 0).text())
        try:
            repair = self.repair_manager.get_repair(repair_id)
            
            # Mise à jour des informations
            self.client_info.setText(f"{repair.client.name} ({repair.client.email})")
            self.device_info.setText(f"{repair.device.brand} {repair.device.model}")
            self.type_info.setText(repair.type)
            self.status_info.setText(repair.status)
            self.priority_info.setText(repair.priority)
            self.description_info.setText(repair.description)
            self.diagnosis_text.setText(repair.diagnosis or "Aucun diagnostic")
            
            # Mise à jour des pièces
            self.parts_table.setRowCount(len(repair.parts))
            for row, part in enumerate(repair.parts):
                self.parts_table.setItem(row, 0, QTableWidgetItem(str(part.id)))
                self.parts_table.setItem(row, 1, QTableWidgetItem(part.part.name))
                self.parts_table.setItem(row, 2, QTableWidgetItem(str(part.quantity)))
                self.parts_table.setItem(row, 3, QTableWidgetItem(f"{part.unit_price:.2f} €"))
                self.parts_table.setItem(row, 4, QTableWidgetItem(f"{part.total_price:.2f} €"))
            
            # Mise à jour des notes
            self.notes_table.setRowCount(len(repair.notes))
            for row, note in enumerate(repair.notes):
                self.notes_table.setItem(row, 0, QTableWidgetItem(
                    note.created_at.strftime("%d/%m/%Y %H:%M")
                ))
                self.notes_table.setItem(row, 1, QTableWidgetItem(note.author.name))
                self.notes_table.setItem(row, 2, QTableWidgetItem(note.content))
                self.notes_table.setItem(row, 3, QTableWidgetItem(note.type))
        
        except RepairError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des détails: {str(e)}")
    
    def _create_new_repair(self):
        """Création d'une nouvelle réparation"""
        dialog = RepairDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                repair_data = dialog.get_repair_data()
                self.repair_manager.create_repair(repair_data)
                self._load_repairs()
                QMessageBox.information(self, "Succès", "Réparation créée avec succès")
            except RepairError as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")
    
    def _edit_repair(self):
        """Modification d'une réparation existante"""
        selected_rows = self.repairs_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une réparation")
            return
        
        repair_id = int(self.repairs_table.item(selected_rows[0].row(), 0).text())
        try:
            repair = self.repair_manager.get_repair(repair_id)
            dialog = RepairDialog(self, repair)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                repair_data = dialog.get_repair_data()
                self.repair_manager.update_repair(repair_id, repair_data)
                self._load_repairs()
                self._show_repair_details()
                QMessageBox.information(self, "Succès", "Réparation mise à jour avec succès")
        except RepairError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification: {str(e)}")
    
    def _delete_repair(self):
        """Suppression d'une réparation"""
        selected_rows = self.repairs_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une réparation")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cette réparation ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            repair_id = int(self.repairs_table.item(selected_rows[0].row(), 0).text())
            try:
                self.repair_manager.delete_repair(repair_id)
                self._load_repairs()
                QMessageBox.information(self, "Succès", "Réparation supprimée avec succès")
            except RepairError as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def _apply_filters(self):
        """Application des filtres sur la liste des réparations"""
        status = self.status_filter.currentText()
        search_text = self.search_input.text().lower()
        
        for row in range(self.repairs_table.rowCount()):
            show_row = True
            
            # Filtre par statut
            if status != "Tous":
                repair_status = self.repairs_table.item(row, 4).text()
                if repair_status != status:
                    show_row = False
            
            # Filtre par recherche
            if search_text:
                found = False
                for col in range(self.repairs_table.columnCount()):
                    item = self.repairs_table.item(row, col)
                    if item and search_text in item.text().lower():
                        found = True
                        break
                if not found:
                    show_row = False
            
            self.repairs_table.setRowHidden(row, not show_row)

class RepairDialog(QDialog):
    def __init__(self, parent=None, repair=None):
        super().__init__(parent)
        self.repair = repair
        self._init_ui()
        if repair:
            self._load_repair_data()
    
    def _init_ui(self):
        """Initialisation de l'interface utilisateur"""
        self.setWindowTitle("Réparation")
        layout = QFormLayout(self)
        
        # Champs de base
        self.client_combo = QComboBox()
        self.device_combo = QComboBox()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["warranty", "paid", "maintenance"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["pending", "in_progress", "completed", "cancelled"])
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high", "urgent"])
        
        self.description_edit = QTextEdit()
        self.diagnosis_edit = QTextEdit()
        
        self.estimated_cost_spin = QDoubleSpinBox()
        self.estimated_cost_spin.setRange(0, 1000000)
        self.estimated_cost_spin.setSuffix(" €")
        
        self.estimated_date_edit = QDateEdit()
        self.estimated_date_edit.setDate(QDate.currentDate().addDays(7))
        
        # Ajout des champs au layout
        layout.addRow("Client:", self.client_combo)
        layout.addRow("Appareil:", self.device_combo)
        layout.addRow("Type:", self.type_combo)
        layout.addRow("Statut:", self.status_combo)
        layout.addRow("Priorité:", self.priority_combo)
        layout.addRow("Description:", self.description_edit)
        layout.addRow("Diagnostic:", self.diagnosis_edit)
        layout.addRow("Coût estimé:", self.estimated_cost_spin)
        layout.addRow("Date estimée:", self.estimated_date_edit)
        
        # Boutons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
    
    def _load_repair_data(self):
        """Chargement des données de la réparation existante"""
        self.client_combo.setCurrentText(self.repair.client.name)
        self.device_combo.setCurrentText(f"{self.repair.device.brand} {self.repair.device.model}")
        self.type_combo.setCurrentText(self.repair.type)
        self.status_combo.setCurrentText(self.repair.status)
        self.priority_combo.setCurrentText(self.repair.priority)
        self.description_edit.setText(self.repair.description)
        self.diagnosis_edit.setText(self.repair.diagnosis)
        self.estimated_cost_spin.setValue(self.repair.estimated_cost)
        self.estimated_date_edit.setDate(QDate.fromString(
            self.repair.estimated_completion_date, "yyyy-MM-dd"
        ))
    
    def get_repair_data(self):
        """Récupération des données du formulaire"""
        return {
            'client_id': self.client_combo.currentData(),
            'device_id': self.device_combo.currentData(),
            'type': self.type_combo.currentText(),
            'status': self.status_combo.currentText(),
            'priority': self.priority_combo.currentText(),
            'description': self.description_edit.toPlainText(),
            'diagnosis': self.diagnosis_edit.toPlainText(),
            'estimated_cost': self.estimated_cost_spin.value(),
            'estimated_completion_date': self.estimated_date_edit.date().toString("yyyy-MM-dd")
        } 