"""Place detail routes."""
import logging
from flask import Blueprint, render_template, session
from models.database import (
    get_place_by_slug, get_photos_by_place,
    get_specialties_by_place, get_nearby_places,
    get_accommodations_by_place, get_reviews_by_place,
    get_avg_rating, increment_view_count,
    get_approved_user_photos, is_wishlisted, is_visited,
    get_place_wishlist_count, get_nearby_services_for_place,
    get_service_type_icon, get_service_group, SERVICE_GROUP_ORDER,
    get_10_nearby_essentials
)
from utils import get_session_id as _get_session_id

logger = logging.getLogger(__name__)
places_bp = Blueprint('places', __name__)


@places_bp.route('/place/<slug>')
def place_detail(slug):
    """Full place detail page with gallery, map, specialties, and reviews."""
    place = get_place_by_slug(slug)
    if not place:
        return render_template('404.html'), 404

    # Increment view count
    increment_view_count(place['id'])

    photos = get_photos_by_place(place['id'])
    specialties = get_specialties_by_place(place['id'])
    accommodations = get_accommodations_by_place(place['id'])
    reviews = get_reviews_by_place(place['id'])
    rating_info = get_avg_rating(place['id'])

    # Get nearby places if coordinates exist
    nearby = []
    if place.get('latitude') and place.get('longitude'):
        nearby = get_nearby_places(
            place['latitude'], place['longitude'],
            radius_km=50, limit=6, exclude_id=place['id'],
            district_id=place.get('district_id')
        )

    # Wishlist / Visited state for current user
    sid = _get_session_id()
    wishlisted = is_wishlisted(sid, place['id'])
    visited = is_visited(sid, place['id'])

    # Stats for the place
    wishlist_count = get_place_wishlist_count(place['id'])

    place_stats = {
        'views': place.get('view_count', 0),
        'saves': wishlist_count,
        'reviews': rating_info.get('review_count', 0),
        'photos': len(photos),
        'rating': rating_info.get('avg_rating'),
    }

    # Get approved visitor photos
    user_photos = get_approved_user_photos(place['id'])

    # Get nearby essential services (grouped by type)
    nearby_services = []
    nearby_services_grouped = {}
    if place.get('district_id'):
        nearby_services = get_nearby_services_for_place(place['id'], place['district_id'])
        # Add icon & group fields for template grouping
        for svc in nearby_services:
            svc['icon'] = get_service_type_icon(svc['service_type'])
            svc['group'] = get_service_group(svc['service_type'])
        # Pre-group by category
        for g in SERVICE_GROUP_ORDER:
            nearby_services_grouped[g] = []
        for svc in nearby_services:
            grp = svc.get('group', 'Other')
            if grp not in nearby_services_grouped:
                nearby_services_grouped[grp] = []
            nearby_services_grouped[grp].append(svc)
        # Remove empty groups
        nearby_services_grouped = {k: v for k, v in nearby_services_grouped.items() if v}

    # Get 10 Nearby Essentials for place coordinates
    ten_nearby_essentials = []
    if place.get('latitude') and place.get('longitude'):
        ten_nearby_essentials = get_10_nearby_essentials(place['latitude'], place['longitude'], district_id=place.get('district_id'), place_id=place['id'])

    return render_template('place.html',
                           place=place,
                           photos=photos,
                           specialties=specialties,
                           accommodations=accommodations,
                           nearby=nearby,
                           reviews=reviews,
                           rating_info=rating_info,
                           place_stats=place_stats,
                           is_wishlisted=wishlisted,
                           is_visited=visited,
                           user_photos=user_photos,
                           nearby_services=nearby_services,
                           nearby_services_grouped=nearby_services_grouped,
                           ten_nearby_essentials=ten_nearby_essentials)
