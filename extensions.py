from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_migrate import Migrate
from flask_compress import Compress
from flask_talisman import Talisman
import redis

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
migrate = Migrate()
compress = Compress()
talisman = Talisman()
redis_client = redis.Redis()

def init_extensions(app):
    """Initialise toutes les extensions Flask avec la configuration de l'application"""
    
    # Configuration de la base de données
    db.init_app(app)
    
    # Configuration de l'authentification
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Configuration du mail
    mail.init_app(app)
    
    # Configuration de la protection CSRF
    csrf.init_app(app)
    
    # Configuration du rate limiting
    limiter.init_app(app)
    
    # Configuration du cache
    cache.init_app(app)
    
    # Configuration des migrations
    migrate.init_app(app, db)
    
    # Configuration de la compression
    compress.init_app(app)
    
    # Configuration de la sécurité (désactivée en développement)
    if app.env != "development":
        talisman.init_app(
            app,
            force_https=True,
            strict_transport_security=True,
            session_cookie_secure=True,
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
                'style-src': "'self' 'unsafe-inline'",
                'img-src': "'self' data:",
                'font-src': "'self'",
                'object-src': "'none'",
                'media-src': "'self'",
                'frame-src': "'none'",
                'sandbox': ['allow-forms', 'allow-same-origin', 'allow-scripts'],
                'report-uri': '/report-violation',
                'worker-src': "'self'",
                'child-src': "'self'",
                'connect-src': "'self'",
                'base-uri': "'self'",
                'form-action': "'self'",
                'frame-ancestors': "'none'",
                'upgrade-insecure-requests': True
            }
        )
    
    # Configuration de Redis
    redis_client.init_app(app)
    
    # Configuration des limites de taux par défaut
    limiter.limit("200 per day")(app)
    limiter.limit("50 per hour")(app)
    limiter.limit("10 per minute")(app)
    
    # Configuration des routes protégées
    @app.before_request
    def before_request():
        if not request.is_secure and app.env != "development":
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if app.env != "development":
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response 