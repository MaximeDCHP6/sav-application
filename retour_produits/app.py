from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app, Response, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timezone, timedelta, time
import os
from werkzeug.utils import secure_filename
import csv
from io import StringIO
from fpdf import FPDF
import logging
from functools import wraps
from io import BytesIO

from extensions import db, login_manager
from models import User, Client, Ticket, Product, Message, ReceptionLog, Attachment
from notifications import init_mail, notify_new_ticket, notify_status_change, notify_anomaly
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    init_mail(app)
    
    # Décorateur pour limiter les tentatives de connexion
    def login_required_with_attempts(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                attempts = session.get('login_attempts', 0)
                if attempts >= app.config['MAX_LOGIN_ATTEMPTS']:
                    flash('Trop de tentatives de connexion. Veuillez réessayer plus tard.', 'danger')
                    return redirect(url_for('login'))
                return login_required(f)(*args, **kwargs)
            return f(*args, **kwargs)
        return decorated_function
    
    # Décorateur pour vérifier les permissions
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                flash('Accès non autorisé', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Décorateur pour journaliser les actions
    def log_action(action_type):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    result = f(*args, **kwargs)
                    if current_user.is_authenticated:
                        app.logger.info(
                            f"Action: {action_type} | User: {current_user.username} | "
                            f"IP: {request.remote_addr} | Path: {request.path}"
                        )
                    return result
                except Exception as e:
                    app.logger.error(
                        f"Error in {action_type} | User: {current_user.username if current_user.is_authenticated else 'Anonymous'} | "
                        f"IP: {request.remote_addr} | Path: {request.path} | Error: {str(e)}"
                    )
                    raise
            return decorated_function
        return decorator
    
    # Fonction pour valider les fichiers
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    # Fonction pour nettoyer les fichiers temporaires
    def cleanup_temp_files():
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        app.logger.error(f"Error cleaning up temp file {file_path}: {str(e)}")
    
    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.now(timezone.utc)
            db.session.commit()
    
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Routes
    @app.route('/')
    @login_required_with_attempts
    @log_action('view_index')
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
                session['login_attempts'] = 0
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                attempts = session.get('login_attempts', 0)
                session['login_attempts'] = attempts + 1
                flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
            
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    @log_action('logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/manage_clients')
    @admin_required
    def manage_clients():
        clients = Client.query.order_by(Client.name).all()
        return render_template('manage_clients.html', clients=clients)

    @app.route('/add_client', methods=['POST'])
    @login_required
    def add_client():
        try:
            client = Client(
                name=request.form.get('name'),
                account_number=request.form.get('account_number'),
                email=request.form.get('contact_email'),
                phone=request.form.get('contact_phone'),
                address=request.form.get('address')
            )
            db.session.add(client)
            db.session.commit()
            flash('Client ajouté avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du client: {str(e)}', 'error')
        return redirect(url_for('manage_clients'))

    @app.route('/client/<int:client_id>/edit', methods=['POST'])
    @admin_required
    def edit_client(client_id):
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
    @admin_required
    def delete_client(client_id):
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
    @admin_required
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
    @admin_required
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
                    'contact': client.contact,
                    'email': client.email,
                    'phone': client.phone,
                    'address': client.address
                }
            })
        return jsonify({'client': None})

    @app.route('/create_ticket', methods=['GET', 'POST'])
    @admin_required
    def create_ticket():
        if request.method == 'POST':
            try:
                # Récupération des données du formulaire
                client_id = request.form.get('client_id')
                return_type = request.form.get('return_type')
                fault_attribution = request.form.get('fault_attribution')
                return_reason = request.form.get('return_reason')
                return_reason_details = request.form.get('return_reason_details')
                
                # Création du ticket
                ticket = Ticket(
                    client_id=client_id,
                    return_type=return_type,
                    fault_attribution=fault_attribution,
                    return_reason=return_reason,
                    return_reason_details=return_reason_details
                )
                ticket.ticket_number = ticket.generate_ticket_number()
                
                # Gestion des frais de transport
                if request.form.get('shipping_cost_refund'):
                    ticket.shipping_cost_refund = True
                    ticket.shipping_cost_amount = float(request.form.get('shipping_cost_amount', 0))
                
                # Gestion des frais d'emballage
                if request.form.get('packaging_cost_refund'):
                    ticket.packaging_cost_refund = True
                    ticket.packaging_cost_amount = float(request.form.get('packaging_cost_amount', 0))
                
                db.session.add(ticket)
                db.session.flush()  # Pour obtenir l'ID du ticket
                
                # Gestion des produits
                product_refs = request.form.getlist('product_ref[]')
                shipping_dates = request.form.getlist('shipping_date[]')
                bl_numbers = request.form.getlist('bl_number[]')
                refund_amounts = request.form.getlist('refund_amount[]')
                discounts = request.form.getlist('discount[]')
                quantities = request.form.getlist('quantity[]')
                
                for i in range(len(product_refs)):
                    if product_refs[i] and shipping_dates[i] and bl_numbers[i] and refund_amounts[i] and quantities[i]:
                        product = Product(
                            name=product_refs[i],
                            price=float(refund_amounts[i]),
                            ticket_id=ticket.id,
                            description=f"BL: {bl_numbers[i]}, Date d'expédition: {shipping_dates[i]}, Quantité: {quantities[i]}",
                            product_ref=product_refs[i]
                        )
                        db.session.add(product)
                
                # Gestion des fichiers joints
                if 'attachments[]' in request.files:
                    files = request.files.getlist('attachments[]')
                    for file in files:
                        if file and file.filename:
                            # Générer un nom de fichier unique
                            filename = secure_filename(file.filename)
                            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                            
                            # Créer le dossier uploads s'il n'existe pas
                            upload_dir = os.path.join(app.root_path, 'uploads', str(ticket.id))
                            os.makedirs(upload_dir, exist_ok=True)
                            
                            # Sauvegarder le fichier
                            file_path = os.path.join(upload_dir, unique_filename)
                            file.save(file_path)
                            
                            # Créer l'entrée dans la base de données
                            attachment = Attachment(
                                filename=unique_filename,
                                original_filename=filename,
                                file_type=file.content_type,
                                file_size=os.path.getsize(file_path),
                                uploaded_by=current_user.id,
                                ticket_id=ticket.id
                            )
                            db.session.add(attachment)
                
                db.session.commit()
                
                # Notification de création de ticket
                notify_new_ticket(ticket)
                
                flash('Ticket créé avec succès !', 'success')
                return redirect(url_for('view_ticket', ticket_id=ticket.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de la création du ticket : {str(e)}', 'danger')
                return redirect(url_for('create_ticket'))
        
        return render_template('create_ticket.html')

    @app.route('/ticket/<int:ticket_id>')
    @admin_required
    def view_ticket(ticket_id):
        ticket = db.session.get(Ticket, ticket_id)
        if ticket is None:
            return render_template('404.html'), 404
        return render_template('view_ticket.html', ticket=ticket)

    @app.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
    @admin_required
    def delete_ticket(ticket_id):
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
    @admin_required
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
    @admin_required
    def edit_ticket(ticket_id):
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            flash('Ticket non trouvé', 'error')
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
            
            # Notification de changement de statut
            if ticket.status != request.form['status']:
                notify_status_change(ticket, ticket.status)
            
            # Vérification d'anomalies
            if ticket.refund_amount and float(ticket.refund_amount) > 1000:
                notify_anomaly(
                    ticket,
                    'Montant élevé',
                    f'Le montant remboursé ({ticket.refund_amount} €) est supérieur à 1000 €'
                )
            
            flash('Ticket mis à jour avec succès', 'success')
            return redirect(url_for('view_ticket', ticket_id=ticket.id))
        
        return render_template('edit_ticket.html', ticket=ticket)

    @app.route('/ticket/<int:ticket_id>/status', methods=['POST'])
    @admin_required
    def update_ticket_status(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)
        status = request.form.get('status')
        if status not in ['en_attente', 'valide', 'refuse']:
            flash('Statut invalide.', 'danger')
            return redirect(url_for('view_ticket', ticket_id=ticket.id))

        ticket.status = status
        ticket.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        # Notification de changement de statut
        notify_status_change(ticket, ticket.status)

        flash('Statut mis à jour avec succès.', 'success')
        return redirect(url_for('view_ticket', ticket_id=ticket.id))

    @app.route('/admin')
    @admin_required
    def admin():
        users = User.query.all()
        return render_template('admin.html', users=users)

    @app.route('/api/users', methods=['POST'])
    @admin_required
    def create_user_api():
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
    @admin_required
    def get_user_api(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        })

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @admin_required
    def update_user_api(user_id):
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
    @admin_required
    def delete_user_api(user_id):
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            return jsonify({'error': 'Impossible de supprimer un administrateur'}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/logistics')
    @admin_required
    def logistics():
        # Récupérer tous les tickets avec leurs produits et clients associés
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        return render_template('logistics.html', tickets=tickets)

    @app.route('/product/<int:product_id>/reception', methods=['GET', 'POST'])
    @admin_required
    def product_reception(product_id):
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
    @admin_required
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

    @app.route('/attachment/<int:attachment_id>/download')
    @admin_required
    def download_attachment(attachment_id):
        attachment = Attachment.query.get_or_404(attachment_id)
        file_path = os.path.join(app.root_path, 'uploads', str(attachment.ticket_id), attachment.filename)
        
        if not os.path.exists(file_path):
            flash('Le fichier n\'existe plus.', 'error')
            return redirect(url_for('view_ticket', ticket_id=attachment.ticket_id))
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=attachment.original_filename
        )

    @app.route('/attachment/<int:attachment_id>/delete', methods=['POST'])
    @admin_required
    def delete_attachment(attachment_id):
        attachment = Attachment.query.get_or_404(attachment_id)
        file_path = os.path.join(app.root_path, 'uploads', str(attachment.ticket_id), attachment.filename)
        
        try:
            # Supprimer le fichier physique
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Supprimer l'entrée dans la base de données
            db.session.delete(attachment)
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # Filtres pour les templates
    @app.template_filter('fault_label')
    def fault_label(value):
        labels = {
            'erreur_alder': 'Erreur ALDER',
            'erreur_client': 'Erreur client',
            'erreur_transporteur': 'Erreur transporteur',
            'erreur_fournisseur': 'Erreur fournisseur'
        }
        return labels.get(value, value)

    @app.template_filter('reason_label')
    def reason_label(value):
        labels = {
            'erreur_client': 'Erreur client',
            'litige_transport': 'Litige transport',
            'non_conforme': 'Non conforme',
            'retard': 'Retard',
            'erreur_alder': 'Erreur ALDER'
        }
        return labels.get(value, value)

    @app.template_filter('status_color')
    def status_color(value):
        colors = {
            'en_attente': 'warning',
            'en_cours': 'info',
            'termine': 'success',
            'valide': 'success',
            'refuse': 'danger'
        }
        return colors.get(value, 'secondary')

    @app.template_filter('status_display')
    def status_display(value):
        displays = {
            'en_attente': 'En attente',
            'en_cours': 'En cours',
            'termine': 'Terminé',
            'valide': 'Validé',
            'refuse': 'Refusé'
        }
        return displays.get(value, value)

    @app.template_filter('return_type_display')
    def return_type_display(value):
        displays = {
            'retour_client': 'Retour client',
            'retour_magasin': 'Retour magasin',
            'retour_garantie': 'Retour garantie'
        }
        return displays.get(value, value)

    @app.route('/accounting')
    @login_required
    def accounting():
        try:
            # Récupérer les données de comptabilité
            tickets = Ticket.query.all()
            total_amount = sum(ticket.total_amount for ticket in tickets if ticket.total_amount)
            paid_amount = sum(ticket.total_amount for ticket in tickets if ticket.total_amount and ticket.status == 'paye')
            pending_amount = total_amount - paid_amount

            # Regrouper par client
            client_totals = {}
            for ticket in tickets:
                if ticket.client_id and ticket.total_amount:
                    if ticket.client_id not in client_totals:
                        client_totals[ticket.client_id] = {
                            'total': 0,
                            'paid': 0,
                            'pending': 0
                        }
                    client_totals[ticket.client_id]['total'] += ticket.total_amount
                    if ticket.status == 'paye':
                        client_totals[ticket.client_id]['paid'] += ticket.total_amount
                    else:
                        client_totals[ticket.client_id]['pending'] += ticket.total_amount

            # Récupérer les informations des clients
            clients = Client.query.filter(Client.id.in_(client_totals.keys())).all()
            client_data = []
            for client in clients:
                if client.id in client_totals:
                    client_data.append({
                        'name': client.name,
                        'total': client_totals[client.id]['total'],
                        'paid': client_totals[client.id]['paid'],
                        'pending': client_totals[client.id]['pending']
                    })

            return render_template('accounting.html',
                                 total_amount=total_amount,
                                 paid_amount=paid_amount,
                                 pending_amount=pending_amount,
                                 clients=client_data)
        except Exception as e:
            flash(f'Erreur lors de la récupération des données comptables : {str(e)}', 'error')
            return render_template('accounting.html',
                                 total_amount=0,
                                 paid_amount=0,
                                 pending_amount=0,
                                 clients=[])

    @app.route('/accounting/search')
    @admin_required
    def accounting_search():
        # Récupérer les paramètres de recherche
        ticket_number = request.args.get('ticket_number', '')
        client = request.args.get('client', '')
        date = request.args.get('date', '')
        status = request.args.get('status', '')
        
        # Construire la requête
        query = Ticket.query.join(Client)
        
        if ticket_number:
            query = query.filter(Ticket.ticket_number.ilike(f'%{ticket_number}%'))
        if client:
            query = query.filter(Client.name.ilike(f'%{client}%'))
        if date:
            query = query.filter(db.func.date(Ticket.created_at) == date)
        if status:
            if status == 'validated':
                query = query.filter(Ticket.credit_note_validated == True)
            elif status == 'pending':
                query = query.filter(Ticket.credit_note_validated == False)
        
        # Exécuter la requête
        tickets = query.order_by(Ticket.created_at.desc()).all()
        
        # Formater les résultats
        results = []
        for ticket in tickets:
            results.append({
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'client_name': ticket.client.name,
                'created_at': ticket.created_at.strftime('%d/%m/%Y'),
                'total_refund': ticket.total_refund,
                'credit_note_number': ticket.credit_note_number,
                'credit_note_date': ticket.credit_note_date.strftime('%d/%m/%Y') if ticket.credit_note_date else None,
                'credit_note_validated': ticket.credit_note_validated
            })
        
        return jsonify({'tickets': results})

    @app.route('/accounting/credit-note', methods=['POST'])
    @admin_required
    def add_credit_note():
        try:
            ticket_id = request.form.get('ticket_id')
            credit_note_number = request.form.get('credit_note_number')
            credit_note_date = request.form.get('credit_note_date')
            
            if not all([ticket_id, credit_note_number, credit_note_date]):
                return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires'}), 400
            
            ticket = Ticket.query.get_or_404(ticket_id)
            
            # Vérifier si l'avoir n'existe pas déjà
            existing_ticket = Ticket.query.filter_by(credit_note_number=credit_note_number).first()
            if existing_ticket and existing_ticket.id != ticket.id:
                return jsonify({'success': False, 'message': 'Ce numéro d\'avoir existe déjà'}), 400
            
            # Mettre à jour le ticket
            ticket.credit_note_number = credit_note_number
            ticket.credit_note_date = datetime.strptime(credit_note_date, '%Y-%m-%d').date()
            ticket.credit_note_validated = True
            ticket.credit_note_validated_by = current_user.id
            ticket.credit_note_validated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/client-data')
    @admin_required
    def client_data():
        return render_template('client_data.html')

    @app.route('/client-data/search')
    @admin_required
    def client_data_search():
        account_number = request.args.get('account_number', '')
        client_name = request.args.get('client_name', '')
        
        query = Client.query
        
        if account_number:
            query = query.filter(Client.account_number.ilike(f'%{account_number}%'))
        if client_name:
            query = query.filter(Client.name.ilike(f'%{client_name}%'))
        
        clients = query.all()
        
        return jsonify({
            'clients': [{
                'id': client.id,
                'account_number': client.account_number,
                'name': client.name,
                'email': client.email,
                'phone': client.phone
            } for client in clients]
        })

    @app.route('/client-data/<int:client_id>')
    @login_required
    def client_data_details(client_id):
        client = Client.query.get_or_404(client_id)
        tickets = Ticket.query.filter_by(client_id=clientid).all()
        
        # Calculer les statistiques
        total_credit_notes = sum(ticket.total_refund for ticket in tickets)
        validated_credit_notes = sum(ticket.total_refund for ticket in tickets if ticket.credit_note_validated)
        pending_credit_notes = sum(ticket.total_refund for ticket in tickets if not ticket.credit_note_validated)
        total_tickets = len(tickets)
        
        # Calculer l'évolution des avoirs
        evolution = {
            'labels': [],
            'validated': [],
            'pending': []
        }
        
        # Grouper les tickets par date
        tickets_by_date = {}
        for ticket in tickets:
            date_str = ticket.created_at.strftime('%Y-%m-%d')
            if date_str not in tickets_by_date:
                tickets_by_date[date_str] = {'validated': 0, 'pending': 0}
            if ticket.credit_note_validated:
                tickets_by_date[date_str]['validated'] += ticket.total_refund
            else:
                tickets_by_date[date_str]['pending'] += ticket.total_refund
        
        # Trier les dates
        sorted_dates = sorted(tickets_by_date.keys())
        evolution['labels'] = sorted_dates
        evolution['validated'] = [tickets_by_date[date]['validated'] for date in sorted_dates]
        evolution['pending'] = [tickets_by_date[date]['pending'] for date in sorted_dates]
        
        # Calculer la répartition par type de retour
        return_types = {
            'S': sum(1 for ticket in tickets if ticket.return_type == 'S'),
            'R': sum(1 for ticket in tickets if ticket.return_type == 'R'),
            'C': sum(1 for ticket in tickets if ticket.return_type == 'C')
        }
        
        return jsonify({
            'client': {
                'id': client.id,
                'account_number': client.account_number,
                'name': client.name,
                'email': client.email,
                'phone': client.phone
            },
            'stats': {
                'totalCreditNotes': total_credit_notes,
                'validatedCreditNotes': validated_credit_notes,
                'pendingCreditNotes': pending_credit_notes,
                'totalTickets': total_tickets
            },
            'evolution': evolution,
            'returnTypes': return_types,
            'tickets': [{
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'created_at': ticket.created_at.strftime('%d/%m/%Y'),
                'return_type': ticket.return_type,
                'status': ticket.status,
                'total_refund': ticket.total_refund
            } for ticket in tickets]
        })

    @app.route('/client-data/<int:client_id>', methods=['PUT'])
    @login_required
    def update_client(client_id):
        try:
            client = Client.query.get_or_404(client_id)
            data = request.get_json()
            
            client.name = data['name']
            client.email = data['email']
            client.phone = data['phone']
            
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/dashboard/data')
    @login_required
    def dashboard_data():
        try:
            # Récupération des statistiques
            total_tickets = Ticket.query.count()
            pending_tickets = Ticket.query.filter_by(status='en_attente').count()
            validated_tickets = Ticket.query.filter_by(status='valide').count()
            refused_tickets = Ticket.query.filter_by(status='refuse').count()
            
            # Calcul du montant total des avoirs validés
            total_credit_notes = db.session.query(db.func.sum(Ticket.total_refund)).filter(Ticket.status == 'valide').scalar() or 0
            
            # Récupération des tickets récents
            recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
            recent_tickets_data = [{
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'client_name': ticket.client.name,
                'status': ticket.status,
                'created_at': ticket.created_at.strftime('%d/%m/%Y %H:%M')
            } for ticket in recent_tickets]
            
            # Récupération des statistiques par type de retour
            return_types = db.session.query(
                Ticket.return_type,
                db.func.count(Ticket.id)
            ).group_by(Ticket.return_type).all()
            
            return_types_data = {
                'labels': [rt[0] for rt in return_types],
                'data': [rt[1] for rt in return_types]
            }
            
            return jsonify({
                'total_tickets': total_tickets,
                'pending_tickets': pending_tickets,
                'validated_tickets': validated_tickets,
                'refused_tickets': refused_tickets,
                'total_credit_notes': float(total_credit_notes),
                'recent_tickets': recent_tickets_data,
                'return_types': return_types_data
            })
        except Exception as e:
            app.logger.error(f"Erreur lors de la récupération des données du tableau de bord: {str(e)}")
            return jsonify({'error': 'Une erreur est survenue'}), 500

    @app.route('/api/tickets/search', methods=['POST'])
    @login_required
    def search_tickets():
        try:
            # Récupération des paramètres de recherche
            page = request.form.get('page', 1, type=int)
            per_page = request.form.get('per_page', 10, type=int)
            
            # Construction de la requête de base
            query = Ticket.query.join(Client)
            
            # Filtres sur les informations client
            account_number = request.form.get('account_number')
            if account_number:
                query = query.filter(Client.account_number.ilike(f'%{account_number}%'))
            
            client_name = request.form.get('client_name')
            if client_name:
                query = query.filter(Client.name.ilike(f'%{client_name}%'))
            
            client_email = request.form.get('client_email')
            if client_email:
                query = query.filter(Client.email.ilike(f'%{client_email}%'))
            
            # Filtres sur les informations ticket
            ticket_number = request.form.get('ticket_number')
            if ticket_number:
                query = query.filter(Ticket.ticket_number.ilike(f'%{ticket_number}%'))
            
            status = request.form.getlist('status')
            if status:
                query = query.filter(Ticket.status.in_(status))
            
            return_type = request.form.getlist('return_type')
            if return_type:
                query = query.filter(Ticket.return_type.in_(return_type))
            
            # Filtres supplémentaires
            fault_attribution = request.form.get('fault_attribution')
            if fault_attribution:
                query = query.filter(Ticket.fault_attribution == fault_attribution)
            
            return_reason = request.form.get('return_reason')
            if return_reason:
                query = query.filter(Ticket.return_reason == return_reason)
            
            has_attachments = request.form.get('has_attachments')
            if has_attachments:
                query = query.filter(Ticket.attachments.any())
            
            # Filtres de date
            date_range = request.form.get('date_range')
            if date_range:
                today = datetime.now().date()
                
                if date_range == 'today':
                    query = query.filter(
                        Ticket.created_at >= datetime.combine(today, time.min),
                        Ticket.created_at <= datetime.combine(today, time.max)
                    )
                elif date_range == 'yesterday':
                    yesterday = today - timedelta(days=1)
                    query = query.filter(
                        Ticket.created_at >= datetime.combine(yesterday, time.min),
                        Ticket.created_at <= datetime.combine(yesterday, time.max)
                    )
                elif date_range == 'last_7_days':
                    seven_days_ago = today - timedelta(days=7)
                    query = query.filter(
                        Ticket.created_at >= datetime.combine(seven_days_ago, time.min),
                        Ticket.created_at <= datetime.combine(today, time.max)
                    )
                elif date_range == 'last_30_days':
                    thirty_days_ago = today - timedelta(days=30)
                    query = query.filter(
                        Ticket.created_at >= datetime.combine(thirty_days_ago, time.min),
                        Ticket.created_at <= datetime.combine(today, time.max)
                    )
                elif date_range == 'this_month':
                    first_day = today.replace(day=1)
                    query = query.filter(
                        Ticket.created_at >= datetime.combine(first_day, time.min),
                        Ticket.created_at <= datetime.combine(today, time.max)
                    )
                elif date_range == 'last_month':
                    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
                    last_day_last_month = today.replace(day=1) - timedelta(days=1)
                    query = query.filter(
                        Ticket.created_at >= datetime.combine(first_day_last_month, time.min),
                        Ticket.created_at <= datetime.combine(last_day_last_month, time.max)
                    )
            else:
                # Utilisation des dates personnalisées
                start_date = request.form.get('start_date')
                end_date = request.form.get('end_date')
                
                if start_date:
                    query = query.filter(Ticket.created_at >= datetime.combine(
                        datetime.strptime(start_date, '%Y-%m-%d').date(),
                        time.min
                    ))
                    
                if end_date:
                    query = query.filter(Ticket.created_at <= datetime.combine(
                        datetime.strptime(end_date, '%Y-%m-%d').date(),
                        time.max
                    ))
            
            # Tri et pagination
            query = query.order_by(Ticket.created_at.desc())
            pagination = query.paginate(page=page, per_page=per_page)
            
            # Préparation des résultats
            tickets = []
            for ticket in pagination.items:
                tickets.append({
                    'id': ticket.id,
                    'ticket_number': ticket.ticket_number,
                    'client_name': ticket.client.name,
                    'account_number': ticket.client.account_number,
                    'return_type': ticket.return_type,
                    'status': ticket.status,
                    'created_at': ticket.created_at.isoformat(),
                    'total_refund': ticket.total_refund
                })
            
            return jsonify({
                'tickets': tickets,
                'current_page': page,
                'total_pages': pagination.pages,
                'total_tickets': pagination.total
            })
            
        except Exception as e:
            app.logger.error(f"Erreur lors de la recherche des tickets: {str(e)}")
            return jsonify({'error': 'Une erreur est survenue lors de la recherche'}), 500

    @app.route('/api/tickets/export/csv', methods=['POST'])
    @login_required
    def export_tickets_csv():
        try:
            # Réutilisation des filtres de recherche
            query = Ticket.query.join(Client)
            
            # Application des mêmes filtres que la recherche
            # ... (code de filtrage identique à la route search_tickets)
            
            tickets = query.order_by(Ticket.created_at.desc()).all()
            
            # Création du fichier CSV
            output = StringIO()
            writer = csv.writer(output)
            
            # En-têtes
            writer.writerow([
                'N° Ticket',
                'Client',
                'N° Compte',
                'Type retour',
                'Statut',
                'Date création',
                'Montant total',
                'Attribution faute',
                'Motif retour'
            ])
            
            # Données
            for ticket in tickets:
                writer.writerow([
                    ticket.ticket_number,
                    ticket.client.name,
                    ticket.client.account_number,
                    ticket.return_type,
                    ticket.status,
                    ticket.created_at.strftime('%d/%m/%Y %H:%M'),
                    f"{ticket.total_refund:.2f} €",
                    ticket.fault_attribution,
                    ticket.return_reason
                ])
            
            output.seek(0)
            return Response(
                output,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename=tickets_export.csv'
                }
            )
            
        except Exception as e:
            app.logger.error(f"Erreur lors de l'export CSV: {str(e)}")
            return jsonify({'error': 'Une erreur est survenue lors de l\'export'}), 500

    @app.route('/api/tickets/export/pdf', methods=['POST'])
    @login_required
    def export_tickets_pdf():
        try:
            # Réutilisation des filtres de recherche
            query = Ticket.query.join(Client)
            
            # Application des mêmes filtres que la recherche
            # ... (code de filtrage identique à la route search_tickets)
            
            tickets = query.order_by(Ticket.created_at.desc()).all()
            
            # Création du PDF
            pdf = FPDF()
            pdf.add_page()
            
            # En-tête
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Export des tickets', 0, 1, 'C')
            pdf.ln(10)
            
            # Tableau
            pdf.set_font('Arial', 'B', 10)
            headers = [
                'N° Ticket',
                'Client',
                'Type',
                'Statut',
                'Date',
                'Montant'
            ]
            
            # Largeurs des colonnes
            col_widths = [30, 40, 30, 30, 30, 30]
            
            # En-têtes du tableau
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
            pdf.ln()
            
            # Données
            pdf.set_font('Arial', '', 9)
            for ticket in tickets:
                pdf.cell(col_widths[0], 10, ticket.ticket_number, 1)
                pdf.cell(col_widths[1], 10, ticket.client.name, 1)
                pdf.cell(col_widths[2], 10, ticket.return_type, 1)
                pdf.cell(col_widths[3], 10, ticket.status, 1)
                pdf.cell(col_widths[4], 10, ticket.created_at.strftime('%d/%m/%Y'), 1)
                pdf.cell(col_widths[5], 10, f"{ticket.total_refund:.2f} €", 1)
                pdf.ln()
            
            # Génération du PDF
            output = BytesIO()
            pdf.output(output)
            output.seek(0)
            
            return Response(
                output,
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': 'attachment; filename=tickets_export.pdf'
                }
            )
            
        except Exception as e:
            app.logger.error(f"Erreur lors de l'export PDF: {str(e)}")
            return jsonify({'error': 'Une erreur est survenue lors de l\'export'}), 500

    @app.route('/actions')
    @login_required
    def actions():
        if not current_user.is_admin:
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('index'))

        # Récupérer les paramètres de filtrage
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user', '')
        action_type = request.args.get('action_type', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        # Construire la requête
        query = UserAction.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if action_type:
            query = query.filter_by(action_type=action_type)
        
        if date_from:
            query = query.filter(UserAction.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
        
        if date_to:
            query = query.filter(UserAction.timestamp <= datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1))

        # Exécuter la requête avec pagination
        pagination = query.order_by(UserAction.timestamp.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'actions': [action.to_dict() for action in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @app.route('/actions-page')
    @login_required
    def actions_page():
        if not current_user.is_admin:
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('index'))
        
        users = User.query.all()
        return render_template('actions.html', users=users)

    # Fonction utilitaire pour logger les actions utilisateurs
    def log_user_action(action_type, module, details, user=None):
        if user is None:
            user = current_user
        action = UserAction(
            user_id=user.id if user else None,
            action_type=action_type,
            module=module,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(action)
        db.session.commit()

    @app.route('/settings')
    @admin_required
    def settings_page():
        settings = Settings.get_settings()
        return render_template('settings.html', settings=settings)

    @app.route('/settings', methods=['POST'])
    @admin_required
    def update_settings():
        settings = Settings.get_settings()
        settings.company_name = request.form.get('company_name')
        settings.company_email = request.form.get('company_email')
        settings.backup_frequency = int(request.form.get('backup_frequency'))
        settings.backup_retention = int(request.form.get('backup_retention'))
        settings.notification_email = request.form.get('notification_email')
        settings.notify_new_ticket = bool(request.form.get('notify_new_ticket'))
        settings.notify_status_change = bool(request.form.get('notify_status_change'))
        settings.notify_anomaly = bool(request.form.get('notify_anomaly'))
        settings.session_timeout = int(request.form.get('session_timeout'))
        settings.max_login_attempts = int(request.form.get('max_login_attempts'))
        settings.tickets_per_page = int(request.form.get('tickets_per_page'))
        settings.date_format = request.form.get('date_format')
        
        db.session.commit()
        flash('Paramètres mis à jour avec succès', 'success')
        return redirect(url_for('settings_page'))

    @app.route('/logs')
    @login_required
    def logs():
        try:
            # Essayer différents encodages
            encodings = ['utf-8', 'latin-1', 'cp1252']
            logs = []
            
            for encoding in encodings:
                try:
                    with open('app.log', 'r', encoding=encoding) as f:
                        logs = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue
            
            # Nettoyer les logs et les formater
            logs = [log.strip() for log in logs if log.strip()]
            return render_template('logs.html', logs=logs)
        except FileNotFoundError:
            flash('Aucun fichier de log trouvé', 'warning')
            return render_template('logs.html', logs=[])
        except Exception as e:
            flash(f'Erreur lors de la lecture des logs : {str(e)}', 'error')
            return render_template('logs.html', logs=[])

    @app.route('/statistics')
    @admin_required
    def statistics():
        # Statistiques de base
        total_tickets = Ticket.query.count()
        total_clients = Client.query.count()
        total_products = Product.query.count()
        
        # Statistiques par statut
        status_stats = db.session.query(
            Ticket.status, 
            db.func.count(Ticket.id)
        ).group_by(Ticket.status).all()
        
        return render_template('statistics.html',
            total_tickets=total_tickets,
            total_clients=total_clients,
            total_products=total_products,
            status_stats=status_stats
        )

    @app.route('/ticket/<int:ticket_id>/product/<int:product_id>/status', methods=['POST'])
    @admin_required
    def update_product_status(ticket_id, product_id):
        ticket = db.session.get(Ticket, ticket_id)
        product = db.session.get(Product, product_id)
        
        if not ticket or not product:
            flash('Ticket ou produit non trouvé', 'error')
            return redirect(url_for('logistics'))
            
        quantity = int(request.form.get(f'quantity_{product_id}', 1))
        
        if quantity <= 0:
            flash('La quantité doit être supérieure à 0', 'error')
            return redirect(url_for('logistics'))
            
        try:
            # Créer un nouveau log de réception
            log = ReceptionLog(
                ticket_id=ticket_id,
                product_id=product_id,
                user_id=current_user.id,
                status='reçu',
                quantity_received=quantity,
                notes=request.form.get('notes', '')
            )
            
            db.session.add(log)
            db.session.commit()
            
            flash('Produit marqué comme reçu avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour du statut: {str(e)}', 'error')
            
        return redirect(url_for('logistics'))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True) 