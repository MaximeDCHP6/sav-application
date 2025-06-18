import os
from datetime import timedelta
from flask import render_template, jsonify

class Config:
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'sav.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des sessions
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = False  # Désactivé en développement
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuration des fichiers
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'msg'}
    
    # Configuration des emails
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Configuration de l'application
    TICKETS_PER_PAGE = 25
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_TIMEOUT = 30  # minutes
    
    # Configuration des sauvegardes
    BACKUP_FOLDER = os.path.join(BASE_DIR, 'backups')
    BACKUP_FREQUENCY = 1  # heures
    BACKUP_RETENTION = 30  # jours
    
    # Configuration des logs
    LOG_FOLDER = os.path.join(BASE_DIR, 'logs')
    LOG_LEVEL = 'INFO'
    
    # Configuration de Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    @staticmethod
    def init_app(app):
        # Créer les dossiers nécessaires
        for folder in [app.config['UPLOAD_FOLDER'], app.config['BACKUP_FOLDER'], app.config['LOG_FOLDER']]:
            os.makedirs(folder, exist_ok=True)
        
        # Configurer le logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        log_file = os.path.join(app.config['LOG_FOLDER'], 'app.log')
        handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=10)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        
        # Configurer la gestion des erreurs
        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('404.html'), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            try:
                from extensions import db
                db.session.rollback()
            except:
                pass  # Ignorer si db n'est pas disponible
            return render_template('500.html'), 500
        
        @app.errorhandler(413)
        def request_entity_too_large(error):
            return jsonify({'error': 'Fichier trop volumineux'}), 413
        
        @app.errorhandler(400)
        def bad_request(error):
            return jsonify({'error': 'Requête invalide'}), 400 