#!/usr/bin/env python3
"""
Main entry point for Railway
Lance l'Agent IA de scraping/analyse des voitures
"""

import sys
import os

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer l'agent
from agent import main

if __name__ == "__main__":
    print("🚀 Lancement de l'Agent IA...")
    main()
    print("✅ Agent terminé!")
