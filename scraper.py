#!/usr/bin/env python3
"""
Scraper multi-sites pour voitures d'occasion
Supporte : Autoscout24, Leboncoin, Mobile.de, Marktplaats, etc.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict
import time
from datetime import datetime, timedelta
import sqlite3
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoituresScraper:
    def __init__(self, db_path="voitures.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self._init_db()
    
    def _init_db(self):
        """Crée la base de données locale"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS voitures (
            id TEXT PRIMARY KEY,
            source TEXT,
            marque TEXT,
            modele TEXT,
            annee INTEGER,
            km INTEGER,
            prix_eur REAL,
            carburant TEXT,
            pays TEXT,
            url TEXT,
            titre TEXT,
            description TEXT,
            date_scrape TIMESTAMP,
            date_annonce TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            voiture_id TEXT,
            cout_import REAL,
            prix_maroc REAL,
            marge REAL,
            marge_pct REAL,
            rentabilite TEXT,
            date_analyse TIMESTAMP,
            FOREIGN KEY(voiture_id) REFERENCES voitures(id)
        )''')
        
        conn.commit()
        conn.close()
    
    def _get_cached(self, marque, modele, pays):
        """Récupère cache si < 24h"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        seuil = datetime.now() - timedelta(hours=24)
        c.execute('''SELECT * FROM voitures 
                     WHERE marque = ? AND modele = ? AND pays = ? AND date_scrape > ?
                     ORDER BY date_scrape DESC LIMIT 50''',
                  (marque, modele, pays, seuil))
        
        resultats = c.fetchall()
        conn.close()
        
        return resultats if resultats else None
    
    def _save_voitures(self, voitures: List[Dict]):
        """Sauvegarde les voitures en DB"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for v in voitures:
            # Hash unique pour éviter doublons
            hash_id = hashlib.md5(
                f"{v['source']}{v['url']}".encode()
            ).hexdigest()
            
            c.execute('''INSERT OR REPLACE INTO voitures VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (hash_id, v.get('source'), v.get('marque'), v.get('modele'),
                      v.get('annee'), v.get('km'), v.get('prix_eur'), v.get('carburant'),
                      v.get('pays'), v.get('url'), v.get('titre'), v.get('description'),
                      datetime.now(), v.get('date_annonce')))
        
        conn.commit()
        conn.close()
        logger.info(f"✓ {len(voitures)} voitures sauvegardées")
    
    # ==================== AUTOSCOUT24 ====================
    def scraper_autoscout24(self, marques: List[str], prix_max: int, km_max: int) -> List[Dict]:
        """Scrape Autoscout24 (DE, FR, BE, ES, IT)"""
        
        resultats = []
        
        # URLs par pays
        urls = {
            "Allemagne": "https://www.autoscout24.de",
            "France": "https://www.autoscout24.fr",
            "Belgique": "https://www.autoscout24.be",
            "Espagne": "https://www.autoscout24.es",
            "Italie": "https://www.autoscout24.it"
        }
        
        for pays, base_url in urls.items():
            for marque in marques:
                try:
                    # Construction URL de recherche
                    search_url = (
                        f"{base_url}/lst/"
                        f"?make={marque.lower()}"
                        f"&fuel=D,H"  # Diesel + Hybride
                        f"&price=0-{prix_max}"
                        f"&km=0-{km_max}"
                        f"&sort=price"
                    )
                    
                    logger.info(f"🔍 Scraping Autoscout24 {pays} - {marque}")
                    
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Sélecteurs Autoscout24 (peuvent varier)
                    voitures_elements = soup.find_all('article', class_='ListItem')
                    
                    for element in voitures_elements[:20]:  # Top 20 par recherche
                        try:
                            titre = element.find('h2')
                            prix = element.find('span', class_='price-amount')
                            km = element.find('span', {'data-testid': 'mileage'})
                            
                            if titre and prix:
                                voiture = {
                                    'source': 'Autoscout24',
                                    'pays': pays,
                                    'titre': titre.text.strip(),
                                    'marque': marque,
                                    'modele': titre.text.strip().split()[-1] if titre else "",
                                    'prix_eur': float(prix.text.replace('€', '').replace('.', '').replace(',', '.').strip()),
                                    'km': int(km.text.split()[0].replace('.', '')) if km else 0,
                                    'carburant': 'Diesel' if 'Diesel' in element.text else 'Hybride',
                                    'url': element.find('a')['href'] if element.find('a') else "",
                                    'description': element.text[:200],
                                    'annee': self._extraire_annee(element.text),
                                    'date_annonce': datetime.now()
                                }
                                resultats.append(voiture)
                        except Exception as e:
                            logger.warning(f"  ⚠️  Erreur parsing: {e}")
                            continue
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"  ❌ Autoscout24 {pays}: {e}")
                    continue
        
        if resultats:
            self._save_voitures(resultats)
        return resultats
    
    # ==================== LEBONCOIN ====================
    def scraper_leboncoin(self, marques: List[str], prix_max: int, km_max: int) -> List[Dict]:
        """Scrape Leboncoin (France)"""
        
        resultats = []
        
        for marque in marques:
            try:
                logger.info(f"🔍 Scraping Leboncoin - {marque}")
                
                # API Leboncoin (plus fiable que scraping)
                search_url = (
                    "https://api.leboncoin.fr/finder/search"
                    f"?q={marque}"
                    f"&category=2"  # Véhicules
                    f"&fuel=diesel,hybrid"
                    f"&price=0-{prix_max}"
                )
                
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for item in data.get('ads', [])[:20]:
                    try:
                        voiture = {
                            'source': 'Leboncoin',
                            'pays': 'France',
                            'titre': item.get('title', ''),
                            'marque': marque,
                            'modele': item.get('model', ''),
                            'prix_eur': float(item.get('price', 0)),
                            'km': int(item.get('mileage', 0)),
                            'carburant': item.get('fuel_type', 'Diesel'),
                            'url': item.get('url', ''),
                            'description': item.get('description', '')[:200],
                            'annee': int(item.get('year', 2020)),
                            'date_annonce': datetime.fromisoformat(item.get('first_publication_date', datetime.now().isoformat()))
                        }
                        resultats.append(voiture)
                    except Exception as e:
                        logger.warning(f"  ⚠️  Erreur item: {e}")
                        continue
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"  ❌ Leboncoin: {e}")
                continue
        
        if resultats:
            self._save_voitures(resultats)
        return resultats
    
    # ==================== MOBILE.DE ====================
    def scraper_mobile_de(self, marques: List[str], prix_max: int, km_max: int) -> List[Dict]:
        """Scrape Mobile.de (Allemagne)"""
        
        resultats = []
        
        for marque in marques:
            try:
                logger.info(f"🔍 Scraping Mobile.de - {marque}")
                
                search_url = (
                    f"https://www.mobile.de/search.html"
                    f"?make={marque.lower()}"
                    f"&fuel=2,3"  # Diesel + Hybrid
                    f"&price=0-{prix_max}"
                    f"&km=0-{km_max}"
                    f"&lang=en"
                )
                
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                voitures_elements = soup.find_all('div', class_='result-item')
                
                for element in voitures_elements[:20]:
                    try:
                        titre = element.find('h2')
                        prix = element.find('span', class_='h3')
                        
                        if titre and prix:
                            voiture = {
                                'source': 'Mobile.de',
                                'pays': 'Allemagne',
                                'titre': titre.text.strip(),
                                'marque': marque,
                                'modele': titre.text.strip().split()[-1] if titre else "",
                                'prix_eur': float(prix.text.replace('€', '').replace('.', '').replace(',', '.').strip()),
                                'km': self._extraire_km(element.text),
                                'carburant': 'Diesel' if 'Diesel' in element.text else 'Hybride',
                                'url': element.find('a')['href'] if element.find('a') else "",
                                'description': element.text[:200],
                                'annee': self._extraire_annee(element.text),
                                'date_annonce': datetime.now()
                            }
                            resultats.append(voiture)
                    except Exception as e:
                        logger.warning(f"  ⚠️  Erreur parsing: {e}")
                        continue
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"  ❌ Mobile.de: {e}")
                continue
        
        if resultats:
            self._save_voitures(resultats)
        return resultats
    
    # ==================== HELPERS ====================
    def _extraire_annee(self, texte: str) -> int:
        """Extrait l'année du texte"""
        import re
        match = re.search(r'\b(20\d{2}|19\d{2})\b', texte)
        return int(match.group(1)) if match else 2020
    
    def _extraire_km(self, texte: str) -> int:
        """Extrait les km du texte"""
        import re
        match = re.search(r'(\d+[\.,]\d+|\d+)\s*(?:km|kms)', texte, re.IGNORECASE)
        if match:
            return int(match.group(1).replace('.', '').replace(',', ''))
        return 0
    
    def scraper_tous(self, marques: List[str], prix_max=25000, km_max=150000):
        """Scrape tous les sites"""
        logger.info("=" * 60)
        logger.info("🚗 DÉMARRAGE DU SCRAPING MULTI-SITES")
        logger.info("=" * 60)
        
        resultats_totaux = []
        
        resultats_totaux.extend(self.scraper_autoscout24(marques, prix_max, km_max))
        resultats_totaux.extend(self.scraper_leboncoin(marques, prix_max, km_max))
        resultats_totaux.extend(self.scraper_mobile_de(marques, prix_max, km_max))
        
        logger.info(f"\n✅ TOTAL: {len(resultats_totaux)} voitures trouvées\n")
        
        return resultats_totaux

if __name__ == "__main__":
    scraper = VoituresScraper()
    voitures = scraper.scraper_tous(
        marques=["Volkswagen", "Mercedes", "BMW", "Audi"],
        prix_max=25000,
        km_max=150000
    )
    
    df = pd.DataFrame(voitures)
    print(df[['source', 'marque', 'modele', 'prix_eur', 'km', 'pays']].head(20))
