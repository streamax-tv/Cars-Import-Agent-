#!/usr/bin/env python3
"""
Exportateur de rapports en multiples formats
CSV, Excel, PDF, JSON
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RapportExporter:
    """Exporte les analyses en différents formats"""
    
    def __init__(self, output_dir="rapports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def exporter_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """Exporte en CSV"""
        try:
            path = self.output_dir / filename
            
            # Sélectionner colonnes principales
            colonnes = [
                'score', 'verdict', 'marque', 'modele', 'annee', 'km', 'carburant',
                'prix_achat_eur', 'prix_revient_eur', 'prix_maroc_mad',
                'marge_brute_eur', 'marge_brute_pct', 'marge_nette_eur',
                'transport_eur', 'douane_taxes_eur', 'source', 'pays_origine', 'url'
            ]
            
            colonnes = [c for c in colonnes if c in df.columns]
            df_export = df[colonnes]
            
            # Renommer pour clarté
            df_export = df_export.rename(columns={
                'score': 'Score',
                'verdict': 'Verdict',
                'marque': 'Marque',
                'modele': 'Modèle',
                'annee': 'Année',
                'km': 'Km',
                'carburant': 'Carburant',
                'prix_achat_eur': 'Prix Achat €',
                'prix_revient_eur': 'Prix Revient €',
                'prix_maroc_mad': 'Prix Maroc (MAD)',
                'marge_brute_eur': 'Marge Brute €',
                'marge_brute_pct': 'Marge %',
                'marge_nette_eur': 'Marge Nette €',
                'transport_eur': 'Transport €',
                'douane_taxes_eur': 'Douane/Taxes €',
                'source': 'Source',
                'pays_origine': 'Pays',
                'url': 'URL'
            })
            
            # Tri par score décroissant
            if 'Score' in df_export.columns:
                df_export = df_export.sort_values('Score', ascending=False)
            
            df_export.to_csv(path, index=False, encoding='utf-8-sig')
            logger.info(f"✅ CSV exporté: {path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Export CSV échoué: {e}")
            return False
    
    def exporter_excel(self, df: pd.DataFrame, filename: str) -> bool:
        """Exporte en Excel avec formatage"""
        try:
            path = self.output_dir / filename
            
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                
                # Feuille 1: Synthèse
                df_synthese = df[[
                    'score', 'verdict', 'marque', 'modele', 'annee', 'km',
                    'prix_achat_eur', 'prix_revient_eur', 'prix_maroc_mad',
                    'marge_nette_eur', 'marge_brute_pct', 'source'
                ]].copy()
                
                df_synthese = df_synthese.sort_values('score', ascending=False)
                df_synthese.to_excel(writer, sheet_name='Synthèse', index=False)
                
                # Feuille 2: Détails coûts
                df_couts = df[[
                    'marque', 'modele', 'prix_achat_eur', 'transport_eur',
                    'douane_taxes_eur', 'frais_admin_eur', 'prix_revient_eur'
                ]].copy()
                df_couts.to_excel(writer, sheet_name='Coûts', index=False)
                
                # Feuille 3: Rentabilité
                df_rent = df[[
                    'marque', 'modele', 'prix_maroc_mad', 'prix_revient_eur',
                    'marge_brute_eur', 'marge_brute_pct', 'marge_nette_eur'
                ]].copy()
                df_rent.to_excel(writer, sheet_name='Rentabilité', index=False)
                
                # Formatage
                workbook = writer.book
                
                for worksheet in workbook.sheetnames:
                    ws = writer.sheets[worksheet]
                    for column in ws.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(cell.value)
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        ws.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"✅ Excel exporté: {path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Export Excel échoué: {e}")
            return False
    
    def exporter_json(self, donnees: list, filename: str) -> bool:
        """Exporte en JSON"""
        try:
            path = self.output_dir / filename
            
            # Convertir datetime en string
            donnees_serializable = []
            for item in donnees:
                item_copy = item.copy()
                if 'date_analyse' in item_copy and hasattr(item_copy['date_analyse'], 'isoformat'):
                    item_copy['date_analyse'] = item_copy['date_analyse'].isoformat()
                donnees_serializable.append(item_copy)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(donnees_serializable, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ JSON exporté: {path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Export JSON échoué: {e}")
            return False
    
    def exporter_txt(self, texte: str, filename: str) -> bool:
        """Exporte rapport texte"""
        try:
            path = self.output_dir / filename
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(texte)
            
            logger.info(f"✅ TXT exporté: {path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Export TXT échoué: {e}")
            return False
    
    def exporter_pdf(self, donnees: list, filename: str) -> bool:
        """Exporte en PDF (optionnel - nécessite reportlab)"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib import colors
            
            path = self.output_dir / filename
            
            doc = SimpleDocTemplate(str(path), pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30
            )
            
            elements.append(Paragraph(
                "📊 Rapport d'Opportunités - Import Voitures Maroc",
                title_style
            ))
            elements.append(Paragraph(
                f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                styles['Normal']
            ))
            elements.append(Spacer(1, 0.3*inch))
            
            # Table données
            data = [['Rang', 'Marque', 'Modèle', 'Prix Achat €', 'Marge Net €', 'Score', 'Verdict']]
            
            for i, v in enumerate(donnees[:30], 1):
                data.append([
                    str(i),
                    v.get('marque', ''),
                    v.get('modele', ''),
                    f"{v.get('prix_achat_eur', 0):.0f}",
                    f"{v.get('marge_nette_eur', 0):.0f}",
                    str(v.get('score', 0)),
                    v.get('verdict', '')
                ])
            
            table = Table(data, colWidths=[0.6*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.8*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            logger.info(f"✅ PDF exporté: {path}")
            return True
        
        except ImportError:
            logger.warning("⚠️  reportlab non installé (optional)")
            return False
        except Exception as e:
            logger.error(f"❌ Export PDF échoué: {e}")
            return False
    
    def generer_synthese_html(self, donnees: list, filename="index.html") -> bool:
        """Génère une page HTML interactive"""
        try:
            path = self.output_dir / filename
            
            html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Opportunités Import Voitures Maroc</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        h1 {
            color: #1f4788;
            margin-bottom: 10px;
            text-align: center;
        }
        .meta {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-box h3 {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .stat-box .value {
            font-size: 2em;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: #1f4788;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .score {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 40px;
            text-align: center;
        }
        .verdict {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        }
        .excellent { background: #4caf50; color: white; }
        .bon { background: #8bc34a; color: white; }
        .moyen { background: #ff9800; color: white; }
        .faible { background: #f44336; color: white; }
        .marge {
            color: #4caf50;
            font-weight: bold;
        }
        a {
            color: #667eea;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 Opportunités Import Voitures Maroc</h1>
        <div class="meta">Rapport généré le """ + datetime.now().strftime('%d/%m/%Y à %H:%M') + """</div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Opportunities</h3>
                <div class="value">""" + str(len(donnees)) + """</div>
            </div>
            <div class="stat-box">
                <h3>Marge Moyenne</h3>
                <div class="value">""" + f"{sum(d.get('marge_nette_eur', 0) for d in donnees) / max(len(donnees), 1):.0f}" + """€</div>
            </div>
            <div class="stat-box">
                <h3>Score Moyen</h3>
                <div class="value">""" + f"{sum(d.get('score', 0) for d in donnees) / max(len(donnees), 1):.0f}" + """/100</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Score</th>
                    <th>Marque</th>
                    <th>Modèle</th>
                    <th>Année</th>
                    <th>Prix Achat</th>
                    <th>Marge Nette</th>
                    <th>Verdict</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for d in donnees[:50]:
                verdict_class = d['verdict'].lower().replace(' ', '')
                html += f"""
                <tr>
                    <td><span class="score">{d['score']}/100</span></td>
                    <td><strong>{d['marque']}</strong></td>
                    <td>{d['modele']}</td>
                    <td>{d['annee']}</td>
                    <td>{d['prix_achat_eur']:.0f}€</td>
                    <td><span class="marge">{d['marge_nette_eur']:.0f}€</span></td>
                    <td><span class="verdict {verdict_class}">{d['verdict']}</span></td>
                    <td><a href="{d['url']}" target="_blank">{d['source']}</a></td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
        
        <div class="footer">
            📊 Agent IA - Import Voitures Maroc | Données à jour
        </div>
    </div>
</body>
</html>
"""
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"✅ HTML exporté: {path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Export HTML échoué: {e}")
            return False

if __name__ == "__main__":
    exporter = RapportExporter()
    print("✅ Exportateur prêt")
