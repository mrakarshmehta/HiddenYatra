-- ═══════════════════════════════════════════════════════════════════
-- HiddenYatra — MySQL Rollback Script
-- Drops all tables in correct dependency order
-- ═══════════════════════════════════════════════════════════════════

USE hiddenyatra;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS user_photos;
DROP TABLE IF EXISTS auth_appearance;
DROP TABLE IF EXISTS homepage_sections;
DROP TABLE IF EXISTS trending_places;
DROP TABLE IF EXISTS hero_settings;
DROP TABLE IF EXISTS hero_media;
DROP TABLE IF EXISTS admin_logs;
DROP TABLE IF EXISTS nearby_services;
DROP TABLE IF EXISTS district_foods;
DROP TABLE IF EXISTS visited_places;
DROP TABLE IF EXISTS user_submissions;
DROP TABLE IF EXISTS itinerary_items;
DROP TABLE IF EXISTS itineraries;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS wishlists;
DROP TABLE IF EXISTS accommodations;
DROP TABLE IF EXISTS specialties;
DROP TABLE IF EXISTS photos;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS blocks;
DROP TABLE IF EXISTS districts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS states;

SET FOREIGN_KEY_CHECKS = 1;
