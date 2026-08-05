"""Admin panel routes — login, dashboard, add/edit/delete places, moderation."""
import os
import uuid
import time as _time
import logging
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify
)
from werkzeug.utils import secure_filename
from PIL import Image
from config import ADMIN_PASSWORD, UPLOAD_FOLDER, allowed_file, validate_image_file, check_file_size
from utils import csrf_required
import json

logger = logging.getLogger(__name__)
from models.database import (
    get_all_states, get_all_places, get_place_by_id,
    create_place, update_place, update_place_extra_fields,
    delete_place, set_place_cover, clear_place_cover_if_match,
    quick_edit_place,
    soft_delete_place, restore_place, permanent_delete_place,
    get_deleted_places, count_deleted_places,
    get_photos_by_place, add_photo, delete_photo,
    get_specialties_by_place, add_specialty,
    delete_specialties_by_place, delete_specialty,
    create_state, create_district, create_block,
    get_stats, get_dashboard_analytics,
    get_pending_submissions, get_all_submissions,
    get_submission_by_id, approve_submission, reject_submission,
    count_pending_submissions, delete_submission,
    get_all_users, search_users, get_user_by_id,
    update_user_status, delete_user as db_delete_user,
    find_duplicates_for_submission, get_filtered_submissions,
    merge_submissions, update_submission, replace_place_with_submission,
    log_admin_action, get_admin_logs, get_place_edit_history,
    get_districts_by_state, get_state_by_slug,
    get_hero_media_all, add_hero_media, delete_hero_media,
    toggle_hero_media, get_hero_settings, update_hero_settings,
    get_pending_user_photos, get_all_user_photos_admin,
    get_user_photos_by_status,
    approve_user_photo, reject_user_photo, delete_user_photo,
    count_pending_user_photos,
    get_all_districts_admin, update_district, delete_district,
    reorder_districts, get_district_by_id,
    get_trending_admin, add_to_trending, remove_from_trending,
    toggle_trending, reorder_trending, search_places_simple,
    get_homepage_sections, update_homepage_section,
    get_auth_appearance, update_auth_appearance,
    get_nearby_services_admin, add_nearby_service as db_add_nearby_service,
    delete_nearby_service as db_delete_nearby_service,
    get_admin_districts_list,
    count_places,
    PLACE_CATEGORIES, SPECIALTY_CATEGORIES
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def _admin_csrf_check():
    """Validate CSRF for all admin POST routes except login."""
    if request.method == 'POST' and request.endpoint != 'admin.login':
        token = (request.headers.get('X-CSRF-Token')
                 or request.form.get('_csrf_token', ''))
        if not token or token != session.get('_csrf_token'):
            if (request.is_json
                    or request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
                from flask import jsonify
                return jsonify({'error': 'Invalid CSRF token'}), 403
            flash('Invalid request. Please try again.', 'error')
            return redirect(url_for('admin.login'))


def admin_required(f):
    """Decorator to protect admin routes."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated




_login_attempts = {}  # IP -> [(timestamp, ...)]
_MAX_LOGIN_ATTEMPTS = 5
_LOGIN_WINDOW = 60  # seconds
_MAX_RATE_STORE_SIZE = 500  # Prevent unbounded growth


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Rate limiting
        ip = request.remote_addr
        now = _time.time()
        attempts = _login_attempts.get(ip, [])
        attempts = [t for t in attempts if now - t < _LOGIN_WINDOW]
        if len(attempts) >= _MAX_LOGIN_ATTEMPTS:
            flash('Too many login attempts. Please wait 1 minute.', 'error')
            return render_template('admin/login.html')

        # CSRF check
        token = request.form.get('_csrf_token', '')
        if not token or token != session.get('_csrf_token'):
            flash('Invalid request. Please try again.', 'error')
            return render_template('admin/login.html')

        password = request.form.get('password', '')
        import secrets as _sec
        if _sec.compare_digest(password, ADMIN_PASSWORD):
            session['admin_logged_in'] = True
            _login_attempts.pop(ip, None)
            flash('Welcome back, Explorer! 🧭', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            attempts.append(now)
            _login_attempts[ip] = attempts
            # Prevent unbounded growth of rate limiter dict
            if len(_login_attempts) > _MAX_RATE_STORE_SIZE:
                cutoff = now - _LOGIN_WINDOW
                _login_attempts.clear()
            flash('Invalid password. Try again.', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@admin_bp.route('/')
@admin_bp.route('/places')
@admin_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    offset = (page - 1) * per_page
    places = get_all_places(limit=per_page, offset=offset)
    stats = get_stats()
    stats['pending_user_photos'] = count_pending_user_photos()
    pending = get_pending_submissions()
    logs = get_admin_logs(limit=10)

    # Analytics from centralized helper
    analytics = get_dashboard_analytics()
    total_places = analytics['total_places']
    total_pages = (total_places + per_page - 1) // per_page

    stats['blocks'] = analytics['blocks_count']
    stats['wishlists'] = analytics['wishlist_count']

    return render_template('admin/dashboard.html',
                           places=places, stats=stats,
                           pending=pending, logs=logs,
                           categories=PLACE_CATEGORIES,
                           top_viewed=analytics['top_viewed'],
                           top_districts=analytics['top_districts'],
                           recent_places=analytics['recent_places'],
                           page=page, per_page=per_page,
                           total_places=total_places,
                           total_pages=total_pages)


# ═══ SUBMISSIONS MANAGEMENT ═══

@admin_bp.route('/submissions')
@admin_required
def submissions():
    status_filter = request.args.get('status', '')
    show_duplicates = request.args.get('duplicates', '') == '1'
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    if status_filter or show_duplicates:
        subs = get_filtered_submissions(status=status_filter or None, has_duplicates=show_duplicates)
    else:
        subs = get_all_submissions()

    total_subs = len(subs)
    paginated_subs = subs[offset:offset + per_page]
    total_pages = max(1, (total_subs + per_page - 1) // per_page)

    # Enrich each pending sub with duplicate info
    for sub in paginated_subs:
        if sub.get('status') == 'pending' and 'duplicate_places' not in sub:
            dup_places, dup_subs = find_duplicates_for_submission(sub['id'])
            sub['duplicate_places'] = dup_places
            sub['duplicate_subs'] = dup_subs
            sub['has_duplicates'] = bool(dup_places or dup_subs)

    return render_template('admin/submissions.html',
                           submissions=paginated_subs,
                           current_filter=status_filter,
                           show_duplicates=show_duplicates,
                           page=page,
                           per_page=per_page,
                           total_submissions=total_subs,
                           total_pages=total_pages)


@admin_bp.route('/submissions/<int:sub_id>')
@admin_required
def submission_detail(sub_id):
    sub = get_submission_by_id(sub_id)
    if not sub:
        flash('Submission not found.', 'error')
        return redirect(url_for('admin.submissions'))
    dup_places, dup_subs = find_duplicates_for_submission(sub_id)
    bihar = get_state_by_slug('bihar')
    districts = get_districts_by_state(bihar['id']) if bihar else []
    return render_template('admin/submission_detail.html',
                           sub=sub, dup_places=dup_places,
                           dup_subs=dup_subs, districts=districts,
                           categories=PLACE_CATEGORIES)


@admin_bp.route('/submissions/approve/<int:sub_id>', methods=['POST'])
@admin_required
def approve_sub(sub_id):
    notes = request.form.get('admin_notes', '')
    approve_submission(sub_id, notes)
    log_admin_action('approve', 'submission', sub_id, notes)
    flash('Submission approved! ✅', 'success')
    return redirect(url_for('admin.submissions'))


@admin_bp.route('/submissions/reject/<int:sub_id>', methods=['POST'])
@admin_required
def reject_sub(sub_id):
    notes = request.form.get('admin_notes', '')
    reject_submission(sub_id, notes)
    log_admin_action('reject', 'submission', sub_id, notes)
    flash('Submission rejected.', 'info')
    return redirect(url_for('admin.submissions'))


@admin_bp.route('/submissions/edit/<int:sub_id>', methods=['POST'])
@admin_required
def edit_sub(sub_id):
    """Edit submission before approving."""
    lat = request.form.get('latitude', '')
    lng = request.form.get('longitude', '')
    data = {
        'place_name': request.form.get('place_name', '').strip(),
        'district_name': request.form.get('district_name', '').strip(),
        'description': request.form.get('description', '').strip(),
        'category': request.form.get('category', 'tourist_spot'),
        'latitude': None,
        'longitude': None,
        'best_time_to_visit': request.form.get('best_time_to_visit', ''),
        'entry_fee': request.form.get('entry_fee', ''),
    }
    try:
        if lat:
            data['latitude'] = float(lat)
    except (ValueError, TypeError):
        pass
    try:
        if lng:
            data['longitude'] = float(lng)
    except (ValueError, TypeError):
        pass
    update_submission(sub_id, data)
    log_admin_action('edit', 'submission', sub_id, f'Edited: {data["place_name"]}')
    flash('Submission updated! ✏️ Now you can approve it.', 'success')
    return redirect(url_for('admin.submission_detail', sub_id=sub_id))


@admin_bp.route('/submissions/merge', methods=['POST'])
@admin_required
def merge_subs():
    """Merge two submissions."""
    keep_id = request.form.get('keep_id', type=int)
    merge_id = request.form.get('merge_id', type=int)
    if keep_id and merge_id:
        merge_submissions(keep_id, merge_id)
        flash(f'Submissions merged! #{merge_id} → #{keep_id} 🔗', 'success')
    return redirect(url_for('admin.submissions'))


@admin_bp.route('/submissions/replace', methods=['POST'])
@admin_required
def replace_place():
    """Replace existing place with submission data."""
    place_id = request.form.get('place_id', type=int)
    sub_id = request.form.get('sub_id', type=int)
    if place_id and sub_id:
        replace_place_with_submission(place_id, sub_id)
        flash('Place data replaced with submission! 🔄', 'success')
    return redirect(url_for('admin.submissions'))


@admin_bp.route('/submissions/delete/<int:sub_id>', methods=['POST'])
@admin_required
def delete_sub(sub_id):
    """Delete a submission permanently (removes photos from disk)."""
    from config import SUBMISSION_UPLOAD
    sub = delete_submission(sub_id)
    name = sub['place_name'] if sub else 'Unknown'
    if sub and sub.get('photos'):
        for fn in sub['photos'].split(','):
            fn = fn.strip()
            if fn:
                fpath = os.path.join(SUBMISSION_UPLOAD, fn)
                if os.path.exists(fpath):
                    os.remove(fpath)
    log_admin_action('delete', 'submission', sub_id, f'Deleted: {name}')
    flash(f'Submission "{name}" deleted. 🗑️', 'info')
    return redirect(url_for('admin.submissions'))


# ═══ ADMIN LOGS ═══

@admin_bp.route('/logs')
@admin_required
def admin_logs():
    logs = get_admin_logs(limit=100)
    return render_template('admin/logs.html', logs=logs)


@admin_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_place_view():
    if request.method == 'POST':
        # Ensure state exists (create if new)
        state_name = request.form.get('state_name', '').strip()
        if not state_name:
            flash('State is required.', 'error')
            return redirect(url_for('admin.add_place_view'))

        state_id = create_state(state_name)

        # District (optional)
        district_id = None
        district_name = request.form.get('district_name', '').strip()
        if district_name:
            district_id = create_district(state_id, district_name)

        # Block (optional)
        block_id = None
        block_name = request.form.get('block_name', '').strip()
        if block_name and district_id:
            block_id = create_block(district_id, block_name)

        # Parse coordinates
        lat = request.form.get('latitude', '')
        lng = request.form.get('longitude', '')

        place_data = {
            'state_id': state_id,
            'district_id': district_id,
            'block_id': block_id,
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category': request.form.get('category', 'tourist_spot'),
            'latitude': float(lat) if lat else None,
            'longitude': float(lng) if lng else None,
            'maps_link': request.form.get('maps_link', '').strip(),
            'is_featured': request.form.get('is_featured') == 'on',
            'cover_image': '',
        }

        if not place_data['name']:
            flash('Place name is required.', 'error')
            return redirect(url_for('admin.add_place_view'))

        # Handle photo uploads
        place_id = create_place(place_data)
        cover_set = False

        files = request.files.getlist('photos')
        for i, f in enumerate(files):
            if f and f.filename and allowed_file(f.filename):
                filename = save_uploaded_image(f, place_id)
                if not filename:
                    continue
                caption = request.form.get(f'caption_{i}', '')
                add_photo(place_id, filename, caption, sort_order=i)
                if not cover_set:
                    set_place_cover(place_id, filename)
                    cover_set = True

        # Handle specialties
        spec_names = request.form.getlist('spec_name[]')
        spec_descs = request.form.getlist('spec_description[]')
        spec_cats = request.form.getlist('spec_category[]')
        spec_where = request.form.getlist('spec_where[]')

        for j in range(len(spec_names)):
            if spec_names[j].strip():
                add_specialty(place_id, {
                    'name': spec_names[j].strip(),
                    'description': spec_descs[j].strip() if j < len(spec_descs) else '',
                    'category': spec_cats[j] if j < len(spec_cats) else 'food',
                    'where_to_find': spec_where[j].strip() if j < len(spec_where) else '',
                })

        flash(f'✅ "{place_data["name"]}" added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    states = get_all_states()
    return render_template('admin/add_place.html',
                           states=states,
                           categories=PLACE_CATEGORIES,
                           specialty_categories=SPECIALTY_CATEGORIES)


@admin_bp.route('/edit/<int:place_id>', methods=['GET', 'POST'])
@admin_required
def edit_place_view(place_id):
    place = get_place_by_id(place_id)
    if not place:
        flash('Place not found.', 'error')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        state_name = request.form.get('state_name', '').strip()
        state_id = create_state(state_name) if state_name else place['state_id']

        district_id = None
        district_name = request.form.get('district_name', '').strip()
        if district_name:
            district_id = create_district(state_id, district_name)

        block_id = None
        block_name = request.form.get('block_name', '').strip()
        if block_name and district_id:
            block_id = create_block(district_id, block_name)

        lat = request.form.get('latitude', '')
        lng = request.form.get('longitude', '')

        place_data = {
            'state_id': state_id,
            'district_id': district_id,
            'block_id': block_id,
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category': request.form.get('category', 'tourist_spot'),
            'latitude': float(lat) if lat else None,
            'longitude': float(lng) if lng else None,
            'maps_link': request.form.get('maps_link', '').strip(),
            'is_featured': request.form.get('is_featured') == 'on',
            'cover_image': place.get('cover_image', ''),
        }

        update_place(place_id, place_data)

        # Update extra fields
        extra_data = {
            'best_time_to_visit': request.form.get('best_time_to_visit', ''),
            'entry_fee': request.form.get('entry_fee', ''),
            'travel_tips': request.form.get('travel_tips', ''),
            'is_hidden_gem': request.form.get('is_hidden_gem'),
            'history': request.form.get('history', '').strip(),
            'local_tips': request.form.get('local_tips', '').strip(),
            'safety_tips': request.form.get('safety_tips', '').strip(),
            'best_season': request.form.get('best_season', ''),
            'best_time_of_day': request.form.get('best_time_of_day', ''),
            'crowd_level': request.form.get('crowd_level', ''),
            'parking_info': request.form.get('parking_info', '').strip(),
            'family_friendly': request.form.get('family_friendly'),
            'nearest_railway': request.form.get('nearest_railway', '').strip(),
            'nearest_bus_stand': request.form.get('nearest_bus_stand', '').strip(),
            'nearest_airport': request.form.get('nearest_airport', '').strip(),
            'road_connectivity': request.form.get('road_connectivity', '').strip(),
        }
        update_place_extra_fields(place_id, extra_data)

        # Handle new photo uploads
        files = request.files.getlist('photos')
        for i, f in enumerate(files):
            if f and f.filename and allowed_file(f.filename):
                filename = save_uploaded_image(f, place_id)
                if not filename:
                    continue
                add_photo(place_id, filename, sort_order=i + 100)
                if not place_data['cover_image']:
                    set_place_cover(place_id, filename)
                    place_data['cover_image'] = filename

        # Update specialties — delete existing and re-add
        delete_specialties_by_place(place_id)
        spec_names = request.form.getlist('spec_name[]')
        spec_descs = request.form.getlist('spec_description[]')
        spec_cats = request.form.getlist('spec_category[]')
        spec_where = request.form.getlist('spec_where[]')

        for j in range(len(spec_names)):
            if spec_names[j].strip():
                add_specialty(place_id, {
                    'name': spec_names[j].strip(),
                    'description': spec_descs[j].strip() if j < len(spec_descs) else '',
                    'category': spec_cats[j] if j < len(spec_cats) else 'food',
                    'where_to_find': spec_where[j].strip() if j < len(spec_where) else '',
                })

        # Log the edit
        changes = []
        if place_data['name'] != place.get('name'):
            changes.append(f'name: {place["name"]} → {place_data["name"]}')
        if place_data['category'] != place.get('category'):
            changes.append(f'category changed to {place_data["category"]}')
        log_admin_action('edit', 'place', place_id,
                         f'Updated: {place_data["name"]}. ' + ', '.join(changes) if changes else f'Updated: {place_data["name"]}')

        flash(f'✅ "{place_data["name"]}" updated successfully!', 'success')
        return redirect(url_for('admin.edit_place_view', place_id=place_id))

    photos = get_photos_by_place(place_id)
    specialties = get_specialties_by_place(place_id)
    states = get_all_states()
    edit_history = get_place_edit_history(place_id)

    return render_template('admin/edit_place.html',
                           place=place,
                           photos=photos,
                           specialties=specialties,
                           states=states,
                           edit_history=edit_history,
                           categories=PLACE_CATEGORIES,
                           specialty_categories=SPECIALTY_CATEGORIES)


@admin_bp.route('/quick-edit/<int:place_id>', methods=['POST'])
@admin_required
def quick_edit(place_id):
    """Quick inline edit — name, description, category, featured."""
    place = get_place_by_id(place_id)
    if not place:
        flash('Place not found.', 'error')
        return redirect(url_for('admin.dashboard'))

    name = request.form.get('name', '').strip()
    desc = request.form.get('description', '').strip()
    cat = request.form.get('category', 'tourist_spot')
    featured = 1 if request.form.get('is_featured') else 0

    quick_edit_place(place_id, name, desc, cat, featured)

    log_admin_action('quick_edit', 'place', place_id, f'Quick edited: {name}')
    flash(f'⚡ "{name}" updated!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/set-cover/<int:place_id>', methods=['POST'])
@admin_required
def set_cover_image(place_id):
    """Change the cover image to an existing gallery photo."""
    filename = request.form.get('filename', '')
    if filename:
        set_place_cover(place_id, filename)
        log_admin_action('cover_change', 'place', place_id, f'Cover changed to {filename}')
        flash('Cover image updated! 📷', 'success')
    return redirect(url_for('admin.edit_place_view', place_id=place_id))




@admin_bp.route('/delete/<int:place_id>', methods=['POST'])
@admin_required
def delete_place_view(place_id):
    place = get_place_by_id(place_id)
    if place:
        delete_place(place_id)
        log_admin_action('soft_delete', 'place', place_id, f'Moved to Recycle Bin: {place["name"]}')
        flash(f'🗑️ "{place["name"]}" moved to Recycle Bin. You can restore it anytime.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete-photo/<int:photo_id>', methods=['POST'])
@admin_required
def delete_photo_view(photo_id):
    photo = delete_photo(photo_id)
    if photo:
        filepath = os.path.join(UPLOAD_FOLDER, photo['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        # If this was the cover image, clear it
        place_id = request.form.get('place_id', type=int)
        if place_id:
            clear_place_cover_if_match(place_id, photo['filename'])
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/upload-cover/<int:place_id>', methods=['POST'])
@admin_required
def upload_cover(place_id):
    """Upload or replace the cover image for a place."""
    f = request.files.get('cover_image')
    if not f or not f.filename or not allowed_file(f.filename):
        flash('Please select a valid image file.', 'error')
        return redirect(url_for('admin.edit_place_view', place_id=place_id))

    filename = save_uploaded_image(f, place_id)
    if not filename:
        flash('Could not process uploaded image.', 'error')
        return redirect(url_for('admin.edit_place_view', place_id=place_id))

    # Save to photos table as type 'cover'
    add_photo(place_id, filename, caption='Cover Image', sort_order=0)

    # Update places.cover_image
    set_place_cover(place_id, filename)

    log_admin_action('cover_upload', 'place', place_id, f'New cover image: {filename}')
    flash('📷 Cover image updated!', 'success')
    return redirect(url_for('admin.edit_place_view', place_id=place_id))


@admin_bp.route('/upload-gallery/<int:place_id>', methods=['POST'])
@admin_required
def upload_gallery(place_id):
    """Upload multiple gallery images for a place."""
    files = request.files.getlist('gallery_images')
    count = 0
    for i, f in enumerate(files):
        if f and f.filename and allowed_file(f.filename):
            filename = save_uploaded_image(f, place_id)
            if not filename:
                continue
            caption = request.form.get(f'caption_{i}', '')
            add_photo(place_id, filename, caption, sort_order=i + 100)
            count += 1

    if count > 0:
        log_admin_action('gallery_upload', 'place', place_id, f'Uploaded {count} gallery image(s)')
        flash(f'📸 {count} gallery image(s) uploaded!', 'success')
    else:
        flash('No valid images selected.', 'error')
    return redirect(url_for('admin.edit_place_view', place_id=place_id))


# ──────────────────────────────────────────────
# File upload helper
# ──────────────────────────────────────────────
def save_uploaded_image(file_obj, place_id):
    """Save uploaded image, resize if needed, return filename."""
    if not validate_image_file(file_obj) or not check_file_size(file_obj):
        return None
    from utils.image import process_and_save_image
    return process_and_save_image(file_obj, UPLOAD_FOLDER, prefix=str(place_id), max_width=1920, quality=85)



# ──────────────────────────────────────────────
# Hero Media Manager
# ──────────────────────────────────────────────
from config import BASE_DIR as _BASE_DIR
HERO_UPLOAD = os.path.join(_BASE_DIR, 'static', 'hero')
os.makedirs(HERO_UPLOAD, exist_ok=True)

ALLOWED_VIDEO = {'mp4', 'webm'}


@admin_bp.route('/hero-media')
@admin_required
def hero_media_manager():
    """Hero media manager page."""
    media = get_hero_media_all()
    settings = get_hero_settings()
    return render_template('admin/hero_media.html', media=media, settings=settings)


@admin_bp.route('/hero-media/upload', methods=['POST'])
@admin_required
def hero_media_upload():
    """Upload new hero background media."""
    files = request.files.getlist('media')
    count = 0
    for f in files:
        if not f or not f.filename:
            continue
        ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
        is_video = ext in ALLOWED_VIDEO
        is_image = ext in {'jpg', 'jpeg', 'png', 'webp', 'gif'}
        if not (is_video or is_image):
            continue
        if not check_file_size(f):
            continue
        if is_image and not validate_image_file(f):
            continue

        fname = f"hero_{uuid.uuid4().hex[:10]}.{ext}"
        fpath = os.path.join(HERO_UPLOAD, fname)

        if is_image:
            try:
                img = Image.open(f)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                # Resize for hero: 1920px wide
                if img.width > 1920:
                    ratio = 1920 / img.width
                    img = img.resize((1920, int(img.height * ratio)), Image.LANCZOS)
                img.save(fpath, quality=85, optimize=True)
            except Exception:
                logger.warning("PIL failed for hero image %s, skipping raw save", fname)
                continue
        else:
            f.save(fpath)

        title = request.form.get('title', '').strip() or f.filename
        media_type = 'video' if is_video else 'image'
        add_hero_media(fname, media_type, title)
        count += 1

    log_admin_action('hero_media_upload', 'hero', 0, f'Uploaded {count} media files')
    flash(f'✅ Uploaded {count} hero background(s).', 'success')
    return redirect(url_for('admin.hero_media_manager'))


@admin_bp.route('/hero-media/delete/<int:media_id>', methods=['POST'])
@admin_required
def hero_media_delete(media_id):
    """Delete a hero media item."""
    try:
        row = delete_hero_media(media_id)
        if row and row.get('filename'):
            fpath = os.path.join(HERO_UPLOAD, row['filename'])
            if os.path.exists(fpath):
                os.remove(fpath)
                logger.info("Removed hero media file: %s", fpath)
            else:
                logger.info("Hero media file already gone: %s", fpath)
        logger.info("Deleted hero media ID=%d from database", media_id)
        log_admin_action('hero_media_delete', 'hero', media_id, 'Deleted hero media')
        flash('🗑️ Media deleted.', 'info')
    except Exception as e:
        logger.error("Hero delete error for ID=%d: %s", media_id, e)
        flash(f'Error deleting media: {e}', 'error')
    return redirect(url_for('admin.hero_media_manager'))


@admin_bp.route('/hero-media/toggle/<int:media_id>', methods=['POST'])
@admin_required
def hero_media_toggle(media_id):
    """Toggle active state of a hero media item."""
    toggle_hero_media(media_id)
    flash('✅ Media visibility toggled.', 'success')
    return redirect(url_for('admin.hero_media_manager'))


@admin_bp.route('/hero-media/settings', methods=['POST'])
@admin_required
def hero_media_settings():
    """Update hero display settings."""
    bg_type = request.form.get('bg_type', 'slideshow')
    try:
        interval = int(request.form.get('slideshow_interval', 6))
        interval = max(2, min(30, interval))  # Clamp to 2-30 seconds
    except (ValueError, TypeError):
        interval = 6
    transition = request.form.get('transition_effect', 'fade')
    try:
        opacity = float(request.form.get('overlay_opacity', 0.55))
        opacity = max(0.0, min(1.0, opacity))  # Clamp to 0-1
    except (ValueError, TypeError):
        opacity = 0.55
    update_hero_settings(bg_type, interval, transition, opacity)
    log_admin_action('hero_settings_update', 'hero', 0, f'Updated: {bg_type}, {interval}s')
    flash('✅ Hero settings saved.', 'success')
    return redirect(url_for('admin.hero_media_manager'))


@admin_bp.route('/hero-media/reorder', methods=['POST'])
@admin_required
def hero_media_reorder():
    """Reorder hero media via AJAX."""
    from models.database import reorder_hero_media
    ids = request.json.get('ids', [])
    if ids:
        reorder_hero_media(ids)
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 400


# ──────────────────────────────────────────────
# Auth Appearance Manager
# ──────────────────────────────────────────────
AUTH_UPLOAD = os.path.join(_BASE_DIR, 'static', 'uploads', 'auth')
os.makedirs(AUTH_UPLOAD, exist_ok=True)


def _compress_auth_image(file_obj, filename):
    """Compress and save auth image, return filename."""
    if not validate_image_file(file_obj) or not check_file_size(file_obj):
        return None
    from utils.image import process_and_save_image
    return process_and_save_image(file_obj, AUTH_UPLOAD, prefix='auth', max_width=1920, quality=85)



def _delete_auth_image(filename):
    """Delete an auth image file if it exists."""
    if not filename:
        return
    fpath = os.path.join(AUTH_UPLOAD, filename)
    if os.path.exists(fpath):
        os.remove(fpath)


@admin_bp.route('/appearance/auth')
@admin_required
def auth_appearance_manager():
    """Auth page appearance settings page."""
    appearance = get_auth_appearance()
    # Parse JSON fields for the template
    appearance['login_stats_list'] = json.loads(appearance.get('login_stats', '[]'))
    appearance['login_slider_list'] = json.loads(appearance.get('login_slider_images', '[]'))
    appearance['signup_stats_list'] = json.loads(appearance.get('signup_stats', '[]'))
    appearance['signup_slider_list'] = json.loads(appearance.get('signup_slider_images', '[]'))
    return render_template('admin/auth_appearance.html', appearance=appearance)


@admin_bp.route('/appearance/auth/save', methods=['POST'])
@admin_required
def auth_appearance_save():
    """Save auth appearance text/boolean fields."""
    page = request.form.get('page', 'login')  # 'login' or 'signup'
    prefix = f"{page}_"

    fields = {}
    fields[f"{prefix}title"] = request.form.get('title', '').strip()[:100]
    fields[f"{prefix}subtitle"] = request.form.get('subtitle', '').strip()[:200]
    fields[f"{prefix}slider_enabled"] = 1 if request.form.get('slider_enabled') else 0

    # Stats JSON
    stat_icons = request.form.getlist('stat_icon[]')
    stat_values = request.form.getlist('stat_value[]')
    stat_labels = request.form.getlist('stat_label[]')
    stats = []
    for i in range(len(stat_icons)):
        if stat_values[i] and stat_labels[i]:
            stats.append({
                'icon': stat_icons[i][:10],
                'value': stat_values[i][:20],
                'label': stat_labels[i][:50],
            })
    fields[f"{prefix}stats"] = json.dumps(stats)

    update_auth_appearance(**fields)
    log_admin_action('auth_appearance_update', 'auth', 0,
                     f'Updated {page} page appearance')
    flash(f'✅ {page.title()} page appearance saved.', 'success')
    return redirect(url_for('admin.auth_appearance_manager'))


@admin_bp.route('/appearance/auth/upload-banner', methods=['POST'])
@admin_required
def auth_appearance_upload_banner():
    """Upload banner image for login or signup page."""
    page = request.form.get('page', 'login')
    file_obj = request.files.get('banner')
    if not file_obj or not file_obj.filename:
        flash('No file selected.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))

    if not allowed_file(file_obj.filename):
        flash('Only JPG, PNG, WebP images allowed.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))

    # Delete old banner if exists
    appearance = get_auth_appearance()
    old = appearance.get(f'{page}_banner')
    if old:
        _delete_auth_image(old)

    filename = _compress_auth_image(file_obj, file_obj.filename)
    if not filename:
        flash('Could not process uploaded image.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))
    update_auth_appearance(**{f'{page}_banner': filename})
    log_admin_action('auth_banner_upload', 'auth', 0,
                     f'Uploaded {page} banner: {filename}')
    flash(f'✅ {page.title()} banner updated.', 'success')
    return redirect(url_for('admin.auth_appearance_manager'))


@admin_bp.route('/appearance/auth/upload-mobile', methods=['POST'])
@admin_required
def auth_appearance_upload_mobile():
    """Upload mobile image for login or signup page."""
    page = request.form.get('page', 'login')
    file_obj = request.files.get('mobile')
    if not file_obj or not file_obj.filename:
        flash('No file selected.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))

    if not allowed_file(file_obj.filename):
        flash('Only JPG, PNG, WebP images allowed.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))

    appearance = get_auth_appearance()
    old = appearance.get(f'{page}_mobile_image')
    if old:
        _delete_auth_image(old)

    filename = _compress_auth_image(file_obj, file_obj.filename)
    if not filename:
        flash('Could not process uploaded image.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))
    update_auth_appearance(**{f'{page}_mobile_image': filename})
    log_admin_action('auth_mobile_upload', 'auth', 0,
                     f'Uploaded {page} mobile image: {filename}')
    flash(f'✅ {page.title()} mobile image updated.', 'success')
    return redirect(url_for('admin.auth_appearance_manager'))


@admin_bp.route('/appearance/auth/upload-slider', methods=['POST'])
@admin_required
def auth_appearance_upload_slider():
    """Upload a slider image for login or signup page."""
    page = request.form.get('page', 'login')
    file_obj = request.files.get('slider')
    if not file_obj or not file_obj.filename:
        flash('No file selected.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))

    if not allowed_file(file_obj.filename):
        flash('Only JPG, PNG, WebP images allowed.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))

    filename = _compress_auth_image(file_obj, file_obj.filename)
    if not filename:
        flash('Could not process uploaded image.', 'error')
        return redirect(url_for('admin.auth_appearance_manager'))
    appearance = get_auth_appearance()
    slider_key = f'{page}_slider_images'
    slider_list = json.loads(appearance.get(slider_key, '[]'))
    slider_list.append(filename)
    update_auth_appearance(**{slider_key: json.dumps(slider_list)})
    log_admin_action('auth_slider_upload', 'auth', 0,
                     f'Uploaded {page} slider image: {filename}')
    flash(f'✅ Slider image added to {page} page.', 'success')
    return redirect(url_for('admin.auth_appearance_manager'))


@admin_bp.route('/appearance/auth/delete-image', methods=['POST'])
@admin_required
def auth_appearance_delete_image():
    """Delete an auth image (banner, mobile, or slider image)."""
    page = request.form.get('page', 'login')
    image_type = request.form.get('type', 'banner')  # banner, mobile, slider
    index = request.form.get('index', type=int)

    appearance = get_auth_appearance()

    if image_type == 'banner':
        key = f'{page}_banner'
        old = appearance.get(key)
        if old:
            _delete_auth_image(old)
            update_auth_appearance(**{key: ''})
        log_admin_action('auth_banner_delete', 'auth', 0, f'Deleted {page} banner')
        flash(f'🗑️ {page.title()} banner removed.', 'info')

    elif image_type == 'mobile':
        key = f'{page}_mobile_image'
        old = appearance.get(key)
        if old:
            _delete_auth_image(old)
            update_auth_appearance(**{key: ''})
        log_admin_action('auth_mobile_delete', 'auth', 0, f'Deleted {page} mobile image')
        flash(f'🗑️ {page.title()} mobile image removed.', 'info')

    elif image_type == 'slider' and index is not None:
        slider_key = f'{page}_slider_images'
        slider_list = json.loads(appearance.get(slider_key, '[]'))
        if 0 <= index < len(slider_list):
            _delete_auth_image(slider_list[index])
            slider_list.pop(index)
            update_auth_appearance(**{slider_key: json.dumps(slider_list)})
        log_admin_action('auth_slider_delete', 'auth', 0,
                         f'Deleted {page} slider image #{index}')
        flash(f'🗑️ Slider image removed from {page} page.', 'info')

    return redirect(url_for('admin.auth_appearance_manager'))


# ──────────────────────────────────────────────
# Recycle Bin
# ──────────────────────────────────────────────
@admin_bp.route('/recycle-bin')
@admin_required
def recycle_bin():
    """View soft-deleted places."""
    deleted = get_deleted_places()
    return render_template('admin/recycle_bin.html', deleted=deleted)


@admin_bp.route('/restore/<int:place_id>', methods=['POST'])
@admin_required
def restore_place_route(place_id):
    """Restore a soft-deleted place."""
    place = get_place_by_id(place_id)
    if not place:
        flash('Place not found.', 'error')
        return redirect(url_for('admin.recycle_bin'))
    restore_place(place_id)
    log_admin_action('restore', 'place', place_id, f'Restored: {place["name"]}')
    flash('✅ Place restored successfully.', 'success')
    return redirect(url_for('admin.recycle_bin'))


@admin_bp.route('/permanent-delete/<int:place_id>', methods=['POST'])
@admin_required
def permanent_delete_route(place_id):
    """Permanently delete a place — irreversible."""
    place = get_place_by_id(place_id)
    if place:
        # Delete uploaded photos from disk
        photos = get_photos_by_place(place_id)
        for photo in photos:
            filepath = os.path.join(UPLOAD_FOLDER, photo['filename'])
            if os.path.exists(filepath):
                os.remove(filepath)
    permanent_delete_place(place_id)
    log_admin_action('permanent_delete', 'place', place_id, f'Permanently deleted: {place["name"] if place else "Unknown"}')
    flash('🗑️ Place permanently deleted. This cannot be undone.', 'info')
    return redirect(url_for('admin.recycle_bin'))


# ──────────────────────────────────────────────
# User Photo Moderation
# ──────────────────────────────────────────────

@admin_bp.route('/user-photos')
@admin_required
def user_photos_admin():
    """Admin page to moderate user-uploaded photos."""
    filter_status = request.args.get('status', 'pending')
    if filter_status == 'all':
        photos = get_all_user_photos_admin()
    else:
        photos = get_user_photos_by_status(filter_status)

    pending_count = count_pending_user_photos()
    return render_template('admin/user_photos.html',
                           photos=photos,
                           filter_status=filter_status,
                           pending_count=pending_count)


@admin_bp.route('/user-photo/approve/<int:photo_id>', methods=['POST'])
@admin_required
def approve_user_photo_view(photo_id):
    approve_user_photo(photo_id)
    log_admin_action('approve_photo', 'user_photo', photo_id, 'Approved user photo')
    flash('✅ Photo approved!', 'success')
    return redirect(request.referrer or url_for('admin.user_photos_admin'))


@admin_bp.route('/user-photo/reject/<int:photo_id>', methods=['POST'])
@admin_required
def reject_user_photo_view(photo_id):
    reject_user_photo(photo_id)
    log_admin_action('reject_photo', 'user_photo', photo_id, 'Rejected user photo')
    flash('❌ Photo rejected.', 'info')
    return redirect(request.referrer or url_for('admin.user_photos_admin'))


@admin_bp.route('/user-photo/delete/<int:photo_id>', methods=['POST'])
@admin_required
def delete_user_photo_view(photo_id):
    photo = delete_user_photo(photo_id)
    if photo:
        filepath = os.path.join(UPLOAD_FOLDER, photo['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
    log_admin_action('delete_photo', 'user_photo', photo_id, 'Deleted user photo')
    flash('🗑️ Photo deleted.', 'info')
    return redirect(request.referrer or url_for('admin.user_photos_admin'))


# ──────────────────────────────────────────────
# District Management
# ──────────────────────────────────────────────
DISTRICT_UPLOAD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads', 'districts')
os.makedirs(DISTRICT_UPLOAD, exist_ok=True)


@admin_bp.route('/districts')
@admin_required
def districts_manager():
    """District management page."""
    districts = get_all_districts_admin()
    return render_template('admin/districts.html', districts=districts)


@admin_bp.route('/districts/edit/<int:district_id>', methods=['GET', 'POST'])
@admin_required
def edit_district_view(district_id):
    """Edit a district."""
    district = get_district_by_id(district_id)
    if not district:
        flash('District not found.', 'error')
        return redirect(url_for('admin.districts_manager'))

    if request.method == 'POST':
        update_district(district_id,
                        name=request.form.get('name', district['name']),
                        description=request.form.get('description', ''),
                        famous_for=request.form.get('famous_for', ''),
                        is_featured=1 if request.form.get('is_featured') else 0,
                        is_visible=1 if request.form.get('is_visible') else 0,
                        sort_order=int(request.form.get('sort_order', 0)))
        log_admin_action('edit_district', 'district', district_id, f'Updated: {request.form.get("name")}')
        flash(f'✅ District "{request.form.get("name")}" updated!', 'success')
        return redirect(url_for('admin.districts_manager'))

    return render_template('admin/edit_district.html', district=district)


@admin_bp.route('/districts/delete/<int:district_id>', methods=['POST'])
@admin_required
def delete_district_view(district_id):
    """Delete a district — only if it has no places."""
    d = get_district_by_id(district_id)
    if not d:
        flash('District not found.', 'error')
        return redirect(url_for('admin.districts_manager'))

    # Safety check: refuse if district has places
    place_count = count_places_in_district(district_id)
    if place_count > 0:
        flash(f'⚠️ Cannot delete "{d["name"]}" — it has {place_count} places. Move or delete them first.', 'error')
        return redirect(url_for('admin.districts_manager'))

    d = delete_district(district_id)
    if d and d.get('cover_image'):
        fpath = os.path.join(DISTRICT_UPLOAD, d['cover_image'])
        if os.path.exists(fpath):
            os.remove(fpath)
    log_admin_action('delete_district', 'district', district_id, f'Deleted: {d["name"] if d else "Unknown"}')
    flash('🗑️ District deleted.', 'info')
    return redirect(url_for('admin.districts_manager'))


@admin_bp.route('/districts/toggle/<int:district_id>', methods=['POST'])
@admin_required
def toggle_district_visibility(district_id):
    """Toggle district visibility."""
    d = get_district_by_id(district_id)
    if d:
        new_vis = 0 if d.get('is_visible', 1) else 1
        update_district(district_id, is_visible=new_vis)
        status = 'visible' if new_vis else 'hidden'
        flash(f'{"👁️" if new_vis else "🙈"} District {d["name"]} is now {status}.', 'success')
    return redirect(url_for('admin.districts_manager'))


@admin_bp.route('/districts/feature/<int:district_id>', methods=['POST'])
@admin_required
def toggle_district_featured(district_id):
    """Toggle district featured status."""
    d = get_district_by_id(district_id)
    if d:
        new_feat = 0 if d.get('is_featured', 0) else 1
        update_district(district_id, is_featured=new_feat)
        status = 'featured' if new_feat else 'unfeatured'
        flash(f'{"⭐" if new_feat else "☆"} District {d["name"]} is now {status}.', 'success')
    return redirect(url_for('admin.districts_manager'))


@admin_bp.route('/districts/upload-cover/<int:district_id>', methods=['POST'])
@admin_required
def upload_district_cover(district_id):
    """Upload/replace cover image for a district."""
    d = get_district_by_id(district_id)
    if not d:
        flash('District not found.', 'error')
        return redirect(url_for('admin.districts_manager'))

    f = request.files.get('cover_image')
    if not f or not f.filename or not allowed_file(f.filename):
        flash('Please select a valid image file.', 'error')
        return redirect(request.referrer or url_for('admin.districts_manager'))
    if not validate_image_file(f) or not check_file_size(f):
        flash('Invalid image or file too large (max 5MB).', 'error')
        return redirect(request.referrer or url_for('admin.districts_manager'))

    # Delete old cover
    old_cover = d.get('cover_image', '')
    if old_cover:
        old_path = os.path.join(DISTRICT_UPLOAD, old_cover)
        if os.path.exists(old_path):
            os.remove(old_path)

    # Save new
    ext = f.filename.rsplit('.', 1)[1].lower()
    filename = f"district_{district_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(DISTRICT_UPLOAD, filename)
    try:
        img = Image.open(f)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 800:
            ratio = 800 / img.width
            img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
        img.save(filepath, quality=85, optimize=True)
    except Exception:
        logger.warning("PIL failed for district cover %d, skipping raw save", district_id)
        flash('Failed to process image. Please try a different file.', 'error')
        return redirect(request.referrer or url_for('admin.districts_manager'))

    update_district(district_id, cover_image=filename)
    log_admin_action('upload_district_cover', 'district', district_id, f'Cover: {filename}')
    flash('📷 District cover updated!', 'success')
    return redirect(request.referrer or url_for('admin.districts_manager'))


@admin_bp.route('/districts/delete-cover/<int:district_id>', methods=['POST'])
@admin_required
def delete_district_cover(district_id):
    """Delete district cover image."""
    d = get_district_by_id(district_id)
    if d and d.get('cover_image'):
        fpath = os.path.join(DISTRICT_UPLOAD, d['cover_image'])
        if os.path.exists(fpath):
            os.remove(fpath)
        update_district(district_id, cover_image='')
        flash('🗑️ Cover image removed.', 'info')
    return redirect(request.referrer or url_for('admin.districts_manager'))


@admin_bp.route('/districts/reorder', methods=['POST'])
@admin_required
def reorder_districts_view():
    """Reorder districts via AJAX."""
    ids = request.json.get('ids', [])
    if ids:
        reorder_districts(ids)
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 400


# ──────────────────────────────────────────────
# Trending Management
# ──────────────────────────────────────────────
@admin_bp.route('/trending')
@admin_required
def trending_manager():
    """Trending places management page."""
    trending = get_trending_admin()
    return render_template('admin/trending.html', trending=trending)


@admin_bp.route('/trending/add', methods=['POST'])
@admin_required
def add_trending_view():
    """Add a place to trending."""
    place_id = request.form.get('place_id', type=int)
    if place_id:
        ok = add_to_trending(place_id)
        if ok:
            flash('🔥 Place added to trending!', 'success')
        else:
            flash('Place is already in trending.', 'info')
    return redirect(url_for('admin.trending_manager'))


@admin_bp.route('/trending/remove/<int:trending_id>', methods=['POST'])
@admin_required
def remove_trending_view(trending_id):
    """Remove a place from trending."""
    remove_from_trending(trending_id)
    flash('🗑️ Removed from trending.', 'info')
    return redirect(url_for('admin.trending_manager'))


@admin_bp.route('/trending/toggle/<int:trending_id>', methods=['POST'])
@admin_required
def toggle_trending_view(trending_id):
    """Toggle trending active state."""
    toggle_trending(trending_id)
    flash('✅ Trending status toggled.', 'success')
    return redirect(url_for('admin.trending_manager'))


@admin_bp.route('/trending/reorder', methods=['POST'])
@admin_required
def reorder_trending_view():
    """Reorder trending via AJAX."""
    ids = request.json.get('ids', [])
    if ids:
        reorder_trending(ids)
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 400


@admin_bp.route('/api/search-places')
@admin_required
def api_search_places():
    """AJAX place search for autocomplete."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    results = search_places_simple(q, limit=10)
    return jsonify(results)


# ═══ NEARBY SERVICES MANAGEMENT ═══

SERVICE_TYPES = [
    ('hospital', '🏥 Hospital'),
    ('pharmacy', '💊 Pharmacy'),
    ('petrol_pump', '⛽ Petrol Pump'),
    ('atm', '🏧 ATM'),
    ('mechanic', '🔧 Mechanic'),
    ('police', '👮 Police Station'),
    ('railway', '🚂 Railway Station'),
    ('bus_stand', '🚌 Bus Stand'),
    ('restaurant', '🍽️ Restaurant'),
    ('dhaba', '🍛 Dhaba / Tea Shop'),
]

@admin_bp.route('/nearby-services')
@admin_required
def nearby_services():
    """Manage nearby essential services."""
    district_id = request.args.get('district_id', type=int)
    services = get_nearby_services_admin(district_id)
    districts = get_admin_districts_list()

    return render_template('admin/nearby_services.html',
                           services=services, districts=districts,
                           service_types=SERVICE_TYPES,
                           selected_district=district_id)


@admin_bp.route('/nearby-services/add', methods=['POST'])
@admin_required
def add_nearby_service_view():
    """Add a nearby service."""
    data = {
        'district_id': request.form.get('district_id', type=int),
        'name': request.form.get('name', '').strip(),
        'service_type': request.form.get('service_type', ''),
        'address': request.form.get('address', '').strip(),
        'phone': request.form.get('phone', '').strip(),
        'latitude': request.form.get('latitude', type=float),
        'longitude': request.form.get('longitude', type=float),
    }
    db_add_nearby_service(data)
    log_admin_action('add', 'nearby_service', 0, f"Added {data['name']}")
    flash('Service added!', 'success')
    return redirect(url_for('admin.nearby_services', district_id=request.form.get('district_id')))


@admin_bp.route('/nearby-services/delete/<int:svc_id>', methods=['POST'])
@admin_required
def delete_nearby_service_view(svc_id):
    """Delete a nearby service."""
    svc = db_delete_nearby_service(svc_id)
    district_id = svc['district_id'] if svc else None
    log_admin_action('delete', 'nearby_service', svc_id, f"Deleted {svc['name'] if svc else 'service'}")
    flash('Service deleted.', 'info')
    return redirect(url_for('admin.nearby_services', district_id=district_id))


# ═══════════════════════════════════════════════════
# ADMIN — USER MANAGEMENT
# ═══════════════════════════════════════════════════
@admin_bp.route('/users')
@admin_required
def users():
    """List all users with search and pagination."""
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    if q:
        user_list = search_users(q)
    else:
        user_list = get_all_users()

    total_users = len(user_list)
    paginated_users = user_list[offset:offset + per_page]
    total_pages = max(1, (total_users + per_page - 1) // per_page)

    return render_template('admin/users.html',
                           users=paginated_users,
                           query=q,
                           page=page,
                           per_page=per_page,
                           total_users=total_users,
                           total_pages=total_pages)


@admin_bp.route('/users/<int:user_id>/status', methods=['POST'])
@admin_required
def change_user_status(user_id):
    """Change user status: activate, suspend, ban."""
    new_status = request.form.get('status', '')
    if new_status not in ('active', 'suspended', 'banned'):
        flash('Invalid status.', 'error')
        return redirect(url_for('admin.users'))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))

    update_user_status(user_id, new_status)
    log_admin_action('user_status', 'user', user_id, f"Changed {user['username']} to {new_status}")
    status_emoji = {'active': '✅', 'suspended': '⏸️', 'banned': '🚫'}
    flash(f'{status_emoji.get(new_status, "")} User "{user["username"]}" is now {new_status}.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user_view(user_id):
    """Permanently delete a user."""
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))

    db_delete_user(user_id)
    log_admin_action('delete', 'user', user_id, f"Deleted user: {user['username']}")
    flash(f'🗑️ User "{user["username"]}" deleted permanently.', 'info')
    return redirect(url_for('admin.users'))

