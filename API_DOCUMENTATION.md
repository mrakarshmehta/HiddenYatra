# 🔌 HiddenYatra — API Documentation

## Overview

HiddenYatra exposes RESTful JSON endpoints for location discovery, AI trip planning, autocomplete, nearby services, wishlist management, and reviews.

---

## Endpoints

### 1. Autocomplete Search
- **URL:** `GET /api/autocomplete`
- **Params:** `q` (string, required)
- **Response:**
```json
{
  "status": "success",
  "results": [
    {
      "id": 1,
      "name": "Golghar",
      "slug": "golghar",
      "category": "historical",
      "district_name": "Patna",
      "type": "place"
    }
  ]
}
```

---

### 2. Smart Nearby Discovery
- **URL:** `GET /api/nearby`
- **Params:**
  - `lat` (float, required)
  - `lng` (float, required)
  - `radius` (float, default `5.0`)
  - `category` (string, optional: `hotel`, `hospital`, `petrol_pump`, `restaurant`, `atm`, `pharmacy`, `police_station`, `bus_stand`, `railway_station`, `airport`, `ev_charging`, `toilet`, `parking`)
- **Response:**
```json
{
  "status": "success",
  "latitude": 25.5941,
  "longitude": 85.1376,
  "radius_km": 5.0,
  "count": 4,
  "results": [
    {
      "id": "service_12",
      "name": "Hotel Maurya",
      "category_code": "hotel",
      "category_label": "Hotel",
      "icon": "🏨",
      "distance_formatted": "1.2 km",
      "walking_time_text": "15 min walk",
      "driving_time_text": "2 min drive",
      "directions_url": "https://www.google.com/maps/dir/?api=1&destination=25.609,85.138"
    }
  ]
}
```

---

### 3. AI Trip Itinerary Generator
- **URL:** `POST /api/itinerary/generate`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "destination": "Patna",
  "days": 3,
  "budget": "standard",
  "interests": ["historical", "nature"]
}
```
- **Response:**
```json
{
  "status": "success",
  "trip_name": "3-Day Patna Heritage Tour",
  "total_budget_estimate": 4500,
  "itinerary": [
    {
      "day": 1,
      "theme": "Historical Landmarks",
      "places": [
        {
          "name": "Golghar",
          "category": "historical",
          "timings": "10:00 AM - 5:00 PM"
        }
      ]
    }
  ]
}
```

---

### 4. Health Check
- **URL:** `GET /health`
- **Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2026-08-05T18:45:00Z"
}
```
