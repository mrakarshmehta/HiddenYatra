"""Itinerary routes — build multi-day trip plans."""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

from models.database import (
    save_itinerary, create_itinerary, get_itineraries, get_itinerary_by_id,
    get_itinerary_items, add_itinerary_item, remove_itinerary_item,
    delete_itinerary, get_place_by_id, search_places
)
from utils import csrf_required, get_session_id as _get_session_id

logger = logging.getLogger(__name__)
itinerary_bp = Blueprint('itinerary', __name__)


@itinerary_bp.route('/itinerary')
def itinerary_page():
    sid = _get_session_id()
    itineraries = get_itineraries(sid)
    return render_template('itinerary.html', itineraries=itineraries)


@itinerary_bp.route('/itinerary/create', methods=['POST'])
@csrf_required
def create_trip():
    sid = _get_session_id()
    name = request.form.get('name', '').strip() or 'My Trip'
    uid = session.get('user_id')
    iid = save_itinerary(session_id=sid, user_id=uid, title=name, days=2, companion='solo', budget='medium', items_data=[])
    flash(f'🗺️ Trip "{name}" created!', 'success')
    return redirect(url_for('itinerary.itinerary_page'))


@itinerary_bp.route('/itinerary/<int:itinerary_id>')
def view_trip(itinerary_id):
    sid = _get_session_id()
    trip = get_itinerary_by_id(itinerary_id, sid)
    if not trip:
        flash('Trip not found.', 'error')
        return redirect(url_for('itinerary.itinerary_page'))
    items = get_itinerary_items(itinerary_id)
    # Group items by day
    days = {}
    for item in items:
        day = item['day_number']
        if day not in days:
            days[day] = []
        days[day].append(item)
    return render_template('itinerary_detail.html', trip=trip, days=days, items=items)


@itinerary_bp.route('/itinerary/<int:itinerary_id>/add', methods=['POST'])
@csrf_required
def add_place_to_trip(itinerary_id):
    sid = _get_session_id()
    trip = get_itinerary_by_id(itinerary_id, sid)
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404

    place_id = request.form.get('place_id', type=int)
    day_number = request.form.get('day_number', 1, type=int)
    notes = request.form.get('notes', '').strip()

    if place_id:
        add_itinerary_item(itinerary_id, place_id, day_number, notes)
        flash('Place added to your trip! 🎉', 'success')

    return redirect(url_for('itinerary.view_trip', itinerary_id=itinerary_id))


@itinerary_bp.route('/itinerary/<int:itinerary_id>/remove/<int:item_id>', methods=['POST'])
@csrf_required
def remove_place_from_trip(itinerary_id, item_id):
    sid = _get_session_id()
    trip = get_itinerary_by_id(itinerary_id, sid)
    if not trip:
        flash('Trip not found or access denied.', 'error')
        return redirect(url_for('itinerary.itinerary_page'))
    # Verify item belongs to this itinerary
    items = get_itinerary_items(itinerary_id)
    item_ids = {item['id'] for item in items}
    if item_id not in item_ids:
        flash('Item not found in this trip.', 'error')
        return redirect(url_for('itinerary.view_trip', itinerary_id=itinerary_id))
    remove_itinerary_item(item_id)
    return redirect(url_for('itinerary.view_trip', itinerary_id=itinerary_id))


@itinerary_bp.route('/itinerary/<int:itinerary_id>/delete', methods=['POST'])
@csrf_required
def delete_trip(itinerary_id):
    sid = _get_session_id()
    delete_itinerary(itinerary_id, sid)
    flash('Trip deleted.', 'info')
    return redirect(url_for('itinerary.itinerary_page'))


@itinerary_bp.route('/api/itinerary/search')
def api_search_places():
    """Search places for adding to itinerary."""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
    results = search_places(q, limit=10)
    return jsonify([{
        'id': p['id'], 'name': p['name'], 'slug': p['slug'],
        'state_name': p['state_name'], 'category': p['category']
    } for p in results])


# ── Scoring weights — externalized for tuning without code changes ──
SCORING_WEIGHTS = {
    'interest_match': 6.0,
    'family_friendly': 4.0,
    'family_category': 2.5,
    'companion_category': 3.5,
    'hidden_gem': 2.0,
    'popularity_divisor': 40.0,
    'popularity_cap': 200,
}


@itinerary_bp.route('/api/itinerary/generate', methods=['POST'])
@csrf_required
def api_generate_trip():
    """AI Trip Planner — generates an optimized, realistic multi-day itinerary.
    Uses Haversine spatial clustering, companion scoring, and district food/hotel matching.
    """
    import math
    from models.database import get_cursor, get_district_foods, get_accommodations_by_place

    data = request.get_json() or {}
    days = min(max(int(data.get('days', 3)), 1), 7)
    interests = data.get('interests', [])
    budget = data.get('budget', 'medium')  # low, medium, high
    companion = data.get('companion', 'solo')  # solo, couple, family, group

    # Fetch all active places with coordinates and district info
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.id, p.name, p.slug, p.category, p.latitude, p.longitude,
                   p.description, p.cover_image, p.view_count, p.family_friendly, p.is_hidden_gem,
                   p.best_season, p.best_time_to_visit, p.district_id,
                   d.name AS district_name, s.name AS state_name
            FROM places p
            JOIN districts d ON p.district_id = d.id
            JOIN states s ON d.state_id = s.id
            WHERE p.deleted_at IS NULL
              AND p.latitude IS NOT NULL AND p.longitude IS NOT NULL
            ORDER BY p.view_count DESC
        """)
        all_places = cur.fetchall()

    if not all_places:
        return jsonify({'error': 'No places available for itinerary generation'}), 404

    W = SCORING_WEIGHTS  # alias for readability

    # Companion-mode filtering & scoring
    scored = []
    for p in all_places:
        score = 1.0
        cat = p.get('category', 'tourist_spot')

        # User interests bonus
        if interests and cat in interests:
            score += W['interest_match']

        # Companion mode bonuses
        if companion == 'family':
            if p.get('family_friendly'): score += W['family_friendly']
            if cat in ['park', 'temple', 'tourist_spot', 'historical']: score += W['family_category']
        elif companion == 'couple':
            if cat in ['hill_station', 'waterfall', 'lake', 'nature', 'historical', 'hidden_gem']: score += W['companion_category']
        elif companion == 'solo':
            if cat in ['fort', 'wildlife', 'hidden_gem', 'waterfall', 'nature']: score += W['companion_category']
        elif companion == 'group':
            if cat in ['fort', 'waterfall', 'lake', 'tourist_spot', 'hidden_gem']: score += W['companion_category']

        # Hidden gem bonus
        if p.get('is_hidden_gem'):
            score += W['hidden_gem']

        # Popularity score weight
        score += min((p.get('view_count') or 0), W['popularity_cap']) / W['popularity_divisor']
        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])
    candidate_pool = [s[1] for s in scored]

    # Haversine Distance Helper (km)
    def haversine(lat1, lng1, lat2, lng2):
        R = 6371
        dlat = math.radians(float(lat2) - float(lat1))
        dlng = math.radians(float(lng2) - float(lng1))
        a = (math.sin(dlat/2)**2 +
             math.cos(math.radians(float(lat1))) *
             math.cos(math.radians(float(lat2))) *
             math.sin(dlng/2)**2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) if a < 1 else 0

    # Cluster-based Day Assignment
    places_per_day = 3
    used_ids = set()
    day_plans = []

    for day in range(1, days + 1):
        day_places = []
        
        # Find highest-scoring unvisited place as Day Anchor
        anchor = None
        for p in candidate_pool:
            if p['id'] not in used_ids:
                anchor = p
                break

        if not anchor:
            break

        day_places.append(anchor)
        used_ids.add(anchor['id'])

        # Find closest unvisited places within 45km radius of the Day Anchor
        while len(day_places) < places_per_day:
            last = day_places[-1]
            candidates = []

            for p in candidate_pool:
                if p['id'] in used_ids:
                    continue
                # Calculate distance from current last place in day
                dist_from_last = haversine(last['latitude'], last['longitude'], p['latitude'], p['longitude'])
                # Calculate distance from day anchor
                dist_from_anchor = haversine(anchor['latitude'], anchor['longitude'], p['latitude'], p['longitude'])

                if dist_from_anchor <= 50.0:  # Max 50km cluster radius
                    candidates.append((dist_from_last, p))

            if candidates:
                candidates.sort(key=lambda x: x[0])  # Sort by proximity to last place
                best_place = candidates[0][1]
                day_places.append(best_place)
                used_ids.add(best_place['id'])
            else:
                # If no place within 50km, pick next closest place overall
                next_best = None
                min_dist = float('inf')
                for p in candidate_pool:
                    if p['id'] not in used_ids:
                        d = haversine(last['latitude'], last['longitude'], p['latitude'], p['longitude'])
                        if d < min_dist:
                            min_dist = d
                            next_best = p
                if next_best:
                    day_places.append(next_best)
                    used_ids.add(next_best['id'])
                else:
                    break

        day_plans.append(day_places)

    # Budget & Pricing Engine
    companion_mult = {'solo': 1.0, 'couple': 1.6, 'family': 2.4, 'group': 3.2}.get(companion, 1.0)
    budget_rates = {
        'low': {'transport': 250, 'food': 350, 'stay': 600, 'entry': 50},
        'medium': {'transport': 600, 'food': 700, 'stay': 1800, 'entry': 100},
        'high': {'transport': 1400, 'food': 1400, 'stay': 4500, 'entry': 250},
    }
    rates = budget_rates.get(budget, budget_rates['medium'])
    total_budget = {
        'transport': int(rates['transport'] * days * (1.3 if companion in ['family', 'group'] else 1.0)),
        'food': int(rates['food'] * days * companion_mult),
        'accommodation': int(rates['stay'] * max(days - 1, 1) * (1.6 if companion == 'group' else (1.4 if companion == 'family' else (1.2 if companion == 'couple' else 1.0)))),
        'entry_fees': int(rates['entry'] * sum(len(d) for d in day_plans) * (2.2 if companion == 'group' else (1.8 if companion == 'family' else (1.4 if companion == 'couple' else 1.0)))),
    }
    total_budget['total'] = sum(total_budget.values())

    companion_labels = {
        'solo': 'Solo Explorer 👤',
        'couple': 'Couple Getaway 👩‍❤️‍👨',
        'family': 'Family Trip 👨‍👩‍👧‍👦',
        'group': 'Group Trip 👥'
    }

    result = {
        'trip_name': f"{days}-Day Bihar {companion_labels.get(companion, 'Explorer')} Itinerary",
        'days': days,
        'budget': budget,
        'companion': companion,
        'estimated_cost': total_budget,
        'itinerary': []
    }

    # Time slot templates
    time_slots = [
        {'time': '09:00 AM', 'phase': 'Morning Exploration'},
        {'time': '01:00 PM', 'phase': 'Afternoon Visit & Lunch'},
        {'time': '04:30 PM', 'phase': 'Evening Sightseeing'}
    ]

    for day_num, day_places in enumerate(day_plans, 1):
        districts = list(dict.fromkeys(p.get('district_name', '') for p in day_places if p.get('district_name')))
        district_text = ', '.join(districts) if districts else 'Bihar'

        day_data = {
            'day': day_num,
            'title': f"Day {day_num} — {district_text}",
            'pacing_note': f"Cluster tour in {district_text} • Short travel time between locations",
            'places': [],
            'recommended_foods': [],
            'recommended_hotels': []
        }

        if day_places:
            # Fetch local foods for visited districts
            district_ids = [p.get('district_id') for p in day_places if p.get('district_id')]
            foods = []
            for did in district_ids:
                df = get_district_foods(did)
                if df: foods.extend(df[:2])

            # Fallback if no specific district foods
            if not foods:
                foods = [
                    {'name': 'Litti Chokha', 'description': 'Traditional roasted wheat balls stuffed with sattu, served with spiced brinjal and mashed potato.'},
                    {'name': 'Khaja', 'description': 'Crispy layered sweet delicacy from Silao, GI-tagged authentic Bihari treat.'},
                    {'name': 'Tilkut', 'description': 'Sesame seed and jaggery brittle specialty from Gaya.'}
                ]

            day_data['recommended_foods'] = [{'name': f['name'], 'description': (f.get('description') or '')[:90]} for f in foods[:3]]

            # Fetch hotels/stays for main day place
            main_p = day_places[0]
            hotels = get_accommodations_by_place(main_p['id']) if main_p else []
            if not hotels:
                # Honest fallback — don't fabricate hotel names
                hotels = [
                    {'name': f"Explore local stays in {district_text}", 'price_range': f"~₹{rates['stay']}/night (estimated)", 'rating': None},
                ]
            day_data['recommended_hotels'] = [{'name': h['name'], 'price_range': h.get('price_range', f"₹{rates['stay']}/night"), 'rating': h.get('rating')} for h in hotels[:2]]

        for order, place in enumerate(day_places):
            slot = time_slots[order] if order < len(time_slots) else {'time': '06:00 PM', 'phase': 'Evening Visit'}
            day_data['places'].append({
                'id': place['id'],
                'name': place['name'],
                'slug': place['slug'],
                'category': place['category'],
                'district': place.get('district_name', ''),
                'description': (place.get('description', '') or '')[:180],
                'cover_image': place.get('cover_image', ''),
                'time': slot['time'],
                'phase': slot['phase'],
                'latitude': float(place['latitude']) if place['latitude'] else None,
                'longitude': float(place['longitude']) if place['longitude'] else None,
            })

        result['itinerary'].append(day_data)

    return jsonify(result)


@itinerary_bp.route('/api/itinerary/save-generated', methods=['POST'])
@csrf_required
def api_save_generated():
    """Save an AI-generated itinerary to the user's trips."""
    sid = _get_session_id()
    data = request.get_json() or {}
    trip_name = data.get('name', 'AI Generated Trip')
    itinerary_data = data.get('itinerary', [])

    iid = create_itinerary(sid, trip_name)

    for day in itinerary_data:
        day_num = day.get('day', 1)
        for order, place in enumerate(day.get('places', [])):
            place_id = place.get('id')
            if place_id:
                add_itinerary_item(iid, place_id, day_num, place.get('time', ''))

    return jsonify({'id': iid, 'redirect': url_for('itinerary.view_trip', itinerary_id=iid)})

