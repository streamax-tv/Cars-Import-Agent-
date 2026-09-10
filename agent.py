#!/usr/bin/env python3
"""
AGENT IA PRINCIPAL - Import Voitures Occasion Maroc
Orchestre: Scraping → Import Maroc → Analyse → Rapports
"""

import logging
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Imports locaux
from scraper import VoituresScraper
from import_maroc import ImportMaroc
from analyste import AnalysteVoitures
from rapport_exporter import RapportExporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentImportVoitures:
    """Agent IA principal pour importation voitures Maroc"""
    
    def __init__(self, db_path="voitures.db"):
        self.db_path = db_path
        self.scraper = VoituresScraper(db_path)
        self.import_calc = ImportMaroc()
        self.analyste = AnalysteVoitures(db_path)
        self.exporter = RapportExporter()
        
        self.voitures_trouvees = []
        self.voitures_analysees = []
        self.voitures_rentables = []
    
    def executer_recherche_complete(self, 
                                   marques=["Volkswagen", "Mercedes", "BMW", "Audi"],
                                   carburants=["Diesel", "Hybride"],
                                   prix_max=25000,
                                   km_max=150000):
        """
        Exécute le pipeline complet:
        1. Scrape tous les sites
        2. Calcule coûts d'import
        3. Analyse rentabilité
        4. Génère rapports
        """
        
        print("\n" + "="*80)
        print("🤖 AGENT IA - RECHERCHE VOITURES D'OCCASION EUROPA → MAROC")
        print("="*80 + "\n")
        
        # ÉTAPE 1: SCRAPING
        print("⏳ ÉTAPE 1/4 : SCRAPING MULTI-SITES...\n")
        try:
            self.voitures_trouvees = self.scraper.scraper_tous(
                marques=marques,
                prix_max=prix_max,
                km_max=km_max
            )
            print(f"✅ {len(self.voitures_trouvees)} voitures trouvées\n")
        except Exception as e:
            logger.error(f"❌ Scraping échoué: {e}")
            return False
        
        if not self.voitures_trouvees:
            print("⚠️  Aucune voiture trouvée\n")
            return False
        
        # ÉTAPE 2: CALCUL IMPORT MAROC
        print("⏳ ÉTAPE 2/4 : CALCUL COÛTS D'IMPORT MAROC...\n")
        try:
            voitures_avec_import = []
            
            for voiture in self.voitures_trouvees:
                import_data = self.import_calc.calculer_import_complet(
                    prix_achat_eur=voiture['prix_eur'],
                    pays_origine=voiture['pays'],
                    modele=voiture['modele'],
                    carburant=voiture['carburant'],
                    annee=voiture['annee']
                )
                
                voiture_complete = {**voiture, **import_data}
                voitures_avec_import.append(voiture_complete)
            
            print(f"✅ Coûts calculés pour {len(voitures_avec_import)} véhicules\n")
        
        except Exception as e:
            logger.error(f"❌ Erreur calcul import: {e}")
            return False
        
        # ÉTAPE 3: ANALYSE RENTABILITÉ
        print("⏳ ÉTAPE 3/4 : ANALYSE RENTABILITÉ...\n")
        try:
            self.voitures_analysees = self.analyste.analyser_batch(voitures_avec_import)
            
            # Filtrer les voitures rentables
            self.voitures_rentables = [v for v in self.voitures_analysees 
                                       if v['rentable']]
            
            print(f"✅ {len(self.voitures_rentables)}/{len(self.voitures_analysees)} voitures RENTABLES\n")
            
            # Stats
            if self.voitures_rentables:
                marge_moyenne = sum(v['marge_nette_eur'] for v in self.voitures_rentables) / len(self.voitures_rentables)
                print(f"   Marge moyenne: {marge_moyenne:.0f}€")
                print(f"   Meilleur score: {max(v['score'] for v in self.voitures_rentables)}/100\n")
        
        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}")
            return False
        
        # ÉTAPE 4: GÉNÉRATION RAPPORTS
        print("⏳ ÉTAPE 4/4 : GÉNÉRATION RAPPORTS...\n")
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Rapport texte
            rapport_txt = self.analyste.generer_rapport(self.voitures_analysees, top_n=20)
            self.exporter.exporter_txt(rapport_txt, f"rapport_{timestamp}.txt")
            print(f"   📄 Rapport TXT généré")
            
            # CSV détaillé
            df_analyses = pd.DataFrame(self.voitures_analysees)
            self.exporter.exporter_csv(df_analyses, f"analyses_{timestamp}.csv")
            print(f"   📊 Fichier CSV généré")
            
            # Excel avec graphiques
            self.exporter.exporter_excel(df_analyses, f"analyses_{timestamp}.xlsx")
            print(f"   📈 Fichier Excel généré")
            
            # JSON (pour intégrations)
            self.exporter.exporter_json(self.voitures_rentables, f"opportunites_{timestamp}.json")
            print(f"   🔗 Fichier JSON généré\n")
            
            # PDF (si disponible)
            try:
                self.exporter.exporter_pdf(self.voitures_rentables, f"rapport_{timestamp}.pdf")
                print(f"   📕 Rapport PDF généré\n")
            except:
                print(f"   ⚠️  PDF non généré (dépendance manquante)\n")
            
        except Exception as e:
            logger.error(f"⚠️  Erreur export: {e}")
        
        # RÉSUMÉ FINAL
        self._afficher_resume()
        
        return True
    
    def _afficher_resume(self):
        """Affiche un résumé des résultats"""
        
        print("="*80)
        print("📋 RÉSUMÉ DE LA SESSION")
        print("="*80 + "\n")
        
        print(f"📍 RECHERCHE")
        print(f"   • Voitures trouvées: {len(self.voitures_trouvees)}")
        print(f"   • Analysées: {len(self.voitures_analysees)}")
        print(f"   • Rentables: {len(self.voitures_rentables)}\n")
        
        if self.voitures_rentables:
            print(f"💰 STATISTIQUES")
            
            marges = [v['marge_nette_eur'] for v in self.voitures_rentables]
            scores = [v['score'] for v in self.voitures_rentables]
            
            print(f"   • Marge nette moyenne: {sum(marges)/len(marges):.0f}€")
            print(f"   • Marge min: {min(marges):.0f}€")
            print(f"   • Marge max: {max(marges):.0f}€")
            print(f"   • Score moyen: {sum(scores)/len(scores):.0f}/100\n")
            
            # Top 5
            print(f"🏆 TOP 5 OPPORTUNITÉS\n")
            for i, v in enumerate(self.voitures_rentables[:5], 1):
                print(f"   {i}. {v['marque'].upper()} {v['modele'].upper()}")
                print(f"      Marge: {v['marge_nette_eur']:.0f}€ | Score: {v['score']}/100")
                print(f"      Prix achat: {v['prix_achat_eur']:.0f}€ → Maroc: {v['prix_maroc_mad']:.0f} MAD\n")
        
        print("="*80)
        print(f"✅ RAPPORTS SAUVEGARDÉS DANS: ./rapports/\n")
    
    def afficher_detailles(self, index: int = 0):
        """Affiche détails complets d'une voiture"""
        if index >= len(self.voitures_rentables):
            print("Index invalide")
            return
        
        voiture = self.voitures_rentables[index]
        
        print("\n" + "="*80)
        print(f"🚗 DÉTAILS COMPLETS - {voiture['marque'].upper()} {voiture['modele'].upper()}")
        print("="*80 + "\n")
        
        print(f"📌 IDENTIFICATION")
        print(f"   Source: {voiture['source']}")
        print(f"   Pays: {voiture['pays_origine']}")
        print(f"   URL: {voiture['url']}\n")
        
        print(f"🚙 CARACTÉRISTIQUES")
        print(f"   Année: {voiture['annee']}")
        print(f"   Kilométrage: {voiture['km']:,} km")
        print(f"   Carburant: {voiture['carburant']}\n")
        
        print(f"💶 PRIX EUROPE")
        print(f"   Achat: {voiture['prix_achat_eur']:.0f}€")
        print(f"   Transport: {voiture['transport_eur']:.0f}€")
        print(f"   Douane/Taxes: {voiture['douane_taxes_eur']:.0f}€")
        print(f"   Frais admin: {voiture['frais_admin_eur']:.0f}€")
        print(f"   TOTAL REVIENT: {voiture['prix_revient_eur']:.0f}€\n")
        
        print(f"💰 PRIX MAROC")
        print(f"   Prix estimé: {voiture['prix_maroc_mad']:.0f} MAD ({voiture['prix_maroc_eur']:.0f}€)\n")
        
        print(f"📊 RENTABILITÉ")
        print(f"   Marge brute: {voiture['marge_brute_eur']:.0f}€ ({voiture['marge_brute_pct']:.1f}%)")
        print(f"   Marge nette: {voiture['marge_nette_eur']:.0f}€")
        print(f"   Score: {voiture['score']}/100")
        print(f"   Verdict: {voiture['verdict']}\n")
        
        print("="*80 + "\n")

if __name__ == "__main__":
    
    agent = AgentImportVoitures()
    
    # Lance recherche complète
    success = agent.executer_recherche_complete(
        marques=["Volkswagen", "Mercedes", "BMW", "Audi"],
        carburants=["Diesel", "Hybride"],
        prix_max=25000,
        km_max=150000
    )
    
    if success and agent.voitures_rentables:
        # Affiche détails du meilleur
        print("\n📍 Affichage du meilleur résultat:\n")
        agent.afficher_detailles(0)
