from app import create_app, db
from models import User, Client, Ticket, Product, Message
from datetime import datetime, timezone

def init_db():
    app = create_app()
    with app.app_context():
        # Supprimer toutes les tables existantes
        db.drop_all()
        
        # Créer toutes les tables
        db.create_all()
        
        # Créer un utilisateur admin
        admin = User(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Créer un utilisateur logistique
        logistics = User(
            username='logistics',
            email='logistics@example.com',
            password='logistics123',
            is_logistics=True
        )
        logistics.set_password('logistics123')
        db.session.add(logistics)
        
        # Créer un client de test
        test_client = Client(
            account_number='CLI001',
            name='Client Test',
            contact_name='Contact Test',
            contact_email='contact@test.com',
            contact_phone='0123456789',
            address='123 rue du test, 75000 Paris'
        )
        db.session.add(test_client)
        db.session.commit()
        
        # Créer un ticket de test
        test_ticket = Ticket(
            ticket_number=f'TKT{datetime.now(timezone.utc).year}0001',
            client_id=test_client.id,
            status='open',
            return_type='standard',
            shipping_cost_refund=True,
            shipping_cost_amount=10.0,
            packaging_cost_refund=True,
            packaging_cost_amount=5.0,
            notes='Ticket de test'
        )
        db.session.add(test_ticket)
        db.session.commit()
        
        # Créer un produit de test
        test_product = Product(
            product_ref='REF001',
            shipping_date=datetime.now().date(),
            bl_number='BL001',
            quantity=1,
            unit_price=100.0,
            refund_amount=100.0,
            ticket_id=test_ticket.id
        )
        db.session.add(test_product)
        
        # Créer un message de test
        test_message = Message(
            content='Message de test',
            ticket_id=test_ticket.id,
            user_id=admin.id
        )
        db.session.add(test_message)
        
        # Sauvegarder les changements
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès!") 