#!/usr/bin/env python3
"""
AGENT IA - Import Voitures Europa → Maroc
Version 8: Prix Maroc (Avito/Moteur.ma) + liens annonces
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

# Prix référence marché marocain (MAD) - Avito.ma / Moteur.ma
PRIX_MAROC_MAD = {
    ("BMW", "320d"): 350000,
    ("Mercedes", "C220d"): 420000,
    ("Audi", "A4"): 400000,
    ("Volkswagen", "Passat"): 300000,
    ("Seat", "Tarraco"): 380000,
    ("Fiat", "500X"): 320000,
}

VOITURES_TEST = [
    {"marque": "BMW", "modele": "320d", "annee": 2023, "km": 35000, "prix": 18500,
     "pays": "Allemagne", "source": "Mobile.de",
     "lien": "https://www.mobile.de/auto/bmw-320d-2023-35000-km"},
    {"marque": "Mercedes", "modele": "C220d", "annee": 2022, "km": 48000, "prix": 22400,
     "pays": "Allemagne", "source": "Mobile.de",
     "lien": "https://www.mobile.de/auto/mercedes-c220d-2022-48000-km"},
    {"marque": "Audi", "modele": "A4", "annee": 2023, "km": 42000, "prix": 24800,
     "pays": "Belgique", "source": "Marktplaats",
     "lien": "https://www.marktplaats.be/auto/audi-a4-2023"},
    {"marque": "Volkswagen", "modele": "Passat", "annee": 2021, "km": 65000, "prix": 19500,
     "pays": "France", "source": "Leboncoin",
     "lien": "https://www.leboncoin.fr/voitures/volkswagen-passat-2021"},
    {"marque": "Seat", "modele": "Tarraco", "annee": 2022, "km": 52000, "prix": 20800,
     "pays": "Espagne", "source": "Coches.com",
     "lien": "https://www.coches.com/seat-tarraco-2022-diesel"},
    {"marque": "Fiat", "modele": "500X", "annee": 2023, "km": 28000, "prix": 17600,
     "pays": "Italie", "source": "Subito.it",
     "lien": "https://www.subito.it/auto/fiat-500x-2023-diesel"},
]

TAUX_EUR_MAD = 10.5
FRAIS_IMPORT_PCT = 0.35

for v in VOITURES_TEST:
    key = (v["marque"], v["modele"])
    prix_maroc_mad = PRIX_MAROC_MAD.get(key, 350000)
    v["prix_maroc_mad"] = prix_maroc_mad
    v["prix_maroc_eur"] = prix_maroc_mad / TAUX_EUR_MAD
    v["cout_import_eur"] = v["prix"] * (1 + FRAIS_IMPORT_PCT)
    v["marge_eur"] = v["prix_maroc_eur"] - v["cout_import_eur"]
    v["marge_mad"] = v["marge_eur"] * TAUX_EUR_MAD
    # Lien recherche Avito pour comparer
    q = f"{v['marque']}+{v['modele']}".replace(" ", "+")
    v["lien_avito"] = f"https://www.avito.ma/fr/maroc/{q}-à_vendre"

print(f"📊 {len(VOITURES_TEST)} voitures analysées\n")

total_marge_eur = sum(v["marge_eur"] for v in VOITURES_TEST)

html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agent IA - Import Voitures</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',sans-serif; background:#f5f5f5; padding:20px; }}
.container {{ max-width:1400px; margin:0 auto; background:white; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1); }}
.header {{ background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; padding:30px; text-align:center; }}
.header h1 {{ font-size:1.8em; margin-bottom:8px; }}
.update-time {{ opacity:0.85; font-size:0.85em; margin-top:6px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; padding:20px; background:#f8f9fa; }}
.stat {{ background:white; padding:14px; border-radius:8px; text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.08); }}
.stat-value {{ font-size:1.5em; font-weight:bold; color:#667eea; }}
.stat-label {{ color:#666; font-size:0.8em; margin-top:4px; }}
.content {{ padding:20px; overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; min-width:900px; }}
th {{ background:#667eea; color:white; padding:10px; text-align:left; font-weight:600; font-size:0.85em; white-space:nowrap; }}
td {{ padding:10px; border-bottom:1px solid #e0e0e0; font-size:0.9em; white-space:nowrap; }}
tr:hover {{ background:#f8f9fa; }}
.marque {{ font-weight:600; color:#667eea; }}
.prix-eu {{ color:#e74c3c; font-weight:600; }}
.prix-ma {{ color:#2980b9; font-weight:600; }}
.marge-pos {{ background:#d4edda; color:#155724; padding:4px 8px; border-radius:4px; font-weight:600; }}
.marge-neg {{ background:#f8d7da; color:#721c24; padding:4px 8px; border-radius:4px; font-weight:600; }}
.btn {{ background:#667eea; color:white; padding:6px 10px; border-radius:5px; text-decoration:none; font-size:0.8em; display:inline-block; margin:2px; }}
.btn:hover {{ background:#5568d3; }}
.btn-avito {{ background:#e67e22; }}
.btn-avito:hover {{ background:#d35400; }}
.footer {{ background:#f8f9fa; padding:15px; text-align:center; color:#666; border-top:1px solid #e0e0e0; font-size:0.85em; }}
@media (max-width:768px) {{ .header h1 {{ font-size:1.3em; }} }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🚗 Agent IA Import Voitures</h1>
        <p>Europa → Maroc</p>
        <div class="update-time">📅 Mise à jour: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</div>
    </div>

    <div class="stats">
        <div class="stat"><div class="stat-value">{len(VOITURES_TEST)}</div><div class="stat-label">Voitures</div></div>
        <div class="stat"><div class="stat-value">{total_marge_eur:,.0f}€</div><div class="stat-label">Marge totale</div></div>
        <div class="stat"><div class="stat-value">{total_marge_eur/len(VOITURES_TEST):,.0f}€</div><div class="stat-label">Marge moyenne</div></div>
    </div>

    <div class="content">
        <table>
            <thead>
                <tr>
                    <th>#</th><th>Marque</th><th>Modèle</th><th>Année</th><th>Km</th>
                    <th>Prix Europe</th><th>Coût import</th><th>Prix Maroc (réf.)</th>
                    <th>Marge est.</th><th>Pays</th><th>Annonce EU</th><th>Comparer Maroc</th>
                </tr>
            </thead>
            <tbody>
"""

for i, v in enumerate(VOITURES_TEST, 1):
    marge_class = "marge-pos" if v["marge_eur"] >= 0 else "marge-neg"
    html_content += f"""                <tr>
                    <td>{i}</td>
                    <td class="marque">{v['marque']}</td>
                    <td>{v['modele']}</td>
                    <td>{v['annee']}</td>
                    <td>{v['km']:,}</td>
                    <td class="prix-eu">{v['prix']:,}€</td>
                    <td>{v['cout_import_eur']:,.0f}€</td>
                    <td class="prix-ma">{v['prix_maroc_mad']:,.0f} MAD<br><small>({v['prix_maroc_eur']:,.0f}€)</small></td>
                    <td><span class="{marge_class}">{v['marge_eur']:,.0f}€</span></td>
                    <td>{v['pays']}</td>
                    <td><a href="{v['lien']}" target="_blank" class="btn">🔗 Voir</a></td>
                    <td><a href="{v['lien_avito']}" target="_blank" class="btn btn-avito">🇲🇦 Avito</a></td>
                </tr>
"""

html_content += """            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>🚀 Agent IA Import Voitures | Prix Maroc: référence Avito.ma (à titre indicatif)</p>
    </div>
</div>
</body>
</html>"""

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "streamax-tv/Cars-Import-Agent-")
FILE_PATH = "index.html"

if GITHUB_TOKEN:
    print("📤 Upload sur GitHub...\n")
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        try:
            req_get = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req_get) as response:
                sha = json.loads(response.read().decode()).get("sha")
        except urllib.error.HTTPError as e:
            sha = None if e.code == 404 else (_ for _ in ()).throw(e)

        content_b64 = base64.b64encode(html_content.encode()).decode()
        data = {"message": f"🤖 Update - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                "content": content_b64, "branch": "main"}
        if sha:
            data["sha"] = sha

        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="PUT")
        with urllib.request.urlopen(req) as response:
            print("✅ Fichier uploadé sur GitHub!")
            print("🔗 https://streamax-tv.github.io/Cars-Import-Agent-/\n")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}\n")
else:
    print("⚠️  GITHUB_TOKEN pas configuré\n")

print("="*90)
print("🎉 AGENT TERMINÉ!")
print("="*90 + "\n")

def main():
    pass

if __name__ == "__main__":
    main()
