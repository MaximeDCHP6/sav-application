import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from config.settings import AUTH_CONFIG

class AuthManager:
    """Gestionnaire d'authentification"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.auth_config = AUTH_CONFIG
    
    def create_user(self, username, password, email, role):
        """Création d'un utilisateur"""
        try:
            # Vérification de l'existence de l'utilisateur
            if self.db_session.query(User).filter_by(username=username).first():
                return False, "Un utilisateur avec ce nom existe déjà"
            
            # Création du sel
            salt = secrets.token_hex(16)
            
            # Hachage du mot de passe
            hashed_password = self._hash_password(password, salt)
            
            # Création de l'utilisateur
            user = User(
                username=username,
                password=hashed_password,
                salt=salt,
                email=email,
                role=role,
                is_active=True,
                date_creation=datetime.now()
            )
            
            self.db_session.add(user)
            self.db_session.commit()
            
            return True, "Utilisateur créé avec succès"
        
        except Exception as e:
            self.db_session.rollback()
            return False, f"Erreur lors de la création de l'utilisateur: {str(e)}"
    
    def authenticate_user(self, username, password):
        """Authentification d'un utilisateur"""
        try:
            # Récupération de l'utilisateur
            user = self.db_session.query(User).filter_by(username=username).first()
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            if not user.is_active:
                return False, "Compte désactivé"
            
            # Vérification du mot de passe
            hashed_password = self._hash_password(password, user.salt)
            if hashed_password != user.password:
                return False, "Mot de passe incorrect"
            
            # Génération du token
            token = self._generate_token(user)
            
            return True, {
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }
        
        except Exception as e:
            return False, f"Erreur lors de l'authentification: {str(e)}"
    
    def change_password(self, user_id, old_password, new_password):
        """Changement de mot de passe"""
        try:
            # Récupération de l'utilisateur
            user = self.db_session.query(User).get(user_id)
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            # Vérification de l'ancien mot de passe
            hashed_old_password = self._hash_password(old_password, user.salt)
            if hashed_old_password != user.password:
                return False, "Ancien mot de passe incorrect"
            
            # Création du nouveau sel
            new_salt = secrets.token_hex(16)
            
            # Hachage du nouveau mot de passe
            hashed_new_password = self._hash_password(new_password, new_salt)
            
            # Mise à jour de l'utilisateur
            user.password = hashed_new_password
            user.salt = new_salt
            user.date_modification = datetime.now()
            
            self.db_session.commit()
            
            return True, "Mot de passe modifié avec succès"
        
        except Exception as e:
            self.db_session.rollback()
            return False, f"Erreur lors du changement de mot de passe: {str(e)}"
    
    def reset_password(self, email):
        """Réinitialisation du mot de passe"""
        try:
            # Récupération de l'utilisateur
            user = self.db_session.query(User).filter_by(email=email).first()
            
            if not user:
                return False, "Aucun utilisateur trouvé avec cet email"
            
            # Génération d'un mot de passe temporaire
            temp_password = secrets.token_urlsafe(8)
            
            # Création du nouveau sel
            new_salt = secrets.token_hex(16)
            
            # Hachage du mot de passe temporaire
            hashed_temp_password = self._hash_password(temp_password, new_salt)
            
            # Mise à jour de l'utilisateur
            user.password = hashed_temp_password
            user.salt = new_salt
            user.date_modification = datetime.now()
            
            self.db_session.commit()
            
            # Envoi du mot de passe temporaire par email
            subject = "Réinitialisation de votre mot de passe"
            body = f"""
            Votre mot de passe a été réinitialisé.
            
            Mot de passe temporaire: {temp_password}
            
            Veuillez vous connecter et changer votre mot de passe.
            """
            
            # TODO: Envoyer l'email
            
            return True, "Mot de passe réinitialisé avec succès"
        
        except Exception as e:
            self.db_session.rollback()
            return False, f"Erreur lors de la réinitialisation du mot de passe: {str(e)}"
    
    def verify_token(self, token):
        """Vérification d'un token"""
        try:
            # Décodage du token
            payload = jwt.decode(
                token,
                self.auth_config['jwt_secret'],
                algorithms=[self.auth_config['jwt_algorithm']]
            )
            
            # Vérification de l'expiration
            if datetime.fromtimestamp(payload['exp']) < datetime.now():
                return False, "Token expiré"
            
            # Récupération de l'utilisateur
            user = self.db_session.query(User).get(payload['user_id'])
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            if not user.is_active:
                return False, "Compte désactivé"
            
            return True, {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        
        except jwt.InvalidTokenError:
            return False, "Token invalide"
        except Exception as e:
            return False, f"Erreur lors de la vérification du token: {str(e)}"
    
    def _hash_password(self, password, salt):
        """Hachage d'un mot de passe"""
        return hashlib.sha256(
            (password + salt).encode()
        ).hexdigest()
    
    def _generate_token(self, user):
        """Génération d'un token JWT"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(
                days=self.auth_config['token_expiration_days']
            )
        }
        
        return jwt.encode(
            payload,
            self.auth_config['jwt_secret'],
            algorithm=self.auth_config['jwt_algorithm']
        )
    
    def get_user_permissions(self, user_id):
        """Récupération des permissions d'un utilisateur"""
        try:
            # Récupération de l'utilisateur
            user = self.db_session.query(User).get(user_id)
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            # Récupération des permissions selon le rôle
            permissions = self.auth_config['role_permissions'].get(user.role, [])
            
            return True, permissions
        
        except Exception as e:
            return False, f"Erreur lors de la récupération des permissions: {str(e)}"
    
    def check_permission(self, user_id, permission):
        """Vérification d'une permission"""
        try:
            # Récupération des permissions
            success, result = self.get_user_permissions(user_id)
            
            if not success:
                return False, result
            
            # Vérification de la permission
            if permission not in result:
                return False, "Permission non accordée"
            
            return True, "Permission accordée"
        
        except Exception as e:
            return False, f"Erreur lors de la vérification de la permission: {str(e)}"
    
    def update_user(self, user_id, data):
        """Mise à jour d'un utilisateur"""
        try:
            # Récupération de l'utilisateur
            user = self.db_session.query(User).get(user_id)
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            # Mise à jour des champs
            for field, value in data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.date_modification = datetime.now()
            
            self.db_session.commit()
            
            return True, "Utilisateur mis à jour avec succès"
        
        except Exception as e:
            self.db_session.rollback()
            return False, f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"
    
    def deactivate_user(self, user_id):
        """Désactivation d'un utilisateur"""
        try:
            # Récupération de l'utilisateur
            user = self.db_session.query(User).get(user_id)
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            # Désactivation
            user.is_active = False
            user.date_modification = datetime.now()
            
            self.db_session.commit()
            
            return True, "Utilisateur désactivé avec succès"
        
        except Exception as e:
            self.db_session.rollback()
            return False, f"Erreur lors de la désactivation de l'utilisateur: {str(e)}"
    
    def activate_user(self, user_id):
        """Activation d'un utilisateur"""
        try:
            # Récupération de l'utilisateur
            user = self.db_session.query(User).get(user_id)
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            # Activation
            user.is_active = True
            user.date_modification = datetime.now()
            
            self.db_session.commit()
            
            return True, "Utilisateur activé avec succès"
        
        except Exception as e:
            self.db_session.rollback()
            return False, f"Erreur lors de l'activation de l'utilisateur: {str(e)}" 