#!/usr/bin/env python3
"""
Script pour corriger automatiquement le fichier base.html
en ajoutant le {% endif %} manquant pour le bloc current_user.is_logistics
"""

import os
import re

def fix_base_html():
    """Corrige le fichier base.html en ajoutant le {% endif %} manquant"""
    
    # Chemin du fichier base.html
    base_html_path = "templates/base.html"
    
    if not os.path.exists(base_html_path):
        print(f"❌ Fichier {base_html_path} non trouvé")
        return False
    
    # Lire le contenu du fichier
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Recherche du problème dans base.html...")
    
    # Chercher le pattern problématique
    pattern = r'(\s*<li class="nav-item">\s*<a class="nav-link" href="{{ url_for\(\'client_data\'\) }}">\s*<i class="fas fa-users me-2"></i>Données clients\s*</a>\s*</li>\s*)({% if current_user\.is_admin %})'
    
    if re.search(pattern, content):
        print("✅ Pattern trouvé, application de la correction...")
        
        # Remplacer le pattern
        replacement = r'\1                    {% endif %}\n\2'
        new_content = re.sub(pattern, replacement, content)
        
        # Sauvegarder le fichier
        with open(base_html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Correction appliquée avec succès!")
        return True
    else:
        print("❌ Pattern non trouvé. Vérification manuelle nécessaire.")
        return False

def verify_fix():
    """Vérifie que la correction a été appliquée correctement"""
    
    base_html_path = "templates/base.html"
    
    if not os.path.exists(base_html_path):
        print(f"❌ Fichier {base_html_path} non trouvé")
        return False
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Compter les blocs if et endif
    if_count = content.count('{% if current_user.is_logistics %}')
    endif_count = content.count('{% endif %}')
    
    print(f"📊 Statistiques:")
    print(f"   - Blocs {{% if current_user.is_logistics %}}: {if_count}")
    print(f"   - Blocs {{% endif %}}: {endif_count}")
    
    if if_count == endif_count:
        print("✅ Structure des blocs if/endif équilibrée!")
        return True
    else:
        print("❌ Structure des blocs if/endif déséquilibrée!")
        return False

if __name__ == "__main__":
    print("🔧 Script de correction du fichier base.html")
    print("=" * 50)
    
    # Appliquer la correction
    if fix_base_html():
        # Vérifier la correction
        verify_fix()
    else:
        print("❌ Échec de la correction automatique")
        print("💡 Vérification manuelle requise") 