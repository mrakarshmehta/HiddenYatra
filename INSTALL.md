# 🚀 HiddenYatra — Installation & Quick Start Guide

## Prerequisites

- **Python**: 3.11+ (Python 3.13 supported)
- **Database**: MySQL 8.0+ or MariaDB 10.5+
- **Package Manager**: `pip`

---

## 🛠️ Local Setup Instructions

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-org/HiddenYatra.git
cd HiddenYatra

python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your MySQL credentials:
```bash
cp .env.example .env
```

Set variables in `.env`:
```ini
FLASK_ENV=development
FLASK_DEBUG=0
SECRET_KEY=change-me-to-a-random-64-char-string
ADMIN_PASSWORD=admin_password_123

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=hiddenyatra
DB_USER=root
DB_PASSWORD=your_mysql_password
```

### 4. Database Initialization & Data Seeding
Create MySQL database:
```sql
CREATE DATABASE hiddenyatra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Seed tables and initial data:
```bash
python scripts/migrations/migrate_schema.py
python scripts/seed/seed_all_essential_services.py
python scripts/seed/update_places_real_photos.py
```

### 5. Run Application
```bash
python app.py
```
Open browser at `http://localhost:5000`

---

## 🧪 Verification & Testing
```bash
python -m unittest discover tests -v
python scripts/seed/verify_full_system.py
```
