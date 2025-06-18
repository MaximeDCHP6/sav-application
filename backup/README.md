# Système de Gestion des Tickets SAV

Ce projet est un système de gestion des tickets SAV (Service Après-Vente) développé avec Flask. Il permet de gérer les retours de produits, les remboursements et le suivi des clients.

## Fonctionnalités

- Gestion des utilisateurs (admin et utilisateurs standards)
- Création et suivi des tickets SAV
- Gestion des produits retournés
- Calcul automatique des remboursements
- Système de messagerie intégré
- Interface moderne et responsive

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_DOSSIER]
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialiser la base de données :
```bash
python init_db.py
```

5. Lancer l'application :
```bash
flask run
```

## Configuration

L'application utilise les variables d'environnement suivantes :
- `FLASK_APP` : Le fichier principal de l'application (app.py)
- `FLASK_ENV` : L'environnement (development/production)
- `SECRET_KEY` : La clé secrète pour les sessions
- `DATABASE_URL` : L'URL de la base de données

## Utilisation

1. Se connecter avec les identifiants par défaut :
   - Utilisateur : admin
   - Mot de passe : admin

2. Créer un nouveau ticket :
   - Remplir les informations du client
   - Ajouter les produits à retourner
   - Spécifier les frais de port et d'emballage

3. Suivre les tickets :
   - Voir l'état des tickets
   - Ajouter des messages
   - Gérer les remboursements

## Structure du Projet

```
.
├── app.py              # Application principale
├── models.py           # Modèles de données
├── routes.py           # Routes de l'application
├── init_db.py          # Script d'initialisation de la base de données
├── requirements.txt    # Dépendances du projet
├── templates/          # Templates HTML
│   ├── base.html
│   ├── create_ticket.html
│   ├── index.html
│   ├── login.html
│   └── view_ticket.html
└── static/            # Fichiers statiques
    ├── css/
    ├── js/
    └── img/
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 