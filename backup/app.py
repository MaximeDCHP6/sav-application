from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timezone
import os
from werkzeug.utils import secure_filename

from extensions import db, login_manager
from models import User, Client, Ticket, Product, Message, ReceptionLog

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'votre_clé_secrète_ici'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'

    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)

    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Routes
    @app.route('/')
    @login_required
    def index():
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        return render_template('index.html', tickets=tickets)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
            
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/manage_clients')
    @login_required
    def manage_clients():
        if not current_user.is_admin:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('index'))
        clients = Client.query.order_by(Client.name).all()
        return render_template('manage_clients.html', clients=clients)

    @app.route('/client/add', methods=['POST'])
    @login_required
    def add_client():
        if not current_user.is_admin:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('index'))
            
        account_number = request.form.get('account_number')
        if Client.query.filter_by(account_number=account_number).first():
            flash('Ce numéro de compte existe déjà', 'error')
            return redirect(url_for('manage_clients'))
            
        client = Client(
            account_number=account_number,
            name=request.form.get('name'),
            address=request.form.get('address'),
            contact_name=request.form.get('contact_name'),
            contact_email=request.form.get('contact_email'),
            contact_phone=request.form.get('contact_phone'),
            siret=request.form.get('siret')
        )
        
        try:
            db.session.add(client)
            db.session.commit()
            flash('Client ajouté avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du client: {str(e)}', 'error')
            
        return redirect(url_for('manage_clients'))

    @app.route('/client/<int:client_id>/edit', methods=['POST'])
    @login_required
    def edit_client(client_id):
        if not current_user.is_admin:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('index'))
            
        client = db.session.get(Client, client_id)
        if not client:
            flash('Client non trouvé', 'error')
            return redirect(url_for('manage_clients'))
            
        new_account = request.form.get('account_number')
        if new_account != client.account_number and Client.query.filter_by(account_number=new_account).first():
            flash('Ce numéro de compte existe déjà', 'error')
            return redirect(url_for('manage_clients'))
            
        try:
            client.account_number = new_account
            client.name = request.form.get('name')
            client.address = request.form.get('address')
            client.contact_name = request.form.get('contact_name')
            client.contact_email = request.form.get('contact_email')
            client.contact_phone = request.form.get('contact_phone')
            client.siret = request.form.get('siret')
            
            db.session.commit()
            flash('Client modifié avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification du client: {str(e)}', 'error')
            
        return redirect(url_for('manage_clients'))

    @app.route('/client/<int:client_id>/delete', methods=['POST'])
    @login_required
    def delete_client(client_id):
        if not current_user.is_admin:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('index'))
            
        client = db.session.get(Client, client_id)
        if not client:
            flash('Client non trouvé', 'error')
            return redirect(url_for('manage_clients'))
            
        if client.tickets:
            flash('Impossible de supprimer un client ayant des tickets', 'error')
            return redirect(url_for('manage_clients'))
            
        try:
            db.session.delete(client)
            db.session.commit()
            flash('Client supprimé avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la suppression du client: {str(e)}', 'error')
            
        return redirect(url_for('manage_clients'))

    @app.route('/api/client/<int:client_id>')
    @login_required
    def get_client(client_id):
        client = db.session.get(Client, client_id)
        if not client:
            return jsonify({'error': 'Client non trouvé'}), 404
        return jsonify({
            'id': client.id,
            'account_number': client.account_number,
            'name': client.name,
            'address': client.address,
            'contact_name': client.contact_name,
            'contact_email': client.contact_email,
            'contact_phone': client.contact_phone,
            'siret': client.siret
        })

    @app.route('/api/check-client/<account_number>')
    @login_required
    def check_client(account_number):
        client = Client.query.filter_by(account_number=account_number).first()
        if not client:
            return jsonify({'exists': False})
        return jsonify({
            'exists': True,
            'id': client.id,
            'name': client.name,
            'address': client.address,
            'contact_name': client.contact_name,
            'contact_email': client.contact_email,
            'contact_phone': client.contact_phone,
            'siret': client.siret
        })

    @app.route('/api/clients/search')
    def search_client():
        account_number = request.args.get('account_number', '')
        if not account_number:
            return jsonify({'error': 'Numéro de compte requis'}), 400

        client = Client.query.filter_by(account_number=account_number).first()
        if client:
            return jsonify({
                'client': {
                    'id': client.id,
                    'name': client.name,
                    'contact_name': client.contact_name,
                    'contact_email': client.contact_email,
                    'contact_phone': client.contact_phone,
                    'siret': client.siret,
                    'address': client.address
                }
            })
        return jsonify({'client': None})

    @app.route('/create_ticket', methods=['GET', 'POST'])
    @login_required
    def create_ticket():
        if request.method == 'POST':
            client_id = request.form.get('client_id')
            return_type = request.form.get('return_type')
            shipping_cost_refund = 'shipping_cost_refund' in request.form
            shipping_cost_amount = float(request.form.get('shipping_cost_amount') or 0)
            packaging_cost_refund = 'packaging_cost_refund' in request.form
            packaging_cost_amount = float(request.form.get('packaging_cost_amount') or 0)
            notes = request.form.get('notes')

            # Générer le numéro de ticket
            ticket_number = Ticket.generate_ticket_number()

            # Créer le ticket
            ticket = Ticket(
                ticket_number=ticket_number,
                client_id=client_id,
                user_id=current_user.id,
                return_type=return_type,
                shipping_cost_refund=shipping_cost_refund,
                shipping_cost_amount=shipping_cost_amount,
                packaging_cost_refund=packaging_cost_refund,
                packaging_cost_amount=packaging_cost_amount,
                notes=notes
            )

            db.session.add(ticket)
            db.session.flush()  # Pour obtenir l'ID du ticket

            # Gérer les produits
            product_refs = request.form.getlist('product_ref[]')
            shipping_dates = request.form.getlist('shipping_date[]')
            bl_numbers = request.form.getlist('bl_number[]')
            refund_amounts = request.form.getlist('refund_amount[]')
            discounts = request.form.getlist('discount[]')
            quantities = request.form.getlist('quantity[]')

            for i in range(len(product_refs)):
                if product_refs[i] and shipping_dates[i] and bl_numbers[i] and refund_amounts[i] and quantities[i]:
                    product = Product(
                        product_ref=product_refs[i],
                        shipping_date=datetime.strptime(shipping_dates[i], '%Y-%m-%d'),
                        bl_number=bl_numbers[i],
                        quantity=int(quantities[i]),
                        unit_price=float(refund_amounts[i]),
                        refund_amount=float(refund_amounts[i]),
                        discount=float(discounts[i] or 0),
                        ticket_id=ticket.id
                    )
                    db.session.add(product)

            try:
                db.session.commit()
                flash('Ticket créé avec succès!', 'success')
                return redirect(url_for('view_ticket', ticket_id=ticket.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de la création du ticket: {str(e)}', 'error')
                return redirect(url_for('create_ticket'))

        # GET request - afficher le formulaire
        clients = Client.query.all()
        return render_template('create_ticket.html', clients=clients)

    @app.route('/ticket/<int:ticket_id>')
    @login_required
    def view_ticket(ticket_id):
        ticket = db.session.get(Ticket, ticket_id)
        if ticket is None:
            return render_template('404.html'), 404
        return render_template('view_ticket.html', ticket=ticket)

    @app.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
    @login_required
    def delete_ticket(ticket_id):
        if not current_user.is_admin:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('index'))
        
        ticket = db.session.get(Ticket, ticket_id)
        if ticket is None:
            return render_template('404.html'), 404
            
        try:
            db.session.delete(ticket)
            db.session.commit()
            flash('Ticket supprimé avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la suppression du ticket: {str(e)}', 'error')
        
        return redirect(url_for('index'))

    @app.route('/ticket/<int:ticket_id>/message', methods=['POST'])
    @login_required
    def add_message(ticket_id):
        ticket = db.session.get(Ticket, ticket_id)
        if ticket is None:
            return render_template('404.html'), 404
            
        content = request.form.get('content')
        
        if content:
            message = Message(
                content=content,
                user_id=current_user.id,
                ticket_id=ticket.id
            )
            try:
                db.session.add(message)
                db.session.commit()
                flash('Message ajouté avec succès', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de l\'ajout du message: {str(e)}', 'error')
        
        return redirect(url_for('view_ticket', ticket_id=ticket.id))

    @app.route('/ticket/<int:ticket_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_ticket(ticket_id):
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            flash('Ticket non trouvé', 'error')
            return redirect(url_for('index'))
        
        if not current_user.is_admin:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            ticket.title = request.form['title']
            ticket.description = request.form['description']
            ticket.vehicle_registration = request.form['vehicle_registration']
            ticket.invoice_numbers = request.form['invoice_numbers']
            ticket.return_type = request.form['return_type']
            ticket.status = request.form['status']
            
            # Gestion des frais supplémentaires
            ticket.shipping_cost_refund = 'shipping_cost_refund' in request.form
            if ticket.shipping_cost_refund:
                ticket.shipping_cost_amount = float(request.form['shipping_cost_amount'])
            
            ticket.packaging_cost_refund = 'packaging_cost_refund' in request.form
            if ticket.packaging_cost_refund:
                ticket.packaging_cost_amount = float(request.form['packaging_cost_amount'])
            
            # Mise à jour des produits
            product_refs = request.form.getlist('product_ref[]')
            shipping_dates = request.form.getlist('shipping_date[]')
            bl_numbers = request.form.getlist('bl_number[]')
            refund_amounts = request.form.getlist('refund_amount[]')
            
            # Suppression des produits existants
            for product in ticket.products:
                db.session.delete(product)
            
            # Ajout des nouveaux produits
            for i in range(len(product_refs)):
                if product_refs[i] and shipping_dates[i] and bl_numbers[i] and refund_amounts[i]:
                    product = Product(
                        product_ref=product_refs[i],
                        shipping_date=datetime.strptime(shipping_dates[i], '%Y-%m-%d'),
                        bl_number=bl_numbers[i],
                        refund_amount=float(refund_amounts[i]),
                        ticket_id=ticket.id
                    )
                    db.session.add(product)
            
            db.session.commit()
            flash('Ticket mis à jour avec succès', 'success')
            return redirect(url_for('view_ticket', ticket_id=ticket.id))
        
        return render_template('edit_ticket.html', ticket=ticket)

    @app.route('/ticket/<int:ticket_id>/status', methods=['POST'])
    @login_required
    def update_ticket_status(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)
        if not current_user.is_admin and ticket.user_id != current_user.id:
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('index'))

        status = request.form.get('status')
        if status not in ['en_attente', 'valide', 'refuse']:
            flash('Statut invalide.', 'danger')
            return redirect(url_for('view_ticket', ticket_id=ticket.id))

        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Statut mis à jour avec succès.', 'success')
        return redirect(url_for('view_ticket', ticket_id=ticket.id))

    @app.route('/admin')
    @login_required
    def admin():
        if not current_user.is_admin:
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('index'))
        
        users = User.query.all()
        return render_template('admin.html', users=users)

    @app.route('/api/users', methods=['POST'])
    @login_required
    def create_user_api():
        if not current_user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403

        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400

        user = User(
            name=data['name'],
            email=data['email'],
            is_admin=data.get('is_admin', False)
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/api/users/<int:user_id>', methods=['GET'])
    @login_required
    def get_user_api(user_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403

        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        })

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @login_required
    def update_user_api(user_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403

        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if data.get('email') != user.email and User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400

        user.name = data['name']
        user.email = data['email']
        if data.get('password'):
            user.set_password(data['password'])
        user.is_admin = data.get('is_admin', False)
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    @login_required
    def delete_user_api(user_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403

        user = User.query.get_or_404(user_id)
        if user.is_admin:
            return jsonify({'error': 'Impossible de supprimer un administrateur'}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/logistics')
    @login_required
    def logistics():
        # Récupérer tous les tickets avec leurs produits et clients associés
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        return render_template('logistics.html', tickets=tickets)

    @app.route('/product/<int:product_id>/reception', methods=['GET', 'POST'])
    @login_required
    def product_reception(product_id):
        if not current_user.is_logistics and not current_user.is_admin:
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('index'))
        
        product = Product.query.get_or_404(product_id)
        
        if request.method == 'POST':
            status = request.form.get('status')
            condition = request.form.get('condition')
            notes = request.form.get('notes')
            
            # Gestion des photos
            photos = []
            if 'photos' in request.files:
                for photo in request.files.getlist('photos'):
                    if photo and allowed_file(photo.filename):
                        filename = secure_filename(photo.filename)
                        photo_path = os.path.join('uploads', 'reception', filename)
                        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], 'reception', filename))
                        photos.append(photo_path)
            
            reception_log = ReceptionLog(
                product_id=product.id,
                status=status,
                condition=condition,
                photos=','.join(photos) if photos else None,
                notes=notes,
                created_by=current_user.id
            )
            
            db.session.add(reception_log)
            db.session.commit()
            
            flash('Réception enregistrée avec succès.', 'success')
            return redirect(url_for('logistics'))
        
        return render_template('logistics/reception.html', product=product)

    @app.route('/receive_product', methods=['POST'])
    @login_required
    def receive_product():
        try:
            ticket_id = request.form.get('ticket_id')
            ticket = db.session.get(Ticket, ticket_id)
            if not ticket:
                flash('Ticket non trouvé', 'error')
                return redirect(url_for('logistics'))

            errors = []
            for product in ticket.products:
                quantity = request.form.get(f'quantity_{product.id}')
                condition = request.form.get(f'condition_{product.id}')
                notes = request.form.get(f'notes_{product.id}')
                
                if quantity and int(quantity) > 0:
                    try:
                        reception = ReceptionLog(
                            ticket_id=ticket.id,
                            product_id=product.id,
                            user_id=current_user.id,
                            quantity_received=int(quantity),
                            condition=condition,
                            notes=notes
                        )
                        db.session.add(reception)
                    except Exception as e:
                        errors.append(f"Erreur pour {product.product_ref} : {str(e)}")

            if errors:
                db.session.rollback()
                flash('Certains produits n\'ont pas pu être réceptionnés : ' + ', '.join(errors), 'warning')
            else:
                db.session.commit()
                flash('Réception(s) enregistrée(s) avec succès', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la réception : {str(e)}', 'error')

        return redirect(url_for('logistics'))

    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True) 