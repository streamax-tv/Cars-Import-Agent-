#!/usr/bin/env python3
"""
Calcul des coûts d'import au Maroc
Tarifs douaniers officiels 2024
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class ImportMaroc:
    """Calcule coût total d'import: acquisition + transport + douane + TVA"""
    
    # Tarifs transport par pays d'origine (€)
    TRANSPORT_COSTS = {
        "Allemagne": 900,
        "France": 700,
        "Belgique": 650,
        "Espagne": 800,
        "Italie": 1000,
    }
    
    # Droits de douane par type carburant (% sur CIF)
    DROITS_DOUANE = {
        "diesel_petit": 0.30,      # < 1.8L
        "diesel_moyen": 0.35,      # 1.8-3.0L
        "diesel_gros": 0.40,       # > 3.0L
        "hybride": 0.25,
    }
    
    # Surtaxe pollution (fixe)
    SURTAXE_POLLUTION = 0.04  # 4%
    
    # TVA Maroc
    TVA = 0.20  # 20%
    
    # Frais divers
    FRAIS_DOSSIER = 500  # € pour papiers douane
    FRAIS_INSPECTION = 300  # € visite technique
    
    # Années - surcharge selon ancienneté
    SURCHARGE_ANCIENNETE = {
        3: 0.10,    # 3-8 ans: +10%
        8: 0.20,    # 8+ ans: +20%
    }
    
    def __init__(self):
        pass
    
    def _extraire_cylindree(self, modele_texte: str, carburant: str) -> str:
        """Estime la cylindrée pour les droits"""
        modele_lower = modele_texte.lower()
        
        # Marques/modèles petits moteurs
        petit_moteur = any(x in modele_lower for x in 
                          ['golf', 'polo', 'a3', 'c1', 'fiesta', 'focus', '1.4', '1.5', '1.6'])
        
        moyen_moteur = any(x in modele_lower for x in 
                          ['passat', 'a4', 'c-class', 'e-class', '2.0', '2.5'])
        
        if carburant == "hybride":
            return "hybride"
        elif petit_moteur:
            return "diesel_petit"
        elif moyen_moteur:
            return "diesel_moyen"
        else:
            return "diesel_gros"
    
    def _calculer_surcharge_anciennete(self, annee: int) -> float:
        """Surtaxe selon l'année du véhicule"""
        from datetime import datetime
        age = datetime.now().year - annee
        
        if age <= 3:
            return 0.00
        elif age <= 8:
            return 0.10
        else:
            return 0.20
    
    def calculer_import_complet(self, 
                                prix_achat_eur: float,
                                pays_origine: str,
                                modele: str,
                                carburant: str,
                                annee: int) -> Dict:
        """
        Calcule le coût complet d'import au Maroc
        
        Args:
            prix_achat_eur: Prix d'achat en Europe (€)
            pays_origine: France, Allemagne, etc.
            modele: Modèle de la voiture (pour estimer cylindrée)
            carburant: "Diesel" ou "Hybride"
            annee: Année de fabrication
        
        Returns:
            Dict avec tous les coûts détaillés
        """
        
        # 1. TRANSPORT
        cout_transport = self.TRANSPORT_COSTS.get(pays_origine, 900)
        
        # 2. CIF (Cost + Insurance + Freight)
        cif = prix_achat_eur + cout_transport
        
        # 3. DROITS DE DOUANE
        type_moteur = self._extraire_cylindree(modele, carburant)
        taux_douane = self.DROITS_DOUANE[type_moteur]
        droits_douane = cif * taux_douane
        
        # 4. SURTAXE POLLUTION
        surtaxe_pollution = cif * self.SURTAXE_POLLUTION
        
        # 5. BASE IMPOSABLE POUR TVA
        # (CIF + droits + surtaxe) selon tarif Maroc
        base_tva = cif + droits_douane + surtaxe_pollution
        tva = base_tva * self.TVA
        
        # 6. SURCHARGE ANCIENNETÉ
        surcharge_anc = self._calculer_surcharge_anciennete(annee)
        surcharge_montant = (droits_douane + surtaxe_pollution) * surcharge_anc
        
        # 7. TOTAL FRAIS DE DOUANE & DÉDOUANEMENT
        frais_douane_total = droits_douane + surtaxe_pollution + tva + surcharge_montant
        
        # 8. FRAIS FIXES
        frais_fixes = self.FRAIS_DOSSIER + self.FRAIS_INSPECTION
        
        # 9. PRIX DE REVIENT MAROC
        prix_revient_maroc = cif + frais_douane_total + frais_fixes
        
        return {
            # Inputs
            "prix_achat_eur": prix_achat_eur,
            "pays_origine": pays_origine,
            "modele": modele,
            "carburant": carburant,
            "annee": annee,
            
            # Détails
            "cout_transport_eur": cout_transport,
            "cif_eur": cif,
            
            # Douane
            "type_moteur": type_moteur,
            "taux_douane_pct": taux_douane * 100,
            "droits_douane_eur": droits_douane,
            "surtaxe_pollution_eur": surtaxe_pollution,
            "surcharge_anciennete_pct": surcharge_anc * 100,
            "surcharge_anciennete_eur": surcharge_montant,
            "tva_eur": tva,
            
            # Total
            "frais_douane_total_eur": frais_douane_total,
            "frais_dossier_eur": self.FRAIS_DOSSIER,
            "frais_inspection_eur": self.FRAIS_INSPECTION,
            "frais_fixes_eur": frais_fixes,
            
            # FINAL
            "prix_revient_eur": prix_revient_maroc,
            "prix_revient_mad": prix_revient_maroc * 10.5,  # Taux change approx
        }
    
    def calculer_batch(self, voitures_list: list) -> list:
        """Calcule l'import pour un batch de voitures"""
        resultats = []
        
        for voiture in voitures_list:
            try:
                analyse = self.calculer_import_complet(
                    prix_achat_eur=voiture['prix_eur'],
                    pays_origine=voiture['pays'],
                    modele=voiture['modele'],
                    carburant=voiture['carburant'],
                    annee=voiture['annee']
                )
                resultats.append({**voiture, **analyse})
            except Exception as e:
                logger.error(f"Erreur calcul {voiture.get('titre')}: {e}")
                continue
        
        return resultats

    def afficher_detailles(self, analyse: Dict):
        """Affiche les détails de coût de façon lisible"""
        print("\n" + "="*60)
        print(f"📊 ANALYSE D'IMPORT - {analyse['modele'].upper()}")
        print("="*60)
        
        print(f"\n🚗 ACQUISITION")
        print(f"  Prix d'achat ({analyse['pays_origine']})  : {analyse['prix_achat_eur']:.0f} €")
        print(f"  Année                           : {analyse['annee']}")
        print(f"  Carburant                       : {analyse['carburant']}")
        
        print(f"\n🚢 TRANSPORT")
        print(f"  Fret vers Maroc                 : {analyse['cout_transport_eur']:.0f} €")
        print(f"  CIF (prix + transport)          : {analyse['cif_eur']:.0f} €")
        
        print(f"\n📋 DOUANES & TAXES MAROC")
        print(f"  Type moteur                     : {analyse['type_moteur']}")
        print(f"  Droits de douane ({analyse['taux_douane_pct']:.0f}%)         : {analyse['droits_douane_eur']:.0f} €")
        print(f"  Surtaxe pollution (4%)          : {analyse['surtaxe_pollution_eur']:.0f} €")
        if analyse['surcharge_anciennete_pct'] > 0:
            print(f"  Surcharge ancienneté ({analyse['surcharge_anciennete_pct']:.0f}%)   : {analyse['surcharge_anciennete_eur']:.0f} €")
        print(f"  TVA Maroc (20%)                 : {analyse['tva_eur']:.0f} €")
        
        print(f"\n💼 FRAIS ADMINISTRATIFS")
        print(f"  Dossier douane                  : {analyse['frais_dossier_eur']:.0f} €")
        print(f"  Inspection technique           : {analyse['frais_inspection_eur']:.0f} €")
        
        print(f"\n💰 PRIX DE REVIENT")
        print(f"  ➜ EN EUROS    : {analyse['prix_revient_eur']:.0f} €")
        print(f"  ➜ EN DIRHAMS  : {analyse['prix_revient_mad']:.0f} MAD")
        print("="*60 + "\n")

if __name__ == "__main__":
    im = ImportMaroc()
    
    # Test
    analyse = im.calculer_import_complet(
        prix_achat_eur=12000,
        pays_origine="Allemagne",
        modele="BMW 320d",
        carburant="Diesel",
        annee=2016
    )
    
    im.afficher_detailles(analyse)
