from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'votre_clé_secrète_ici'  # À changer en production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/alder_sav.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    
    # Configuration du login manager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Import et enregistrement des routes
    from routes import main_bp
    app.register_blueprint(main_bp)
    
    return app 