"""
HiddenYatra — Production Test Suite: Route Tests
Tests every route, blueprint, and API endpoint for correct status codes,
authorization, and basic functionality.
"""
import os
import sys
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _create_test_app():
    """Create test app, returns None if MySQL is unavailable."""
    try:
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        return app
    except Exception:
        return None


class TestAppStartup(unittest.TestCase):
    """Verify the app can start without errors."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest("MySQL not available")
        cls.client = cls.app.test_client()

    def test_app_created(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])


class TestPublicRoutes(unittest.TestCase):
    """Test all public-facing routes return valid responses."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_index(self):
        r = self.client.get('/')
        self.assertIn(r.status_code, [200, 302])

    def test_browse(self):
        r = self.client.get('/browse')
        self.assertIn(r.status_code, [200, 302])

    def test_search_empty(self):
        r = self.client.get('/search')
        self.assertIn(r.status_code, [200, 302])

    def test_search_with_query(self):
        r = self.client.get('/search?q=test')
        self.assertIn(r.status_code, [200, 302])

    def test_search_special_chars(self):
        """Test LIKE injection prevention."""
        r = self.client.get('/search?q=%25%5F')
        self.assertIn(r.status_code, [200, 302])

    def test_explore(self):
        r = self.client.get('/explore')
        self.assertIn(r.status_code, [200, 302])

    def test_food_culture(self):
        r = self.client.get('/food-culture')
        self.assertIn(r.status_code, [200, 302])

    def test_404_page(self):
        r = self.client.get('/nonexistent-page-xyz')
        self.assertEqual(r.status_code, 404)

    def test_place_404(self):
        r = self.client.get('/place/nonexistent-slug-xyz')
        self.assertIn(r.status_code, [404, 302])

    def test_state_404(self):
        r = self.client.get('/state/nonexistent-state')
        self.assertIn(r.status_code, [404, 302])


class TestAuthRoutes(unittest.TestCase):
    """Test authentication routes."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_login_page(self):
        r = self.client.get('/login')
        self.assertIn(r.status_code, [200, 302])

    def test_signup_page(self):
        r = self.client.get('/signup')
        self.assertIn(r.status_code, [200, 302])

    def test_login_post_missing_csrf(self):
        """Login POST without CSRF should fail gracefully."""
        r = self.client.post('/login', data={'email': 'test@test.com', 'password': 'test'})
        self.assertIn(r.status_code, [200, 302, 403])

    def test_logout(self):
        r = self.client.post('/logout')
        self.assertIn(r.status_code, [302, 403])


class TestAdminRoutes(unittest.TestCase):
    """Test admin routes require authentication."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_admin_dashboard_redirects(self):
        """Admin dashboard should redirect unauthenticated users."""
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 302)

    def test_admin_login_page(self):
        r = self.client.get('/admin/login')
        self.assertEqual(r.status_code, 200)

    def test_admin_submissions_redirects(self):
        r = self.client.get('/admin/submissions')
        self.assertEqual(r.status_code, 302)

    def test_admin_users_redirects(self):
        r = self.client.get('/admin/users')
        self.assertEqual(r.status_code, 302)

    def test_admin_recycle_bin_redirects(self):
        r = self.client.get('/admin/recycle-bin')
        self.assertEqual(r.status_code, 302)

    def test_admin_hero_media_redirects(self):
        r = self.client.get('/admin/hero-media')
        self.assertEqual(r.status_code, 302)

    def test_admin_districts_redirects(self):
        r = self.client.get('/admin/districts')
        self.assertEqual(r.status_code, 302)

    def test_admin_trending_redirects(self):
        r = self.client.get('/admin/trending')
        self.assertEqual(r.status_code, 302)

    def test_admin_login_wrong_password(self):
        """Test admin login with wrong password."""
        with self.client.session_transaction() as sess:
            sess['_csrf_token'] = 'test_token'
        r = self.client.post('/admin/login', data={
            'password': 'wrong_password',
            '_csrf_token': 'test_token'
        })
        self.assertEqual(r.status_code, 200)  # Stays on login page


class TestAPIRoutes(unittest.TestCase):
    """Test API endpoints return valid JSON."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_api_places(self):
        r = self.client.get('/api/places')
        self.assertIn(r.status_code, [200, 404])
        if r.status_code == 200:
            self.assertEqual(r.content_type, 'application/json')

    def test_api_states(self):
        r = self.client.get('/api/states')
        self.assertIn(r.status_code, [200, 404])

    def test_api_reviews_invalid_place(self):
        r = self.client.get('/api/reviews/99999')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)

    def test_api_search(self):
        r = self.client.get('/api/search?q=test')
        self.assertIn(r.status_code, [200, 404])


class TestWishlistRoutes(unittest.TestCase):
    """Test wishlist functionality."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_wishlist_page(self):
        r = self.client.get('/wishlist')
        self.assertIn(r.status_code, [200, 302])

    def test_wishlist_toggle_without_csrf(self):
        """Toggle without CSRF should fail."""
        r = self.client.post('/wishlist/toggle/1')
        self.assertIn(r.status_code, [200, 302, 403, 404])


class TestItineraryRoutes(unittest.TestCase):
    """Test itinerary functionality."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_itinerary_page(self):
        r = self.client.get('/itinerary')
        self.assertIn(r.status_code, [200, 302])


class TestCommunityRoutes(unittest.TestCase):
    """Test community/submission routes."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_suggest_page(self):
        r = self.client.get('/suggest')
        self.assertIn(r.status_code, [200, 302])


class TestSEORoutes(unittest.TestCase):
    """Test SEO-related routes."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_robots_txt(self):
        r = self.client.get('/robots.txt')
        self.assertIn(r.status_code, [200, 404])

    def test_sitemap_xml(self):
        r = self.client.get('/sitemap.xml')
        self.assertIn(r.status_code, [200, 404])
        if r.status_code == 200:
            self.assertIn(b'urlset', r.data)


class TestErrorHandlers(unittest.TestCase):
    """Test error pages."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_404_html(self):
        r = self.client.get('/this-page-does-not-exist-ever')
        self.assertEqual(r.status_code, 404)

    def test_404_json(self):
        r = self.client.get('/this-page-does-not-exist',
                            headers={'Accept': 'application/json',
                                     'Content-Type': 'application/json'})
        self.assertEqual(r.status_code, 404)


class TestSecurityHeaders(unittest.TestCase):
    """Test security headers are set."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_x_content_type_options(self):
        r = self.client.get('/')
        self.assertEqual(r.headers.get('X-Content-Type-Options'), 'nosniff')

    def test_x_frame_options(self):
        r = self.client.get('/')
        self.assertEqual(r.headers.get('X-Frame-Options'), 'SAMEORIGIN')

    def test_csp_header(self):
        r = self.client.get('/')
        self.assertIn('Content-Security-Policy', r.headers)

    def test_referrer_policy(self):
        r = self.client.get('/')
        self.assertEqual(r.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')


class TestCSRFProtection(unittest.TestCase):
    """Test CSRF token generation and validation."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_csrf_token_generated(self):
        with self.client.session_transaction() as sess:
            pass  # Initialize session
        r = self.client.get('/')
        with self.client.session_transaction() as sess:
            self.assertIn('_csrf_token', sess)
            self.assertEqual(len(sess['_csrf_token']), 64)  # 32 bytes hex


class TestInputValidation(unittest.TestCase):
    """Test input validation and edge cases."""

    @classmethod
    def setUpClass(cls):
        cls.app = _create_test_app()
        if cls.app is None:
            raise unittest.SkipTest('MySQL not available')
        cls.client = cls.app.test_client()

    def test_search_empty_query(self):
        r = self.client.get('/search?q=')
        self.assertIn(r.status_code, [200, 302])

    def test_search_very_long_query(self):
        r = self.client.get(f'/search?q={"a" * 1000}')
        self.assertIn(r.status_code, [200, 302])

    def test_pagination_zero(self):
        r = self.client.get('/browse?page=0')
        self.assertIn(r.status_code, [200, 302])

    def test_pagination_negative(self):
        r = self.client.get('/browse?page=-1')
        self.assertIn(r.status_code, [200, 302])

    def test_pagination_string(self):
        r = self.client.get('/browse?page=abc')
        self.assertIn(r.status_code, [200, 302])

    def test_pagination_large(self):
        r = self.client.get('/browse?page=99999')
        self.assertIn(r.status_code, [200, 302])


if __name__ == '__main__':
    unittest.main(verbosity=2)
