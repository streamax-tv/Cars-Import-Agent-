#!/usr/bin/env python3
"""
Analyse comparative et scoring des opportunités d'import
Marges, rentabilité, recommandations
"""

import sqlite3
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnalysteVoitures:
    """Analyse la rentabilité des voitures et formule recommandations"""
    
    # Prix de référence au Maroc (MAD)
    PRIX_MAROC_REFERENCE = {
        "volkswagen golf": 160000,
        "volkswagen passat": 220000,
        "mercedes c220": 280000,
        "mercedes e220": 350000,
        "bmw 320": 250000,
        "bmw 520": 300000,
        "audi a3": 200000,
        "audi a4": 260000,
        "audi a6": 320000,
    }
    
    # Ajustements prix selon condition
    AJUSTEMENT_KM = 50  # MAD par 1000 km
    AJUSTEMENT_ANNEE = 2000  # MAD par an
    
    # Seuils rentabilité
    MARGE_MIN_MAD = 30000  # Minimum pour être viable
    MARGE_MIN_PCT = 15  # % minimum
    
    def __init__(self, db_path="voitures.db"):
        self.db_path = db_path
    
    def _estimer_prix_maroc(self, marque: str, modele: str, 
                            annee: int, km: int) -> float:
        """Estime le prix de vente probable au Maroc"""
        
        # Cherche prix de référence
        clé = f"{marque.lower()} {modele.lower()}".strip()
        prix_base = self.PRIX_MAROC_REFERENCE.get(clé)
        
        if not prix_base:
            # Estimation par marque si modèle pas trouvé
            for ref_key, ref_price in self.PRIX_MAROC_REFERENCE.items():
                if marque.lower() in ref_key:
                    prix_base = ref_price
                    break
        
        if not prix_base:
            # Estimation par défaut selon marque
            estimations = {
                "volkswagen": 190000,
                "mercedes": 300000,
                "bmw": 280000,
                "audi": 260000,
            }
            prix_base = estimations.get(marque.lower(), 250000)
        
        # Ajustements
        depréciation_km = (km / 1000) * self.AJUSTEMENT_KM
        depréciation_annee = (datetime.now().year - annee) * self.AJUSTEMENT_ANNEE
        
        prix_estime = prix_base - depréciation_km - depréciation_annee
        
        # Min-max raisonnable
        return max(min(prix_estime, prix_base), prix_base * 0.5)
    
    def analyser_voiture(self, voiture: dict, import_data: dict) -> dict:
        """Analyse complète d'une opportunité"""
        
        # Prix estimé Maroc
        prix_maroc_mad = self._estimer_prix_maroc(
            voiture['marque'], voiture['modele'],
            voiture['annee'], voiture['km']
        )
        prix_maroc_eur = prix_maroc_mad / 10.5
        
        # Coût de revient
        prix_revient_eur = import_data['prix_revient_eur']
        prix_revient_mad = import_data['prix_revient_mad']
        
        # Calcul marges
        marge_eur = prix_maroc_eur - prix_revient_eur
        marge_mad = prix_maroc_mad - prix_revient_mad
        marge_pct = (marge_eur / prix_revient_eur * 100) if prix_revient_eur > 0 else 0
        
        # Frais supplémentaires estimés (marketing, logistique, documentation)
        frais_supplementaires = 3000  # MAD
        marge_nette_mad = marge_mad - frais_supplementaires
        marge_nette_eur = marge_nette_mad / 10.5
        
        # Scoring & recommandation
        score = self._calculer_score(marge_eur, marge_pct, voiture['annee'], voiture['km'])
        verdict = self._evaluer_verdict(marge_eur, marge_pct, score)
        
        return {
            # Infos voiture
            "id": f"{voiture['source']}_{voiture['url']}",
            "source": voiture['source'],
            "titre": voiture.get('titre', ''),
            "marque": voiture['marque'],
            "modele": voiture['modele'],
            "annee": voiture['annee'],
            "km": voiture['km'],
            "carburant": voiture['carburant'],
            "pays_origine": voiture['pays'],
            
            # Prix
            "prix_achat_eur": voiture['prix_eur'],
            "prix_maroc_mad": prix_maroc_mad,
            "prix_maroc_eur": prix_maroc_eur,
            
            # Coûts
            "transport_eur": import_data['cout_transport_eur'],
            "douane_taxes_eur": import_data['frais_douane_total_eur'],
            "frais_admin_eur": import_data['frais_fixes_eur'],
            "prix_revient_eur": prix_revient_eur,
            "prix_revient_mad": prix_revient_mad,
            
            # Marges
            "marge_brute_eur": marge_eur,
            "marge_brute_mad": marge_mad,
            "marge_brute_pct": marge_pct,
            "frais_supplementaires_mad": frais_supplementaires,
            "marge_nette_eur": marge_nette_eur,
            "marge_nette_mad": marge_nette_mad,
            
            # Scoring
            "score": score,
            "verdict": verdict,
            "rentable": verdict in ["EXCELLENT", "BON"],
            "url": voiture.get('url', ''),
            "date_analyse": datetime.now().isoformat()
        }
    
    def _calculer_score(self, marge_eur: float, marge_pct: float, annee: int, km: int) -> int:
        """Score de qualité de l'opportunité (0-100)"""
        
        score = 50  # Base
        
        # Marge brute (30 pts max)
        if marge_eur > 20000:
            score += 30
        elif marge_eur > 15000:
            score += 25
        elif marge_eur > 10000:
            score += 20
        elif marge_eur > 5000:
            score += 10
        
        # Pourcentage marge (20 pts max)
        if marge_pct > 25:
            score += 20
        elif marge_pct > 20:
            score += 15
        elif marge_pct > 15:
            score += 10
        elif marge_pct > 10:
            score += 5
        
        # Condition véhicule (20 pts max)
        age = datetime.now().year - annee
        if age <= 5 and km < 80000:
            score += 20
        elif age <= 8 and km < 120000:
            score += 15
        elif age <= 10 and km < 150000:
            score += 10
        else:
            score += 5
        
        # Bonus marques premium
        return min(score, 100)
    
    def _evaluer_verdict(self, marge_eur: float, marge_pct: float, score: int) -> str:
        """Évalue le verdict final"""
        
        if marge_eur > 20000 and marge_pct > 25 and score >= 80:
            return "EXCELLENT"
        elif marge_eur > 15000 and marge_pct > 20 and score >= 70:
            return "BON"
        elif marge_eur > 10000 and marge_pct > 15 and score >= 60:
            return "MOYEN"
        elif marge_eur > 5000 and marge_pct > 10 and score >= 50:
            return "LIMITE"
        else:
            return "FAIBLE"
    
    def analyser_batch(self, voitures_with_import: list) -> list:
        """Analyse batch de voitures"""
        resultats = []
        
        for item in voitures_with_import:
            try:
                # Séparer voiture et données import
                voiture = {k: v for k, v in item.items() 
                          if k not in ['prix_revient_eur', 'cout_transport_eur', 'frais_douane_total_eur', 'frais_fixes_eur', 'prix_revient_mad']}
                import_data = {k: v for k, v in item.items() 
                              if k in ['prix_revient_eur', 'cout_transport_eur', 'frais_douane_total_eur', 'frais_fixes_eur', 'prix_revient_mad']}
                
                analyse = self.analyser_voiture(voiture, import_data)
                resultats.append(analyse)
            except Exception as e:
                logger.error(f"Erreur analyse: {e}")
                continue
        
        # Tri par score décroissant
        return sorted(resultats, key=lambda x: x['score'], reverse=True)
    
    def sauvegarder_analyses(self, analyses: list):
        """Sauvegarde les analyses en DB"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for analyse in analyses:
            c.execute('''INSERT OR REPLACE INTO analyses VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (analyse['id'], 
                      f"{analyse['source']}_{analyse['url']}",
                      analyse['prix_revient_eur'],
                      analyse['prix_maroc_eur'],
                      analyse['marge_nette_eur'],
                      analyse['marge_brute_pct'],
                      analyse['verdict'],
                      datetime.now()))
        
        conn.commit()
        conn.close()
    
    def generer_rapport(self, analyses: list, top_n: int = 10) -> str:
        """Génère un rapport texte des meilleures opportunités"""
        
        bonnes = [a for a in analyses if a['rentable']][:top_n]
        
        rapport = "\n" + "="*80 + "\n"
        rapport += f"📊 RAPPORT D'OPPORTUNITÉS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        rapport += "="*80 + "\n\n"
        
        rapport += f"✅ VOITURES RENTABLES IDENTIFIÉES : {len(bonnes)}\n\n"
        
        for i, a in enumerate(bonnes, 1):
            rapport += f"{i}. ⭐ {a['score']}/100 - {a['marque'].upper()} {a['modele'].upper()}\n"
            rapport += f"   Année: {a['annee']} | {a['km']:,} km | {a['carburant']}\n"
            rapport += f"   Pays: {a['pays_origine']} | Source: {a['source']}\n"
            rapport += f"   Prix achat: {a['prix_achat_eur']:.0f}€ | Coût revient: {a['prix_revient_eur']:.0f}€\n"
            rapport += f"   Marge nette: {a['marge_nette_eur']:.0f}€ ({a['marge_brute_pct']:.1f}%) ➜ {a['prix_maroc_mad']:.0f} MAD\n"
            rapport += f"   Verdict: {a['verdict']} ✓\n"
            rapport += f"   URL: {a['url']}\n\n"
        
        rapport += "="*80 + "\n"
        
        return rapport

if __name__ == "__main__":
    analyste = AnalysteVoitures()
    
    # Test
    voiture_test = {
        'source': 'Autoscout24',
        'marque': 'BMW',
        'modele': '320d',
        'prix_eur': 12000,
        'km': 85000,
        'annee': 2016,
        'carburant': 'Diesel',
        'pays': 'Allemagne',
        'url': 'https://...',
        'titre': 'BMW 320d 2016'
    }
    
    import_test = {
        'prix_revient_eur': 16500,
        'cout_transport_eur': 900,
        'frais_douane_total_eur': 3000,
        'frais_fixes_eur': 800,
        'prix_revient_mad': 173250
    }
    
    analyse = analyste.analyser_voiture(voiture_test, import_test)
    
    print(f"\n🎯 SCORE: {analyse['score']}/100")
    print(f"💰 MARGE NETTE: {analyse['marge_nette_eur']:.0f}€ ({analyse['marge_brute_pct']:.1f}%)")
    print(f"✅ VERDICT: {analyse['verdict']}")
