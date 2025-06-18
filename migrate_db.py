from flask import Flask
from extensions import db
from models import Product, ReceptionLog
from config import Config
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def migrate():
    with app.app_context():
        # Ajouter la colonne quantity à la table product
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE product ADD COLUMN quantity INTEGER DEFAULT 1'))
            conn.commit()
            # Ajouter la colonne quantity_received à la table reception_log
            conn.execute(text('ALTER TABLE reception_log ADD COLUMN quantity_received INTEGER DEFAULT 1'))
            conn.commit()
        print("Migration terminée avec succès!")

if __name__ == '__main__':
    migrate() 