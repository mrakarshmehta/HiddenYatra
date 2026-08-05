# HiddenYatra — Database Data Dictionary

## Overview

The HiddenYatra database is built on **MySQL 8.4** using the `InnoDB` storage engine with `utf8mb4` character encoding. It contains **23 tables** managing tourism destinations, geographical hierarchies, administrative roles, user submissions, reviews, saved trips, and nearby facilities.

---

## 📊 Complete Table Specifications

### 1. `places` (Core Destination Entity)
| Column | Type | Nullable | Key | Default | Description |
|--------|------|----------|-----|---------|-------------|
| `id` | `INT UNSIGNED` | NO | PRI | AUTO_INCREMENT | Unique Place Identifier |
| `name` | `VARCHAR(200)` | NO | | NULL | Full place name |
| `slug` | `VARCHAR(200)` | NO | UNI | NULL | URL-safe slug |
| `category` | `VARCHAR(50)` | NO | MUL | 'tourist_spot' | Category enum code |
| `district_id` | `INT UNSIGNED` | NO | MUL | NULL | Foreign Key -> `districts(id)` |
| `block_id` | `INT UNSIGNED` | YES | MUL | NULL | Foreign Key -> `blocks(id)` |
| `latitude` | `DECIMAL(10,7)`| YES | | NULL | GPS latitude |
| `longitude`| `DECIMAL(10,7)`| YES | | NULL | GPS longitude |
| `description`| `TEXT` | YES | | NULL | Long description |
| `cover_image`| `VARCHAR(500)`| YES | | NULL | Main cover image URL |
| `is_hidden_gem`| `TINYINT(1)`| NO | | 0 | Flag for hidden gem badge |
| `is_featured` | `TINYINT(1)`| NO | | 0 | Flag for homepage feature |
| `view_count` | `INT UNSIGNED`| NO | | 0 | Lifetime page views |
| `created_at` | `DATETIME` | NO | | CURRENT_TIMESTAMP | Creation timestamp |

---

### 2. `photos` (Official Place Gallery)
| Column | Type | Nullable | Key | Default | Description |
|--------|------|----------|-----|---------|-------------|
| `id` | `INT UNSIGNED` | NO | PRI | AUTO_INCREMENT | Unique Photo ID |
| `place_id` | `INT UNSIGNED` | NO | MUL | NULL | Foreign Key -> `places(id)` |
| `filename` | `VARCHAR(500)` | NO | | NULL | Image URL or static file path |
| `caption` | `VARCHAR(500)` | NO | | '' | Photo caption |
| `photo_type`| `VARCHAR(20)` | NO | | 'official' | Type ('official', 'user') |
| `sort_order`| `INT` | NO | | 0 | Display sequence order |

---

### 3. `nearby_services` (Essential Facilities)
| Column | Type | Nullable | Key | Default | Description |
|--------|------|----------|-----|---------|-------------|
| `id` | `INT UNSIGNED` | NO | PRI | AUTO_INCREMENT | Facility ID |
| `district_id`| `INT UNSIGNED` | YES | MUL | NULL | District Foreign Key |
| `place_id` | `INT UNSIGNED` | YES | MUL | NULL | Optional Place Foreign Key |
| `name` | `VARCHAR(200)` | NO | | NULL | Facility Name |
| `service_type`| `VARCHAR(50)`| NO | MUL | NULL | Code (hospital, atm, hotel, etc.) |
| `phone` | `VARCHAR(30)` | YES | | NULL | Contact phone number |
| `latitude` | `DECIMAL(10,7)`| YES | | NULL | Facility Latitude |
| `longitude`| `DECIMAL(10,7)`| YES | | NULL | Facility Longitude |

---

### 4. `reviews` (Visitor Feedback)
| Column | Type | Nullable | Key | Default | Description |
|--------|------|----------|-----|---------|-------------|
| `id` | `INT UNSIGNED` | NO | PRI | AUTO_INCREMENT | Review ID |
| `place_id` | `INT UNSIGNED` | NO | MUL | NULL | Foreign Key -> `places(id)` |
| `session_id`| `VARCHAR(64)` | NO | MUL | '' | User session identifier |
| `author_name`| `VARCHAR(100)`| NO | | NULL | Reviewer name |
| `rating` | `TINYINT UNSIGNED`| NO | | NULL | Star rating (1-5) |
| `comment` | `TEXT` | NO | | '' | Review text content |

---

### 5. `specialties` (Place Features & Local Food)
| Column | Type | Nullable | Key | Default | Description |
|--------|------|----------|-----|---------|-------------|
| `id` | `INT UNSIGNED` | NO | PRI | AUTO_INCREMENT | Specialty ID |
| `place_id` | `INT UNSIGNED` | NO | MUL | NULL | Foreign Key -> `places(id)` |
| `name` | `VARCHAR(200)` | NO | | NULL | Specialty Title |
| `description`| `TEXT` | NO | | '' | Specialty Description |
| `category` | `VARCHAR(50)` | NO | | 'attraction'| Type ('attraction', 'food') |

---

## 🔗 Relational Schema Map

```
  [ states ]
      │ (1:N)
      ▼
  [ districts ]
   ├───(1:N)────> [ blocks ]
   │                 │ (1:N)
   ├───(1:N)────┐    ▼
   │            └─> [ places ] <───────(1:N)────── [ photos ]
   │                   │ (1:N)
   │                   ├───────────────(1:N)────── [ reviews ]
   │                   ├───────────────(1:N)────── [ specialties ]
   │                   └───────────────(1:N)────── [ itinerary_items ]
   ▼
[ nearby_services ]
```
