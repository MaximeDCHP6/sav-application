from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime
from app import app, db
from models import User, Ticket, Product, Message, Client

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template('index.html', tickets=tickets)

@app.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        # Récupérer le client
        client_account = request.form.get('client_account')
        client = Client.query.filter_by(account_number=client_account).first()
        
        if not client:
            flash('Client non trouvé', 'error')
            return redirect(url_for('create_ticket'))
        
        # Créer le ticket
        ticket = Ticket(
            ticket_number=f'TKT-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
            title=request.form.get('title'),
            description=request.form.get('description'),
            user_id=current_user.id,
            client_id=client.id,
            vehicle_registration=request.form.get('vehicle_registration'),
            invoice_numbers=request.form.get('invoice_numbers'),
            return_type=request.form.get('return_type'),
            shipping_cost_refund=bool(request.form.get('shipping_cost_refund')),
            shipping_cost_amount=float(request.form.get('shipping_cost_amount', 0) or 0),
            packaging_cost_refund=bool(request.form.get('packaging_cost_refund')),
            packaging_cost_amount=float(request.form.get('packaging_cost_amount', 0) or 0)
        )
        
        # Ajouter les produits
        product_refs = request.form.getlist('product_ref[]')
        shipping_dates = request.form.getlist('shipping_date[]')
        bl_numbers = request.form.getlist('bl_number[]')
        refund_amounts = request.form.getlist('refund_amount[]')
        
        for i in range(len(product_refs)):
            if product_refs[i] and shipping_dates[i] and bl_numbers[i] and refund_amounts[i]:
                product = Product(
                    reference=product_refs[i],
                    shipping_date=datetime.strptime(shipping_dates[i], '%Y-%m-%d').date(),
                    bl_number=bl_numbers[i],
                    refund_amount=float(refund_amounts[i])
                )
                ticket.products.append(product)
        
        try:
            db.session.add(ticket)
            db.session.commit()
            flash('Ticket créé avec succès', 'success')
            return redirect(url_for('view_ticket', ticket_id=ticket.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du ticket: {str(e)}', 'error')
            return redirect(url_for('create_ticket'))
    
    return render_template('create_ticket.html')

@app.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('view_ticket.html', ticket=ticket)

@app.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    if not current_user.is_admin:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('index'))
    
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket supprimé avec succès', 'success')
    return redirect(url_for('index'))

@app.route('/ticket/<int:ticket_id>/message', methods=['POST'])
@login_required
def add_message(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    content = request.form.get('content')
    
    if content:
        message = Message(
            content=content,
            user_id=current_user.id,
            ticket_id=ticket.id
        )
        db.session.add(message)
        db.session.commit()
        flash('Message ajouté avec succès', 'success')
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    users = db.session.query(User).all()
    return render_template('admin.html', users=users)

@app.route('/admin/user/add', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if db.session.query(User).filter_by(username=username).first():
        flash('Ce nom d\'utilisateur existe déjà.', 'danger')
        return redirect(url_for('admin'))
    
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    flash('Utilisateur créé avec succès.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/user/edit', methods=['POST'])
@login_required
def edit_user():
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    user = db.session.get(User, int(user_id))
    if not user:
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('admin'))
    
    # Vérifier si le nouveau nom d'utilisateur existe déjà
    existing_user = db.session.query(User).filter_by(username=username).first()
    if existing_user and existing_user.id != int(user_id):
        flash('Ce nom d\'utilisateur existe déjà.', 'danger')
        return redirect(url_for('admin'))
    
    user.username = username
    if password:  # Ne changer le mot de passe que si un nouveau est fourni
        user.set_password(password)
    user.role = role
    
    db.session.commit()
    flash('Utilisateur modifié avec succès.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/user/delete', methods=['POST'])
@login_required
def delete_user():
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    user_id = request.form.get('user_id')
    user = db.session.get(User, int(user_id))
    if not user:
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('admin'))
    
    # Empêcher la suppression de l'utilisateur actuel
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('admin'))
    
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès.', 'success')
    return redirect(url_for('admin'))

@app.route('/clients')
@login_required
def manage_clients():
    clients = Client.query.order_by(Client.name).all()
    return render_template('manage_clients.html', clients=clients)

@app.route('/client/add', methods=['POST'])
@login_required
def add_client():
    if not current_user.is_admin:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('index'))
    
    # Vérifier si le numéro de compte existe déjà
    existing_client = Client.query.filter_by(account_number=request.form.get('account_number')).first()
    if existing_client:
        flash('Ce numéro de compte existe déjà', 'danger')
        return redirect(url_for('manage_clients'))
    
    client = Client(
        account_number=request.form.get('account_number'),
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
        flash('Erreur lors de l\'ajout du client', 'danger')
    
    return redirect(url_for('manage_clients'))

@app.route('/client/<int:client_id>/edit', methods=['POST'])
@login_required
def edit_client(client_id):
    if not current_user.is_admin:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('index'))
    
    client = Client.query.get_or_404(client_id)
    
    # Vérifier si le nouveau numéro de compte existe déjà
    if client.account_number != request.form.get('account_number'):
        existing_client = Client.query.filter_by(account_number=request.form.get('account_number')).first()
        if existing_client:
            flash('Ce numéro de compte existe déjà', 'danger')
            return redirect(url_for('manage_clients'))
    
    client.account_number = request.form.get('account_number')
    client.name = request.form.get('name')
    client.address = request.form.get('address')
    client.contact_name = request.form.get('contact_name')
    client.contact_email = request.form.get('contact_email')
    client.contact_phone = request.form.get('contact_phone')
    client.siret = request.form.get('siret')
    
    try:
        db.session.commit()
        flash('Client modifié avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la modification du client', 'danger')
    
    return redirect(url_for('manage_clients'))

@app.route('/client/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    if not current_user.is_admin:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('index'))
    
    client = Client.query.get_or_404(client_id)
    
    # Vérifier si le client a des tickets
    if client.tickets:
        flash('Impossible de supprimer ce client car il a des tickets associés', 'danger')
        return redirect(url_for('manage_clients'))
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Client supprimé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression du client', 'danger')
    
    return redirect(url_for('manage_clients'))

@app.route('/api/client/<int:client_id>')
@login_required
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify({
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
    if client:
        return jsonify({
            'exists': True,
            'client': {
                'name': client.name,
                'address': client.address,
                'contact_name': client.contact_name,
                'contact_phone': client.contact_phone,
                'contact_email': client.contact_email
            }
        })
    return jsonify({'exists': False}) 