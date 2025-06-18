import zipfile
import os
import shutil
from pathlib import Path

def create_project_zip():
    """Crée un ZIP du projet en excluant les fichiers problématiques"""
    
    # Dossier source
    source_dir = Path('.')
    
    # Nom du fichier ZIP
    zip_name = 'mon_programme.zip'
    
    # Fichiers et dossiers à exclure
    excludes = {
        'venv', '__pycache__', 'instance', 'uploads', 'backups', 'logs',
        '*.log', '*.pyc', '.git', '.gitignore', 'mon_programme.zip'
    }
    
    print(f"Création du ZIP: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclure les dossiers
            dirs[:] = [d for d in dirs if d not in excludes]
            
            for file in files:
                file_path = Path(root) / file
                
                # Vérifier si le fichier doit être exclu
                should_exclude = False
                for exclude in excludes:
                    if exclude.startswith('*'):
                        if file.endswith(exclude[1:]):
                            should_exclude = True
                            break
                    elif file == exclude:
                        should_exclude = True
                        break
                
                if should_exclude:
                    print(f"Exclu: {file_path}")
                    continue
                
                try:
                    # Ajouter le fichier au ZIP
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
                    print(f"Ajouté: {arcname}")
                except Exception as e:
                    print(f"Erreur avec {file_path}: {e}")
    
    print(f"\nZIP créé avec succès: {zip_name}")
    print(f"Taille: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    create_project_zip() 