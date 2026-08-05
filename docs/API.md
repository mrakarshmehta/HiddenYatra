# HiddenYatra — API Documentation

## Base URL

```
http://localhost:5000
```

## Authentication

| Endpoint Type | Auth Method |
|---|---|
| Public API | None required |
| User actions (review, wishlist) | Session-based (auto `_session_id`) |
| Admin endpoints | `session['admin_logged_in'] = True` |

All POST requests require a valid CSRF token via `_csrf_token` form field or `X-CSRF-Token` header.

---

## Public Pages

| Method | Route | Description |
|---|---|---|
| GET | `/` | Homepage |
| GET | `/browse` | Browse places (paginated) |
| GET | `/search?q=...` | Search results |
| GET | `/explore` | Interactive map |
| GET | `/food-culture` | Food & culture page |
| GET | `/state/{slug}` | State detail |
| GET | `/state/{state_slug}/{district_slug}` | District detail |
| GET | `/state/{state_slug}/{district_slug}/{block_slug}` | Block detail |
| GET | `/place/{slug}` | Place detail page |

---

## JSON API Endpoints

### `GET /api/autocomplete?q={query}`
Quick search autocomplete (min 2 chars).

**Response** (200):
```json
[
  {
    "id": 1,
    "name": "Bodh Gaya",
    "slug": "bodh-gaya",
    "state_name": "Bihar",
    "district_name": "Gaya",
    "category": "temple"
  }
]
```

### `GET /api/smart-search?q={query}`
Natural language search (e.g., "I am going to Patna").

**Response** (200):
```json
{
  "query": "Patna",
  "places": [...],
  "foods": [...],
  "hotels": [...]
}
```

### `GET /api/trending`
Get trending places.

**Response** (200):
```json
[
  {
    "id": 1,
    "name": "Bodh Gaya",
    "slug": "bodh-gaya",
    "state_name": "Bihar",
    "category": "temple",
    "cover_image": "bodh_gaya.jpg"
  }
]
```

### `GET /api/reviews/{place_id}?limit=20&offset=0`
Get reviews for a place (paginated, max 100 per page).

**Response** (200):
```json
[
  {
    "id": 1,
    "place_id": 5,
    "author_name": "Traveler",
    "rating": 5,
    "comment": "Amazing!",
    "created_at": "2026-01-15T10:30:00"
  }
]
```

### `POST /api/visited/{place_id}`
Toggle visited status. Requires CSRF token.

**Response** (200):
```json
{ "status": "marked" }
// or
{ "status": "unmarked" }
```

### `GET /api/visited/{place_id}`
Check if a place is visited.

**Response** (200):
```json
{ "visited": true }
```

### `GET /api/nearby-services/{place_id}?lat={lat}&lng={lng}`
Get nearby services grouped by category.

**Response** (200):
```json
{
  "services": {
    "Food & Dining": [
      {
        "id": 1,
        "name": "Bihar Hotel",
        "service_type": "restaurant",
        "icon": "🍽️",
        "address": "Main Road, Patna",
        "phone": "+91-...",
        "distance_km": 1.2
      }
    ]
  }
}
```

**Error** (400): `{ "error": "lat and lng required" }`

---

## Auth Routes

| Method | Route | Description |
|---|---|---|
| GET | `/login` | Login page |
| POST | `/login` | Process login |
| GET | `/signup` | Signup page |
| POST | `/signup` | Process signup |
| GET | `/logout` | Logout |
| POST | `/verify-otp` | Verify email OTP |
| POST | `/resend-otp` | Resend OTP |
| GET | `/profile` | User profile |

---

## Wishlist Routes

| Method | Route | Description |
|---|---|---|
| GET | `/wishlist` | View wishlist |
| POST | `/wishlist/toggle/{place_id}` | Add/remove from wishlist |
| GET | `/wishlist/count` | Get wishlist count |

---

## Review Routes

| Method | Route | Description |
|---|---|---|
| POST | `/review/{place_id}` | Submit review |
| POST | `/review/edit/{review_id}` | Edit own review |
| POST | `/review/delete/{review_id}` | Delete own review |

---

## Itinerary Routes

| Method | Route | Description |
|---|---|---|
| GET | `/itinerary` | View all trips |
| POST | `/itinerary/create` | Create new trip |
| GET | `/itinerary/{id}` | View trip details |
| POST | `/itinerary/{id}/add` | Add place to trip |
| POST | `/itinerary/{id}/remove/{item_id}` | Remove item |
| POST | `/itinerary/{id}/delete` | Delete trip |

---

## Community Routes

| Method | Route | Description |
|---|---|---|
| GET | `/suggest` | Suggest a place page |
| POST | `/suggest` | Submit suggestion |
| GET | `/my-submissions` | View own submissions |
| POST | `/suggest/upload-temp` | Temp image upload (AJAX) |

---

## Admin Routes (require `admin_logged_in` session)

| Method | Route | Description |
|---|---|---|
| GET/POST | `/admin/login` | Admin login |
| GET | `/admin/` | Dashboard |
| POST | `/admin/add` | Add place |
| POST | `/admin/edit/{id}` | Edit place |
| POST | `/admin/delete/{id}` | Soft-delete place |
| GET | `/admin/submissions` | Moderation queue |
| POST | `/admin/submissions/approve/{id}` | Approve submission |
| POST | `/admin/submissions/reject/{id}` | Reject submission |
| GET | `/admin/users` | User management |
| GET | `/admin/recycle-bin` | Deleted places |
| POST | `/admin/restore/{id}` | Restore place |
| GET | `/admin/hero-media` | Hero media manager |
| GET | `/admin/districts` | District manager |
| GET | `/admin/trending` | Trending manager |

---

## SEO Routes

| Method | Route | Description |
|---|---|---|
| GET | `/robots.txt` | Robots directives |
| GET | `/sitemap.xml` | XML sitemap |

---

## Error Responses

| Code | Description |
|---|---|
| 403 | Forbidden (CSRF failure, unauthorized) |
| 404 | Not found |
| 413 | File too large (>16MB) |
| 500 | Internal server error |

JSON API endpoints return JSON errors:
```json
{ "error": "Error description" }
```
