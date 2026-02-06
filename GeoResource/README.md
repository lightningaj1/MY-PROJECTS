# GeoResource Explorer

### Video Demo: <https://www.youtube.com/watch?v=1AT8WNPEaBI>

### Description

GeoResource Explorer is a full-stack web-based economic geology application built as a final project for CS50.
The application allows users to explore mineral resources, their chemical composition, economic importance and global distribution. it is designed for students, geologists, and anyone interested in mineral economics.

The project demonstrates full-stack web development using Flask, SQlite, HTML, CSS, and Javascript.

---

## Features

### User Features
- User registration and login with password hashing
- Secure password hashing using Werkzeug
- Browse minerals with detailed descriptions
- Search minerals by name, properties, or countries
- view mineral locations on an interactive map
- Add minerals to personal favorites
- Responsive design for mobile, tablet, and desktop
- Light mode and dark mode toggle
- View commodity prices (with API support)


### Amdin Features
- Secure amin-only access
- Add new minerals to the database
- Upload and display mineral images
- Edit existing mineral records
- Delete minerals safely
- Role-based access control using adminflag

### Additional functionality
- Paginated minerals list
- Interactive map using Leaflet.js showing mineral-producing countries
- Commodity prices page demonstrating API usage with caching and fallback data
- Session based access control for protected routes
---

## Technologies used
- Python (Flask) - backend framework
- SQlite - database
- HTML / CSS / Javascript - frontend
- Leaflet.js - interactive maps
- Werkzeug - password hashing and security
- API - live commodity prices

---

## Project Structure
project/
|
|---- app.py
|---- helpers.py
|---- init_db.py
|---- minerals.db
|---- requirements.txt
|
|---- templates/
| |---- layout.html
| |---- home.html
| |---- login.html
| |---- register.html
| |---- mineral.html
| |---- minerals.html
| |---- add.html
| |---- edit.html
| |---- admin.html
| |---- favorites.html
| |---- search.html
| |---- map.html
| |____ prices.html
|
|---- static/
| |---- style.css
| |____ images/
|
|____README.md

---

## Database Design

The database consists of three main tables:

- Users: stores user accounts and asmin roles
- Minerals: stores mineral data and images
- Favorites: links users to their favorite minerals

The database schema is initialized using `init_db.py`, ensuring reproducibility without including raw database files
Passwords are securely hashed using Werkzeug.

---

## Security Measures
- Passwords are securely hashed
- Admin-only routes are protected
- User sessions are validated before accessing restricted pages
- File uploads use secure filenames
- Direct database manipulation by users is prevented
---

## Responsive Design
The application is fully responsive:
- Mobile-friendly navigation menu
- Adaptive layouts using CSS Grid and Flexbox
- Optimized typography and spacing
- Touch-friendly buttons and controls

## How the application works
1. Users register and log in to the system
2. Authenticated users can browse, search, and view mineral details
3. Users can add minerals to their favorites
4. Adminusers can add, edit, and delete minerals
5. Maps and commodity prices enhance real-world context

---

## Design Decisions
- Flask was chosen for its simplicity and flexibility
- SQLite was used for ease of setup and portability
- Leaflet.js enables interactive geographical visualization
- Role-based access control ensures safe content managenent
- Responsive design ensures usability on all devices

---

## Challenges and Solutions
One major challenge was implementing secure admin-only functionality. This was solved by adding an `is_admin` field in the users table and enforcing route protection using session checks.

Another challenge was handling image uploads and didplay. This was resolved securely saving image files to a static directory and storing their paths in the database.

## How to Run locally
1. Clone the repository
2. Install dependencies: pip install flask requests
3. Initialize the database: python init_db.py
4. run the app: flask run
5. open the provided local URL in your browser

## Admin Account

Default admin credentials (used for demonstration purposes only and can be changed):
- Username: `admin`
- Password: `Admin@123`

---

## what this project demonstrates
- Full-stack web development
- SQL database design queries
- Secure authentication and authorization
- Responsive UI/UX design
- clean code organization
- practical application of CS50 concepts

## Acknowledgements
this project was created as part of CS50: Introduction to Computer Science by Harvard University


## Author

Ater John Kuei
CS50 Final Project


