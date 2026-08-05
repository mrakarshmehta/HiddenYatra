"""
HiddenYatra — Application configuration.
Loads sensitive values from environment variables with secure defaults.
"""
import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ── Environment ──
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
IS_PRODUCTION = FLASK_ENV == 'production'

# ── Database (MySQL) ──
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))
DB_NAME = os.environ.get('DB_NAME', 'hiddenyatra')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_CHARSET = os.environ.get('DB_CHARSET', 'utf8mb4')
DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '5'))
DB_POOL_MAX = int(os.environ.get('DB_POOL_MAX', '20'))
DB_TIMEOUT = int(os.environ.get('DB_TIMEOUT', '10'))

# ── Uploads ──
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'places')
AUTH_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'auth')
SUBMISSION_UPLOAD = os.path.join(BASE_DIR, 'static', 'uploads', 'submissions')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB total request body
MAX_SINGLE_FILE_SIZE = 5 * 1024 * 1024   # 5 MB per individual file
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
ALLOWED_MIMETYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'image/gif'
}

# ── Secrets ──
# In production, these MUST be set via environment variables.
# In development, a random key is generated per-run (safe for dev).
_env_secret = os.environ.get('SECRET_KEY', '')
if IS_PRODUCTION and not _env_secret:
    raise RuntimeError(
        "SECRET_KEY environment variable is required in production. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )
SECRET_KEY = _env_secret or secrets.token_hex(32)

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
if IS_PRODUCTION and not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD environment variable is required in production.")
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = 'admin@hidden123'  # Dev-only fallback

# ── App Branding ──
APP_NAME = 'HiddenYatra'
APP_TAGLINE = "Discover Bihar's Hidden Gems"
PRIMARY_STATE = 'Bihar'


# ── File Validation Helpers ──
def allowed_file(filename):
    """Check file extension is allowed."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_image_file(file_obj):
    """Validate file is actually an image by checking magic bytes."""
    header = file_obj.read(16)
    file_obj.seek(0)

    # JPEG: FF D8 FF
    if header[:3] == b'\xff\xd8\xff':
        return True
    # PNG: 89 50 4E 47
    if header[:4] == b'\x89PNG':
        return True
    # GIF: GIF87a or GIF89a
    if header[:3] == b'GIF':
        return True
    # WebP: RIFF....WEBP
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return True
    return False


def check_file_size(file_obj):
    """Check individual file doesn't exceed MAX_SINGLE_FILE_SIZE.
    Returns True if file is within limits, False otherwise.
    """
    file_obj.seek(0, 2)  # Seek to end
    size = file_obj.tell()
    file_obj.seek(0)     # Reset to start
    return size <= MAX_SINGLE_FILE_SIZE
