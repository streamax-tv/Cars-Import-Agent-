#!/usr/bin/env python3
"""
Exemples d'utilisation de l'Agent Import Voitures
"""

from agent import AgentImportVoitures
from analyste import AnalysteVoitures
import json

# ============= EXEMPLE 1 =============
# Recherche basique pour Mercedes et BMW
print("\n" + "="*60)
print("📌 EXEMPLE 1 - Recherche Mercedes + BMW")
print("="*60)

agent = AgentImportVoitures()
agent.executer_recherche_complete(
    marques=["Mercedes", "BMW"],
    prix_max=20000,
    km_max=120000
)

# Affiche top 3
for i in range(min(3, len(agent.voitures_rentables))):
    agent.afficher_detailles(i)


# ============= EXEMPLE 2 =============
# Recherche Audi uniquement - budget serré
print("\n" + "="*60)
print("📌 EXEMPLE 2 - Audi budget 15k€")
print("="*60)

agent2 = AgentImportVoitures("voitures_audi.db")
agent2.executer_recherche_complete(
    marques=["Audi"],
    prix_max=15000,
    km_max=100000
)


# ============= EXEMPLE 3 =============
# Recherche VW Passat budget moyen
print("\n" + "="*60)
print("📌 EXEMPLE 3 - Volkswagen Passat")
print("="*60)

agent3 = AgentImportVoitures()

# Scraper uniquement
voitures = agent3.scraper.scraper_tous(
    marques=["Volkswagen"],
    prix_max=18000,
    km_max=140000
)

print(f"\n✅ {len(voitures)} Volkswagen trouvées\n")

# Filtrer Passat
passats = [v for v in voitures if 'passat' in v['modele'].lower()]
print(f"📍 Dont {len(passats)} Passat\n")

# Analyser chaque Passat
import_calc = agent3.import_calc
analyste = agent3.analyste

voitures_passats_complet = []
for v in passats:
    import_data = import_calc.calculer_import_complet(
        prix_achat_eur=v['prix_eur'],
        pays_origine=v['pays'],
        modele=v['modele'],
        carburant=v['carburant'],
        annee=v['annee']
    )
    voitures_passats_complet.append({**v, **import_data})

analyses = analyste.analyser_batch(voitures_passats_complet)
bonnes = [a for a in analyses if a['rentable']]

print(f"🎯 Dont {len(bonnes)} RENTABLES !\n")

for analyse in bonnes[:5]:
    print(f"✓ {analyse['marque']} {analyse['modele']} ({analyse['annee']})")
    print(f"  Prix achat: {analyse['prix_achat_eur']:.0f}€ → Maroc: {analyse['prix_maroc_mad']:.0f} MAD")
    print(f"  Marge: {analyse['marge_nette_eur']:.0f}€ ({analyse['marge_brute_pct']:.1f}%) | Score: {analyse['score']}/100\n")


# ============= EXEMPLE 4 =============
# Recherche par critères strictes
print("\n" + "="*60)
print("📌 EXEMPLE 4 - Critères premium: BMW/Mercedes, diesel, récent")
print("="*60)

agent4 = AgentImportVoitures()

# Phase 1: Scraping
voitures = agent4.scraper.scraper_tous(
    marques=["BMW", "Mercedes"],
    prix_max=22000,
    km_max=100000
)

# Phase 2: Filtrer diesel récent (2015+)
voitures_filtered = [
    v for v in voitures 
    if v['carburant'].lower() == 'diesel' and v['annee'] >= 2015
]

print(f"Après filtrage: {len(voitures_filtered)} voitures\n")

# Phase 3: Calculer + analyser
import_calc = agent4.import_calc
analyste = agent4.analyste

voitures_complet = []
for v in voitures_filtered:
    import_data = import_calc.calculer_import_complet(
        prix_achat_eur=v['prix_eur'],
        pays_origine=v['pays'],
        modele=v['modele'],
        carburant=v['carburant'],
        annee=v['annee']
    )
    voitures_complet.append({**v, **import_data})

analyses = analyste.analyser_batch(voitures_complet)
top_rentables = [a for a in analyses if a['rentable']][:10]

print(f"🏆 TOP 10 OPPORTUNITÉS PREMIUM\n")
for i, a in enumerate(top_rentables, 1):
    print(f"{i}. {a['marque']} {a['modele']} ({a['annee']}) | {a['km']:,}km")
    print(f"   {a['prix_achat_eur']:.0f}€ → {a['prix_maroc_mad']:.0f} MAD")
    print(f"   Marge: {a['marge_nette_eur']:.0f}€ | Score: {a['score']}/100\n")


# ============= EXEMPLE 5 =============
# Exporter résultats dans différents formats
print("\n" + "="*60)
print("📌 EXEMPLE 5 - Exporter en multiple formats")
print("="*60)

import pandas as pd
from rapport_exporter import RapportExporter

if agent.voitures_analysees:
    df = pd.DataFrame(agent.voitures_analysees)
    exporter = RapportExporter()
    
    # CSV
    exporter.exporter_csv(df, "resultats_personnalises.csv")
    print("✓ CSV exporté")
    
    # Excel
    exporter.exporter_excel(df, "resultats_personnalises.xlsx")
    print("✓ Excel exporté")
    
    # JSON
    rentables_only = [v for v in agent.voitures_analysees if v['rentable']]
    exporter.exporter_json(rentables_only, "resultats_rentables.json")
    print("✓ JSON exporté")
    
    # HTML interactif
    exporter.generer_synthese_html(agent.voitures_analysees)
    print("✓ HTML exporté\n")


# ============= EXEMPLE 6 =============
# Monitoring prix - même voiture sur plusieurs jours
print("\n" + "="*60)
print("📌 EXEMPLE 6 - Suivi prix (Comparaison jour après jour)")
print("="*60)

# Jour 1
agent_jour1 = AgentImportVoitures("tracking.db")
voitures_j1 = agent_jour1.scraper.scraper_tous(
    marques=["BMW"],
    prix_max=15000
)

print(f"Jour 1: {len(voitures_j1)} BMW trouvées")
prix_moyens_j1 = sum(v['prix_eur'] for v in voitures_j1) / len(voitures_j1) if voitures_j1 else 0
print(f"Prix moyen: {prix_moyens_j1:.0f}€\n")

# Jour 2 (simulation)
voitures_j2 = agent_jour1.scraper.scraper_tous(
    marques=["BMW"],
    prix_max=15000
)

prix_moyens_j2 = sum(v['prix_eur'] for v in voitures_j2) / len(voitures_j2) if voitures_j2 else 0
print(f"Jour 2: {len(voitures_j2)} BMW trouvées")
print(f"Prix moyen: {prix_moyens_j2:.0f}€")

if prix_moyens_j2 < prix_moyens_j1:
    reduction = prix_moyens_j1 - prix_moyens_j2
    print(f"📉 Les prix baissent ! -{reduction:.0f}€ de réduction moyenne\n")
else:
    hausse = prix_moyens_j2 - prix_moyens_j1
    print(f"📈 Les prix montent. +{hausse:.0f}€ de hausse moyenne\n")


# ============= EXEMPLE 7 =============
# Calculer ROI pour importateur
print("\n" + "="*60)
print("📌 EXEMPLE 7 - Simulation ROI")
print("="*60)

# Hypothèses
voitures_par_mois = 10
marge_moyenne = 20000  # €
frais_operationnels = 2000  # € par voiture (documents, assurance, etc)
frais_fixes_maroc = 5000  # € par mois (local, employe, etc)

def calculer_roi_mensuel(nb_voitures, marge_unit):
    revenue = nb_voitures * marge_unit
    charges = (nb_voitures * frais_operationnels) + frais_fixes_maroc
    profit = revenue - charges
    roi = (profit / charges * 100) if charges > 0 else 0
    return {
        'revenue': revenue,
        'charges': charges,
        'profit': profit,
        'roi': roi
    }

scenarios = [5, 10, 15, 20]

print("Scenario | Voitures/mois | Profit/mois | ROI%")
print("-" * 50)

for nb in scenarios:
    result = calculer_roi_mensuel(nb, marge_moyenne)
    print(f"{nb:>8} | {nb:>13} | {result['profit']:>11.0f}€ | {result['roi']:>6.1f}%")

print()


# ============= EXEMPLE 8 =============
# Alertes automatiques pour meilleures opportunités
print("\n" + "="*60)
print("📌 EXEMPLE 8 - Système d'alertes (meilleures affaires)")
print("="*60)

def generer_alerte(voitures_list, seuil_marge=20000, min_score=80):
    """Génère alerte pour meilleures affaires"""
    
    excellentes = [
        v for v in voitures_list 
        if v.get('marge_nette_eur', 0) >= seuil_marge and v.get('score', 0) >= min_score
    ]
    
    if excellentes:
        message = f"""
🚨 ALERTE - EXCELLENTES OPPORTUNITÉS DÉTECTÉES !

{len(excellentes)} voiture(s) correspondent à vos critères:

"""
        for v in excellentes[:5]:
            message += f"""
✓ {v['marque']} {v['modele']} ({v['annee']})
  Prix: {v['prix_achat_eur']:.0f}€ | Marge: {v['marge_nette_eur']:.0f}€
  Score: {v['score']}/100 | Verdict: {v['verdict']}
  Source: {v['source']} | Pays: {v['pays_origine']}
  URL: {v['url']}
"""
        
        return message
    else:
        return "Pas d'opportunité exceptionnelle cette fois."

if agent.voitures_analysees:
    alerte = generer_alerte(agent.voitures_analysees)
    print(alerte)

print("\n" + "="*60)
print("✅ EXEMPLES TERMINÉS")
print("="*60)
