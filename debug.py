import sys
import os
import traceback
from pathlib import Path

# Ajouter le répertoire courant au PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    print("Démarrage du débogage...")
    
    # Créer les répertoires nécessaires
    data_dir = current_dir / "alder_sav" / "data"
    logs_dir = current_dir / "logs"
    for directory in [data_dir, logs_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("Importation des modules...")
    from alder_sav.main import main
    
    print("Lancement de l'application...")
    main()
    
except Exception as e:
    print("\nERREUR CRITIQUE:")
    print(f"Type d'erreur: {type(e).__name__}")
    print(f"Message d'erreur: {str(e)}")
    print("\nTraceback complet:")
    traceback.print_exc()
    
    # Attendre que l'utilisateur appuie sur une touche avant de fermer
    input("\nAppuyez sur Entrée pour quitter...") 