from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from alder_sav.database.models.user import User, Role, Permission
from alder_sav.utils.exceptions import UserError

class UserManager:
    """Gestionnaire des utilisateurs et des permissions"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        role_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Crée un nouvel utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            email: Adresse email
            role_id: ID du rôle
            first_name: Prénom (optionnel)
            last_name: Nom de famille (optionnel)
            
        Returns:
            Utilisateur créé
            
        Raises:
            UserError: Si l'utilisateur existe déjà ou si le rôle n'existe pas
        """
        # Vérifier si l'utilisateur existe déjà
        if self.session.query(User).filter(User.username == username).first():
            raise UserError(f"L'utilisateur {username} existe déjà")
        
        # Vérifier si le rôle existe
        role = self.session.query(Role).get(role_id)
        if not role:
            raise UserError(f"Le rôle {role_id} n'existe pas")
        
        # Créer l'utilisateur
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            role_id=role_id,
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.now(),
            is_active=True
        )
        
        self.session.add(user)
        self.session.commit()
        
        return user
    
    def get_user(self, user_id: int) -> User:
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Utilisateur
            
        Raises:
            UserError: Si l'utilisateur n'existe pas
        """
        user = self.session.query(User).get(user_id)
        if not user:
            raise UserError(f"L'utilisateur {user_id} n'existe pas")
        return user
    
    def get_user_by_username(self, username: str) -> User:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            Utilisateur
            
        Raises:
            UserError: Si l'utilisateur n'existe pas
        """
        user = self.session.query(User).filter(User.username == username).first()
        if not user:
            raise UserError(f"L'utilisateur {username} n'existe pas")
        return user
    
    def update_user(
        self,
        user_id: int,
        data: dict
    ) -> User:
        """
        Met à jour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            data: Données à mettre à jour
            
        Returns:
            Utilisateur mis à jour
            
        Raises:
            UserError: Si l'utilisateur n'existe pas
        """
        user = self.get_user(user_id)
        
        # Mettre à jour les champs
        for key, value in data.items():
            if key == 'password':
                user.password_hash = generate_password_hash(value)
            elif key == 'role_id':
                role = self.session.query(Role).get(value)
                if not role:
                    raise UserError(f"Le rôle {value} n'existe pas")
                user.role_id = value
            elif hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.now()
        self.session.commit()
        
        return user
    
    def delete_user(self, user_id: int) -> None:
        """
        Supprime un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Raises:
            UserError: Si l'utilisateur n'existe pas
        """
        user = self.get_user(user_id)
        self.session.delete(user)
        self.session.commit()
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            Utilisateur authentifié ou None
        """
        try:
            user = self.get_user_by_username(username)
            if user.is_active and check_password_hash(user.password_hash, password):
                return user
        except UserError:
            pass
        return None
    
    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change le mot de passe d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            
        Raises:
            UserError: Si l'utilisateur n'existe pas ou si le mot de passe actuel est incorrect
        """
        user = self.get_user(user_id)
        
        if not check_password_hash(user.password_hash, current_password):
            raise UserError("Mot de passe actuel incorrect")
        
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.now()
        self.session.commit()
    
    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ) -> Role:
        """
        Crée un nouveau rôle.
        
        Args:
            name: Nom du rôle
            description: Description du rôle (optionnel)
            permissions: Liste des permissions (optionnel)
            
        Returns:
            Rôle créé
            
        Raises:
            UserError: Si le rôle existe déjà
        """
        if self.session.query(Role).filter(Role.name == name).first():
            raise UserError(f"Le rôle {name} existe déjà")
        
        role = Role(
            name=name,
            description=description,
            created_at=datetime.now()
        )
        
        if permissions:
            for perm_name in permissions:
                permission = Permission(name=perm_name)
                role.permissions.append(permission)
        
        self.session.add(role)
        self.session.commit()
        
        return role
    
    def get_role(self, role_id: int) -> Role:
        """
        Récupère un rôle par son ID.
        
        Args:
            role_id: ID du rôle
            
        Returns:
            Rôle
            
        Raises:
            UserError: Si le rôle n'existe pas
        """
        role = self.session.query(Role).get(role_id)
        if not role:
            raise UserError(f"Le rôle {role_id} n'existe pas")
        return role
    
    def update_role(
        self,
        role_id: int,
        data: dict
    ) -> Role:
        """
        Met à jour un rôle.
        
        Args:
            role_id: ID du rôle
            data: Données à mettre à jour
            
        Returns:
            Rôle mis à jour
            
        Raises:
            UserError: Si le rôle n'existe pas
        """
        role = self.get_role(role_id)
        
        # Mettre à jour les champs
        for key, value in data.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        role.updated_at = datetime.now()
        self.session.commit()
        
        return role
    
    def delete_role(self, role_id: int) -> None:
        """
        Supprime un rôle.
        
        Args:
            role_id: ID du rôle
            
        Raises:
            UserError: Si le rôle n'existe pas ou s'il est utilisé par des utilisateurs
        """
        role = self.get_role(role_id)
        
        # Vérifier si le rôle est utilisé
        if self.session.query(User).filter(User.role_id == role_id).first():
            raise UserError("Ce rôle est utilisé par des utilisateurs")
        
        self.session.delete(role)
        self.session.commit()
    
    def add_permission_to_role(
        self,
        role_id: int,
        permission_name: str
    ) -> None:
        """
        Ajoute une permission à un rôle.
        
        Args:
            role_id: ID du rôle
            permission_name: Nom de la permission
            
        Raises:
            UserError: Si le rôle n'existe pas ou si la permission existe déjà
        """
        role = self.get_role(role_id)
        
        # Vérifier si la permission existe déjà
        if any(p.name == permission_name for p in role.permissions):
            raise UserError(f"La permission {permission_name} existe déjà pour ce rôle")
        
        permission = Permission(name=permission_name)
        role.permissions.append(permission)
        self.session.commit()
    
    def remove_permission_from_role(
        self,
        role_id: int,
        permission_name: str
    ) -> None:
        """
        Supprime une permission d'un rôle.
        
        Args:
            role_id: ID du rôle
            permission_name: Nom de la permission
            
        Raises:
            UserError: Si le rôle n'existe pas ou si la permission n'existe pas
        """
        role = self.get_role(role_id)
        
        # Trouver la permission
        permission = next(
            (p for p in role.permissions if p.name == permission_name),
            None
        )
        
        if not permission:
            raise UserError(f"La permission {permission_name} n'existe pas pour ce rôle")
        
        role.permissions.remove(permission)
        self.session.commit()
    
    def check_permission(
        self,
        user_id: int,
        permission_name: str
    ) -> bool:
        """
        Vérifie si un utilisateur a une permission.
        
        Args:
            user_id: ID de l'utilisateur
            permission_name: Nom de la permission
            
        Returns:
            True si l'utilisateur a la permission, False sinon
        """
        try:
            user = self.get_user(user_id)
            return any(p.name == permission_name for p in user.role.permissions)
        except UserError:
            return False 