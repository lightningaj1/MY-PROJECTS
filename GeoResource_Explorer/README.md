# GeoResource Explorer

A Flask-based web application for exploring mineral resources, their properties, economic importance, and global distribution.

## Features

- User authentication (login/register)
- Mineral database with search and filtering
- Admin panel for adding/editing/deleting minerals
- Favorites system
- Global mineral distribution map
- Commodity price tracking
- Image uploads for minerals
- **QGIS Integration:** Import mineral deposits and mining claims directly from QGIS
- **Interactive Maps:** Populated with real geospatial data from QGIS exports

## Project Structure

```
GeoResource_Explorer/
├── app.py                 # Entry point
├── requirements.txt       # Dependencies
├── minerals.db           # SQLite database
├── app/
│   ├── __init__.py       # App factory (create_app)
│   ├── auth.py           # Authentication routes
│   ├── admin.py          # Admin routes
│   ├── minerals.py       # Mineral routes (browse, search)
│   ├── prices.py         # Price tracking routes
│   ├── map.py            # Map visualization routes
│   ├── routes.py         # Route registration
│   ├── db.py             # Database connection
│   ├── helpers.py        # Helper functions (login_required decorator)
│   ├── utils.py          # Utility functions (is_admin, file handling)
│   └── init_db.py        # Database initialization script
├── templates/            # Jinja2 HTML templates
│   ├── layout.html       # Base template
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── minerals.html
│   ├── mineral.html
│   ├── admin.html
│   ├── add.html
│   ├── edit.html
│   ├── search.html
│   ├── favorites.html
│   ├── prices.html
│   └── map.html
└── static/
    ├── style.css
    └── images/           # Mineral images
```

## Setup & Installation

### 1. Install Dependencies
```bash
cd GeoResource_Explorer
pip install -r requirements.txt
```

### 2. Initialize Database (if needed)
```bash
python -c "import sys; sys.path.insert(0, '.'); from app.init_db import *"
```

### 3. Run the Application
```bash
python app.py
```

The app will start on `http://localhost:5000`

## Default Admin Credentials

- **Username:** `admin`
- **Password:** `Admin@123`

## QGIS Data Import

GeoResource Explorer now supports importing mineral deposits and mining claims directly from QGIS!

### Quick Start

1. **Export your data from QGIS** as GeoJSON or CSV
2. **Login as admin** and go to **Admin Dashboard** → **QGIS Data Import**
3. **Upload your file** and watch the maps populate with your data

### Supported Formats
- **GeoJSON** - Standard geospatial format (recommended)
- **CSV** - Comma-separated values with coordinates
- **JSON** - Alternative JSON format

### Example Data

Sample files are provided in `samples/`:
- `sample_deposits.geojson` - Example mineral deposits
- `sample_claims.csv` - Example mining claims

### Full Documentation

For detailed QGIS export instructions, field mappings, and troubleshooting:
➡️ **[QGIS_IMPORT_GUIDE.md](QGIS_IMPORT_GUIDE.md)**

## Database Schema

### users
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE NOT NULL)
- `hash` (TEXT NOT NULL) - Password hash
- `is_admin` (INTEGER DEFAULT 0)

### minerals
- `id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY)
- `name` (TEXT NOT NULL)
- `formula` (TEXT)
- `properties` (TEXT)
- `uses` (TEXT)
- `economic` (TEXT)
- `countries` (TEXT)
- `image` (TEXT)

### favorites
- `id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY)
- `mineral_id` (INTEGER, FOREIGN KEY)

## Routes

### Public
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Process registration
- `GET /logout` - Logout

### Authenticated
- `GET /` - Home page (6 latest minerals)
- `GET /minerals` - Browse all minerals with pagination
- `GET /mineral/<id>` - Mineral detail page
- `GET /search` - Search minerals
- `GET /favorites` - View favorited minerals
- `GET /prices` - Commodity prices
- `GET /map` - Global mineral distribution map

### Admin Only
- `GET /admin` - Admin dashboard
- `POST /admin/upload` - Upload mineral data
- `GET /admin/edit/<id>` - Edit mineral form
- `POST /admin/edit/<id>` - Update mineral
- `POST /admin/delete/<id>` - Delete mineral

## Technologies

- **Backend:** Flask 2.3
- **Database:** SQLite3
- **Frontend:** HTML/CSS/JavaScript
- **Maps:** Leaflet.js
- **API:** Metals-API for commodity prices (optional)

## Notes

- Images are stored in `static/images/`
- Admin user is seeded with `is_admin=1`
- Mineral images are optional; uploads are handled via file forms
- Price data can be live (requires METALS_API_KEY env var) or cached/mock data

## Future Enhancements

- Advanced filtering and sorting
- User-submitted mineral data
- Export data to CSV/JSON
- Enhanced admin statistics dashboard
- Multi-language support
