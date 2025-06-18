from flask import Flask
from extensions import db
from models import Product, ReceptionLog
from config import Config
from sqlalchemy import text, inspect

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def column_exists(table_name, column_name):
    """Vérifie si une colonne existe dans une table"""
    with db.engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_info({table_name})"))
        columns = result.fetchall()
        return any(col[1] == column_name for col in columns)

def migrate():
    with app.app_context():
        with db.engine.connect() as conn:
            # Ajouter la colonne quantity à la table product si elle n'existe pas
            if not column_exists('product', 'quantity'):
                conn.execute(text('ALTER TABLE product ADD COLUMN quantity INTEGER DEFAULT 1'))
                print("Colonne 'quantity' ajoutée à la table 'product'")
            else:
                print("Colonne 'quantity' existe déjà dans la table 'product'")
            
            # Ajouter la colonne quantity_received à la table reception_log si elle n'existe pas
            if not column_exists('reception_log', 'quantity_received'):
                conn.execute(text('ALTER TABLE reception_log ADD COLUMN quantity_received INTEGER DEFAULT 1'))
                print("Colonne 'quantity_received' ajoutée à la table 'reception_log'")
            else:
                print("Colonne 'quantity_received' existe déjà dans la table 'reception_log'")
            
            conn.commit()
        print("Migration terminée avec succès!")

if __name__ == '__main__':
    migrate() 