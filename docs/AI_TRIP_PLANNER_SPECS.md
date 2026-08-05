# HiddenYatra — AI Trip Planner Specification & Architecture

## Overview

The **AI Trip Planner** is a cornerstone feature of HiddenYatra designed to generate personalized, multi-day itineraries for tourists exploring Bihar. It solves the cold-start travel planning problem by leveraging geographic clustering, category matching, and algorithmic budget estimation.

---

## 📐 Algorithmic Design

### 1. Geographic Clustering (Haversine Formula)

To ensure generated itineraries do not require excessive backtracking across distant districts, the planner groups nearby destinations together on the same day using the Haversine distance formula:

$$d = 2R \cdot \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \text{lat}}{2}\right) + \cos(\text{lat}_1) \cdot \cos(\text{lat}_2) \cdot \sin^2\left(\frac{\Delta \text{lng}}{2}\right)} \right)$$

where $R = 6371 \text{ km}$ (earth radius).

#### Clustering Pipeline:
1. Filter database records where `latitude` and `longitude` are non-null.
2. Rank destinations by interest category match and popularity view count.
3. Select top candidates ($N = \text{Days} \times 3$).
4. Apply greedy nearest-neighbor clustering to allocate 3 destinations per day.

---

## 💰 Budget Estimation Engine

The budget estimator provides transparent cost breakdowns based on historical travel data across Bihar:

| Tier | Transport / Day | Food / Day | Stay / Day | Entry Fees / Place |
|------|-----------------|------------|------------|--------------------+
| **Budget (`low`)** | ₹200 | ₹300 | ₹500 | ₹50 |
| **Standard (`medium`)** | ₹500 | ₹600 | ₹1,500 | ₹100 |
| **Premium (`high`)** | ₹1,200 | ₹1,200 | ₹4,000 | ₹200 |

### Mathematical Model:
$$\text{Total Cost} = (\text{Transport} \times D) + (\text{Food} \times D) + (\text{Stay} \times (D - 1)) + (\text{Entry} \times P)$$
where $D = \text{Trip Days}$ and $P = \text{Total Selected Places}$.

---

## 🔌 API Specification

### Endpoint: Generate Itinerary
`POST /api/itinerary/generate`

#### Request Payload (JSON):
```json
{
  "days": 3,
  "budget": "medium",
  "interests": ["temple", "historical", "nature"]
}
```

#### Response Structure (JSON):
```json
{
  "trip_name": "3-Day Bihar Explorer",
  "days": 3,
  "budget": "medium",
  "estimated_cost": {
    "transport": 1500,
    "food": 1800,
    "accommodation": 3000,
    "entry_fees": 900,
    "total": 7200
  },
  "itinerary": [
    {
      "day": 1,
      "title": "Day 1 — Patna",
      "places": [
        {
          "id": 1,
          "name": "Golghar",
          "slug": "golghar",
          "category": "historical",
          "district": "Patna",
          "time": "9:00 AM",
          "latitude": 25.62,
          "longitude": 85.1448
        }
      ]
    }
  ]
}
```

---

## 🖨️ PDF & Print Export

The Trip Planner UI includes custom print CSS (`@media print`) that formats the generated itinerary into a clean, printable document or downloadable PDF with zero page bleed, hidden navigation bars, and explicit color fills for key itinerary markers.
