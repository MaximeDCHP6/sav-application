import os
import re
import json
import uuid
import hashlib
import datetime
import random
import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal

from .logger import logger
from .exceptions import ValidationError, FormatError

def generate_id(prefix: str = "") -> str:
    """Génère un identifiant unique.
    
    Args:
        prefix: Préfixe de l'identifiant (optionnel)
        
    Returns:
        str: Identifiant unique
    """
    return f"{prefix}{uuid.uuid4().hex}"

def generate_password(length: int = 12) -> str:
    """Génère un mot de passe aléatoire.
    
    Args:
        length: Longueur du mot de passe
        
    Returns:
        str: Mot de passe généré
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hache un mot de passe avec un sel.
    
    Args:
        password: Mot de passe à hacher
        salt: Sel à utiliser (optionnel)
        
    Returns:
        tuple: (mot de passe haché, sel)
    """
    if salt is None:
        salt = os.urandom(32).hex()
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    
    return key.hex(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Vérifie un mot de passe.
    
    Args:
        password: Mot de passe à vérifier
        hashed: Mot de passe haché
        salt: Sel utilisé
        
    Returns:
        bool: True si le mot de passe est correct
    """
    key, _ = hash_password(password, salt)
    return key == hashed

def format_date(date: Union[str, datetime.datetime], format: str = "%d/%m/%Y") -> str:
    """Formate une date.
    
    Args:
        date: Date à formater
        format: Format de sortie
        
    Returns:
        str: Date formatée
        
    Raises:
        FormatError: Si la date est invalide
    """
    try:
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        return date.strftime(format)
    except Exception as e:
        raise FormatError(f"Date invalide : {str(e)}")

def parse_date(date: str, format: str = "%d/%m/%Y") -> datetime.datetime:
    """Parse une date.
    
    Args:
        date: Date à parser
        format: Format d'entrée
        
    Returns:
        datetime: Date parsée
        
    Raises:
        FormatError: Si la date est invalide
    """
    try:
        return datetime.datetime.strptime(date, format)
    except Exception as e:
        raise FormatError(f"Date invalide : {str(e)}")

def format_number(number: Union[int, float, Decimal], format: str = "%.2f") -> str:
    """Formate un nombre.
    
    Args:
        number: Nombre à formater
        format: Format de sortie
        
    Returns:
        str: Nombre formaté
        
    Raises:
        FormatError: Si le nombre est invalide
    """
    try:
        return format % number
    except Exception as e:
        raise FormatError(f"Nombre invalide : {str(e)}")

def parse_number(number: str) -> Decimal:
    """Parse un nombre.
    
    Args:
        number: Nombre à parser
        
    Returns:
        Decimal: Nombre parsé
        
    Raises:
        FormatError: Si le nombre est invalide
    """
    try:
        return Decimal(number.replace(',', '.'))
    except Exception as e:
        raise FormatError(f"Nombre invalide : {str(e)}")

def format_currency(amount: Union[int, float, Decimal], currency: str = "€") -> str:
    """Formate un montant.
    
    Args:
        amount: Montant à formater
        currency: Devise
        
    Returns:
        str: Montant formaté
        
    Raises:
        FormatError: Si le montant est invalide
    """
    try:
        return f"{format_number(amount)} {currency}"
    except Exception as e:
        raise FormatError(f"Montant invalide : {str(e)}")

def parse_currency(amount: str) -> Decimal:
    """Parse un montant.
    
    Args:
        amount: Montant à parser
        
    Returns:
        Decimal: Montant parsé
        
    Raises:
        FormatError: Si le montant est invalide
    """
    try:
        return parse_number(amount.replace('€', '').strip())
    except Exception as e:
        raise FormatError(f"Montant invalide : {str(e)}")

def validate_email(email: str) -> bool:
    """Valide une adresse email.
    
    Args:
        email: Email à valider
        
    Returns:
        bool: True si l'email est valide
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Valide un numéro de téléphone.
    
    Args:
        phone: Numéro à valider
        
    Returns:
        bool: True si le numéro est valide
    """
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone))

def validate_postal_code(code: str) -> bool:
    """Valide un code postal.
    
    Args:
        code: Code à valider
        
    Returns:
        bool: True si le code est valide
    """
    pattern = r'^[0-9]{5}$'
    return bool(re.match(pattern, code))

def validate_siret(siret: str) -> bool:
    """Valide un numéro SIRET.
    
    Args:
        siret: SIRET à valider
        
    Returns:
        bool: True si le SIRET est valide
    """
    pattern = r'^[0-9]{14}$'
    return bool(re.match(pattern, siret))

def validate_siren(siren: str) -> bool:
    """Valide un numéro SIREN.
    
    Args:
        siren: SIREN à valider
        
    Returns:
        bool: True si le SIREN est valide
    """
    pattern = r'^[0-9]{9}$'
    return bool(re.match(pattern, siren))

def validate_vat(vat: str) -> bool:
    """Valide un numéro de TVA.
    
    Args:
        vat: TVA à valider
        
    Returns:
        bool: True si la TVA est valide
    """
    pattern = r'^[A-Z]{2}[0-9]{11}$'
    return bool(re.match(pattern, vat))

def validate_iban(iban: str) -> bool:
    """Valide un numéro IBAN.
    
    Args:
        iban: IBAN à valider
        
    Returns:
        bool: True si l'IBAN est valide
    """
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}$'
    return bool(re.match(pattern, iban))

def validate_bic(bic: str) -> bool:
    """Valide un code BIC.
    
    Args:
        bic: BIC à valider
        
    Returns:
        bool: True si le BIC est valide
    """
    pattern = r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$'
    return bool(re.match(pattern, bic))

def validate_url(url: str) -> bool:
    """Valide une URL.
    
    Args:
        url: URL à valider
        
    Returns:
        bool: True si l'URL est valide
    """
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))

def validate_ip(ip: str) -> bool:
    """Valide une adresse IP.
    
    Args:
        ip: IP à valider
        
    Returns:
        bool: True si l'IP est valide
    """
    pattern = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    return bool(re.match(pattern, ip))

def validate_mac(mac: str) -> bool:
    """Valide une adresse MAC.
    
    Args:
        mac: MAC à valider
        
    Returns:
        bool: True si la MAC est valide
    """
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))

def validate_hex_color(color: str) -> bool:
    """Valide une couleur hexadécimale.
    
    Args:
        color: Couleur à valider
        
    Returns:
        bool: True si la couleur est valide
    """
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return bool(re.match(pattern, color))

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Valide l'extension d'un fichier.
    
    Args:
        filename: Nom du fichier
        allowed_extensions: Liste des extensions autorisées
        
    Returns:
        bool: True si l'extension est valide
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

def validate_file_size(filepath: str, max_size: int) -> bool:
    """Valide la taille d'un fichier.
    
    Args:
        filepath: Chemin du fichier
        max_size: Taille maximale en octets
        
    Returns:
        bool: True si la taille est valide
    """
    return os.path.getsize(filepath) <= max_size

def validate_file_type(filepath: str, allowed_types: List[str]) -> bool:
    """Valide le type MIME d'un fichier.
    
    Args:
        filepath: Chemin du fichier
        allowed_types: Liste des types MIME autorisés
        
    Returns:
        bool: True si le type est valide
    """
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type in allowed_types

def validate_json(data: str) -> bool:
    """Valide une chaîne JSON.
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def validate_xml(data: str) -> bool:
    """Valide une chaîne XML.
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(data)
        return True
    except ET.ParseError:
        return False

def validate_yaml(data: str) -> bool:
    """Valide une chaîne YAML.
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        import yaml
        yaml.safe_load(data)
        return True
    except yaml.YAMLError:
        return False

def validate_csv(data: str, delimiter: str = ',') -> bool:
    """Valide une chaîne CSV.
    
    Args:
        data: Données à valider
        delimiter: Délimiteur
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        import csv
        csv.reader(data.splitlines(), delimiter=delimiter)
        return True
    except csv.Error:
        return False

def validate_ini(data: str) -> bool:
    """Valide une chaîne INI.
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read_string(data)
        return True
    except configparser.Error:
        return False

def validate_toml(data: str) -> bool:
    """Valide une chaîne TOML.
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        import toml
        toml.loads(data)
        return True
    except toml.TomlDecodeError:
        return False

def validate_html(data: str) -> bool:
    """Valide une chaîne HTML.
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        from bs4 import BeautifulSoup
        BeautifulSoup(data, 'html.parser')
        return True
    except Exception:
        return False

def validate_markdown(data: str) -> bool:
    """Valide une chaîne Markdown.
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si les données sont valides
    """
    try:
        import markdown
        markdown.markdown(data)
        return True
    except Exception:
        return False

def validate_regex(pattern: str) -> bool:
    """Valide une expression régulière.
    
    Args:
        pattern: Pattern à valider
        
    Returns:
        bool: True si le pattern est valide
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

def validate_date_range(start_date: datetime.datetime, end_date: datetime.datetime) -> bool:
    """Valide une plage de dates.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        bool: True si la plage est valide
    """
    return start_date <= end_date

def validate_number_range(number: Union[int, float, Decimal], min_value: Union[int, float, Decimal], max_value: Union[int, float, Decimal]) -> bool:
    """Valide une plage de nombres.
    
    Args:
        number: Nombre à valider
        min_value: Valeur minimale
        max_value: Valeur maximale
        
    Returns:
        bool: True si le nombre est dans la plage
    """
    return min_value <= number <= max_value

def validate_string_length(string: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """Valide la longueur d'une chaîne.
    
    Args:
        string: Chaîne à valider
        min_length: Longueur minimale
        max_length: Longueur maximale (optionnel)
        
    Returns:
        bool: True si la longueur est valide
    """
    if max_length is None:
        return len(string) >= min_length
    return min_length <= len(string) <= max_length

def validate_list_length(items: List[Any], min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """Valide la longueur d'une liste.
    
    Args:
        items: Liste à valider
        min_length: Longueur minimale
        max_length: Longueur maximale (optionnel)
        
    Returns:
        bool: True si la longueur est valide
    """
    if max_length is None:
        return len(items) >= min_length
    return min_length <= len(items) <= max_length

def validate_dict_keys(data: Dict[str, Any], required_keys: List[str], optional_keys: Optional[List[str]] = None) -> bool:
    """Valide les clés d'un dictionnaire.
    
    Args:
        data: Dictionnaire à valider
        required_keys: Clés requises
        optional_keys: Clés optionnelles (optionnel)
        
    Returns:
        bool: True si les clés sont valides
    """
    if not all(key in data for key in required_keys):
        return False
    
    if optional_keys is not None:
        return all(key in required_keys + optional_keys for key in data.keys())
    
    return True

def validate_dict_values(data: Dict[str, Any], value_types: Dict[str, type]) -> bool:
    """Valide les valeurs d'un dictionnaire.
    
    Args:
        data: Dictionnaire à valider
        value_types: Types des valeurs
        
    Returns:
        bool: True si les valeurs sont valides
    """
    return all(
        key in data and isinstance(data[key], value_types[key])
        for key in value_types
    )

def validate_enum(value: Any, enum_values: List[Any]) -> bool:
    """Valide une valeur d'énumération.
    
    Args:
        value: Valeur à valider
        enum_values: Valeurs possibles
        
    Returns:
        bool: True si la valeur est valide
    """
    return value in enum_values 