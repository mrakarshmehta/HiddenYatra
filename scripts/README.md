# Scripts

Utility scripts for database seeding, migrations, and legacy references.

## Directory Structure

```
scripts/
├── seed/               # Database seeding scripts
│   ├── seed_bihar.py           # Core Bihar places data
│   ├── seed_bihar_complete.py  # Extended Bihar dataset
│   ├── seed_bihar_hierarchy.py # State → District → Block hierarchy
│   ├── seed_data.py            # General seed data
│   ├── seed_hotels.py          # Hotel/accommodation data
│   └── seed_images.py          # Image URL seeding
├── migrations/         # Database schema migrations
│   ├── migrate_auth.py         # User auth columns (OTP, status)
│   └── migrate_schema.py       # Nearby services, reach fields
└── legacy/             # Old static HTML prototype (reference only)
    ├── index.html
    ├── app.js
    ├── data.js
    └── styles.css
```

## Usage

### Running Seeds
```bash
# From project root
python scripts/seed/seed_bihar.py
python scripts/seed/seed_bihar_complete.py
```

### Running Migrations
```bash
python scripts/migrations/migrate_auth.py
python scripts/migrations/migrate_schema.py
```

> **Note:** Migrations are idempotent (safe to run multiple times).
> Seeds should only be run on a fresh database to avoid duplicates.
