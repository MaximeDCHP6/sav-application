import unittest
import time
from datetime import datetime, timedelta
from decimal import Decimal
from alder_sav.utils.cache import CacheManager
from alder_sav.utils.exceptions import CacheError

class TestCacheManager(unittest.TestCase):
    """Tests pour le gestionnaire de cache."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.cache_manager = CacheManager()

    def test_set_get_cache(self):
        """Test de mise en cache et récupération."""
        # Données à mettre en cache
        test_data = {
            "user_id": 123,
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        # Mettre en cache
        self.cache_manager.set("user:123", test_data)
        
        # Récupérer du cache
        cached_data = self.cache_manager.get("user:123")
        self.assertEqual(cached_data, test_data)

    def test_cache_expiration(self):
        """Test de l'expiration du cache."""
        # Données à mettre en cache avec expiration
        test_data = {"key": "value"}
        self.cache_manager.set("expiring_key", test_data, ttl=1)  # 1 seconde
        
        # Vérifier que les données sont en cache
        self.assertEqual(self.cache_manager.get("expiring_key"), test_data)
        
        # Attendre l'expiration
        time.sleep(2)
        
        # Vérifier que les données ont expiré
        self.assertIsNone(self.cache_manager.get("expiring_key"))

    def test_cache_invalidation(self):
        """Test de l'invalidation du cache."""
        # Mettre des données en cache
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        
        # Invalider une clé
        self.cache_manager.invalidate("key1")
        
        # Vérifier l'invalidation
        self.assertIsNone(self.cache_manager.get("key1"))
        self.assertEqual(self.cache_manager.get("key2"), "value2")

    def test_cache_clear(self):
        """Test du nettoyage du cache."""
        # Mettre des données en cache
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        
        # Nettoyer le cache
        self.cache_manager.clear()
        
        # Vérifier le nettoyage
        self.assertIsNone(self.cache_manager.get("key1"))
        self.assertIsNone(self.cache_manager.get("key2"))

    def test_cache_pattern_invalidation(self):
        """Test de l'invalidation par motif."""
        # Mettre des données en cache
        self.cache_manager.set("user:1", "data1")
        self.cache_manager.set("user:2", "data2")
        self.cache_manager.set("order:1", "data3")
        
        # Invalider par motif
        self.cache_manager.invalidate_pattern("user:*")
        
        # Vérifier l'invalidation
        self.assertIsNone(self.cache_manager.get("user:1"))
        self.assertIsNone(self.cache_manager.get("user:2"))
        self.assertEqual(self.cache_manager.get("order:1"), "data3")

    def test_cache_size_limit(self):
        """Test de la limite de taille du cache."""
        # Configurer la limite
        self.cache_manager.configure(max_size=2)
        
        # Mettre des données en cache
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        self.cache_manager.set("key3", "value3")
        
        # Vérifier la limite
        self.assertIsNone(self.cache_manager.get("key1"))
        self.assertEqual(self.cache_manager.get("key2"), "value2")
        self.assertEqual(self.cache_manager.get("key3"), "value3")

    def test_cache_memory_usage(self):
        """Test de l'utilisation de la mémoire."""
        # Mettre des données en cache
        large_data = "x" * 1000000  # 1 MB
        self.cache_manager.set("large_key", large_data)
        
        # Vérifier l'utilisation de la mémoire
        memory_usage = self.cache_manager.get_memory_usage()
        self.assertGreater(memory_usage, 0)

    def test_cache_statistics(self):
        """Test des statistiques du cache."""
        # Utiliser le cache
        self.cache_manager.set("key1", "value1")
        self.cache_manager.get("key1")
        self.cache_manager.get("nonexistent")
        
        # Vérifier les statistiques
        stats = self.cache_manager.get_statistics()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)

    def test_cache_serialization(self):
        """Test de la sérialisation du cache."""
        # Données complexes à mettre en cache
        complex_data = {
            "datetime": datetime.now(),
            "decimal": Decimal("10.5"),
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }
        
        # Mettre en cache
        self.cache_manager.set("complex_key", complex_data)
        
        # Récupérer du cache
        cached_data = self.cache_manager.get("complex_key")
        self.assertEqual(cached_data, complex_data)

    def test_cache_atomic_operations(self):
        """Test des opérations atomiques du cache."""
        # Incrémenter une valeur
        self.cache_manager.set("counter", 0)
        self.cache_manager.increment("counter")
        self.assertEqual(self.cache_manager.get("counter"), 1)
        
        # Décrémenter une valeur
        self.cache_manager.decrement("counter")
        self.assertEqual(self.cache_manager.get("counter"), 0)

    def test_cache_bulk_operations(self):
        """Test des opérations en masse du cache."""
        # Mettre plusieurs valeurs en cache
        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        self.cache_manager.set_many(data)
        
        # Récupérer plusieurs valeurs
        cached_data = self.cache_manager.get_many(["key1", "key2", "key3"])
        self.assertEqual(cached_data, data)

    def test_cache_locking(self):
        """Test du verrouillage du cache."""
        # Verrouiller une clé
        with self.cache_manager.lock("locked_key"):
            # Vérifier que la clé est verrouillée
            self.assertTrue(self.cache_manager.is_locked("locked_key"))
            
            # Tenter d'accéder à la clé verrouillée
            with self.assertRaises(CacheError):
                self.cache_manager.set("locked_key", "value")

    def test_cache_compression(self):
        """Test de la compression du cache."""
        # Données compressibles
        large_data = "x" * 1000000  # 1 MB
        
        # Mettre en cache avec compression
        self.cache_manager.set("compressed_key", large_data, compress=True)
        
        # Vérifier la compression
        cached_data = self.cache_manager.get("compressed_key")
        self.assertEqual(cached_data, large_data)

if __name__ == '__main__':
    unittest.main() 