from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_logistics = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, username, email, password, is_admin=False, is_logistics=False):
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.is_logistics = is_logistics
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, account_number, name, contact_name=None, contact_email=None, contact_phone=None, address=None):
        self.account_number = account_number
        self.name = name
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.address = address

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    return_type = db.Column(db.String(50), nullable=False)  # 'retour', 'echange', 'garantie'
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'in_progress', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    shipping_cost_refund = db.Column(db.Boolean, default=False)
    shipping_cost_amount = db.Column(db.Float)
    packaging_cost_refund = db.Column(db.Boolean, default=False)
    packaging_cost_amount = db.Column(db.Float)

    def __init__(self, ticket_number, client_id, status='en_attente', return_type='standard',
                 shipping_cost_refund=False, shipping_cost_amount=0.0,
                 packaging_cost_refund=False, packaging_cost_amount=0.0, notes=None):
        self.ticket_number = ticket_number
        self.client_id = client_id
        self.status = status
        self.return_type = return_type
        self.shipping_cost_refund = shipping_cost_refund
        self.shipping_cost_amount = shipping_cost_amount
        self.packaging_cost_refund = packaging_cost_refund
        self.packaging_cost_amount = packaging_cost_amount
        self.notes = notes

    @staticmethod
    def generate_ticket_number():
        # Obtenir le dernier ticket
        last_ticket = Ticket.query.order_by(Ticket.id.desc()).first()
        
        # Si aucun ticket n'existe, commencer à 1
        if not last_ticket:
            return "TKT2025-0001"
        
        # Extraire le numéro du dernier ticket
        try:
            last_number = int(last_ticket.ticket_number.split('-')[1])
        except (IndexError, ValueError):
            # Si le format n'est pas correct, commencer à 1
            return "TKT2025-0001"
        
        # Générer le nouveau numéro
        new_number = last_number + 1
        
        # Formater le numéro avec des zéros devant
        return f"TKT2025-{new_number:04d}"

    @property
    def total_refund(self):
        total = sum([p.refund_amount for p in self.products])
        if self.shipping_cost_refund:
            total += self.shipping_cost_amount or 0
        if self.packaging_cost_refund:
            total += self.packaging_cost_amount or 0
        return total

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_ref = db.Column(db.String(50), nullable=False)
    shipping_date = db.Column(db.Date)
    bl_number = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)

    def __init__(self, product_ref, quantity, unit_price, refund_amount, discount=0, shipping_date=None, bl_number=None, ticket_id=None):
        self.product_ref = product_ref
        self.quantity = quantity
        self.unit_price = unit_price
        self.refund_amount = refund_amount
        self.discount = discount
        self.shipping_date = shipping_date
        self.bl_number = bl_number
        self.ticket_id = ticket_id

class ReceptionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reception_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    quantity_received = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(50), nullable=False)  # 'bon', 'cassé', 'rayé', 'manquant', 'autre'
    notes = db.Column(db.Text)

    def __init__(self, ticket_id, product_id, user_id, quantity_received, condition, notes=None):
        self.ticket_id = ticket_id
        self.product_id = product_id
        self.user_id = user_id
        self.quantity_received = quantity_received
        self.condition = condition
        self.notes = notes

    @property
    def total_quantity_received(self):
        """Calcule la quantité totale reçue pour ce produit dans ce ticket"""
        return sum(log.quantity_received for log in self.product.receptions 
                  if log.ticket_id == self.ticket_id)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, content, ticket_id, user_id):
        self.content = content
        self.ticket_id = ticket_id
        self.user_id = user_id

# Relations
User.messages = db.relationship('Message', backref='user', lazy=True)
User.reception_logs = db.relationship('ReceptionLog', backref='user', lazy=True)

Client.tickets = db.relationship('Ticket', backref='client', lazy=True)

Ticket.products = db.relationship('Product', backref='ticket', lazy=True, cascade='all, delete-orphan')
Ticket.reception_logs = db.relationship('ReceptionLog', backref='ticket', lazy=True, cascade='all, delete-orphan')
Ticket.messages = db.relationship('Message', backref='ticket', lazy=True, cascade='all, delete-orphan')

Product.receptions = db.relationship('ReceptionLog', backref='product', lazy=True) 