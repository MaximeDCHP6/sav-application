from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DashboardView(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Tableau de bord")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Statistiques
        stats_layout = QGridLayout()
        
        # En cours
        in_progress = self.create_stat_card("En cours", "12")
        stats_layout.addWidget(in_progress, 0, 0)
        
        # Terminées
        completed = self.create_stat_card("Terminées", "45")
        stats_layout.addWidget(completed, 0, 1)
        
        # En attente
        pending = self.create_stat_card("En attente", "8")
        stats_layout.addWidget(pending, 0, 2)
        
        # Clients
        clients = self.create_stat_card("Clients", "156")
        stats_layout.addWidget(clients, 1, 0)
        
        # Techniciens
        technicians = self.create_stat_card("Techniciens", "8")
        stats_layout.addWidget(technicians, 1, 1)
        
        # Satisfaction
        satisfaction = self.create_stat_card("Satisfaction", "92%")
        stats_layout.addWidget(satisfaction, 1, 2)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
    def create_stat_card(self, title, value):
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card 