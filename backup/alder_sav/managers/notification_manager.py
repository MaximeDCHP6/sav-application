from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

from alder_sav.database.models.notification import Notification, NotificationTemplate
from alder_sav.utils.exceptions import NotificationError
from alder_sav.config.settings import SMTP_CONFIG

class NotificationManager:
    """Gestionnaire des notifications"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_notification(
        self,
        recipient_id: int,
        type: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = 'normal'
    ) -> Notification:
        """
        Crée une nouvelle notification.
        
        Args:
            recipient_id: ID du destinataire
            type: Type de notification
            content: Contenu de la notification
            data: Données supplémentaires (optionnel)
            priority: Priorité de la notification
            
        Returns:
            Notification créée
        """
        notification = Notification(
            recipient_id=recipient_id,
            type=type,
            content=content,
            data=json.dumps(data) if data else None,
            priority=priority,
            status='pending',
            created_at=datetime.now()
        )
        
        self.session.add(notification)
        self.session.commit()
        
        return notification
    
    def get_notification(self, notification_id: int) -> Notification:
        """
        Récupère une notification par son ID.
        
        Args:
            notification_id: ID de la notification
            
        Returns:
            Notification
            
        Raises:
            NotificationError: Si la notification n'existe pas
        """
        notification = self.session.query(Notification).get(notification_id)
        if not notification:
            raise NotificationError(f"La notification {notification_id} n'existe pas")
        return notification
    
    def update_notification(
        self,
        notification_id: int,
        data: dict
    ) -> Notification:
        """
        Met à jour une notification.
        
        Args:
            notification_id: ID de la notification
            data: Données à mettre à jour
            
        Returns:
            Notification mise à jour
            
        Raises:
            NotificationError: Si la notification n'existe pas
        """
        notification = self.get_notification(notification_id)
        
        # Mettre à jour les champs
        for key, value in data.items():
            if key == 'data' and value is not None:
                setattr(notification, key, json.dumps(value))
            elif hasattr(notification, key):
                setattr(notification, key, value)
        
        notification.updated_at = datetime.now()
        self.session.commit()
        
        return notification
    
    def delete_notification(self, notification_id: int) -> None:
        """
        Supprime une notification.
        
        Args:
            notification_id: ID de la notification
            
        Raises:
            NotificationError: Si la notification n'existe pas
        """
        notification = self.get_notification(notification_id)
        self.session.delete(notification)
        self.session.commit()
    
    def get_notifications_by_recipient(
        self,
        recipient_id: int,
        status: Optional[str] = None
    ) -> List[Notification]:
        """
        Récupère les notifications d'un destinataire.
        
        Args:
            recipient_id: ID du destinataire
            status: Filtre par statut (optionnel)
            
        Returns:
            Liste des notifications
        """
        query = self.session.query(Notification).filter(
            Notification.recipient_id == recipient_id
        )
        
        if status:
            query = query.filter(Notification.status == status)
        
        return query.order_by(Notification.created_at.desc()).all()
    
    def get_notifications_by_type(
        self,
        type: str,
        status: Optional[str] = None
    ) -> List[Notification]:
        """
        Récupère les notifications d'un type donné.
        
        Args:
            type: Type de notification
            status: Filtre par statut (optionnel)
            
        Returns:
            Liste des notifications
        """
        query = self.session.query(Notification).filter(
            Notification.type == type
        )
        
        if status:
            query = query.filter(Notification.status == status)
        
        return query.order_by(Notification.created_at.desc()).all()
    
    def send_notification(self, notification_id: int) -> None:
        """
        Envoie une notification.
        
        Args:
            notification_id: ID de la notification
            
        Raises:
            NotificationError: Si la notification n'existe pas ou si l'envoi échoue
        """
        notification = self.get_notification(notification_id)
        
        try:
            # Préparer le message
            msg = MIMEMultipart()
            msg['From'] = SMTP_CONFIG['username']
            msg['To'] = notification.recipient.email
            msg['Subject'] = f"Notification: {notification.type}"
            
            # Ajouter le contenu
            msg.attach(MIMEText(notification.content, 'plain'))
            
            # Envoyer l'email
            with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
                server.starttls()
                server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
                server.send_message(msg)
            
            # Mettre à jour le statut
            notification.status = 'sent'
            notification.sent_at = datetime.now()
            self.session.commit()
            
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            self.session.commit()
            raise NotificationError(f"Erreur lors de l'envoi de la notification: {str(e)}")
    
    def send_bulk_notifications(
        self,
        notification_ids: List[int]
    ) -> Dict[str, int]:
        """
        Envoie plusieurs notifications en masse.
        
        Args:
            notification_ids: Liste des IDs de notifications
            
        Returns:
            Dictionnaire avec le nombre de notifications envoyées et échouées
        """
        results = {'success': 0, 'failed': 0}
        
        for notification_id in notification_ids:
            try:
                self.send_notification(notification_id)
                results['success'] += 1
            except NotificationError:
                results['failed'] += 1
        
        return results
    
    def create_notification_template(
        self,
        name: str,
        type: str,
        subject: str,
        content: str,
        variables: Optional[List[str]] = None
    ) -> NotificationTemplate:
        """
        Crée un modèle de notification.
        
        Args:
            name: Nom du modèle
            type: Type de notification
            subject: Sujet
            content: Contenu
            variables: Liste des variables (optionnel)
            
        Returns:
            Modèle de notification créé
            
        Raises:
            NotificationError: Si le modèle existe déjà
        """
        if self.session.query(NotificationTemplate).filter(
            NotificationTemplate.name == name
        ).first():
            raise NotificationError(f"Le modèle {name} existe déjà")
        
        template = NotificationTemplate(
            name=name,
            type=type,
            subject=subject,
            content=content,
            variables=json.dumps(variables) if variables else None,
            created_at=datetime.now()
        )
        
        self.session.add(template)
        self.session.commit()
        
        return template
    
    def get_notification_template(
        self,
        template_id: int
    ) -> NotificationTemplate:
        """
        Récupère un modèle de notification par son ID.
        
        Args:
            template_id: ID du modèle
            
        Returns:
            Modèle de notification
            
        Raises:
            NotificationError: Si le modèle n'existe pas
        """
        template = self.session.query(NotificationTemplate).get(template_id)
        if not template:
            raise NotificationError(f"Le modèle {template_id} n'existe pas")
        return template
    
    def update_notification_template(
        self,
        template_id: int,
        data: dict
    ) -> NotificationTemplate:
        """
        Met à jour un modèle de notification.
        
        Args:
            template_id: ID du modèle
            data: Données à mettre à jour
            
        Returns:
            Modèle de notification mis à jour
            
        Raises:
            NotificationError: Si le modèle n'existe pas
        """
        template = self.get_notification_template(template_id)
        
        # Mettre à jour les champs
        for key, value in data.items():
            if key == 'variables' and value is not None:
                setattr(template, key, json.dumps(value))
            elif hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.now()
        self.session.commit()
        
        return template
    
    def delete_notification_template(self, template_id: int) -> None:
        """
        Supprime un modèle de notification.
        
        Args:
            template_id: ID du modèle
            
        Raises:
            NotificationError: Si le modèle n'existe pas
        """
        template = self.get_notification_template(template_id)
        self.session.delete(template)
        self.session.commit()
    
    def get_notification_templates_by_type(
        self,
        type: str
    ) -> List[NotificationTemplate]:
        """
        Récupère les modèles de notification d'un type donné.
        
        Args:
            type: Type de notification
            
        Returns:
            Liste des modèles de notification
        """
        return self.session.query(NotificationTemplate).filter(
            NotificationTemplate.type == type
        ).all()
    
    def render_template(
        self,
        template_id: int,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Rend un modèle de notification avec des variables.
        
        Args:
            template_id: ID du modèle
            variables: Variables à remplacer
            
        Returns:
            Dictionnaire avec le sujet et le contenu rendus
            
        Raises:
            NotificationError: Si le modèle n'existe pas ou si des variables sont manquantes
        """
        template = self.get_notification_template(template_id)
        
        # Vérifier les variables requises
        required_vars = json.loads(template.variables) if template.variables else []
        missing_vars = [var for var in required_vars if var not in variables]
        
        if missing_vars:
            raise NotificationError(
                f"Variables manquantes: {', '.join(missing_vars)}"
            )
        
        # Remplacer les variables
        subject = template.subject
        content = template.content
        
        for key, value in variables.items():
            subject = subject.replace(f"{{{{{key}}}}}", str(value))
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        return {
            'subject': subject,
            'content': content
        } 