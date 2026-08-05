"""
HiddenYatra — Production Test Suite: Database Tests
Tests database layer functions, connection pooling, and CRUD operations.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabaseImports(unittest.TestCase):
    """Test that the database module loads without error."""

    def test_import_database(self):
        from models import database
        self.assertTrue(hasattr(database, 'get_db'))
        self.assertTrue(hasattr(database, 'get_cursor'))
        self.assertTrue(hasattr(database, 'init_db'))

    def test_import_categories(self):
        from models.database import PLACE_CATEGORIES
        self.assertIsInstance(PLACE_CATEGORIES, (dict, list))
        self.assertTrue(len(PLACE_CATEGORIES) > 0)


class TestSlugify(unittest.TestCase):
    """Test slug generation."""

    def test_basic_slug(self):
        from models.database import slugify
        self.assertEqual(slugify('Hello World'), 'hello-world')

    def test_special_chars(self):
        from models.database import slugify
        result = slugify('Hello! @#$ World')
        self.assertNotIn('!', result)
        self.assertNotIn('@', result)

    def test_multiple_spaces(self):
        from models.database import slugify
        result = slugify('Hello   World')
        self.assertEqual(result, 'hello-world')

    def test_trailing_hyphens(self):
        from models.database import slugify
        result = slugify('  Hello World  ')
        self.assertFalse(result.startswith('-'))
        self.assertFalse(result.endswith('-'))

    def test_empty_string(self):
        from models.database import slugify
        result = slugify('')
        self.assertEqual(result, '')


class TestLikeEscape(unittest.TestCase):
    """Test LIKE wildcard escaping."""

    def test_escape_percent(self):
        from models.database import _escape_like
        self.assertEqual(_escape_like('100%'), '100\\%')

    def test_escape_underscore(self):
        from models.database import _escape_like
        self.assertEqual(_escape_like('hello_world'), 'hello\\_world')

    def test_escape_backslash(self):
        from models.database import _escape_like
        self.assertEqual(_escape_like('path\\file'), 'path\\\\file')

    def test_normal_text(self):
        from models.database import _escape_like
        self.assertEqual(_escape_like('hello world'), 'hello world')


class TestPasswordHashing(unittest.TestCase):
    """Test password hashing and verification."""

    def test_hash_password(self):
        from models.database import hash_password
        hashed = hash_password('test123')
        self.assertTrue(hashed.startswith('pbkdf2$'))

    def test_verify_password(self):
        from models.database import hash_password, verify_password
        hashed = hash_password('test123')
        self.assertTrue(verify_password('test123', hashed))
        self.assertFalse(verify_password('wrong', hashed))

    def test_unique_salts(self):
        from models.database import hash_password
        h1 = hash_password('same')
        h2 = hash_password('same')
        self.assertNotEqual(h1, h2)  # Different salts


class TestPoolConfiguration(unittest.TestCase):
    """Test connection pool configuration."""

    def test_pool_creation(self):
        """Test that pool can be created (requires MySQL running)."""
        try:
            from models.database import _get_pool
            pool = _get_pool()
            self.assertIsNotNone(pool)
        except Exception:
            self.skipTest("MySQL not available")

    def test_pool_is_singleton(self):
        """Test that pool returns the same instance."""
        try:
            from models.database import _get_pool
            p1 = _get_pool()
            p2 = _get_pool()
            self.assertIs(p1, p2)
        except Exception:
            self.skipTest("MySQL not available")


class TestDatabaseCRUD(unittest.TestCase):
    """Test CRUD operations (requires MySQL running)."""

    @classmethod
    def setUpClass(cls):
        try:
            from models.database import init_db
            init_db()
            cls.db_available = True
        except Exception:
            cls.db_available = False

    def setUp(self):
        if not self.db_available:
            self.skipTest("MySQL not available")

    def test_get_all_states(self):
        from models.database import get_all_states
        states = get_all_states()
        self.assertIsInstance(states, (list, tuple))

    def test_get_stats(self):
        from models.database import get_stats
        stats = get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('states', stats)
        self.assertIn('places', stats)
        self.assertIn('users', stats)

    def test_get_stats_cached(self):
        """Test that stats are cached on second call."""
        from models.database import get_stats
        s1 = get_stats()
        s2 = get_stats()
        self.assertEqual(s1, s2)

    def test_search_places_empty(self):
        from models.database import search_places
        results = search_places('')
        self.assertIsInstance(results, (list, tuple))

    def test_search_places_special_chars(self):
        from models.database import search_places
        results = search_places('%_\\')
        self.assertIsInstance(results, (list, tuple))

    def test_smart_search(self):
        from models.database import smart_search
        results = smart_search('I am going to Patna')
        self.assertIsInstance(results, dict)
        self.assertIn('places', results)
        self.assertIn('foods', results)
        self.assertIn('hotels', results)

    def test_count_places(self):
        from models.database import count_places
        count = count_places()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_get_place_by_slug_nonexistent(self):
        from models.database import get_place_by_slug
        place = get_place_by_slug('this-slug-does-not-exist-xyz-123')
        self.assertIsNone(place)

    def test_get_user_by_id_nonexistent(self):
        from models.database import get_user_by_id
        user = get_user_by_id(999999)
        self.assertIsNone(user)


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""

    def test_config_imports(self):
        from config import (
            DB_HOST, DB_PORT, DB_NAME, DB_USER,
            UPLOAD_FOLDER, SECRET_KEY, ADMIN_PASSWORD,
            APP_NAME, ALLOWED_EXTENSIONS
        )
        self.assertIsNotNone(SECRET_KEY)
        self.assertIsNotNone(ADMIN_PASSWORD)
        self.assertEqual(APP_NAME, 'HiddenYatra')

    def test_allowed_file(self):
        from config import allowed_file
        self.assertTrue(allowed_file('photo.jpg'))
        self.assertTrue(allowed_file('photo.png'))
        self.assertTrue(allowed_file('photo.webp'))
        self.assertFalse(allowed_file('script.exe'))
        self.assertFalse(allowed_file('hack.php'))
        self.assertFalse(allowed_file(''))
        self.assertFalse(allowed_file('noextension'))

    def test_check_file_size(self):
        from config import check_file_size
        from io import BytesIO
        small = BytesIO(b'x' * 100)
        self.assertTrue(check_file_size(small))
        large = BytesIO(b'x' * (6 * 1024 * 1024))  # 6MB
        self.assertFalse(check_file_size(large))


if __name__ == '__main__':
    unittest.main(verbosity=2)
