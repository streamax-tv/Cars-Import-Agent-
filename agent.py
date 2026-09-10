#!/usr/bin/env python3
"""
AGENT IA - Import Voitures Europa → Maroc
Version 5: HTML auto-upload sur GitHub + GitHub Pages
"""

import json
import os
from datetime import datetime
import base64
import urllib.request
import urllib.error

print("\n" + "="*90)
print("🚗 AGENT IA IMPORT VOITURES MAROC")
print("="*90 + "\n")

print("✅ Agent démarré avec succès!")
print(f"📅 Date/heure: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")

# Données de test
VOITURES_TEST = [
    {"marque": "BMW", "modele": "320d", "annee": 2023, "km": 35000, "prix": 18500, "pays": "Allemagne", "source": "Autoscout24", "marge": 6500, "lien": "https://www.autoscout24.de/"},
    {"marque": "Mercedes", "modele": "C220d", "annee": 2022, "km": 48000, "prix": 22400, "pays": "Allemagne", "source": "Autoscout24", "marge": 7200, "lien": "https://www.autoscout24.de/"},
    {"marque": "Audi", "modele": "A4 2.0d", "annee": 2023, "km": 42000, "prix": 24800, "pays": "Belgique", "source": "Autoscout24", "marge": 5800, "lien": "https://www.autoscout24.be/"},
    {"marque": "Volkswagen", "modele": "Passat", "annee": 2021, "km": 65000, "prix": 19500, "pays": "France", "source": "Leboncoin", "marge": 4200, "lien": "https://www.leboncoin.fr/"},
]

print(f"📊 {len(VOITURES_TEST)} voitures trouvées\n")

# ============ GÉNÉRER HTML ============
html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent IA - Import Voitures</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; padding: 20px; background: #f8f9fa; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 1.8em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        .content {{ padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .marque {{ font-weight: 600; color: #667eea; }}
        .prix {{ color: #e74c3c; font-weight: 600; }}
        .marge {{ background: #d4edda; color: #155724; padding: 5px 8px; border-radius: 4px; font-weight: 600; }}
        .btn {{ background: #667eea; color: white; padding: 8px 12px; border-radius: 5px; text-decoration: none; font-size: 0.9em; display: inline-block; }}
        .btn:hover {{ background: #5568d3; }}
        .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Agent IA Import Voitures</h1>
            <p>Europa → Maroc | {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(VOITURES_TEST)}</div>
                <div class="stat-label">Voitures</div>
            </div>
            <div class="stat">
                <div class="stat-value">{sum(v['marge'] for v in VOITURES_TEST):,}€</div>
                <div class="stat-label">Marge totale</div>
            </div>
            <div class="stat">
                <div class="stat-value">{int(sum(v['marge'] for v in VOITURES_TEST) / len(VOITURES_TEST)):,}€</div>
                <div class="stat-label">Marge moy.</div>
            </div>
        </div>
        
        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th>#</th><th>Marque</th><th>Modèle</th><th>Année</th><th>Km</th><th>Prix €</th><th>Pays</th><th>Marge €</th><th>Lien</th>
                    </tr>
                </thead>
                <tbody>
"""

for i, v in enumerate(VOITURES_TEST, 1):
    html_content += f"""                    <tr>
                        <td>{i}</td>
                        <td class="marque">{v['marque']}</td>
                        <td>{v['modele']}</td>
                        <td>{v['annee']}</td>
                        <td>{v['km']:,}</td>
                        <td class="prix">{v['prix']:,}€</td>
                        <td>{v['pays']}</td>
                        <td class="marge">{v['marge']:,}€</td>
                        <td><a href="{v['lien']}" target="_blank" class="btn">Voir</a></td>
                    </tr>
"""

html_content += """                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>🚀 Agent IA Import Voitures | Auto-updated</p>
        </div>
    </div>
</body>
</html>"""

# ============ UPLOADER SUR GITHUB ============

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "votreusername/agent-voitures")
FILE_PATH = "index.html"

if GITHUB_TOKEN:
    print("📤 Upload sur GitHub...\n")
    
    try:
        # Encoder le contenu en base64
        content_b64 = base64.b64encode(html_content.encode()).decode()
        
        # URL API GitHub
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
        
        # Préparer la requête
        data = json.dumps({
            "message": f"🤖 Update rapport - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "content": content_b64,
            "branch": "main"
        }).encode()
        
        # Headers avec token
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Content-Type": "application/json",
        }
        
        # Faire la requête PUT
        req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print("✅ Fichier uploadé sur GitHub!")
                print(f"📄 Fichier: {FILE_PATH}")
                print(f"🔗 URL: https://yourname.github.io/agent-voitures/\n")
        except urllib.error.HTTPError as e:
            print(f"❌ Erreur GitHub: {e.read().decode()}\n")
    
    except Exception as e:
        print(f"⚠️  Erreur upload: {str(e)}\n")
else:
    print("⚠️  GITHUB_TOKEN pas configuré")
    print("   Voir les instructions pour configurer le token!\n")

print("="*90)
print("🎉 AGENT TERMINÉ!")
print("="*90 + "\n")

def main():
    pass

if __name__ == "__main__":
    main()
