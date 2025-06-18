from typing import List, Dict, Any, Callable
from datetime import datetime
from decimal import Decimal

class SearchFilter:
    """Classe utilitaire pour la recherche et le filtrage"""
    
    @staticmethod
    def filter_by_text(items: List[Any], text: str, fields: List[str]) -> List[Any]:
        """
        Filtre une liste d'objets en fonction d'un texte de recherche.
        
        Args:
            items: Liste d'objets à filtrer
            text: Texte de recherche
            fields: Liste des champs à rechercher
            
        Returns:
            Liste filtrée d'objets
        """
        if not text:
            return items
        
        text = text.lower()
        filtered_items = []
        
        for item in items:
            for field in fields:
                value = getattr(item, field, None)
                if value and text in str(value).lower():
                    filtered_items.append(item)
                    break
        
        return filtered_items
    
    @staticmethod
    def filter_by_date_range(
        items: List[Any],
        start_date: datetime,
        end_date: datetime,
        date_field: str
    ) -> List[Any]:
        """
        Filtre une liste d'objets en fonction d'une plage de dates.
        
        Args:
            items: Liste d'objets à filtrer
            start_date: Date de début
            end_date: Date de fin
            date_field: Champ contenant la date
            
        Returns:
            Liste filtrée d'objets
        """
        filtered_items = []
        
        for item in items:
            date_value = getattr(item, date_field, None)
            if date_value and start_date <= date_value <= end_date:
                filtered_items.append(item)
        
        return filtered_items
    
    @staticmethod
    def filter_by_value(
        items: List[Any],
        value: Any,
        field: str,
        operator: str = '=='
    ) -> List[Any]:
        """
        Filtre une liste d'objets en fonction d'une valeur.
        
        Args:
            items: Liste d'objets à filtrer
            value: Valeur à comparer
            field: Champ à comparer
            operator: Opérateur de comparaison ('==', '!=', '>', '<', '>=', '<=')
            
        Returns:
            Liste filtrée d'objets
        """
        operators = {
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y
        }
        
        if operator not in operators:
            raise ValueError(f"Opérateur non valide: {operator}")
        
        compare_func = operators[operator]
        filtered_items = []
        
        for item in items:
            field_value = getattr(item, field, None)
            if field_value is not None and compare_func(field_value, value):
                filtered_items.append(item)
        
        return filtered_items
    
    @staticmethod
    def filter_by_range(
        items: List[Any],
        min_value: Any,
        max_value: Any,
        field: str
    ) -> List[Any]:
        """
        Filtre une liste d'objets en fonction d'une plage de valeurs.
        
        Args:
            items: Liste d'objets à filtrer
            min_value: Valeur minimale
            max_value: Valeur maximale
            field: Champ à comparer
            
        Returns:
            Liste filtrée d'objets
        """
        filtered_items = []
        
        for item in items:
            field_value = getattr(item, field, None)
            if field_value is not None and min_value <= field_value <= max_value:
                filtered_items.append(item)
        
        return filtered_items
    
    @staticmethod
    def filter_by_multiple_values(
        items: List[Any],
        values: List[Any],
        field: str
    ) -> List[Any]:
        """
        Filtre une liste d'objets en fonction de plusieurs valeurs possibles.
        
        Args:
            items: Liste d'objets à filtrer
            values: Liste des valeurs possibles
            field: Champ à comparer
            
        Returns:
            Liste filtrée d'objets
        """
        filtered_items = []
        
        for item in items:
            field_value = getattr(item, field, None)
            if field_value in values:
                filtered_items.append(item)
        
        return filtered_items
    
    @staticmethod
    def sort_items(
        items: List[Any],
        field: str,
        reverse: bool = False
    ) -> List[Any]:
        """
        Trie une liste d'objets en fonction d'un champ.
        
        Args:
            items: Liste d'objets à trier
            field: Champ de tri
            reverse: True pour trier dans l'ordre décroissant
            
        Returns:
            Liste triée d'objets
        """
        return sorted(
            items,
            key=lambda x: getattr(x, field),
            reverse=reverse
        )
    
    @staticmethod
    def group_by(
        items: List[Any],
        field: str
    ) -> Dict[Any, List[Any]]:
        """
        Groupe une liste d'objets en fonction d'un champ.
        
        Args:
            items: Liste d'objets à grouper
            field: Champ de groupement
            
        Returns:
            Dictionnaire des groupes
        """
        groups = {}
        
        for item in items:
            key = getattr(item, field)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        
        return groups
    
    @staticmethod
    def aggregate(
        items: List[Any],
        field: str,
        operation: str
    ) -> Any:
        """
        Effectue une opération d'agrégation sur un champ.
        
        Args:
            items: Liste d'objets à agréger
            field: Champ à agréger
            operation: Opération ('sum', 'avg', 'min', 'max', 'count')
            
        Returns:
            Résultat de l'agrégation
        """
        values = [getattr(item, field) for item in items if hasattr(item, field)]
        
        if not values:
            return None
        
        operations = {
            'sum': sum,
            'avg': lambda x: sum(x) / len(x),
            'min': min,
            'max': max,
            'count': len
        }
        
        if operation not in operations:
            raise ValueError(f"Opération non valide: {operation}")
        
        return operations[operation](values) 