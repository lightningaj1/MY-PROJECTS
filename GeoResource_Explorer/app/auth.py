from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from app.roles import ROLES

def auth_routes(app):

    @app.route("/login", methods=["GET", "POST"])
    def login():
        session.clear()
        if request.method == "POST":
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE username = ?",
                (request.form.get("username"),)
            ).fetchone()

            if user and check_password_hash(user["hash"], request.form.get("password")):
                session["user_id"] = user["id"]
                return redirect("/")
            return render_template("login.html", error="Invalid credentials")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            confirm = request.form.get("confirm")
            role = request.form.get("role", "viewer")
            organization = request.form.get("organization", "")
            expertise = request.form.get("expertise", "")
            
            # Validate password
            if len(password) < 6:
                return render_template("register.html", error="Password must be at least 6 characters", roles=ROLES)
            
            if password != confirm:
                return render_template("register.html", error="Passwords do not match", roles=ROLES)
            
            # Validate role
            if role not in ROLES:
                role = "viewer"
            
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
            except:
                return render_template("register.html", error="Username already exists", roles=ROLES)
        
        return render_template("register.html", roles=ROLES)
