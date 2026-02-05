from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db

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
            db = get_db()
            hash_pw = generate_password_hash(request.form.get("password"))
            try:
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)",
                    (request.form.get("username"), hash_pw)
                )
                db.commit()
                return redirect("/login")
            except:
                return render_template("register.html", error="Username exists")

        return render_template("register.html")
