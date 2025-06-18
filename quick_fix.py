#!/usr/bin/env python3
"""
Script de correction rapide pour base.html
"""

def fix_base_html():
    """Corrige le fichier base.html en ajoutant le {% endif %} manquant"""
    
    try:
        # Lire le fichier
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Recherche du problème...")
        
        # Chercher la ligne avec "Données clients" dans la navbar
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Données clients' in line and 'nav-link' in line:
                print(f"📍 Trouvé 'Données clients' à la ligne {i+1}")
                
                # Chercher la fin du lien (</li>)
                for j in range(i, min(i+5, len(lines))):
                    if '</li>' in lines[j]:
                        print(f"📍 Fin du lien trouvée à la ligne {j+1}")
                        
                        # Vérifier la ligne suivante
                        if j+1 < len(lines):
                            next_line = lines[j+1].strip()
                            if '{% if current_user.is_admin %}' in next_line:
                                print("❌ {% endif %} manquant détecté!")
                                
                                # Insérer le {% endif %} manquant
                                lines.insert(j+1, '                    {% endif %}')
                                print("✅ {% endif %} ajouté!")
                                
                                # Sauvegarder le fichier
                                with open('templates/base.html', 'w', encoding='utf-8') as f:
                                    f.write('\n'.join(lines))
                                
                                print("✅ Fichier corrigé et sauvegardé!")
                                return True
                            elif '{% endif %}' in next_line:
                                print("✅ {% endif %} déjà présent")
                                return True
                        break
                break
        
        print("❌ Problème non détecté ou déjà corrigé")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Correction rapide de base.html")
    print("=" * 40)
    fix_base_html() 