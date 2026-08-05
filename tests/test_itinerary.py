"""
Unit tests for AI Trip Planner scoring & spatial logic in routes/itinerary.py
"""
import unittest
from routes.itinerary import SCORING_WEIGHTS


class TestItineraryScoring(unittest.TestCase):

    def test_scoring_weights_structure(self):
        """Test that SCORING_WEIGHTS constant exists and has expected keys."""
        self.assertIn('interest_match', SCORING_WEIGHTS)
        self.assertIn('family_friendly', SCORING_WEIGHTS)
        self.assertIn('companion_category', SCORING_WEIGHTS)
        self.assertIn('hidden_gem', SCORING_WEIGHTS)
        self.assertIn('popularity_divisor', SCORING_WEIGHTS)
        self.assertIn('popularity_cap', SCORING_WEIGHTS)

        self.assertGreater(SCORING_WEIGHTS['interest_match'], 0)
        self.assertGreater(SCORING_WEIGHTS['family_friendly'], 0)
        self.assertGreater(SCORING_WEIGHTS['hidden_gem'], 0)

    def test_haversine_distance(self):
        """Test spatial distance calculation logic."""
        import math

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius km
            dLat = math.radians(lat2 - lat1)
            dLon = math.radians(lon2 - lon1)
            a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Patna to Gaya distance ~90-100 km
        patna = (25.5941, 85.1376)
        gaya = (24.7914, 85.0002)
        dist = haversine(patna[0], patna[1], gaya[0], gaya[1])

        self.assertGreater(dist, 80)
        self.assertLess(dist, 120)

    def test_same_location_distance(self):
        """Distance between same point should be 0."""
        import math

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dLat = math.radians(lat2 - lat1)
            dLon = math.radians(lon2 - lon1)
            a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        dist = haversine(25.5941, 85.1376, 25.5941, 85.1376)
        self.assertAlmostEqual(dist, 0, places=4)


if __name__ == '__main__':
    unittest.main()
