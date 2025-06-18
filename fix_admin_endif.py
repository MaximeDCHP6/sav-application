#!/usr/bin/env python3
"""
Script pour corriger le bloc {% if current_user.is_admin %} non fermé
"""

import os

def fix_admin_endif():
    """Corrige le bloc admin non fermé"""
    
    base_html_path = "templates/base.html"
    
    if not os.path.exists(base_html_path):
        print(f"❌ Fichier {base_html_path} non trouvé")
        return False
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified = False
    
    print("🔍 Recherche du bloc admin non fermé...")
    
    # Chercher la structure problématique
    for i, line in enumerate(lines):
        if '{% if current_user.is_admin %}' in line:
            print(f"📍 Bloc admin ouvert à la ligne {i+1}")
            
            # Chercher le bloc logistics qui suit
            for j in range(i+1, min(i+10, len(lines))):
                if '{% if current_user.is_logistics %}' in lines[j]:
                    print(f"📍 Bloc logistics trouvé à la ligne {j+1}")
                    
                    # Chercher la fin du bloc logistics
                    for k in range(j+1, min(j+25, len(lines))):
                        if '{% endif %}' in lines[k]:
                            print(f"📍 Fin du bloc logistics à la ligne {k+1}")
                            
                            # Vérifier la ligne suivante
                            if k+1 < len(lines) and '{% if current_user.is_admin %}' in lines[k+1]:
                                print("❌ Problème détecté : bloc admin non fermé!")
                                
                                # Insérer le {% endif %} manquant
                                lines.insert(k+1, '                    {% endif %}')
                                modified = True
                                print("✅ {% endif %} ajouté pour fermer le premier bloc admin!")
                                break
                    break
    
    if modified:
        # Sauvegarder le fichier
        with open(base_html_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Fichier corrigé et sauvegardé!")
        return True
    else:
        print("❌ Aucune modification nécessaire")
        return False

def verify_structure():
    """Vérifie la structure finale"""
    
    base_html_path = "templates/base.html"
    
    if not os.path.exists(base_html_path):
        return False
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    admin_if = content.count('{% if current_user.is_admin %}')
    logistics_if = content.count('{% if current_user.is_logistics %}')
    endif_count = content.count('{% endif %}')
    
    total_if = admin_if + logistics_if
    
    print(f"\n📊 Vérification finale:")
    print(f"   - Blocs {{% if current_user.is_admin %}}: {admin_if}")
    print(f"   - Blocs {{% if current_user.is_logistics %}}: {logistics_if}")
    print(f"   - Blocs {{% endif %}}: {endif_count}")
    print(f"   - Total if: {total_if}")
    
    if total_if == endif_count:
        print("✅ Structure équilibrée!")
        return True
    else:
        print(f"❌ Structure déséquilibrée! (différence: {total_if - endif_count})")
        return False

if __name__ == "__main__":
    print("🔧 Correction du bloc admin non fermé")
    print("=" * 50)
    
    if fix_admin_endif():
        verify_structure()
    else:
        print("💡 Vérification manuelle requise") 