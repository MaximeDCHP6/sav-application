# Application de Gestion des Retours Produits

Cette application permet de gérer les retours de produits, leur réception et leur suivi.

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
- Windows :
```bash
venv\Scripts\activate
```
- Linux/Mac :
```bash
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialiser la base de données :
```bash
python init_db.py
```

## Utilisation

1. Lancer l'application :
```bash
python app.py
```

2. Accéder à l'application dans votre navigateur :
```
http://localhost:5000
```

## Fonctionnalités

- Gestion des tickets de retour
- Suivi des produits
- Gestion des réceptions
- Système de messagerie interne
- Gestion des pièces jointes
- Interface d'administration 