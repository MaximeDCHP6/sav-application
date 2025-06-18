import schedule
import time
import threading
from datetime import datetime, time as dtime
from config.settings import SCHEDULER_CONFIG

class SchedulerManager:
    """Gestionnaire de tâches planifiées"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.scheduler_config = SCHEDULER_CONFIG
        self.running = False
        self.thread = None
    
    def start(self):
        """Démarrage du planificateur"""
        if self.running:
            return False, "Le planificateur est déjà en cours d'exécution"
        
        try:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()
            
            return True, "Planificateur démarré avec succès"
        
        except Exception as e:
            self.running = False
            return False, f"Erreur lors du démarrage du planificateur: {str(e)}"
    
    def stop(self):
        """Arrêt du planificateur"""
        if not self.running:
            return False, "Le planificateur n'est pas en cours d'exécution"
        
        try:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            
            return True, "Planificateur arrêté avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'arrêt du planificateur: {str(e)}"
    
    def _run_scheduler(self):
        """Exécution du planificateur"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def schedule_daily_tasks(self, notification_manager):
        """Planification des tâches quotidiennes"""
        try:
            # Nettoyage des sauvegardes
            schedule.every().day.at(self.scheduler_config['backup_cleanup_time']).do(
                self._cleanup_old_backups
            )
            
            # Vérification des FRP en retard
            schedule.every().day.at(self.scheduler_config['delay_check_time']).do(
                notification_manager.notify_delayed_frps
            )
            
            # Envoi du résumé quotidien
            schedule.every().day.at(self.scheduler_config['daily_summary_time']).do(
                notification_manager.notify_daily_summary
            )
            
            return True, "Tâches quotidiennes planifiées avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de la planification des tâches quotidiennes: {str(e)}"
    
    def schedule_weekly_tasks(self, notification_manager):
        """Planification des tâches hebdomadaires"""
        try:
            # Envoi du rapport hebdomadaire
            schedule.every().monday.at(self.scheduler_config['weekly_report_time']).do(
                notification_manager.notify_weekly_report
            )
            
            return True, "Tâches hebdomadaires planifiées avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de la planification des tâches hebdomadaires: {str(e)}"
    
    def schedule_monthly_tasks(self):
        """Planification des tâches mensuelles"""
        try:
            # Archivage des anciens FRP
            schedule.every().month.at(self.scheduler_config['archive_time']).do(
                self._archive_old_frps
            )
            
            return True, "Tâches mensuelles planifiées avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de la planification des tâches mensuelles: {str(e)}"
    
    def _cleanup_old_backups(self):
        """Nettoyage des anciennes sauvegardes"""
        try:
            # Récupération de la configuration
            retention_days = self.scheduler_config['backup_retention_days']
            backup_dir = self.scheduler_config['backup_dir']
            
            # Calcul de la date limite
            limit_date = datetime.now() - timedelta(days=retention_days)
            
            # Suppression des anciennes sauvegardes
            for backup_file in backup_dir.glob("*.db"):
                if datetime.fromtimestamp(backup_file.stat().st_mtime) < limit_date:
                    backup_file.unlink()
            
            return True, "Nettoyage des sauvegardes effectué avec succès"
        
        except Exception as e:
            return False, f"Erreur lors du nettoyage des sauvegardes: {str(e)}"
    
    def _archive_old_frps(self):
        """Archivage des anciens FRP"""
        try:
            # Récupération de la configuration
            archive_months = self.scheduler_config['archive_months']
            archive_dir = self.scheduler_config['archive_dir']
            
            # Calcul de la date limite
            limit_date = datetime.now() - timedelta(days=30 * archive_months)
            
            # Archivage des FRP
            old_frps = self.db_session.query(FRP).filter(
                FRP.date_creation < limit_date,
                FRP.statut == 'Résolu'
            ).all()
            
            for frp in old_frps:
                # Création du dossier d'archive
                frp_archive_dir = archive_dir / frp.numero
                frp_archive_dir.mkdir(parents=True, exist_ok=True)
                
                # Export des données
                self._export_frp_for_archive(frp, frp_archive_dir)
                
                # Suppression du FRP de la base de données
                self.db_session.delete(frp)
            
            self.db_session.commit()
            
            return True, "Archivage des FRP effectué avec succès"
        
        except Exception as e:
            self.db_session.rollback()
            return False, f"Erreur lors de l'archivage des FRP: {str(e)}"
    
    def _export_frp_for_archive(self, frp, archive_dir):
        """Export d'un FRP pour l'archivage"""
        try:
            # Export des données en JSON
            frp_data = {
                'numero': frp.numero,
                'date_creation': frp.date_creation.isoformat(),
                'client': frp.client.nom,
                'statut': frp.statut,
                'type_motif': frp.type_motif,
                'produits': [
                    {
                        'reference': p.reference,
                        'quantite': p.quantite,
                        'numero_bl': p.numero_bl,
                        'numero_lot': p.numero_lot,
                        'date_achat': p.date_achat.isoformat(),
                        'prix': p.prix
                    }
                    for p in frp.produits
                ],
                'documents': [
                    {
                        'type': d.type,
                        'date_creation': d.date_creation.isoformat(),
                        'chemin_fichier': d.chemin_fichier
                    }
                    for d in frp.documents
                ]
            }
            
            # Sauvegarde des données
            with open(archive_dir / 'frp_data.json', 'w') as f:
                json.dump(frp_data, f, indent=4)
            
            # Copie des documents
            for document in frp.documents:
                src_path = Path(document.chemin_fichier)
                if src_path.exists():
                    dst_path = archive_dir / src_path.name
                    shutil.copy2(src_path, dst_path)
            
            return True, "Export du FRP effectué avec succès"
        
        except Exception as e:
            return False, f"Erreur lors de l'export du FRP: {str(e)}" 