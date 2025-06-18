from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QMenuBar,
    QStatusBar, QMessageBox, QToolBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from alder_sav.config.settings import APP_NAME, UI_CONFIG
from alder_sav.ui.frp.repair_view import RepairView
from alder_sav.ui.clients.client_view import ClientView
from alder_sav.ui.dashboard.dashboard_view import DashboardView

class MainWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(UI_CONFIG['window']['width'], UI_CONFIG['window']['height'])
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Menu latéral
        self.sidebar = QWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        
        # Boutons du menu
        self.btn_dashboard = QPushButton("Tableau de bord")
        self.btn_repairs = QPushButton("Réparations")
        self.btn_clients = QPushButton("Clients")
        
        # Ajout des boutons au menu
        self.sidebar_layout.addWidget(self.btn_dashboard)
        self.sidebar_layout.addWidget(self.btn_repairs)
        self.sidebar_layout.addWidget(self.btn_clients)
        self.sidebar_layout.addStretch()
        
        # Zone de contenu
        self.content = QStackedWidget()
        self.dashboard_view = DashboardView(self.session)
        self.repair_view = RepairView(self.session)
        self.client_view = ClientView(self.session)
        
        self.content.addWidget(self.dashboard_view)
        self.content.addWidget(self.repair_view)
        self.content.addWidget(self.client_view)
        
        # Ajout des widgets au layout principal
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content)
        
        # Connexion des signaux
        self.btn_dashboard.clicked.connect(lambda: self.content.setCurrentWidget(self.dashboard_view))
        self.btn_repairs.clicked.connect(lambda: self.content.setCurrentWidget(self.repair_view))
        self.btn_clients.clicked.connect(lambda: self.content.setCurrentWidget(self.client_view))
        
        # Afficher le tableau de bord par défaut
        self.content.setCurrentWidget(self.dashboard_view)
        
        # Création des composants
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """Création de la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        
        new_frp_action = QAction("Nouveau FRP", self)
        new_frp_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_frp_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Édition
        edit_menu = menubar.addMenu("Édition")
        
        # Menu Affichage
        view_menu = menubar.addMenu("Affichage")
        
        # Menu Outils
        tools_menu = menubar.addMenu("Outils")
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Création de la barre d'outils"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        # Ajout des actions
        new_frp_action = QAction(QIcon("resources/icons/new_frp.png"), "Nouveau FRP", self)
        toolbar.addAction(new_frp_action)
        
        toolbar.addSeparator()
        
        search_action = QAction(QIcon("resources/icons/search.png"), "Rechercher", self)
        toolbar.addAction(search_action)
    
    def _create_status_bar(self):
        """Création de la barre de statut"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Ajout d'un label permanent
        status_bar.addPermanentWidget(QLabel("Prêt"))
    
    def _show_about(self):
        """Affichage de la boîte de dialogue À propos"""
        QMessageBox.about(
            self,
            f"À propos de {APP_NAME}",
            f"{APP_NAME}\n\n"
            "Logiciel de gestion SAV\n"
            "© 2024 Alder. Tous droits réservés."
        )
    
    def closeEvent(self, event):
        """Gestion de la fermeture de l'application"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment quitter l'application ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore() 