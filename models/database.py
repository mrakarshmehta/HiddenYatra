"""
Database layer for HiddenYatra — Backward Compatibility Shim.
Re-exports all database domain modules for seamless compatibility:
  - models.connection (pool & context manager)
  - models.constants (categories & display labels)
  - models.auth (user accounts & authentication)
  - models.places (places, photos, specialties, accommodations, search)
  - models.districts (states, districts, blocks)
  - models.reviews (reviews & ratings)
  - models.wishlists (wishlist & visited places)
  - models.itineraries (saved itineraries)
  - models.services (nearby services, hero media, homepage sections)
  - models.admin_db (submissions moderation, audit logs, analytics)
"""

from models.connection import (
    get_db, get_cursor, init_db, slugify, _slugify, _escape_like
)
from models.constants import (
    PLACE_CATEGORIES, SPECIALTY_CATEGORIES, ACCOMMODATION_TYPES,
    SERVICE_GROUP_ORDER, get_category_label
)
from models.auth import (
    hash_password, verify_password, upgrade_password_hash, register_user,
    login_user, get_user_by_id, get_user_by_email, activate_user,
    update_user_status, update_user_password, search_users, count_users,
    get_all_users, delete_user
)
from models.places import (
    get_all_places, get_featured_places, get_recent_places, get_trending_places,
    get_place_by_slug, get_place_by_id, get_places_by_state, get_places_by_district,
    count_places_in_district, get_places_by_block, count_places_in_block,
    increment_view_count, create_place, update_place, update_place_extra_fields,
    quick_edit_place, set_place_cover, clear_place_cover_if_match, delete_place,
    soft_delete_place, restore_place, permanent_delete_place, get_deleted_places,
    count_places, count_deleted_places, get_photos_by_place, add_photo, delete_photo,
    get_specialties_by_place, add_specialty, delete_specialty, delete_specialties_by_place,
    get_accommodations_by_place, add_accommodation, delete_accommodations_by_place,
    get_district_foods, get_all_district_foods_by_state, add_district_food,
    delete_district_food, search_places, search_all, smart_search, nl_search, search_places_simple,
    get_nearby_places, get_places_for_map
)
from models.districts import (
    get_all_states, get_state_by_slug, get_state_by_id, create_state, update_state_image,
    get_districts_by_state, create_district, get_district_by_id, get_district_by_slug,
    get_all_districts_admin, update_district, delete_district, reorder_districts,
    get_districts_for_homepage, get_featured_districts, get_blocks_by_district,
    get_blocks_grouped_by_district, create_block, get_block_by_slug
)
from models.reviews import (
    add_review, get_reviews_by_place, get_review_by_id, update_review,
    delete_review, get_avg_rating, count_reviews_by_session
)
from models.wishlists import (
    add_to_wishlist, remove_from_wishlist, is_wishlisted, get_wishlist,
    get_wishlist_count, get_place_wishlist_count, mark_visited, unmark_visited,
    is_visited, get_visited_places, get_visited_count
)
from models.itineraries import (
    save_itinerary, create_itinerary, get_user_itineraries, get_itineraries,
    get_itinerary_by_id, get_itinerary_items, add_itinerary_item,
    remove_itinerary_item, delete_itinerary
)
from models.services import (
    SERVICE_TYPE_LABELS, get_service_type_icon, get_service_group,
    get_nearby_services_with_distance, get_nearby_services_for_place,
    get_nearby_services_admin, add_nearby_service, delete_nearby_service,
    get_trending_admin, add_to_trending, remove_from_trending, toggle_trending,
    reorder_trending, get_trending_for_homepage, get_homepage_sections,
    update_homepage_section, get_hero_media_active, get_hero_media_all,
    add_hero_media, delete_hero_media, toggle_hero_media, reorder_hero_media,
    get_hero_settings, update_hero_settings, get_auth_appearance, update_auth_appearance,
    get_smart_nearby_discovery, get_10_nearby_essentials, compute_travel_metrics, SMART_DISCOVERY_CATEGORIES, TEN_ESSENTIAL_ORDER,
    get_nearby_api_data, fetch_overpass_nearby
)
from models.admin_db import (
    submit_place, get_user_submissions, get_pending_submissions, get_all_submissions,
    get_submission_by_id, count_pending_submissions, delete_submission,
    approve_submission, reject_submission, find_duplicates_for_submission,
    get_filtered_submissions, merge_submissions, update_submission,
    replace_place_with_submission, log_admin_action, get_admin_logs,
    add_user_photo, get_approved_user_photos, get_pending_user_photos,
    get_all_user_photos_admin, get_user_photos_by_status, approve_user_photo, reject_user_photo,
    delete_user_photo, count_pending_user_photos, get_stats, get_dashboard_analytics,
    get_place_edit_history, get_sitemap_districts, get_admin_districts_list
)
