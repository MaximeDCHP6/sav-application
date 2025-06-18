import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from config.settings import STATS_CONFIG

class StatisticsManager:
    """Gestionnaire de statistiques"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    def get_frp_stats(self, start_date=None, end_date=None):
        """Obtention des statistiques des FRP"""
        try:
            # Définition de la période
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Récupération des FRP
            frps = self.db_session.query(FRP).filter(
                FRP.date_creation.between(start_date, end_date)
            ).all()
            
            stats = {
                'total': len(frps),
                'par_statut': self._count_by_status(frps),
                'par_type': self._count_by_type(frps),
                'par_client': self._count_by_client(frps),
                'delais_moyens': self._calculate_average_delays(frps),
                'evolution_temporelle': self._calculate_temporal_evolution(frps),
                'produits_retournes': self._analyze_returned_products(frps)
            }
            
            return True, stats
        
        except Exception as e:
            return False, f"Erreur lors du calcul des statistiques: {str(e)}"
    
    def _count_by_status(self, frps):
        """Comptage des FRP par statut"""
        status_count = defaultdict(int)
        for frp in frps:
            status_count[frp.statut] += 1
        return dict(status_count)
    
    def _count_by_type(self, frps):
        """Comptage des FRP par type de motif"""
        type_count = defaultdict(int)
        for frp in frps:
            type_count[frp.type_motif] += 1
        return dict(type_count)
    
    def _count_by_client(self, frps):
        """Comptage des FRP par client"""
        client_count = defaultdict(int)
        for frp in frps:
            client_count[frp.client.nom] += 1
        return dict(client_count)
    
    def _calculate_average_delays(self, frps):
        """Calcul des délais moyens"""
        delays = {
            'creation_traitement': [],
            'traitement_resolution': [],
            'total': []
        }
        
        for frp in frps:
            if frp.date_traitement:
                delays['creation_traitement'].append(
                    (frp.date_traitement - frp.date_creation).days
                )
            
            if frp.date_resolution:
                delays['total'].append(
                    (frp.date_resolution - frp.date_creation).days
                )
                
                if frp.date_traitement:
                    delays['traitement_resolution'].append(
                        (frp.date_resolution - frp.date_traitement).days
                    )
        
        return {
            'creation_traitement': np.mean(delays['creation_traitement']) if delays['creation_traitement'] else 0,
            'traitement_resolution': np.mean(delays['traitement_resolution']) if delays['traitement_resolution'] else 0,
            'total': np.mean(delays['total']) if delays['total'] else 0
        }
    
    def _calculate_temporal_evolution(self, frps):
        """Calcul de l'évolution temporelle"""
        evolution = defaultdict(lambda: defaultdict(int))
        
        for frp in frps:
            date = frp.date_creation.strftime("%Y-%m-%d")
            evolution[date]['total'] += 1
            evolution[date][frp.statut] += 1
        
        return dict(evolution)
    
    def _analyze_returned_products(self, frps):
        """Analyse des produits retournés"""
        products_analysis = {
            'total': 0,
            'par_reference': defaultdict(int),
            'prix_moyen': 0,
            'quantite_totale': 0
        }
        
        total_price = 0
        for frp in frps:
            for produit in frp.produits:
                products_analysis['total'] += 1
                products_analysis['par_reference'][produit.reference] += produit.quantite
                total_price += produit.prix * produit.quantite
                products_analysis['quantite_totale'] += produit.quantite
        
        if products_analysis['total'] > 0:
            products_analysis['prix_moyen'] = total_price / products_analysis['total']
        
        products_analysis['par_reference'] = dict(products_analysis['par_reference'])
        return products_analysis
    
    def generate_report(self, stats, format="pdf"):
        """Génération d'un rapport de statistiques"""
        try:
            if format == "pdf":
                return self._generate_pdf_report(stats)
            elif format == "excel":
                return self._generate_excel_report(stats)
            else:
                return False, f"Format de rapport non supporté: {format}"
        
        except Exception as e:
            return False, f"Erreur lors de la génération du rapport: {str(e)}"
    
    def _generate_pdf_report(self, stats):
        """Génération d'un rapport PDF"""
        try:
            # Création du fichier PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"reports/stats_report_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Styles
            styles = getSampleStyleSheet()
            elements = []
            
            # Titre
            elements.append(Paragraph("Rapport de Statistiques SAV", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Résumé général
            elements.append(Paragraph("Résumé Général", styles['Heading1']))
            elements.append(Spacer(1, 12))
            
            summary_data = [
                ['Métrique', 'Valeur'],
                ['Total FRP', str(stats['total'])],
                ['Délai moyen création-traitement', f"{stats['delais_moyens']['creation_traitement']:.1f} jours"],
                ['Délai moyen traitement-résolution', f"{stats['delais_moyens']['traitement_resolution']:.1f} jours"],
                ['Délai moyen total', f"{stats['delais_moyens']['total']:.1f} jours"]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 20))
            
            # Distribution par statut
            elements.append(Paragraph("Distribution par Statut", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            status_data = [['Statut', 'Nombre']]
            for status, count in stats['par_statut'].items():
                status_data.append([status, str(count)])
            
            status_table = Table(status_data)
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(status_table)
            elements.append(Spacer(1, 20))
            
            # Distribution par type
            elements.append(Paragraph("Distribution par Type", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            type_data = [['Type', 'Nombre']]
            for type_motif, count in stats['par_type'].items():
                type_data.append([type_motif, str(count)])
            
            type_table = Table(type_data)
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(type_table)
            
            # Génération du PDF
            doc.build(elements)
            
            return True, f"Rapport généré avec succès: {filepath}"
        
        except Exception as e:
            return False, f"Erreur lors de la génération du rapport PDF: {str(e)}"
    
    def _generate_excel_report(self, stats):
        """Génération d'un rapport Excel"""
        try:
            # Création du fichier Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"reports/stats_report_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Résumé général
                summary_data = {
                    'Métrique': [
                        'Total FRP',
                        'Délai moyen création-traitement',
                        'Délai moyen traitement-résolution',
                        'Délai moyen total'
                    ],
                    'Valeur': [
                        stats['total'],
                        f"{stats['delais_moyens']['creation_traitement']:.1f} jours",
                        f"{stats['delais_moyens']['traitement_resolution']:.1f} jours",
                        f"{stats['delais_moyens']['total']:.1f} jours"
                    ]
                }
                pd.DataFrame(summary_data).to_excel(
                    writer,
                    sheet_name='Résumé',
                    index=False
                )
                
                # Distribution par statut
                status_data = {
                    'Statut': list(stats['par_statut'].keys()),
                    'Nombre': list(stats['par_statut'].values())
                }
                pd.DataFrame(status_data).to_excel(
                    writer,
                    sheet_name='Par Statut',
                    index=False
                )
                
                # Distribution par type
                type_data = {
                    'Type': list(stats['par_type'].keys()),
                    'Nombre': list(stats['par_type'].values())
                }
                pd.DataFrame(type_data).to_excel(
                    writer,
                    sheet_name='Par Type',
                    index=False
                )
                
                # Évolution temporelle
                evolution_data = []
                for date, values in stats['evolution_temporelle'].items():
                    row = {'Date': date}
                    row.update(values)
                    evolution_data.append(row)
                pd.DataFrame(evolution_data).to_excel(
                    writer,
                    sheet_name='Évolution',
                    index=False
                )
            
            return True, f"Rapport généré avec succès: {filepath}"
        
        except Exception as e:
            return False, f"Erreur lors de la génération du rapport Excel: {str(e)}" 