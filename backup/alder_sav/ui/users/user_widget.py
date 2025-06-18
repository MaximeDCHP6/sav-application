from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from database.models import User, UserRole
from config.settings import SECURITY_CONFIG

class UserWidget(QWidget):
    """Widget de gestion des utilisateurs"""
    
    # Signaux
    user_created = pyqtSignal(User)
    user_updated = pyqtSignal(User)
    user_deleted = pyqtSignal(int)  # ID de l'utilisateur
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialisation de l'interface"""
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        # Titre
        title = QLabel("Gestion des utilisateurs")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Formulaire utilisateur
        form_group = QWidget()
        form_layout = QVBoxLayout(form_group)
        
        # Nom d'utilisateur
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Nom d'utilisateur:"))
        self.username = QLineEdit()
        username_layout.addWidget(self.username)
        form_layout.addLayout(username_layout)
        
        # Mot de passe
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Mot de passe:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password)
        form_layout.addLayout(password_layout)
        
        # Confirmation mot de passe
        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("Confirmer mot de passe:"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_layout.addWidget(self.confirm_password)
        form_layout.addLayout(confirm_layout)
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email = QLineEdit()
        email_layout.addWidget(self.email)
        form_layout.addLayout(email_layout)
        
        # Rôle
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Rôle:"))
        self.role = QComboBox()
        self.role.addItems([role.value for role in UserRole])
        role_layout.addWidget(self.role)
        form_layout.addLayout(role_layout)
        
        # Actif
        active_layout = QHBoxLayout()
        self.active = QCheckBox("Utilisateur actif")
        self.active.setChecked(True)
        active_layout.addWidget(self.active)
        form_layout.addLayout(active_layout)
        
        layout.addWidget(form_group)
        
        # Liste des utilisateurs
        list_group = QWidget()
        list_layout = QVBoxLayout(list_group)
        list_layout.addWidget(QLabel("Liste des utilisateurs"))
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "Nom d'utilisateur", "Email", "Rôle", "Dernière connexion", "Statut"
        ])
        list_layout.addWidget(self.users_table)
        
        layout.addWidget(list_group)
        
        # Boutons d'action
        action_buttons = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self._save_user)
        action_buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self._cancel)
        action_buttons.addWidget(cancel_btn)
        
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self._delete_user)
        action_buttons.addWidget(delete_btn)
        
        layout.addLayout(action_buttons)
    
    def _save_user(self):
        """Sauvegarde de l'utilisateur"""
        # Validation des données
        if not self._validate_data():
            return
        
        # Création ou mise à jour de l'utilisateur
        if self.current_user is None:
            self.current_user = User()
        
        # Mise à jour des données
        self._update_user_data()
        
        # Émission du signal approprié
        if self.current_user.id is None:
            self.user_created.emit(self.current_user)
        else:
            self.user_updated.emit(self.current_user)
        
        QMessageBox.information(
            self,
            "Succès",
            "Utilisateur enregistré avec succès"
        )
    
    def _validate_data(self):
        """Validation des données de l'utilisateur"""
        if not self.username.text():
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom d'utilisateur est requis"
            )
            return False
        
        if not self.password.text():
            QMessageBox.warning(
                self,
                "Erreur",
                "Le mot de passe est requis"
            )
            return False
        
        if self.password.text() != self.confirm_password.text():
            QMessageBox.warning(
                self,
                "Erreur",
                "Les mots de passe ne correspondent pas"
            )
            return False
        
        if len(self.password.text()) < SECURITY_CONFIG['password_min_length']:
            QMessageBox.warning(
                self,
                "Erreur",
                f"Le mot de passe doit contenir au moins {SECURITY_CONFIG['password_min_length']} caractères"
            )
            return False
        
        if SECURITY_CONFIG['password_require_special']:
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in self.password.text()):
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Le mot de passe doit contenir au moins un caractère spécial"
                )
                return False
        
        return True
    
    def _update_user_data(self):
        """Mise à jour des données de l'utilisateur"""
        self.current_user.username = self.username.text()
        self.current_user.password = self.password.text()  # TODO: Hasher le mot de passe
        self.current_user.email = self.email.text()
        self.current_user.role = UserRole(self.role.currentText())
        
        if self.current_user.id is None:
            self.current_user.created_at = datetime.now()
    
    def _cancel(self):
        """Annulation des modifications"""
        if self.current_user is not None:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Voulez-vous vraiment annuler les modifications ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.clear()
    
    def _delete_user(self):
        """Suppression de l'utilisateur"""
        if self.current_user is None:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet utilisateur ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.user_deleted.emit(self.current_user.id)
            self.clear()
    
    def clear(self):
        """Réinitialisation du formulaire"""
        self.current_user = None
        self.username.clear()
        self.password.clear()
        self.confirm_password.clear()
        self.email.clear()
        self.role.setCurrentIndex(0)
        self.active.setChecked(True)
    
    def load_user(self, user):
        """Chargement d'un utilisateur existant"""
        self.clear()
        self.current_user = user
        
        # Remplissage des champs
        self.username.setText(user.username)
        self.email.setText(user.email)
        self.role.setCurrentText(user.role.value)
        self.active.setChecked(True)  # TODO: Ajouter un champ actif dans le modèle
    
    def update_users_table(self, users):
        """Mise à jour de la table des utilisateurs"""
        self.users_table.setRowCount(0)
        
        for user in users:
            row = self.users_table.rowCount()
            self.users_table.insertRow(row)
            
            self.users_table.setItem(row, 0, QTableWidgetItem(user.username))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.email))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.role.value))
            self.users_table.setItem(
                row, 3,
                QTableWidgetItem(
                    user.last_login.strftime("%d/%m/%Y %H:%M")
                    if user.last_login else "Jamais"
                )
            )
            self.users_table.setItem(row, 4, QTableWidgetItem("Actif")) 