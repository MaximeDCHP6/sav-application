import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from config.settings import EXPORT_CONFIG, REPORT_CONFIG
import csv
import json
import xlsxwriter
import pdfkit
from jinja2 import Environment, FileSystemLoader

class ExportManager:
    """Gestionnaire d'exports"""
    
    def __init__(self):
        self.export_dir = Path("exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_frp(self, frp, format="xlsx"):
        """Export d'un FRP"""
        try:
            # Génération du nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"FRP_{frp.numero}_{timestamp}"
            
            if format == "xlsx":
                return self._export_frp_excel(frp, filename)
            elif format == "pdf":
                return self._export_frp_pdf(frp, filename)
            else:
                return False, f"Format d'export non supporté: {format}"
        
        except Exception as e:
            return False, f"Erreur lors de l'export du FRP: {str(e)}"
    
    def export_frp_list(self, frps, format="xlsx"):
        """Export d'une liste de FRP"""
        try:
            # Génération du nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Liste_FRP_{timestamp}"
            
            if format == "xlsx":
                return self._export_frp_list_excel(frps, filename)
            elif format == "pdf":
                return self._export_frp_list_pdf(frps, filename)
            else:
                return False, f"Format d'export non supporté: {format}"
        
        except Exception as e:
            return False, f"Erreur lors de l'export de la liste des FRP: {str(e)}"
    
    def _export_frp_excel(self, frp, filename):
        """Export d'un FRP en Excel"""
        try:
            # Création du fichier Excel
            filepath = self.export_dir / f"{filename}.xlsx"
            
            # Création du writer Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Informations générales
                general_data = {
                    'Champ': [
                        'Numéro FRP',
                        'Date création',
                        'Client',
                        'Statut',
                        'Type motif'
                    ],
                    'Valeur': [
                        frp.numero,
                        frp.date_creation.strftime("%d/%m/%Y"),
                        frp.client.nom,
                        frp.statut,
                        frp.type_motif
                    ]
                }
                pd.DataFrame(general_data).to_excel(
                    writer,
                    sheet_name='Informations',
                    index=False
                )
                
                # Produits
                products_data = []
                for produit in frp.produits:
                    products_data.append({
                        'Référence': produit.reference,
                        'Quantité': produit.quantite,
                        'N° BL': produit.numero_bl,
                        'N° Lot': produit.numero_lot,
                        'Date achat': produit.date_achat.strftime("%d/%m/%Y"),
                        'Prix': produit.prix
                    })
                pd.DataFrame(products_data).to_excel(
                    writer,
                    sheet_name='Produits',
                    index=False
                )
                
                # Documents
                documents_data = []
                for document in frp.documents:
                    documents_data.append({
                        'Type': document.type,
                        'Date': document.date_creation.strftime("%d/%m/%Y"),
                        'Chemin': document.chemin_fichier
                    })
                pd.DataFrame(documents_data).to_excel(
                    writer,
                    sheet_name='Documents',
                    index=False
                )
            
            return True, f"FRP exporté avec succès: {filepath}"
        
        except Exception as e:
            return False, f"Erreur lors de l'export Excel: {str(e)}"
    
    def _export_frp_pdf(self, frp, filename):
        """Export d'un FRP en PDF"""
        try:
            # Création du fichier PDF
            filepath = self.export_dir / f"{filename}.pdf"
            doc = SimpleDocTemplate(
                str(filepath),
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
            elements.append(Paragraph(f"FRP {frp.numero}", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Informations générales
            general_data = [
                ['Champ', 'Valeur'],
                ['Numéro FRP', frp.numero],
                ['Date création', frp.date_creation.strftime("%d/%m/%Y")],
                ['Client', frp.client.nom],
                ['Statut', frp.statut],
                ['Type motif', frp.type_motif]
            ]
            
            general_table = Table(general_data)
            general_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(general_table)
            elements.append(Spacer(1, 20))
            
            # Produits
            elements.append(Paragraph("Produits", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            products_data = [['Référence', 'Quantité', 'N° BL', 'N° Lot', 'Date achat', 'Prix']]
            for produit in frp.produits:
                products_data.append([
                    produit.reference,
                    str(produit.quantite),
                    produit.numero_bl,
                    produit.numero_lot,
                    produit.date_achat.strftime("%d/%m/%Y"),
                    f"{produit.prix:.2f}"
                ])
            
            products_table = Table(products_data)
            products_table.setStyle(TableStyle([
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
            
            elements.append(products_table)
            elements.append(Spacer(1, 20))
            
            # Documents
            elements.append(Paragraph("Documents", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            documents_data = [['Type', 'Date', 'Chemin']]
            for document in frp.documents:
                documents_data.append([
                    document.type,
                    document.date_creation.strftime("%d/%m/%Y"),
                    document.chemin_fichier
                ])
            
            documents_table = Table(documents_data)
            documents_table.setStyle(TableStyle([
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
            
            elements.append(documents_table)
            
            # Génération du PDF
            doc.build(elements)
            
            return True, f"FRP exporté avec succès: {filepath}"
        
        except Exception as e:
            return False, f"Erreur lors de l'export PDF: {str(e)}"
    
    def _export_frp_list_excel(self, frps, filename):
        """Export d'une liste de FRP en Excel"""
        try:
            # Création du fichier Excel
            filepath = self.export_dir / f"{filename}.xlsx"
            
            # Préparation des données
            data = []
            for frp in frps:
                data.append({
                    'Numéro': frp.numero,
                    'Date': frp.date_creation.strftime("%d/%m/%Y"),
                    'Client': frp.client.nom,
                    'Statut': frp.statut,
                    'Type': frp.type_motif,
                    'Produits': len(frp.produits),
                    'Documents': len(frp.documents)
                })
            
            # Création du DataFrame et export
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False)
            
            return True, f"Liste des FRP exportée avec succès: {filepath}"
        
        except Exception as e:
            return False, f"Erreur lors de l'export Excel: {str(e)}"
    
    def _export_frp_list_pdf(self, frps, filename):
        """Export d'une liste de FRP en PDF"""
        try:
            # Création du fichier PDF
            filepath = self.export_dir / f"{filename}.pdf"
            doc = SimpleDocTemplate(
                str(filepath),
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
            elements.append(Paragraph("Liste des FRP", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Données
            data = [['Numéro', 'Date', 'Client', 'Statut', 'Type', 'Produits', 'Documents']]
            for frp in frps:
                data.append([
                    frp.numero,
                    frp.date_creation.strftime("%d/%m/%Y"),
                    frp.client.nom,
                    frp.statut,
                    frp.type_motif,
                    str(len(frp.produits)),
                    str(len(frp.documents))
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
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
            
            elements.append(table)
            
            # Génération du PDF
            doc.build(elements)
            
            return True, f"Liste des FRP exportée avec succès: {filepath}"
        
        except Exception as e:
            return False, f"Erreur lors de l'export PDF: {str(e)}"

class DataExporter:
    """Classe utilitaire pour l'export des données"""
    
    @staticmethod
    def export_to_csv(
        data: List[Dict[str, Any]],
        headers: List[str],
        filename: str
    ) -> str:
        """
        Exporte des données au format CSV.
        
        Args:
            data: Liste des données à exporter
            headers: En-têtes des colonnes
            filename: Nom du fichier
            
        Returns:
            Chemin du fichier créé
        """
        filepath = Path(filename)
        if not filepath.suffix:
            filepath = filepath.with_suffix('.csv')
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        
        return str(filepath)
    
    @staticmethod
    def export_to_json(
        data: List[Dict[str, Any]],
        filename: str
    ) -> str:
        """
        Exporte des données au format JSON.
        
        Args:
            data: Liste des données à exporter
            filename: Nom du fichier
            
        Returns:
            Chemin du fichier créé
        """
        filepath = Path(filename)
        if not filepath.suffix:
            filepath = filepath.with_suffix('.json')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    @staticmethod
    def export_to_excel(
        data: List[Dict[str, Any]],
        headers: List[str],
        filename: str,
        sheet_name: str = 'Sheet1'
    ) -> str:
        """
        Exporte des données au format Excel.
        
        Args:
            data: Liste des données à exporter
            headers: En-têtes des colonnes
            filename: Nom du fichier
            sheet_name: Nom de la feuille
            
        Returns:
            Chemin du fichier créé
        """
        filepath = Path(filename)
        if not filepath.suffix:
            filepath = filepath.with_suffix('.xlsx')
        
        workbook = xlsxwriter.Workbook(str(filepath))
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#CCCCCC',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'border': 1
        })
        
        # Écrire les en-têtes
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Écrire les données
        for row, item in enumerate(data, start=1):
            for col, header in enumerate(headers):
                worksheet.write(row, col, item.get(header, ''), cell_format)
        
        # Ajuster la largeur des colonnes
        for col, header in enumerate(headers):
            worksheet.set_column(col, col, len(header) + 2)
        
        workbook.close()
        return str(filepath)
    
    @staticmethod
    def export_to_pdf(
        data: List[Dict[str, Any]],
        template_path: str,
        filename: str,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Exporte des données au format PDF en utilisant un template HTML.
        
        Args:
            data: Liste des données à exporter
            template_path: Chemin du template HTML
            filename: Nom du fichier
            template_vars: Variables supplémentaires pour le template
            
        Returns:
            Chemin du fichier créé
        """
        filepath = Path(filename)
        if not filepath.suffix:
            filepath = filepath.with_suffix('.pdf')
        
        # Charger le template
        env = Environment(loader=FileSystemLoader(str(Path(template_path).parent)))
        template = env.get_template(Path(template_path).name)
        
        # Préparer les variables
        template_data = {
            'data': data,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
            **(template_vars or {})
        }
        
        # Rendre le template
        html_content = template.render(**template_data)
        
        # Convertir en PDF
        pdfkit.from_string(html_content, str(filepath))
        
        return str(filepath)

class ReportGenerator:
    """Classe utilitaire pour la génération de rapports"""
    
    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_repair_report(
        self,
        repairs: List[Dict[str, Any]],
        filename: str,
        format: str = 'pdf'
    ) -> str:
        """
        Génère un rapport de réparations.
        
        Args:
            repairs: Liste des réparations
            filename: Nom du fichier
            format: Format du rapport ('pdf', 'excel', 'csv', 'json')
            
        Returns:
            Chemin du fichier créé
        """
        # Préparer les données
        headers = [
            'ID', 'Client', 'Appareil', 'Type', 'Statut',
            'Date création', 'Date fin', 'Coût'
        ]
        
        data = []
        for repair in repairs:
            data.append({
                'ID': repair['id'],
                'Client': repair['client_name'],
                'Appareil': f"{repair['device_brand']} {repair['device_model']}",
                'Type': repair['type'],
                'Statut': repair['status'],
                'Date création': repair['created_at'].strftime('%d/%m/%Y'),
                'Date fin': repair['completion_date'].strftime('%d/%m/%Y') if repair['completion_date'] else '-',
                'Coût': f"{repair['actual_cost']:.2f} €" if repair['actual_cost'] else '-'
            })
        
        # Générer le rapport
        if format == 'pdf':
            return DataExporter.export_to_pdf(
                data,
                str(Path(self.template_dir) / 'repair_report.html'),
                filename,
                {'title': 'Rapport de réparations'}
            )
        elif format == 'excel':
            return DataExporter.export_to_excel(data, headers, filename)
        elif format == 'csv':
            return DataExporter.export_to_csv(data, headers, filename)
        elif format == 'json':
            return DataExporter.export_to_json(data, filename)
        else:
            raise ValueError(f"Format non supporté: {format}")
    
    def generate_client_report(
        self,
        clients: List[Dict[str, Any]],
        filename: str,
        format: str = 'pdf'
    ) -> str:
        """
        Génère un rapport de clients.
        
        Args:
            clients: Liste des clients
            filename: Nom du fichier
            format: Format du rapport ('pdf', 'excel', 'csv', 'json')
            
        Returns:
            Chemin du fichier créé
        """
        # Préparer les données
        headers = [
            'ID', 'Nom', 'Email', 'Téléphone', 'Adresse',
            'Nombre appareils', 'Nombre réparations'
        ]
        
        data = []
        for client in clients:
            data.append({
                'ID': client['id'],
                'Nom': client['name'],
                'Email': client['email'],
                'Téléphone': client['phone'],
                'Adresse': client['address'],
                'Nombre appareils': client['device_count'],
                'Nombre réparations': client['repair_count']
            })
        
        # Générer le rapport
        if format == 'pdf':
            return DataExporter.export_to_pdf(
                data,
                str(Path(self.template_dir) / 'client_report.html'),
                filename,
                {'title': 'Rapport de clients'}
            )
        elif format == 'excel':
            return DataExporter.export_to_excel(data, headers, filename)
        elif format == 'csv':
            return DataExporter.export_to_csv(data, headers, filename)
        elif format == 'json':
            return DataExporter.export_to_json(data, filename)
        else:
            raise ValueError(f"Format non supporté: {format}")
    
    def generate_statistics_report(
        self,
        statistics: Dict[str, Any],
        filename: str,
        format: str = 'pdf'
    ) -> str:
        """
        Génère un rapport de statistiques.
        
        Args:
            statistics: Statistiques à exporter
            filename: Nom du fichier
            format: Format du rapport ('pdf', 'excel', 'csv', 'json')
            
        Returns:
            Chemin du fichier créé
        """
        # Préparer les données
        data = []
        for category, values in statistics.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    data.append({
                        'Catégorie': category,
                        'Métrique': key,
                        'Valeur': value
                    })
            else:
                data.append({
                    'Catégorie': category,
                    'Métrique': 'Valeur',
                    'Valeur': values
                })
        
        headers = ['Catégorie', 'Métrique', 'Valeur']
        
        # Générer le rapport
        if format == 'pdf':
            return DataExporter.export_to_pdf(
                data,
                str(Path(self.template_dir) / 'statistics_report.html'),
                filename,
                {'title': 'Rapport de statistiques'}
            )
        elif format == 'excel':
            return DataExporter.export_to_excel(data, headers, filename)
        elif format == 'csv':
            return DataExporter.export_to_csv(data, headers, filename)
        elif format == 'json':
            return DataExporter.export_to_json(data, filename)
        else:
            raise ValueError(f"Format non supporté: {format}") 