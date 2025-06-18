from extensions import db
from models import Product

def migrate():
    # Ajouter la colonne quantity à la table product
    with db.engine.connect() as conn:
        conn.execute('ALTER TABLE product ADD COLUMN quantity INTEGER DEFAULT 1')
        conn.commit()

if __name__ == '__main__':
    migrate() 