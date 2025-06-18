from app import db
from models import Product
from datetime import datetime

def upgrade():
    # Ajouter la colonne product_ref
    db.engine.execute('ALTER TABLE product ADD COLUMN product_ref VARCHAR(50)')
    
    # Mettre à jour les produits existants avec une référence unique
    products = Product.query.all()
    for product in products:
        product.product_ref = f"PRD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{product.id}"
    
    db.session.commit()
    
    # Ajouter la contrainte unique
    db.engine.execute('ALTER TABLE product ALTER COLUMN product_ref SET NOT NULL')
    db.engine.execute('ALTER TABLE product ADD CONSTRAINT product_ref_unique UNIQUE (product_ref)')

if __name__ == '__main__':
    upgrade() 