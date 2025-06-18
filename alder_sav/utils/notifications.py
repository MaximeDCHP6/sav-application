import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from config.settings import EMAIL_CONFIG, NOTIFICATION_CONFIG

class NotificationManager:
    """Gestionnaire de notifications"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.email_config = EMAIL_CONFIG
        self.notification_config = NOTIFICATION_CONFIG
    
    def send_email(self, to_email, subject, body, is_html=False):
        """Envoi d'un email"""
        try:
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Ajout du contenu
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connexion au serveur SMTP
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            return True, "Email envoyé avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'envoi de l'email: {str(e)}"
    
    def notify_frp_creation(self, frp):
        """Notification de création d'un FRP"""
        try:
            # Préparation du contenu
            subject = f"Nouveau FRP créé: {frp.numero}"
            
            body = f"""
            Un nouveau FRP a été créé:
            
            Numéro: {frp.numero}
            Client: {frp.client.nom}
            Date: {frp.date_creation.strftime("%d/%m/%Y")}
            Type: {frp.type_motif}
            
            Vous pouvez consulter les détails dans l'application SAV.
            """
            
            # Envoi aux destinataires configurés
            for recipient in self.notification_config['frp_creation_recipients']:
                success, message = self.send_email(recipient, subject, body)
                if not success:
                    return False, message
            
            return True, "Notifications envoyées avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'envoi des notifications: {str(e)}"
    
    def notify_frp_status_change(self, frp, old_status):
        """Notification de changement de statut d'un FRP"""
        try:
            # Préparation du contenu
            subject = f"Changement de statut FRP: {frp.numero}"
            
            body = f"""
            Le statut du FRP {frp.numero} a été modifié:
            
            Ancien statut: {old_status}
            Nouveau statut: {frp.statut}
            Client: {frp.client.nom}
            Date: {datetime.now().strftime("%d/%m/%Y")}
            
            Vous pouvez consulter les détails dans l'application SAV.
            """
            
            # Envoi aux destinataires configurés
            for recipient in self.notification_config['status_change_recipients']:
                success, message = self.send_email(recipient, subject, body)
                if not success:
                    return False, message
            
            return True, "Notifications envoyées avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'envoi des notifications: {str(e)}"
    
    def notify_delayed_frps(self):
        """Notification des FRP en retard"""
        try:
            # Récupération des FRP en retard
            delay_threshold = self.notification_config['delay_threshold']
            current_date = datetime.now()
            
            delayed_frps = self.db_session.query(FRP).filter(
                FRP.statut != 'Résolu',
                FRP.date_creation <= current_date - timedelta(days=delay_threshold)
            ).all()
            
            if not delayed_frps:
                return True, "Aucun FRP en retard"
            
            # Préparation du contenu
            subject = "FRP en retard - Rappel"
            
            body = f"""
            Les FRP suivants sont en retard (plus de {delay_threshold} jours):
            
            """
            
            for frp in delayed_frps:
                body += f"""
                Numéro: {frp.numero}
                Client: {frp.client.nom}
                Date création: {frp.date_creation.strftime("%d/%m/%Y")}
                Statut actuel: {frp.statut}
                Délai: {(current_date - frp.date_creation).days} jours
                """
            
            body += """
            Veuillez prendre les mesures nécessaires.
            """
            
            # Envoi aux destinataires configurés
            for recipient in self.notification_config['delay_recipients']:
                success, message = self.send_email(recipient, subject, body)
                if not success:
                    return False, message
            
            return True, "Notifications envoyées avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'envoi des notifications: {str(e)}"
    
    def notify_daily_summary(self):
        """Notification du résumé quotidien"""
        try:
            # Récupération des statistiques du jour
            today = datetime.now().date()
            frps_today = self.db_session.query(FRP).filter(
                FRP.date_creation >= today
            ).all()
            
            # Préparation du contenu
            subject = f"Résumé quotidien SAV - {today.strftime('%d/%m/%Y')}"
            
            body = f"""
            Résumé des activités SAV du {today.strftime('%d/%m/%Y')}:
            
            Nouveaux FRP: {len(frps_today)}
            
            Détail par type:
            """
            
            type_count = {}
            for frp in frps_today:
                type_count[frp.type_motif] = type_count.get(frp.type_motif, 0) + 1
            
            for type_motif, count in type_count.items():
                body += f"{type_motif}: {count}\n"
            
            body += """
            Vous pouvez consulter les détails dans l'application SAV.
            """
            
            # Envoi aux destinataires configurés
            for recipient in self.notification_config['daily_summary_recipients']:
                success, message = self.send_email(recipient, subject, body)
                if not success:
                    return False, message
            
            return True, "Résumé quotidien envoyé avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'envoi du résumé quotidien: {str(e)}"
    
    def notify_weekly_report(self):
        """Notification du rapport hebdomadaire"""
        try:
            # Récupération des statistiques de la semaine
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            frps_week = self.db_session.query(FRP).filter(
                FRP.date_creation.between(start_date, end_date)
            ).all()
            
            # Préparation du contenu
            subject = f"Rapport hebdomadaire SAV - Semaine du {start_date.strftime('%d/%m/%Y')}"
            
            body = f"""
            Rapport hebdomadaire SAV du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}:
            
            Total FRP: {len(frps_week)}
            
            Distribution par statut:
            """
            
            status_count = {}
            for frp in frps_week:
                status_count[frp.statut] = status_count.get(frp.statut, 0) + 1
            
            for status, count in status_count.items():
                body += f"{status}: {count}\n"
            
            body += """
            Distribution par type:
            """
            
            type_count = {}
            for frp in frps_week:
                type_count[frp.type_motif] = type_count.get(frp.type_motif, 0) + 1
            
            for type_motif, count in type_count.items():
                body += f"{type_motif}: {count}\n"
            
            body += """
            Vous pouvez consulter les détails dans l'application SAV.
            """
            
            # Envoi aux destinataires configurés
            for recipient in self.notification_config['weekly_report_recipients']:
                success, message = self.send_email(recipient, subject, body)
                if not success:
                    return False, message
            
            return True, "Rapport hebdomadaire envoyé avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'envoi du rapport hebdomadaire: {str(e)}" 