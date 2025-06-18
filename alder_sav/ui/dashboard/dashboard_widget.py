from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from database.models import FRP, Client, Statistique

class DashboardWidget(QWidget):
    """Widget de tableau de bord"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._setup_timer()
    
    def _init_ui(self):
        """Initialisation de l'interface"""
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        # Titre
        title = QLabel("Tableau de bord")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Filtre période
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Période:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Aujourd'hui",
            "Cette semaine",
            "Ce mois",
            "Cette année"
        ])
        self.period_combo.currentTextChanged.connect(self._update_statistics)
        period_layout.addWidget(self.period_combo)
        header_layout.addLayout(period_layout)
        
        layout.addWidget(header)
        
        # Statistiques
        stats_group = QWidget()
        stats_layout = QHBoxLayout(stats_group)
        
        # FRP en cours
        frp_widget = self._create_stat_widget(
            "FRP en cours",
            "0",
            "orange"
        )
        stats_layout.addWidget(frp_widget)
        
        # FRP validés
        validated_widget = self._create_stat_widget(
            "FRP validés",
            "0",
            "green"
        )
        stats_layout.addWidget(validated_widget)
        
        # FRP refusés
        rejected_widget = self._create_stat_widget(
            "FRP refusés",
            "0",
            "red"
        )
        stats_layout.addWidget(rejected_widget)
        
        # Clients actifs
        clients_widget = self._create_stat_widget(
            "Clients actifs",
            "0",
            "blue"
        )
        stats_layout.addWidget(clients_widget)
        
        layout.addWidget(stats_group)
        
        # FRP récents
        recent_frp_group = QWidget()
        recent_frp_layout = QVBoxLayout(recent_frp_group)
        recent_frp_layout.addWidget(QLabel("FRP récents"))
        
        self.recent_frp_table = QTableWidget()
        self.recent_frp_table.setColumnCount(5)
        self.recent_frp_table.setHorizontalHeaderLabels([
            "Numéro", "Client", "Date", "Statut", "Type"
        ])
        recent_frp_layout.addWidget(self.recent_frp_table)
        
        layout.addWidget(recent_frp_group)
        
        # Actions rapides
        quick_actions = QWidget()
        quick_actions_layout = QHBoxLayout(quick_actions)
        
        new_frp_btn = QPushButton("Nouveau FRP")
        new_frp_btn.clicked.connect(self._create_new_frp)
        quick_actions_layout.addWidget(new_frp_btn)
        
        new_client_btn = QPushButton("Nouveau client")
        new_client_btn.clicked.connect(self._create_new_client)
        quick_actions_layout.addWidget(new_client_btn)
        
        export_btn = QPushButton("Exporter")
        export_btn.clicked.connect(self._export_data)
        quick_actions_layout.addWidget(export_btn)
        
        layout.addWidget(quick_actions)
    
    def _create_stat_widget(self, title, value, color):
        """Création d'un widget de statistique"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        widget.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        
        layout = QVBoxLayout(widget)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Valeur
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(value_label)
        
        return widget
    
    def _setup_timer(self):
        """Configuration du timer de mise à jour"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_statistics)
        self.timer.start(300000)  # Mise à jour toutes les 5 minutes
    
    def _update_statistics(self):
        """Mise à jour des statistiques"""
        # Récupération de la période
        period = self.period_combo.currentText()
        start_date = self._get_start_date(period)
        
        # Mise à jour des statistiques
        self._update_frp_stats(start_date)
        self._update_client_stats(start_date)
        self._update_recent_frp()
    
    def _get_start_date(self, period):
        """Récupération de la date de début selon la période"""
        now = datetime.now()
        
        if period == "Aujourd'hui":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "Cette semaine":
            return now - timedelta(days=now.weekday())
        elif period == "Ce mois":
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # Cette année
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def _update_frp_stats(self, start_date):
        """Mise à jour des statistiques FRP"""
        # TODO: Implémenter la récupération des statistiques depuis la base de données
        pass
    
    def _update_client_stats(self, start_date):
        """Mise à jour des statistiques clients"""
        # TODO: Implémenter la récupération des statistiques depuis la base de données
        pass
    
    def _update_recent_frp(self):
        """Mise à jour de la liste des FRP récents"""
        # TODO: Implémenter la récupération des FRP récents depuis la base de données
        pass
    
    def _create_new_frp(self):
        """Création d'un nouveau FRP"""
        # TODO: Implémenter la création d'un nouveau FRP
        pass
    
    def _create_new_client(self):
        """Création d'un nouveau client"""
        # TODO: Implémenter la création d'un nouveau client
        pass
    
    def _export_data(self):
        """Export des données"""
        # TODO: Implémenter l'export des données
        pass 