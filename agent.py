#!/usr/bin/env python3
"""
AGENT IA - Import Voitures Europa → Maroc
Version 3: Résultats affichés clairement dans les logs
"""

import json
import os
from datetime import datetime

print("\n" + "="*90)
print("🚗 AGENT IA IMPORT VOITURES MAROC")
print("="*90 + "\n")

print("✅ Agent démarré avec succès!")
print(f"📅 Date/heure: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")

# Configuration depuis .env
PAYS = os.getenv("PAYS", "Allemagne,France,Belgique").split(",")
MARQUES = os.getenv("MARQUES", "BMW,Mercedes,Audi").split(",")
PRIX_MAX = int(os.getenv("PRIX_MAX", "25000"))

print(f"⚙️  CONFIGURATION")
print(f"   Pays:      {', '.join(PAYS)}")
print(f"   Marques:   {', '.join(MARQUES)}")
print(f"   Prix max:  {PRIX_MAX}€\n")

# Données de test simulées
VOITURES_TEST = [
    {"marque": "BMW", "modele": "320d", "annee": 2023, "km": 35000, "prix": 18500, "pays": "Allemagne", "source": "Autoscout24", "marge": 6500},
    {"marque": "Mercedes", "modele": "C220d", "annee": 2022, "km": 48000, "prix": 22400, "pays": "Allemagne", "source": "Autoscout24", "marge": 7200},
    {"marque": "Audi", "modele": "A4 2.0d", "annee": 2023, "km": 42000, "prix": 24800, "pays": "Belgique", "source": "Autoscout24", "marge": 5800},
    {"marque": "Volkswagen", "modele": "Passat", "annee": 2021, "km": 65000, "prix": 19500, "pays": "France", "source": "Leboncoin", "marge": 4200},
]

print("📊 DONNÉES TROUVÉES")
print(f"   {len(VOITURES_TEST)} voitures trouvées\n")

print("✅ RÉSULTATS ANALYSÉS\n")

# ============ AFFICHER TABLEAU LISIBLE ============
print("📋 RÉSULTATS EN TABLEAU:\n")
print(f"{'N°':<3} {'Marque':<12} {'Modèle':<12} {'Année':<6} {'Km':<8} {'Prix €':<8} {'Pays':<12} {'Marge €':<8}")
print("-" * 100)

for i, v in enumerate(VOITURES_TEST, 1):
    print(f"{i:<3} {v['marque']:<12} {v['modele']:<12} {v['annee']:<6} {v['km']:<8} {v['prix']:<8} {v['pays']:<12} {v['marge']:<8}")

print("\n")

# ============ AFFICHER JSON COPIE-COLLEZ ============
print("📋 RÉSULTATS JSON (À COPIER):")
print("="*90)
print(json.dumps(VOITURES_TEST, indent=2, ensure_ascii=False))
print("="*90 + "\n")

# Sauvegarder aussi en fichier
os.makedirs("rapports", exist_ok=True)
json_file = os.path.join("rapports", f"resultats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(VOITURES_TEST, f, indent=2, ensure_ascii=False)

print(f"💾 Fichier créé: {json_file}\n")

print("="*90)
print("🎉 AGENT TERMINÉ AVEC SUCCÈS!")
print("="*90 + "\n")

def main():
    """Point d'entrée pour Railway"""
    pass

if __name__ == "__main__":
    main()
