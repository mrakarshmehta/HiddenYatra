-- ═══════════════════════════════════════════════════════════════════
-- HiddenYatra — Production MySQL Schema
-- Engine: InnoDB | Charset: utf8mb4 | Collation: utf8mb4_unicode_ci
-- Generated for MySQL 8.x
-- ═══════════════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS hiddenyatra
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hiddenyatra;

-- ──────────────────────────────────────────────
-- 1. STATES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS states (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL,
    description TEXT NOT NULL DEFAULT (''),
    image_url VARCHAR(500) NOT NULL DEFAULT '',
    sort_order INT NOT NULL DEFAULT 0,
    UNIQUE KEY uq_states_name (name),
    UNIQUE KEY uq_states_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 2. DISTRICTS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS districts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    state_id INT UNSIGNED NOT NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL,
    description TEXT NOT NULL DEFAULT (''),
    famous_for TEXT NOT NULL DEFAULT (''),
    image_url VARCHAR(500) NOT NULL DEFAULT '',
    sort_order INT NOT NULL DEFAULT 0,
    is_featured TINYINT(1) NOT NULL DEFAULT 0,
    is_visible TINYINT(1) NOT NULL DEFAULT 1,
    cover_image VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE KEY uq_districts_state_slug (state_id, slug),
    INDEX idx_districts_state (state_id),
    INDEX idx_districts_visible (is_visible, sort_order),
    INDEX idx_districts_featured (is_featured),
    CONSTRAINT fk_districts_state FOREIGN KEY (state_id) REFERENCES states(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 3. BLOCKS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS blocks (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED NOT NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL,
    UNIQUE KEY uq_blocks_district_slug (district_id, slug),
    INDEX idx_blocks_district (district_id),
    CONSTRAINT fk_blocks_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 4. PLACES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS places (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    state_id INT UNSIGNED NOT NULL,
    district_id INT UNSIGNED DEFAULT NULL,
    block_id INT UNSIGNED DEFAULT NULL,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(250) NOT NULL,
    description TEXT NOT NULL DEFAULT (''),
    category VARCHAR(50) NOT NULL DEFAULT 'tourist_spot',
    latitude DECIMAL(10,7) DEFAULT NULL,
    longitude DECIMAL(10,7) DEFAULT NULL,
    maps_link VARCHAR(500) NOT NULL DEFAULT '',
    cover_image VARCHAR(255) NOT NULL DEFAULT '',
    is_featured TINYINT(1) NOT NULL DEFAULT 0,
    is_hidden_gem TINYINT(1) NOT NULL DEFAULT 0,
    family_friendly TINYINT(1) NOT NULL DEFAULT 0,
    best_time_to_visit VARCHAR(200) NOT NULL DEFAULT '',
    entry_fee VARCHAR(200) NOT NULL DEFAULT '',
    travel_tips TEXT NOT NULL DEFAULT (''),
    history TEXT NOT NULL DEFAULT (''),
    local_tips TEXT NOT NULL DEFAULT (''),
    safety_tips TEXT NOT NULL DEFAULT (''),
    best_season VARCHAR(100) NOT NULL DEFAULT '',
    best_time_of_day VARCHAR(100) NOT NULL DEFAULT '',
    crowd_level VARCHAR(50) NOT NULL DEFAULT '',
    parking_info TEXT NOT NULL DEFAULT (''),
    nearest_railway VARCHAR(200) NOT NULL DEFAULT '',
    nearest_bus_stand VARCHAR(200) NOT NULL DEFAULT '',
    nearest_airport VARCHAR(200) NOT NULL DEFAULT '',
    road_connectivity TEXT NOT NULL DEFAULT (''),
    view_count INT UNSIGNED NOT NULL DEFAULT 0,
    deleted_at DATETIME DEFAULT NULL,
    deleted_by VARCHAR(100) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_places_slug (slug),
    INDEX idx_places_state (state_id),
    INDEX idx_places_district (district_id),
    INDEX idx_places_block (block_id),
    INDEX idx_places_category (category),
    INDEX idx_places_featured (is_featured),
    INDEX idx_places_views (view_count),
    INDEX idx_places_deleted (deleted_at),
    INDEX idx_places_featured_views (is_featured, view_count DESC),
    INDEX idx_places_created (created_at),
    FULLTEXT INDEX ft_places_search (name, description),
    CONSTRAINT fk_places_state FOREIGN KEY (state_id) REFERENCES states(id) ON DELETE CASCADE,
    CONSTRAINT fk_places_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE SET NULL,
    CONSTRAINT fk_places_block FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 5. PHOTOS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS photos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    place_id INT UNSIGNED NOT NULL,
    filename VARCHAR(255) NOT NULL,
    caption VARCHAR(500) NOT NULL DEFAULT '',
    photo_type VARCHAR(20) NOT NULL DEFAULT 'official',
    sort_order INT NOT NULL DEFAULT 0,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_photos_place (place_id),
    CONSTRAINT fk_photos_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 6. SPECIALTIES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS specialties (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    place_id INT UNSIGNED NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT (''),
    category VARCHAR(50) NOT NULL DEFAULT 'food',
    where_to_find VARCHAR(500) NOT NULL DEFAULT '',
    location_hint VARCHAR(500) NOT NULL DEFAULT '',
    latitude DECIMAL(10,7) DEFAULT NULL,
    longitude DECIMAL(10,7) DEFAULT NULL,
    distance_km DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    INDEX idx_specialties_place (place_id),
    CONSTRAINT fk_specialties_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 7. ACCOMMODATIONS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS accommodations (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    place_id INT UNSIGNED NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'hotel',
    price_range VARCHAR(100) NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT (''),
    address VARCHAR(500) NOT NULL DEFAULT '',
    phone VARCHAR(30) NOT NULL DEFAULT '',
    website VARCHAR(500) NOT NULL DEFAULT '',
    rating DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    latitude DECIMAL(10,7) DEFAULT NULL,
    longitude DECIMAL(10,7) DEFAULT NULL,
    distance_km DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    INDEX idx_accommodations_place (place_id),
    CONSTRAINT fk_accommodations_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 8. USERS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100) NOT NULL DEFAULT '',
    full_name VARCHAR(150) NOT NULL DEFAULT '',
    phone VARCHAR(20) NOT NULL DEFAULT '',
    status ENUM('pending','active','suspended','banned') NOT NULL DEFAULT 'active',
    email_verified TINYINT(1) NOT NULL DEFAULT 0,
    avatar_emoji VARCHAR(10) NOT NULL DEFAULT '🧳',
    is_admin TINYINT(1) NOT NULL DEFAULT 0,
    otp_code VARCHAR(10) DEFAULT NULL,
    otp_expires_at DATETIME DEFAULT NULL,
    otp_purpose VARCHAR(20) DEFAULT NULL,
    failed_login_count INT UNSIGNED NOT NULL DEFAULT 0,
    locked_until DATETIME DEFAULT NULL,
    last_login DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    INDEX idx_users_email (email),
    INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 9. WISHLISTS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wishlists (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    place_id INT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wishlists_session_place (session_id, place_id),
    INDEX idx_wishlists_session (session_id),
    INDEX idx_wishlists_place (place_id),
    CONSTRAINT fk_wishlists_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 10. REVIEWS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    place_id INT UNSIGNED NOT NULL,
    session_id VARCHAR(64) NOT NULL DEFAULT '',
    author_name VARCHAR(100) NOT NULL,
    rating TINYINT UNSIGNED NOT NULL,
    comment TEXT NOT NULL DEFAULT (''),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_reviews_place (place_id),
    INDEX idx_reviews_session (session_id),
    INDEX idx_reviews_created (created_at),
    CONSTRAINT fk_reviews_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 11. ITINERARIES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS itineraries (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    name VARCHAR(200) NOT NULL DEFAULT 'My Trip',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_itineraries_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 12. ITINERARY_ITEMS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS itinerary_items (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    itinerary_id INT UNSIGNED NOT NULL,
    place_id INT UNSIGNED NOT NULL,
    day_number INT UNSIGNED NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT (''),
    INDEX idx_itinerary_items_itinerary (itinerary_id),
    INDEX idx_itinerary_items_place (place_id),
    CONSTRAINT fk_itinerary_items_itinerary FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE CASCADE,
    CONSTRAINT fk_itinerary_items_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 13. USER_SUBMISSIONS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_submissions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED DEFAULT NULL,
    session_id VARCHAR(64) NOT NULL DEFAULT '',
    place_name VARCHAR(200) NOT NULL,
    district_name VARCHAR(100) NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT (''),
    short_description VARCHAR(500) NOT NULL DEFAULT '',
    category VARCHAR(50) NOT NULL DEFAULT 'tourist_spot',
    latitude DECIMAL(10,7) DEFAULT NULL,
    longitude DECIMAL(10,7) DEFAULT NULL,
    photos TEXT NOT NULL DEFAULT (''),
    submitter_name VARCHAR(100) NOT NULL DEFAULT '',
    best_time_to_visit VARCHAR(200) NOT NULL DEFAULT '',
    entry_fee VARCHAR(200) NOT NULL DEFAULT '',
    crowd_level VARCHAR(50) NOT NULL DEFAULT '',
    safety_level VARCHAR(50) NOT NULL DEFAULT '',
    local_tips TEXT NOT NULL DEFAULT (''),
    nearby_food TEXT NOT NULL DEFAULT (''),
    nearby_stay TEXT NOT NULL DEFAULT (''),
    status ENUM('pending','approved','rejected','merged') NOT NULL DEFAULT 'pending',
    admin_notes TEXT NOT NULL DEFAULT (''),
    merged_into INT UNSIGNED DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_submissions_status (status),
    INDEX idx_submissions_user (user_id),
    INDEX idx_submissions_created (created_at),
    CONSTRAINT fk_submissions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 14. VISITED_PLACES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS visited_places (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    place_id INT UNSIGNED NOT NULL,
    visited_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_visited_session_place (session_id, place_id),
    INDEX idx_visited_session (session_id),
    INDEX idx_visited_place (place_id),
    CONSTRAINT fk_visited_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 15. DISTRICT_FOODS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS district_foods (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT (''),
    category VARCHAR(50) NOT NULL DEFAULT 'food',
    image_url VARCHAR(500) NOT NULL DEFAULT '',
    best_places_to_eat TEXT NOT NULL DEFAULT (''),
    INDEX idx_district_foods_district (district_id),
    CONSTRAINT fk_district_foods_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 16. NEARBY_SERVICES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS nearby_services (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED DEFAULT NULL,
    place_id INT UNSIGNED DEFAULT NULL,
    name VARCHAR(200) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    address VARCHAR(500) DEFAULT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    latitude DECIMAL(10,7) DEFAULT NULL,
    longitude DECIMAL(10,7) DEFAULT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nearby_district (district_id),
    INDEX idx_nearby_place (place_id),
    INDEX idx_nearby_type (service_type),
    CONSTRAINT fk_nearby_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE SET NULL,
    CONSTRAINT fk_nearby_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 17. ADMIN_LOGS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50) NOT NULL DEFAULT 'submission',
    target_id INT UNSIGNED DEFAULT NULL,
    details TEXT NOT NULL DEFAULT (''),
    admin_user VARCHAR(100) NOT NULL DEFAULT 'admin',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_admin_logs_action (action),
    INDEX idx_admin_logs_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 18. HERO_MEDIA
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hero_media (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    media_type VARCHAR(20) NOT NULL DEFAULT 'image',
    title VARCHAR(200) NOT NULL DEFAULT '',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hero_active (is_active, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 19. HERO_SETTINGS (singleton row)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hero_settings (
    id INT UNSIGNED PRIMARY KEY DEFAULT 1,
    bg_type VARCHAR(30) NOT NULL DEFAULT 'slideshow',
    slideshow_interval INT UNSIGNED NOT NULL DEFAULT 6,
    transition_effect VARCHAR(30) NOT NULL DEFAULT 'fade',
    overlay_opacity DECIMAL(3,2) NOT NULL DEFAULT 0.55,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_hero_id CHECK (id = 1),
    CONSTRAINT chk_hero_opacity CHECK (overlay_opacity BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO hero_settings (id) VALUES (1);

-- ──────────────────────────────────────────────
-- 20. TRENDING_PLACES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trending_places (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    place_id INT UNSIGNED NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_trending_place (place_id),
    INDEX idx_trending_place (place_id),
    INDEX idx_trending_active (is_active, sort_order),
    CONSTRAINT fk_trending_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- 21. HOMEPAGE_SECTIONS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS homepage_sections (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    section_key VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL DEFAULT '',
    is_visible TINYINT(1) NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    max_items INT UNSIGNED NOT NULL DEFAULT 12,
    UNIQUE KEY uq_homepage_section_key (section_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO homepage_sections (section_key, title, sort_order, max_items) VALUES
    ('featured', 'Featured Destinations', 1, 8),
    ('districts', 'Explore Bihar by District', 2, 12),
    ('trending', 'Trending Right Now', 3, 8),
    ('categories', 'Explore by Category', 4, 20),
    ('map_cta', 'Explore Bihar on Map', 5, 1),
    ('community_cta', 'Know a Hidden Gem?', 6, 1);

-- ──────────────────────────────────────────────
-- 22. AUTH_APPEARANCE (singleton row)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auth_appearance (
    id INT UNSIGNED PRIMARY KEY DEFAULT 1,
    login_banner VARCHAR(255) NOT NULL DEFAULT '',
    login_mobile_image VARCHAR(255) NOT NULL DEFAULT '',
    login_title VARCHAR(100) NOT NULL DEFAULT 'Welcome Back, Explorer!',
    login_subtitle VARCHAR(200) NOT NULL DEFAULT 'Continue your journey through Bihar hidden gems.',
    login_stats TEXT NOT NULL DEFAULT ('[]'),
    login_slider_images TEXT NOT NULL DEFAULT ('[]'),
    login_slider_enabled TINYINT(1) NOT NULL DEFAULT 1,
    signup_banner VARCHAR(255) NOT NULL DEFAULT '',
    signup_mobile_image VARCHAR(255) NOT NULL DEFAULT '',
    signup_title VARCHAR(100) NOT NULL DEFAULT 'Join HiddenYatra',
    signup_subtitle VARCHAR(200) NOT NULL DEFAULT 'Start discovering Bihar hidden gems',
    signup_stats TEXT NOT NULL DEFAULT ('[]'),
    signup_slider_images TEXT NOT NULL DEFAULT ('[]'),
    signup_slider_enabled TINYINT(1) NOT NULL DEFAULT 1,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_auth_id CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO auth_appearance (id) VALUES (1);

-- ──────────────────────────────────────────────
-- 23. USER_PHOTOS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_photos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    place_id INT UNSIGNED NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    uploader_name VARCHAR(100) NOT NULL DEFAULT 'Anonymous Traveler',
    filename VARCHAR(255) NOT NULL,
    caption VARCHAR(500) NOT NULL DEFAULT '',
    status ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending',
    reviewed_by VARCHAR(100) NOT NULL DEFAULT '',
    reviewed_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_photos_place (place_id),
    INDEX idx_user_photos_status (status),
    INDEX idx_user_photos_session (session_id),
    CONSTRAINT fk_user_photos_place FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────
-- ADDITIONAL COMPOSITE INDEXES (Production Optimizations)
-- ──────────────────────────────────────────────
CREATE INDEX idx_places_slug_deleted ON places (slug, deleted_at);
CREATE INDEX idx_places_lat_lng ON places (latitude, longitude);
CREATE INDEX idx_reviews_place_created ON reviews (place_id, created_at DESC);

-- ──────────────────────────────────────────────
-- 24. SAVED_ITINERARIES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS saved_itineraries (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id INT UNSIGNED DEFAULT NULL,
    title VARCHAR(255) NOT NULL DEFAULT 'My Bihar Trip',
    days INT UNSIGNED NOT NULL DEFAULT 3,
    companion VARCHAR(50) NOT NULL DEFAULT 'solo',
    budget VARCHAR(50) NOT NULL DEFAULT 'medium',
    items_data JSON NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_itineraries_session (session_id),
    INDEX idx_itineraries_user (user_id),
    CONSTRAINT fk_itineraries_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

