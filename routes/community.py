"""Community routes — advanced suggest places with image upload."""
import os
import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from config import SUBMISSION_UPLOAD, allowed_file, validate_image_file, check_file_size
from models.database import (
    submit_place, get_user_submissions, get_districts_by_state,
    get_state_by_slug, PLACE_CATEGORIES
)
from utils import csrf_required, login_required, get_session_id as _get_session_id
import uuid

logger = logging.getLogger(__name__)
community_bp = Blueprint('community', __name__)

# Ensure submission uploads folder exists
os.makedirs(SUBMISSION_UPLOAD, exist_ok=True)


# Category emoji icons for suggest-place UI (supplements PLACE_CATEGORIES from database.py)
CATEGORY_ICONS = {
    'temple': '🛕',
    'waterfall': '💧',
    'nature': '🌿',
    'historical': '🏛️',
    'mountain': '⛰️',
    'lake': '🏞️',
    'park': '🌳',
    'religious': '🙏',
    'adventure': '🧗',
    'cultural': '🎭',
    'museum': '🏛️',
    'beach': '🏖️',
    'fort': '🏰',
    'cave': '🕳️',
    'garden': '🌺',
    'tourist_spot': '📍',
    'hidden_gem': '💎',
}


@community_bp.route('/suggest', methods=['GET', 'POST'])
@community_bp.route('/suggest-place', methods=['GET', 'POST'])
def suggest_place():
    """Advanced multi-step suggest a place form."""
    if request.method == 'POST':
        # ── CSRF check (manual, since @csrf_required blocks GET) ──
        token = (request.headers.get('X-CSRF-Token')
                 or request.form.get('_csrf_token', ''))
        if not token or token != session.get('_csrf_token'):
            flash('Invalid request. Please try again.', 'error')
            return redirect(url_for('community.suggest_place'))

        # ── LOGIN REQUIRED to submit ──
        if not session.get('user_id'):
            flash('Please login to suggest a place.', 'error')
            return redirect(url_for('auth.login'))

        sid = _get_session_id()
        place_name = request.form.get('place_name', '').strip()
        if not place_name:
            flash('Place name is required.', 'error')
            return redirect(url_for('community.suggest_place'))

        lat = request.form.get('latitude', '')
        lng = request.form.get('longitude', '')

        # Handle image uploads (using shared utility)
        from utils.image import process_and_save_image
        uploaded_filenames = []
        files = request.files.getlist('photos')
        for f in files:
            if f and f.filename and allowed_file(f.filename) and validate_image_file(f) and check_file_size(f):
                fname = process_and_save_image(f, SUBMISSION_UPLOAD, prefix='sub', max_width=1600, quality=80)
                if fname:
                    uploaded_filenames.append(fname)

        # Build nearby food JSON
        food_names = request.form.getlist('food_name[]')
        food_famous = request.form.getlist('food_famous[]')
        nearby_food_list = []
        for i in range(len(food_names)):
            if food_names[i].strip():
                nearby_food_list.append({
                    'name': food_names[i].strip(),
                    'famous': food_famous[i].strip() if i < len(food_famous) else ''
                })

        # Build nearby stay JSON
        stay_names = request.form.getlist('stay_name[]')
        stay_prices = request.form.getlist('stay_price[]')
        stay_contacts = request.form.getlist('stay_contact[]')
        nearby_stay_list = []
        for i in range(len(stay_names)):
            if stay_names[i].strip():
                nearby_stay_list.append({
                    'name': stay_names[i].strip(),
                    'price': stay_prices[i].strip() if i < len(stay_prices) else '',
                    'contact': stay_contacts[i].strip() if i < len(stay_contacts) else ''
                })

        # Get contributor name
        submitter = request.form.get('submitter_name', '').strip()
        if not submitter and session.get('user_id'):
            submitter = session.get('user_name', 'Traveler')

        # Safe float conversion for coordinates
        try:
            latitude = float(lat) if lat else None
        except (ValueError, TypeError):
            latitude = None
        try:
            longitude = float(lng) if lng else None
        except (ValueError, TypeError):
            longitude = None

        data = {
            'user_id': session.get('user_id'),
            'session_id': sid,
            'place_name': place_name,
            'district_name': request.form.get('district_name', '').strip(),
            'short_description': request.form.get('short_description', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category': request.form.get('category', 'tourist_spot'),
            'latitude': latitude,
            'longitude': longitude,
            'photos': ','.join(uploaded_filenames),
            'best_time_to_visit': request.form.get('best_time_to_visit', '').strip(),
            'entry_fee': request.form.get('entry_fee', '').strip(),
            'crowd_level': request.form.get('crowd_level', ''),
            'safety_level': request.form.get('safety_level', ''),
            'local_tips': request.form.get('local_tips', '').strip(),
            'nearby_food': json.dumps(nearby_food_list),
            'nearby_stay': json.dumps(nearby_stay_list),
            'submitter_name': submitter or 'Anonymous Explorer',
        }
        submit_place(data)
        flash('🎉 Amazing! Your place has been submitted for review. Thank you for sharing this hidden gem!', 'success')
        return redirect(url_for('community.my_submissions'))

    # GET — render the wizard form
    bihar = get_state_by_slug('bihar')
    districts = []
    if bihar:
        districts = get_districts_by_state(bihar['id'])

    return render_template('community/suggest_place.html',
                           districts=districts,
                           categories=PLACE_CATEGORIES,
                           category_icons=CATEGORY_ICONS)


@community_bp.route('/my-submissions')
@login_required
def my_submissions():
    """View current user's submissions — login required."""
    sid = _get_session_id()
    submissions = get_user_submissions(session_id=sid, user_id=session.get('user_id'))
    return render_template('community/my_submissions.html', submissions=submissions)


@community_bp.route('/api/upload-temp', methods=['POST'])
@csrf_required
def upload_temp():
    """AJAX endpoint for drag & drop image uploads — login required."""
    if not session.get('user_id'):
        return jsonify({'error': 'Login required'}), 401
    f = request.files.get('file')
    if not f or not allowed_file(f.filename) or not validate_image_file(f) or not check_file_size(f):
        return jsonify({'error': 'Invalid file'}), 400

    from utils.image import process_and_save_image
    fname = process_and_save_image(f, SUBMISSION_UPLOAD, prefix='temp', max_width=1600, quality=80)
    if not fname:
        return jsonify({'error': 'Failed to process image'}), 400

    return jsonify({'filename': fname, 'url': f'/static/uploads/submissions/{fname}'})
