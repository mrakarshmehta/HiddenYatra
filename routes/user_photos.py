"""User photo upload routes — visitors can upload photos for places."""
import os
import logging
from flask import Blueprint, request, redirect, url_for, flash, session
from config import UPLOAD_FOLDER, allowed_file, validate_image_file, check_file_size
from models.database import add_user_photo, get_place_by_id
from utils import csrf_required, get_session_id as _get_session_id
from utils.image import process_and_save_image

logger = logging.getLogger(__name__)
user_photos_bp = Blueprint('user_photos', __name__)


def save_user_photo(file_obj, place_id):
    """Save user uploaded image, resize if needed, return filename or None."""
    return process_and_save_image(
        file_obj, UPLOAD_FOLDER,
        prefix=f"user_{place_id}",
        max_width=1920, quality=85
    )


@user_photos_bp.route('/place/<int:place_id>/upload-photo', methods=['POST'])
@csrf_required
def upload_user_photo(place_id):
    """User uploads a photo for a place — goes to pending moderation."""
    place = get_place_by_id(place_id)
    if not place:
        flash('Place not found.', 'error')
        return redirect(url_for('main.index'))

    files = request.files.getlist('user_photos')
    if not files or not files[0].filename:
        flash('Please select at least one photo.', 'error')
        return redirect(url_for('places.place_detail', slug=place['slug']))

    sid = _get_session_id()
    uploader = request.form.get('uploader_name', '').strip() or 'Anonymous Traveler'
    caption = request.form.get('caption', '').strip()

    count = 0
    for f in files:
        if f and f.filename and allowed_file(f.filename) and validate_image_file(f) and check_file_size(f):
            filename = save_user_photo(f, place_id)
            if filename:
                add_user_photo(place_id, sid, uploader, filename, caption)
                count += 1

    if count > 0:
        flash(f'📸 {count} photo(s) uploaded! They will appear in the gallery after admin approval.', 'success')
    else:
        flash('No valid images selected. Allowed: JPG, PNG, WebP.', 'error')

    return redirect(url_for('places.place_detail', slug=place['slug']))
