from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from extensions import db
import os
from sqlalchemy import event
from sqlalchemy.orm import validates

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_logistics = db.Column(db.Boolean, default=False)
    is_accounting = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    
    messages = db.relationship('Message', backref='author', lazy=True)
    reception_logs = db.relationship('ReceptionLog', backref='user', lazy=True)
    attachments = db.relationship('Attachment', backref='user', lazy=True)
    
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

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        db.session.commit()

    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError('Email invalide')
        return email.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username) < 3:
            raise ValueError('Le nom d\'utilisateur doit contenir au moins 3 caractères')
        return username.lower()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    tickets = db.relationship('Ticket', backref='client', lazy=True)
    
    @validates('account_number')
    def validate_account_number(self, key, account_number):
        if not account_number or len(account_number) < 3:
            raise ValueError('Le numéro de compte doit contenir au moins 3 caractères')
        return account_number.upper()
    
    @validates('email')
    def validate_email(self, key, email):
        if email and '@' not in email:
            raise ValueError('Email invalide')
        return email.lower() if email else None

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    return_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='en_attente')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    shipping_cost_refund = db.Column(db.Boolean, default=False)
    shipping_cost_amount = db.Column(db.Float, default=0.0)
    packaging_cost_refund = db.Column(db.Boolean, default=False)
    packaging_cost_amount = db.Column(db.Float, default=0.0)
    fault_attribution = db.Column(db.String(50))
    return_reason = db.Column(db.String(100))
    return_reason_details = db.Column(db.Text)
    credit_note_number = db.Column(db.String(20))
    credit_note_date = db.Column(db.DateTime)
    credit_note_validated = db.Column(db.Boolean, default=False)
    credit_note_validated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    products = db.relationship('Product', backref='ticket', lazy=True, cascade='all, delete-orphan')
    reception_logs = db.relationship('ReceptionLog', backref='ticket', lazy=True)
    messages = db.relationship('Message', backref='ticket', lazy=True)
    attachments = db.relationship('Attachment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def generate_ticket_number(self):
        last_ticket = Ticket.query.order_by(Ticket.id.desc()).first()
        if last_ticket:
            last_number = int(last_ticket.ticket_number[3:])
            new_number = last_number + 1
        else:
            new_number = 1
        return f'TKT{new_number:06d}'
    
    @property
    def total_refund(self):
        total = 0
        if self.shipping_cost_refund:
            total += self.shipping_cost_amount
        if self.packaging_cost_refund:
            total += self.packaging_cost_amount
        for product in self.products:
            if product.refund_amount:
                total += product.refund_amount
        return total
    
    @validates('return_type')
    def validate_return_type(self, key, return_type):
        valid_types = ['retour_client', 'retour_magasin', 'retour_garantie']
        if return_type not in valid_types:
            raise ValueError('Type de retour invalide')
        return return_type
    
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['en_attente', 'valide', 'refuse']
        if status not in valid_statuses:
            raise ValueError('Statut invalide')
        return status

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    product_ref = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    receptions = db.relationship('ReceptionLog', backref='product', lazy=True)

    def __init__(self, name, price, ticket_id, description=None, product_ref=None):
        self.name = name
        self.price = price
        self.ticket_id = ticket_id
        self.description = description
        self.product_ref = product_ref or f"PRD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    @property
    def total_quantity(self):
        return 1  # Par défaut, chaque produit a une quantité de 1

    @property
    def total_received(self):
        return sum(log.quantity_received for log in self.receptions if log.status == 'reçu')

    def __repr__(self):
        return f'<Product {self.name}>'

class ReceptionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    quantity_received = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['reçu', 'refusé', 'en_attente']
        if status not in valid_statuses:
            raise ValueError('Statut invalide')
        return status

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    @validates('content')
    def validate_content(self, key, content):
        if not content or len(content.strip()) == 0:
            raise ValueError('Le message ne peut pas être vide')
        return content

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    @validates('filename', 'original_filename')
    def validate_filename(self, key, filename):
        if not filename or len(filename.strip()) == 0:
            raise ValueError('Le nom du fichier ne peut pas être vide')
        return filename
    
    @validates('file_size')
    def validate_file_size(self, key, file_size):
        if file_size is not None and file_size < 0:
            raise ValueError('La taille du fichier ne peut pas être négative')
        return file_size

# Événements pour la gestion des fichiers
@event.listens_for(Attachment, 'after_delete')
def delete_attachment_file(mapper, connection, target):
    try:
        file_path = os.path.join('uploads', str(target.ticket_id), target.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier {file_path}: {str(e)}")

# Événements pour la validation des données
@event.listens_for(Ticket, 'before_insert')
def set_ticket_number(mapper, connection, target):
    if not target.ticket_number:
        target.ticket_number = target.generate_ticket_number()

@event.listens_for(User, 'before_insert')
def set_user_defaults(mapper, connection, target):
    if not target.created_at:
        target.created_at = datetime.now(timezone.utc)

# Relations
User.messages = db.relationship('Message', backref='user', lazy=True)
User.reception_logs = db.relationship('ReceptionLog', backref='user', lazy=True)
User.attachments = db.relationship('Attachment', backref='user', lazy=True)

Client.tickets = db.relationship('Ticket', backref='client', lazy=True)

Ticket.products = db.relationship('Product', backref='ticket', lazy=True, cascade='all, delete-orphan')
Ticket.reception_logs = db.relationship('ReceptionLog', backref='ticket', lazy=True, cascade='all, delete-orphan')
Ticket.messages = db.relationship('Message', backref='ticket', lazy=True, cascade='all, delete-orphan')
Ticket.attachments = db.relationship('Attachment', backref='ticket', lazy=True, cascade='all, delete-orphan')
Ticket.credit_note_validator = db.relationship('User', foreign_keys=[Ticket.credit_note_validated_by], backref='validated_credit_notes')

Product.receptions = db.relationship('ReceptionLog', backref='product', lazy=True)

class UserAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='actions')
    action_type = db.Column(db.String(20))  # create, update, delete, login, logout
    module = db.Column(db.String(50))  # tickets, users, etc.
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action_type': self.action_type,
            'module': self.module,
            'details': self.details,
            'ip_address': self.ip_address
        }

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), default='ALDER')
    company_email = db.Column(db.String(100), default='contact@alder.fr')
    backup_frequency = db.Column(db.Integer, default=1)  # heures
    backup_retention = db.Column(db.Integer, default=30)  # jours
    notification_email = db.Column(db.String(100))
    notify_new_ticket = db.Column(db.Boolean, default=True)
    notify_status_change = db.Column(db.Boolean, default=True)
    notify_anomaly = db.Column(db.Boolean, default=True)
    session_timeout = db.Column(db.Integer, default=30)  # minutes
    max_login_attempts = db.Column(db.Integer, default=5)
    tickets_per_page = db.Column(db.Integer, default=25)
    date_format = db.Column(db.String(10), default='DD/MM/YYYY')

    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings 