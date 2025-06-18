from app import create_app, db
from models import User, Client, Ticket, Product, Message
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Supprimer toutes les tables existantes
        db.drop_all()
        
        # Créer toutes les tables
        db.create_all()
        
        # Vérifier si un utilisateur admin existe déjà
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Créer un utilisateur admin
            admin = User(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur admin créé avec succès !")
        else:
            print("L'utilisateur admin existe déjà.")
        
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
            account_number='C0001',
            name='Client Test',
            address='123 rue de Paris',
            email='client@test.com',
            phone='0123456789'
        )
        db.session.add(test_client)
        db.session.commit()
        print("Client de test créé avec succès !")
        
        # Créer un ticket de test
        test_ticket = Ticket(
            ticket_number='TKT000001',
            client_id=test_client.id,
            return_type='retour_client',
            status='en_attente',
            shipping_cost_refund=True,
            shipping_cost_amount=10.0,
            packaging_cost_refund=True,
            packaging_cost_amount=5.0
        )
        db.session.add(test_ticket)
        db.session.commit()
        print("Ticket de test créé avec succès !")
        
        # Créer un produit de test
        test_product = Product(
            name='Produit de test',
            price=100.0,
            ticket_id=test_ticket.id,
            description='Description du produit de test'
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