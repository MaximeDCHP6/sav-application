import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("Test des imports...")

try:
    print("Import de settings...")
    from alder_sav.config.settings import LOG_CONFIG, APP_NAME, APP_VERSION
    print(f"APP_NAME: {APP_NAME}")
    print(f"APP_VERSION: {APP_VERSION}")
except Exception as e:
    print(f"Erreur lors de l'import de settings: {str(e)}")

try:
    print("\nImport de models...")
    from alder_sav.database.models import init_db
    print("init_db importé avec succès")
except Exception as e:
    print(f"Erreur lors de l'import de models: {str(e)}")

try:
    print("\nImport de main_window...")
    from alder_sav.ui.main_window import MainWindow
    print("MainWindow importé avec succès")
except Exception as e:
    print(f"Erreur lors de l'import de main_window: {str(e)}")

input("\nAppuyez sur Entrée pour quitter...") 