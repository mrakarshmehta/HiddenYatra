"""
HiddenYatra — Smart Nearby Discovery System Automated Tests
Tests backend functions, API endpoints, travel metric calculations, and place page integrations.
"""
import unittest
from app import create_app
from models.database import (
    get_smart_nearby_discovery,
    get_10_nearby_essentials,
    compute_travel_metrics,
    TEN_ESSENTIAL_ORDER,
    get_place_by_id
)


class TestSmartNearby(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def test_compute_travel_metrics(self):
        """Test Haversine distance and walking/driving time calculations."""
        metrics = compute_travel_metrics(25.6, 85.14, 25.61, 85.15)
        self.assertIn('distance_km', metrics)
        self.assertIn('distance_formatted', metrics)
        self.assertIn('walking_time_text', metrics)
        self.assertIn('driving_time_text', metrics)
        self.assertGreater(metrics['distance_km'], 0)
        self.assertTrue('min walk' in metrics['walking_time_text'] or 'hr' in metrics['walking_time_text'])
        self.assertTrue('min drive' in metrics['driving_time_text'] or '< 1 min drive' in metrics['driving_time_text'])

    def test_get_10_nearby_essentials(self):
        """Test that get_10_nearby_essentials returns exactly 10 essential categories sorted by distance."""
        essentials = get_10_nearby_essentials(25.5941, 85.1376)
        self.assertEqual(len(essentials), 10)
        
        returned_cats = [item['category_code'] for item in essentials]
        for essential_code in TEN_ESSENTIAL_ORDER:
            self.assertIn(essential_code, returned_cats)

        # Verify items are sorted by distance ascending
        distances = [item['distance_km'] for item in essentials]
        self.assertEqual(distances, sorted(distances))

    def test_get_smart_nearby_discovery(self):
        """Test get_smart_nearby_discovery with category filters and travel metric payload."""
        results = get_smart_nearby_discovery(25.5941, 85.1376, category=None, limit=10)
        self.assertGreater(len(results), 0)
        
        first = results[0]
        self.assertIn('name', first)
        self.assertIn('category_code', first)
        self.assertIn('distance_formatted', first)
        self.assertIn('walking_time_text', first)
        self.assertIn('driving_time_text', first)
        self.assertIn('directions_url', first)
        self.assertIn('nearby_essentials', first)
        self.assertEqual(len(first['nearby_essentials']), 10)

        # Test specific category filter (e.g., hospital)
        hospitals = get_smart_nearby_discovery(25.5941, 85.1376, category='hospital', limit=5)
        for h in hospitals:
            self.assertEqual(h['category_code'], 'hospital')

    def test_api_smart_nearby_endpoint(self):
        """Test GET /api/smart-nearby endpoint."""
        res = self.client.get('/api/smart-nearby?lat=25.5941&lng=85.1376')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)

    def test_api_place_nearby_essentials_endpoint(self):
        """Test GET /api/place/<id>/nearby-essentials endpoint."""
        res = self.client.get('/api/place/1/nearby-essentials')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('essentials', data)
        self.assertEqual(len(data['essentials']), 10)

    def test_api_nearby_endpoint(self):
        """Test GET /api/nearby endpoint with lat, lng, radius, and category parameters."""
        res = self.client.get('/api/nearby?lat=25.5941&lng=85.1376&radius=5.0&category=hotel')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
        first = data['results'][0]
        self.assertIn('name', first)
        self.assertIn('distance_formatted', first)
        self.assertIn('directions_url', first)

    def test_nearby_radius_filtering_and_sorting(self):
        """Test that results from GET /api/nearby are strictly sorted nearest first and within requested radius."""
        for radius in [1.0, 2.0, 5.0, 10.0]:
            res = self.client.get(f'/api/nearby?lat=25.5941&lng=85.1376&radius={radius}')
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            results = data.get('results', [])
            distances = [item['distance_km'] for item in results]
            self.assertEqual(distances, sorted(distances))
            for d in distances:
                self.assertLessEqual(d, radius)

    def test_place_detail_page_has_nearby_essentials(self):
        """Test that tourist place page contains the Nearby Essentials section."""
        res = self.client.get('/place/golghar')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn('Nearby Essentials', html)
        self.assertIn('10 Essential Facilities', html)


if __name__ == '__main__':
    unittest.main()
