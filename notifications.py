from flask import current_app
from flask_mail import Mail, Message
from threading import Thread
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notifications.log'),
        logging.StreamHandler()
    ]
)

mail = Mail()

def init_mail(app):
    """Initialise l'extension Flask-Mail."""
    app.config['MAIL_SERVER'] = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = app.config.get('MAIL_PORT', 587)
    app.config['MAIL_USE_TLS'] = app.config.get('MAIL_USE_TLS', True)
    app.config['MAIL_USERNAME'] = app.config.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = app.config.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = app.config.get('MAIL_DEFAULT_SENDER')
    
    mail.init_app(app)

def send_async_email(app, msg):
    """Envoie un email de manière asynchrone."""
    with app.app_context():
        try:
            mail.send(msg)
            logging.info(f"Email envoyé avec succès à {msg.recipients}")
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de l'email : {str(e)}")

def send_email(subject, recipients, body, html=None):
    """Envoie un email de manière asynchrone."""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html
        )
        
        Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        ).start()
        
        return True
    except Exception as e:
        logging.error(f"Erreur lors de la préparation de l'email : {str(e)}")
        return False

def notify_new_ticket(ticket):
    """Notifie de la création d'un nouveau ticket."""
    try:
        settings = current_app.config.get('SETTINGS')
        if not settings.notify_new_ticket:
            return False

        subject = f"Nouveau ticket #{ticket.number} créé"
        recipients = [settings.notification_email]
        
        body = f"""
        Un nouveau ticket a été créé :
        
        Numéro : {ticket.number}
        Client : {ticket.client_name}
        Compte : {ticket.account_number}
        Type de retour : {ticket.return_type}
        Statut : {ticket.status}
        
        Pour plus de détails, connectez-vous à l'application.
        """
        
        html = f"""
        <h2>Nouveau ticket #{ticket.number}</h2>
        <p>Un nouveau ticket a été créé :</p>
        <ul>
            <li><strong>Client :</strong> {ticket.client_name}</li>
            <li><strong>Compte :</strong> {ticket.account_number}</li>
            <li><strong>Type de retour :</strong> {ticket.return_type}</li>
            <li><strong>Statut :</strong> {ticket.status}</li>
        </ul>
        <p>Pour plus de détails, <a href="{current_app.config.get('BASE_URL')}/tickets/{ticket.id}">connectez-vous à l'application</a>.</p>
        """
        
        return send_email(subject, recipients, body, html)
    except Exception as e:
        logging.error(f"Erreur lors de la notification de nouveau ticket : {str(e)}")
        return False

def notify_status_change(ticket, old_status):
    """Notifie du changement de statut d'un ticket."""
    try:
        settings = current_app.config.get('SETTINGS')
        if not settings.notify_status_change:
            return False

        subject = f"Ticket #{ticket.number} - Changement de statut"
        recipients = [settings.notification_email]
        
        body = f"""
        Le statut du ticket #{ticket.number} a été modifié :
        
        Ancien statut : {old_status}
        Nouveau statut : {ticket.status}
        Client : {ticket.client_name}
        Compte : {ticket.account_number}
        
        Pour plus de détails, connectez-vous à l'application.
        """
        
        html = f"""
        <h2>Changement de statut - Ticket #{ticket.number}</h2>
        <p>Le statut du ticket a été modifié :</p>
        <ul>
            <li><strong>Ancien statut :</strong> {old_status}</li>
            <li><strong>Nouveau statut :</strong> {ticket.status}</li>
            <li><strong>Client :</strong> {ticket.client_name}</li>
            <li><strong>Compte :</strong> {ticket.account_number}</li>
        </ul>
        <p>Pour plus de détails, <a href="{current_app.config.get('BASE_URL')}/tickets/{ticket.id}">connectez-vous à l'application</a>.</p>
        """
        
        return send_email(subject, recipients, body, html)
    except Exception as e:
        logging.error(f"Erreur lors de la notification de changement de statut : {str(e)}")
        return False

def notify_anomaly(ticket, anomaly_type, details):
    """Notifie d'une anomalie détectée sur un ticket."""
    try:
        settings = current_app.config.get('SETTINGS')
        if not settings.notify_anomaly:
            return False

        subject = f"Anomalie détectée - Ticket #{ticket.number}"
        recipients = [settings.notification_email]
        
        body = f"""
        Une anomalie a été détectée sur le ticket #{ticket.number} :
        
        Type d'anomalie : {anomaly_type}
        Détails : {details}
        Client : {ticket.client_name}
        Compte : {ticket.account_number}
        
        Pour plus de détails, connectez-vous à l'application.
        """
        
        html = f"""
        <h2>Anomalie détectée - Ticket #{ticket.number}</h2>
        <p>Une anomalie a été détectée :</p>
        <ul>
            <li><strong>Type d'anomalie :</strong> {anomaly_type}</li>
            <li><strong>Détails :</strong> {details}</li>
            <li><strong>Client :</strong> {ticket.client_name}</li>
            <li><strong>Compte :</strong> {ticket.account_number}</li>
        </ul>
        <p>Pour plus de détails, <a href="{current_app.config.get('BASE_URL')}/tickets/{ticket.id}">connectez-vous à l'application</a>.</p>
        """
        
        return send_email(subject, recipients, body, html)
    except Exception as e:
        logging.error(f"Erreur lors de la notification d'anomalie : {str(e)}")
        return False 