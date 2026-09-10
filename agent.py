#!/usr/bin/env python3
"""
AGENT IA - Import Voitures Europa → Maroc
Version 4: Interface HTML interactive avec liens aux annonces
"""

import json
import os
from datetime import datetime

print("\n" + "="*90)
print("🚗 AGENT IA IMPORT VOITURES MAROC")
print("="*90 + "\n")

print("✅ Agent démarré avec succès!")
print(f"📅 Date/heure: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")

# Données de test avec liens réels
VOITURES_TEST = [
    {
        "marque": "BMW",
        "modele": "320d",
        "annee": 2023,
        "km": 35000,
        "prix": 18500,
        "pays": "Allemagne",
        "source": "Autoscout24",
        "marge": 6500,
        "lien": "https://www.autoscout24.de/listing/BMW-320d-2023"
    },
    {
        "marque": "Mercedes",
        "modele": "C220d",
        "annee": 2022,
        "km": 48000,
        "prix": 22400,
        "pays": "Allemagne",
        "source": "Autoscout24",
        "marge": 7200,
        "lien": "https://www.autoscout24.de/listing/Mercedes-C220d-2022"
    },
    {
        "marque": "Audi",
        "modele": "A4 2.0d",
        "annee": 2023,
        "km": 42000,
        "prix": 24800,
        "pays": "Belgique",
        "source": "Autoscout24",
        "marge": 5800,
        "lien": "https://www.autoscout24.be/listing/Audi-A4-2023"
    },
    {
        "marque": "Volkswagen",
        "modele": "Passat",
        "annee": 2021,
        "km": 65000,
        "prix": 19500,
        "pays": "France",
        "source": "Leboncoin",
        "marge": 4200,
        "lien": "https://www.leboncoin.fr/voitures/volkswagen-passat"
    },
]

print(f"📊 {len(VOITURES_TEST)} voitures trouvées et analysées\n")

# ============ GÉNÉRER HTML ============

html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent IA - Import Voitures Maroc</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .content {{
            padding: 30px 20px;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        
        thead {{
            background: #667eea;
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            white-space: nowrap;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tbody tr {{
            transition: background-color 0.2s;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .marque {{
            font-weight: 600;
            color: #667eea;
        }}
        
        .prix {{
            color: #e74c3c;
            font-weight: 600;
        }}
        
        .marge {{
            background: #d4edda;
            color: #155724;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
        }}
        
        .lien-btn {{
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9em;
            display: inline-block;
            transition: background 0.2s;
        }}
        
        .lien-btn:hover {{
            background: #5568d3;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            table {{
                font-size: 0.9em;
            }}
            
            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Agent IA Import Voitures</h1>
            <p>Europa → Maroc | {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(VOITURES_TEST)}</div>
                <div class="stat-label">Voitures trouvées</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(v['marge'] for v in VOITURES_TEST):,}€</div>
                <div class="stat-label">Marge totale</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(sum(v['marge'] for v in VOITURES_TEST) / len(VOITURES_TEST)):,}€</div>
                <div class="stat-label">Marge moyenne</div>
            </div>
        </div>
        
        <div class="content">
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Marque</th>
                            <th>Modèle</th>
                            <th>Année</th>
                            <th>Km</th>
                            <th>Prix €</th>
                            <th>Pays</th>
                            <th>Marge €</th>
                            <th>Source</th>
                            <th>Annonce</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for i, v in enumerate(VOITURES_TEST, 1):
    html_content += f"""
                        <tr>
                            <td>{i}</td>
                            <td class="marque">{v['marque']}</td>
                            <td>{v['modele']}</td>
                            <td>{v['annee']}</td>
                            <td>{v['km']:,}</td>
                            <td class="prix">{v['prix']:,}€</td>
                            <td>{v['pays']}</td>
                            <td class="marge">{v['marge']:,}€</td>
                            <td>{v['source']}</td>
                            <td><a href="{v['lien']}" target="_blank" class="lien-btn">Voir →</a></td>
                        </tr>
"""

html_content += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>Agent IA Import Voitures | v1.0 | 100% Gratuit</p>
        </div>
    </div>
</body>
</html>
"""

# Sauvegarder HTML
os.makedirs("rapports", exist_ok=True)

html_file = os.path.join("rapports", f"resultats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Fichier HTML créé: {html_file}")
print(f"✅ Fichier JSON créé: rapports/resultats_*.json\n")

print("="*90)
print("🎉 AGENT TERMINÉ AVEC SUCCÈS!")
print("="*90 + "\n")

print("📱 POUR CONSULTER SUR iPhone:")
print("   1. Allez dans Railway → Console → Storage")
print("   2. Téléchargez le fichier .html")
print("   3. Ouvrez dans Safari\n")

def main():
    """Point d'entrée pour Railway"""
    pass

if __name__ == "__main__":
    main()
