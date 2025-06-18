from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from extensions import db, login_manager, init_extensions
from config import Config
import os
from dotenv import load_dotenv
from flask_redis import FlaskRedis
import redis

# Charger les variables d'environnement
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Charger la configuration
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Initialiser Redis
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
    app.redis = redis_client
    
    # Créer les dossiers nécessaires
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)
    
    # Configurer la journalisation
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Créer le dossier de logs s'il n'existe pas
        if not os.path.exists(app.config['LOG_FOLDER']):
            os.mkdir(app.config['LOG_FOLDER'])
        
        # Configurer le fichier de log
        file_handler = RotatingFileHandler(
            os.path.join(app.config['LOG_FOLDER'], 'app.log'),
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application démarrée')
    
    # Enregistrer les blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)
    
    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template('413.html'), 413
    
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('400.html'), 400
    
    return app 