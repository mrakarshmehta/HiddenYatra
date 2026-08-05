# HiddenYatra — Developer Guide

## Getting Started

### Prerequisites
- Python 3.11+
- MySQL 8.x running locally
- Git

### Quick Start

```bash
git clone <repo-url>
cd HiddenYatra
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # Edit with your MySQL credentials
python app.py
```

Open `http://localhost:5000` in your browser.

Admin panel: `http://localhost:5000/admin` (default password: `admin@hidden123`)

---

## Project Structure

```
HiddenYatra/
├── app.py              # App factory — start here
├── config.py           # All configuration
├── models/database.py  # All SQL queries (single file)
├── routes/             # Blueprint route handlers
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS, images, uploads
├── utils/              # CSRF, auth decorators, OTP
├── tests/              # Test suites
└── docs/               # This documentation
```

---

## Coding Conventions

### Python
- **Style**: PEP 8, 4 spaces, 100 char line limit
- **Docstrings**: Triple-quote for all public functions
- **Imports**: stdlib → third-party → local, separated by blank lines
- **Logging**: Use `logger = logging.getLogger(__name__)` per module, never `print()`
- **SQL**: Always use parameterized queries (`%s` placeholders), never f-strings
- **Error handling**: Catch specific exceptions, log with `logger.error()`, flash user-friendly messages

### Templates
- **Base template**: All pages extend `base.html`
- **Auto-escaping**: Enabled by default — use `{{ var }}` safely
- **CSRF**: Include `{{ csrf_input() }}` in every form
- **Assets**: Reference via `url_for('static', filename='...')`

### CSS
- Vanilla CSS with BEM-like naming
- Design tokens in `main.css` (`:root` variables)
- Component styles in `components.css`
- Admin styles in `admin.css`

### JavaScript
- Vanilla JS — no frameworks
- Main app logic in `app.js`
- Map logic in `map.js`
- Gallery in `gallery.js`

---

## Adding a New Feature

### 1. Add Database Functions

Edit `models/database.py`:

```python
def get_my_feature(feature_id):
    """Fetch feature by ID."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM my_table WHERE id = %s", (feature_id,))
        return cur.fetchone()

def create_my_feature(name, value):
    """Create a new feature record."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO my_table (name, value) VALUES (%s, %s)",
            (name, value)
        )
        return cur.lastrowid
```

### 2. Create Blueprint

Create `routes/my_feature.py`:

```python
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import get_my_feature, create_my_feature
from utils import csrf_required

logger = logging.getLogger(__name__)
my_feature_bp = Blueprint('my_feature', __name__)


@my_feature_bp.route('/my-feature')
def index():
    return render_template('my_feature.html')


@my_feature_bp.route('/my-feature/create', methods=['POST'])
@csrf_required
def create():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Name is required.', 'error')
        return redirect(url_for('my_feature.index'))
    create_my_feature(name, 'value')
    flash('Created!', 'success')
    return redirect(url_for('my_feature.index'))
```

### 3. Register Blueprint

Edit `app.py`:

```python
from routes.my_feature import my_feature_bp
app.register_blueprint(my_feature_bp)
```

### 4. Create Template

Create `templates/my_feature.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1>My Feature</h1>
<form method="POST" action="{{ url_for('my_feature.create') }}">
    {{ csrf_input() }}
    <input type="text" name="name" required>
    <button type="submit">Create</button>
</form>
{% endblock %}
```

### 5. Add Tests

Create `tests/test_my_feature.py` following the pattern in `tests/test_routes.py`.

---

## Database Access Pattern

**Always use the context manager:**

```python
# READ — auto-closes cursor and connection
with get_cursor() as cur:
    cur.execute("SELECT ...", params)
    return cur.fetchall()

# WRITE — auto-commits on success, auto-rollbacks on exception
with get_cursor(commit=True) as cur:
    cur.execute("INSERT ...", params)
    return cur.lastrowid
```

**Never do this:**
```python
# ❌ Raw connection without proper cleanup
conn = get_db()
cur = conn.cursor()
cur.execute(...)  # If this throws, connection leaks
```

---

## Debugging Guide

### Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| `OperationalError: Can't connect to MySQL` | MySQL not running | Start MySQL service |
| `CSRF token invalid` | Session expired or missing token | Clear cookies, check `csrf_input()` |
| `413 Request Entity Too Large` | File > 16MB | Reduce file size |
| `500 Internal Server Error` | Check `app.log` for traceback | Fix the underlying error |
| Template not found | Wrong template path | Check `templates/` directory |
| Static file 404 | Wrong `url_for` path | Check `static/` directory |

### Logging

All modules use Python's `logging` module:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General info")
logger.warning("Something unexpected")
logger.error("Error occurred: %s", error)
logger.exception("Error with traceback")
```

### Database Debugging

```python
# In Python shell
from models.database import get_cursor
with get_cursor() as cur:
    cur.execute("SHOW TABLES")
    print(cur.fetchall())
```

---

## Testing

```bash
# Run all tests
python -m unittest discover -s tests -v

# Run specific test file
python -m unittest tests.test_database -v

# Run specific test class
python -m unittest tests.test_security.TestUploadSecurity -v
```

Note: Route tests require MySQL to be running. They skip gracefully when MySQL is unavailable.
