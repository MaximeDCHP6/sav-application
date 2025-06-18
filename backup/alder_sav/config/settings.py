import os
from pathlib import Path

# Informations de l'application
APP_NAME = "Alder SAV"
APP_VERSION = "1.0.0"

# Chemins des répertoires
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
EXPORT_DIR = DATA_DIR / "exports"
ARCHIVE_DIR = DATA_DIR / "archives"
REPORT_DIR = DATA_DIR / "reports"
TEMPLATE_DIR = BASE_DIR / "resources" / "templates"
ICON_DIR = BASE_DIR / "resources" / "icons"

# Création des répertoires
for directory in [DATA_DIR, BACKUP_DIR, EXPORT_DIR, ARCHIVE_DIR, REPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration de la base de données
DATABASE_CONFIG = {
    'url': 'sqlite:///alder_sav.db',
    'echo': False
}

# Configuration de l'authentification
AUTH_CONFIG = {
    'jwt_secret': os.getenv('JWT_SECRET', 'your-secret-key'),
    'jwt_algorithm': 'HS256',
    'token_expiration_days': 7,
    'role_permissions': {
        'admin': [
            'manage_users',
            'manage_frp',
            'manage_clients',
            'view_statistics',
            'export_data',
            'manage_backups'
        ],
        'manager': [
            'manage_frp',
            'manage_clients',
            'view_statistics',
            'export_data'
        ],
        'operator': [
            'manage_frp',
            'view_statistics'
        ],
        'viewer': [
            'view_frp',
            'view_statistics'
        ]
    }
}

# Configuration des emails
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'sender': os.getenv('EMAIL_SENDER', 'sav@alder.fr')
}

# Configuration des notifications
NOTIFICATION_CONFIG = {
    'email': {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True
    },
    'sms': {
        'enabled': False,
        'provider': 'twilio'
    },
    'frp_creation_recipients': [
        'manager@alder.fr',
        'sav@alder.fr'
    ],
    'status_change_recipients': [
        'manager@alder.fr',
        'sav@alder.fr'
    ],
    'delay_recipients': [
        'manager@alder.fr'
    ],
    'daily_summary_recipients': [
        'manager@alder.fr',
        'director@alder.fr'
    ],
    'weekly_report_recipients': [
        'manager@alder.fr',
        'director@alder.fr'
    ],
    'delay_threshold': 7  # jours
}

# Configuration du planificateur
SCHEDULER_CONFIG = {
    'backup_cleanup_time': '03:00',
    'delay_check_time': '09:00',
    'daily_summary_time': '18:00',
    'weekly_report_time': '09:00',
    'archive_time': '01:00',
    'backup_retention_days': 30,
    'archive_months': 6
}

# Configuration des exports
EXPORT_CONFIG = {
    'default_format': 'xlsx',
    'date_format': '%d/%m/%Y',
    'number_format': '%.2f',
    'excel_template': TEMPLATE_DIR / 'excel_template.xlsx',
    'pdf_template': TEMPLATE_DIR / 'pdf_template.html'
}

# Configuration des rapports
REPORT_CONFIG = {
    'export_dir': 'exports',
    'templates_dir': 'templates/reports',
    'formats': ['pdf', 'excel', 'csv'],
    'default_format': 'pdf',
    'company_name': 'Alder',
    'company_address': '123 Rue Example, 75000 Paris',
    'company_phone': '01 23 45 67 89',
    'company_email': 'contact@alder.fr',
    'logo_path': ICON_DIR / 'logo.png'
}

# Configuration des statistiques
STATS_CONFIG = {
    'default_period': 30,  # jours
    'chart_colors': [
        '#1f77b4',  # bleu
        '#ff7f0e',  # orange
        '#2ca02c',  # vert
        '#d62728',  # rouge
        '#9467bd',  # violet
        '#8c564b',  # marron
        '#e377c2',  # rose
        '#7f7f7f',  # gris
        '#bcbd22',  # jaune-vert
        '#17becf'   # cyan
    ]
}

# Configuration de l'interface
UI_CONFIG = {
    'theme': 'light',
    'language': 'fr',
    'window': {
        'width': 1200,
        'height': 800,
        'title': APP_NAME
    },
    'date_format': '%d/%m/%Y',
    'time_format': '%H:%M',
    'number_format': '%.2f',
    'currency': '€',
    'window_icon': ICON_DIR / 'icon.png',
    'window_size': (1200, 800),
    'window_min_size': (800, 600)
}

# Configuration des logs
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/alder_sav.log'
}

# Configuration des sauvegardes
BACKUP_CONFIG = {
    'auto_backup': True,
    'backup_interval': 24,  # heures
    'backup_time': '02:00',
    'backup_dir': BACKUP_DIR,
    'backup_format': '%Y%m%d_%H%M%S',
    'backup_prefix': 'sav_backup_',
    'backup_extension': '.db'
}

# Configuration des archives
ARCHIVE_CONFIG = {
    'auto_archive': True,
    'archive_interval': 30,  # jours
    'archive_time': '01:00',
    'archive_dir': ARCHIVE_DIR,
    'archive_format': '%Y%m%d_%H%M%S',
    'archive_prefix': 'sav_archive_',
    'archive_extension': '.zip'
}

# Configuration des documents
DOCUMENT_CONFIG = {
    'allowed_extensions': [
        '.pdf',
        '.doc',
        '.docx',
        '.xls',
        '.xlsx',
        '.jpg',
        '.jpeg',
        '.png'
    ],
    'max_size': 10 * 1024 * 1024,  # 10 Mo
    'upload_dir': DATA_DIR / 'documents',
    'temp_dir': DATA_DIR / 'temp'
}

# Configuration des clients
CLIENT_CONFIG = {
    'auto_numbering': True,
    'number_prefix': 'CLI',
    'number_padding': 6,
    'number_start': 1
}

# Configuration des FRP
FRP_CONFIG = {
    'auto_numbering': True,
    'number_prefix': 'FRP',
    'number_padding': 6,
    'number_start': 1,
    'max_products': 10,
    'max_documents': 5,
    'statuses': [
        'Nouveau',
        'En cours',
        'En attente',
        'Résolu',
        'Annulé'
    ],
    'types': [
        'Retour',
        'Réclamation',
        'Garantie',
        'Autre'
    ]
}

# Configuration des fournisseurs
SUPPLIER_CONFIG = {
    'auto_numbering': True,
    'number_prefix': 'FOU',
    'number_padding': 6,
    'number_start': 1
}

# Configuration des transporteurs
CARRIER_CONFIG = {
    'auto_numbering': True,
    'number_prefix': 'TRA',
    'number_padding': 6,
    'number_start': 1
}

# Configuration de la sécurité
SECURITY_CONFIG = {
    'password_min_length': 8,
    'require_special_chars': True,
    'require_numbers': True,
    'require_uppercase': True,
    'session_timeout': 3600  # 1 heure
} 