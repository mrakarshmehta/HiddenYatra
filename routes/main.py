"""Public page routes — home, browse, search, district, block, explore map, food & culture."""
from flask import Blueprint, render_template, request
from models.database import (
    get_all_states, get_state_by_slug, get_featured_places,
    get_recent_places, get_places_by_state, get_districts_by_state,
    get_blocks_by_district, get_blocks_grouped_by_district,
    get_district_by_slug, get_block_by_slug,
    get_places_by_district, get_places_by_block, count_places_in_block,
    search_places, search_all, smart_search, get_stats, get_places_for_map,
    get_trending_places, get_district_foods, get_all_district_foods_by_state,
    get_hero_media_active, get_hero_settings,
    get_districts_for_homepage, get_featured_districts,
    get_trending_for_homepage, get_homepage_sections,
    count_places_in_district,
    PLACE_CATEGORIES
)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page — Bihar-focused with hero, districts, trending, food preview."""
    featured = get_featured_places(limit=8)
    states = get_all_states()
    stats = get_stats()

    # Dynamic districts from admin ordering
    districts = get_districts_for_homepage(limit=12)
    featured_districts = get_featured_districts()

    # Dynamic trending: admin-managed if available, fallback to auto
    trending = get_trending_for_homepage(limit=8)
    if not trending:
        trending = get_trending_places(limit=8)

    # Hero media from admin
    hero_media = get_hero_media_active()
    hero_settings = get_hero_settings()

    # Homepage section settings
    hp_sections = get_homepage_sections()
    sections = {s['section_key']: s for s in hp_sections}

    # Get Bihar state
    bihar = get_state_by_slug('bihar')

    return render_template('index.html',
                           featured=featured,
                           trending=trending,
                           states=states,
                           stats=stats,
                           districts=districts,
                           featured_districts=featured_districts,
                           bihar=bihar,
                           categories=PLACE_CATEGORIES,
                           hero_media=hero_media,
                           hero_settings=hero_settings,
                           sections=sections)


@main_bp.route('/browse')
def browse():
    """Browse all states."""
    states = get_all_states()
    return render_template('browse.html', states=states)


@main_bp.route('/state/<slug>')
def state_detail(slug):
    """State detail page with hierarchical district/block display."""
    state = get_state_by_slug(slug)
    if not state:
        return render_template('404.html'), 404

    places = get_places_by_state(state['id'])
    districts = get_districts_by_state(state['id'])

    # Enrich districts with blocks data (single batch query instead of N+1)
    blocks_map = get_blocks_grouped_by_district(state['id'])
    for district in districts:
        district['blocks'] = blocks_map.get(district['id'], [])

    # Group places by category
    category_filter = request.args.get('category', '')
    if category_filter:
        places = [p for p in places if p['category'] == category_filter]

    stats = get_stats()

    return render_template('state.html',
                           state=state,
                           places=places,
                           districts=districts,
                           categories=PLACE_CATEGORIES,
                           current_category=category_filter,
                           stats=stats)


@main_bp.route('/state/<state_slug>/<district_slug>')
def district_detail(state_slug, district_slug):
    """District detail page showing blocks, places, foods."""
    state = get_state_by_slug(state_slug)
    if not state:
        return render_template('404.html'), 404

    district = get_district_by_slug(state['id'], district_slug)
    if not district:
        return render_template('404.html'), 404

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    total = count_places_in_district(district['id'])
    blocks = get_blocks_by_district(district['id'])
    places = get_places_by_district(district['id'], limit=per_page, offset=offset)
    foods = get_district_foods(district['id'])

    # Related districts (same state, excluding current)
    all_districts = get_districts_by_state(state['id'])
    related_districts = [d for d in all_districts if d['id'] != district['id']]

    return render_template('district.html',
                           state=state,
                           district=district,
                           blocks=blocks,
                           places=places,
                           foods=foods,
                           related_districts=related_districts,
                           page=page,
                           per_page=per_page,
                           total=total)


@main_bp.route('/state/<state_slug>/<district_slug>/<block_slug>')
def block_detail(state_slug, district_slug, block_slug):
    """Block detail page showing places within the block."""
    state = get_state_by_slug(state_slug)
    if not state:
        return render_template('404.html'), 404

    district = get_district_by_slug(state['id'], district_slug)
    if not district:
        return render_template('404.html'), 404

    block = get_block_by_slug(district['id'], block_slug)
    if not block:
        return render_template('404.html'), 404

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    places = get_places_by_block(block['id'], limit=per_page, offset=offset)
    total = count_places_in_block(block['id'])

    return render_template('block.html',
                           state=state,
                           district=district,
                           block=block,
                           places=places,
                           page=page,
                           per_page=per_page,
                           total=total)


@main_bp.route('/search')
def search():
    """Enhanced search results page with hierarchical results."""
    query = request.args.get('q', '').strip()
    results = {'states': [], 'districts': [], 'blocks': [], 'places': [], 'foods': []}
    smart = None
    if query:
        results = search_all(query, limit=30)
        smart_raw = smart_search(query, limit=10)
        # smart_search returns a dict like {'query': ..., 'places': [...], 'foods': [...], 'hotels': [...]}
        # Extract just the places list for the template's place_card rendering
        if smart_raw and isinstance(smart_raw, dict):
            smart = smart_raw.get('places', [])
        elif isinstance(smart_raw, list):
            smart = smart_raw
    return render_template('search.html', query=query, results=results, smart=smart)


@main_bp.route('/explore')
def explore_map():
    """Full-screen interactive map with all places."""
    states = get_all_states()
    bihar = get_state_by_slug('bihar')
    districts = []
    if bihar:
        districts = get_districts_by_state(bihar['id'])
    places = get_places_for_map()
    return render_template('explore_map.html',
                           states=states,
                           districts=districts,
                           categories=PLACE_CATEGORIES,
                           places=places)


@main_bp.route('/food-culture')
def food_culture():
    """Food & Culture page — Bihar focused."""
    bihar = get_state_by_slug('bihar')
    foods = []
    districts = []
    if bihar:
        foods = get_all_district_foods_by_state(bihar['id'])
        districts = get_districts_by_state(bihar['id'])
    return render_template('food_culture.html',
                           bihar=bihar,
                           foods=foods,
                           districts=districts)
