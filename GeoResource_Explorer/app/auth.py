from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from app.roles import ROLES
from app.helpers import validate_password
import re

def auth_routes(app):
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri="memory://"
    )

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def login():
        session.clear()
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            
            # Input validation
            if not username or not password:
                return render_template("login.html", error="Username and password required")
            
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if user and check_password_hash(user["hash"], password):
                session["user_id"] = user["id"]
                session.permanent = True
                return redirect("/")
            
            # Generic error to prevent username enumeration
            return render_template("login.html", error="Invalid credentials")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    @app.route("/register", methods=["GET", "POST"])
    @limiter.limit("3 per minute")
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm", "")
            role = request.form.get("role", "viewer")
            organization = request.form.get("organization", "").strip()
            expertise = request.form.get("expertise", "").strip()
            
            # Input validation
            if not username or not password or not confirm:
                return render_template("register.html", error="All fields required", roles=ROLES)
            
            if len(username) < 3 or len(username) > 50:
                return render_template("register.html", error="Username must be 3-50 characters", roles=ROLES)
            
            # Validate username format (alphanumeric, underscore, hyphen only)
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                return render_template("register.html", error="Username can only contain letters, numbers, underscores, and hyphens", roles=ROLES)
            
            # Enhanced password validation
            password_error = validate_password(password)
            if password_error:
                return render_template("register.html", error=password_error, roles=ROLES)
            
            if password != confirm:
                return render_template("register.html", error="Passwords do not match", roles=ROLES)
            
            # Validate role
            if role not in ROLES:
                role = "viewer"
            
            # Validate organization and expertise length
            if len(organization) > 255 or len(expertise) > 500:
                return render_template("register.html", error="Input fields too long", roles=ROLES)
            
            hash_pw = generate_password_hash(password)
            db = get_db()
            
            try:
                db.execute(
                    """INSERT INTO users (username, hash, role, organization, expertise) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (username, hash_pw, role, organization, expertise)
                )
                db.commit()
                return redirect("/login")
            except Exception as e:
                # Generic error message to prevent information leakage
                return render_template("register.html", error="Registration failed. Please try again.", roles=ROLES)
        
        return render_template("register.html", roles=ROLES)
