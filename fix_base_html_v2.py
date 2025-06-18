#!/usr/bin/env python3
"""
Script de correction amélioré pour le fichier base.html
Gère différentes variantes de la structure HTML
"""

import os
import re

def analyze_base_html():
    """Analyse le fichier base.html pour identifier les problèmes"""
    
    base_html_path = "templates/base.html"
    
    if not os.path.exists(base_html_path):
        print(f"❌ Fichier {base_html_path} non trouvé")
        return None
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Analyse du fichier base.html...")
    
    # Compter les différents types de blocs
    logistics_if = content.count('{% if current_user.is_logistics %}')
    admin_if = content.count('{% if current_user.is_admin %}')
    endif_count = content.count('{% endif %}')
    
    print(f"📊 Statistiques:")
    print(f"   - {{% if current_user.is_logistics %}}: {logistics_if}")
    print(f"   - {{% if current_user.is_admin %}}: {admin_if}")
    print(f"   - {{% endif %}}: {endif_count}")
    
    # Chercher la section problématique
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Données clients' in line:
            print(f"\n📍 Ligne {i+1} - 'Données clients' trouvé:")
            print(f"   {line.strip()}")
            
            # Voir les lignes suivantes
            for j in range(i+1, min(i+6, len(lines))):
                print(f"   {j+1}: {lines[j].strip()}")
            
            # Voir les lignes précédentes
            for j in range(max(0, i-5), i):
                print(f"   {j+1}: {lines[j].strip()}")
            break
    
    return content

def fix_base_html_manual():
    """Correction manuelle basée sur l'analyse"""
    
    base_html_path = "templates/base.html"
    
    if not os.path.exists(base_html_path):
        print(f"❌ Fichier {base_html_path} non trouvé")
        return False
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified = False
    
    print("\n🔧 Application de la correction manuelle...")
    
    # Chercher la ligne avec "Données clients"
    for i, line in enumerate(lines):
        if 'Données clients' in line:
            print(f"📍 Trouvé 'Données clients' à la ligne {i+1}")
            
            # Chercher la fin du lien (</li>)
            for j in range(i, min(i+5, len(lines))):
                if '</li>' in lines[j]:
                    print(f"📍 Fin du lien trouvée à la ligne {j+1}")
                    
                    # Vérifier si le {% endif %} manque
                    next_line_idx = j + 1
                    if next_line_idx < len(lines):
                        next_line = lines[next_line_idx].strip()
                        if '{% if current_user.is_admin %}' in next_line:
                            print("❌ {% endif %} manquant détecté!")
                            
                            # Insérer le {% endif %} manquant
                            lines.insert(next_line_idx, '                    {% endif %}')
                            modified = True
                            print("✅ {% endif %} ajouté!")
                            break
                        elif '{% endif %}' in next_line:
                            print("✅ {% endif %} déjà présent")
                            break
                    break
    
    if modified:
        # Sauvegarder le fichier
        with open(base_html_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Fichier corrigé et sauvegardé!")
        return True
    else:
        print("❌ Aucune modification nécessaire ou problème non détecté")
        return False

def verify_structure():
    """Vérifie la structure finale"""
    
    base_html_path = "templates/base.html"
    
    if not os.path.exists(base_html_path):
        return False
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    logistics_if = content.count('{% if current_user.is_logistics %}')
    admin_if = content.count('{% if current_user.is_admin %}')
    endif_count = content.count('{% endif %}')
    
    total_if = logistics_if + admin_if
    
    print(f"\n📊 Vérification finale:")
    print(f"   - Blocs if totaux: {total_if}")
    print(f"   - Blocs endif: {endif_count}")
    
    if total_if == endif_count:
        print("✅ Structure équilibrée!")
        return True
    else:
        print(f"❌ Structure déséquilibrée! (différence: {total_if - endif_count})")
        return False

if __name__ == "__main__":
    print("🔧 Script de correction amélioré pour base.html")
    print("=" * 60)
    
    # Analyser le fichier
    content = analyze_base_html()
    
    if content:
        # Appliquer la correction
        if fix_base_html_manual():
            # Vérifier la structure
            verify_structure()
        else:
            print("\n💡 Correction manuelle requise")
            print("Vérifiez la structure des blocs if/endif dans le fichier") 