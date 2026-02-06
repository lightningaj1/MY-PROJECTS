
from flask import render_template, request, redirect, session
from werkzeug.utils import secure_filename
from app.db import get_db
from app.utils import is_admin, UPLOAD_FOLDER, allowed_file
from app.helpers import login_required
import pathlib, os

def admin_routes(app):

    @app.route("/admin")
    @login_required
    def admin_page():
        if not is_admin():
            return redirect("/")
        db = get_db()
        minerals = db.execute("SELECT * FROM minerals").fetchall()
        return render_template("admin.html", minerals=minerals)

    @app.route("/add", methods=["GET", "POST"])
    @login_required
    def add():
        if not is_admin():
            return redirect("/")
        if request.method == "POST":
            return redirect("/admin/upload")
        return render_template("add.html")

    @app.route("/admin/upload", methods=["POST"])
    @login_required
    def admin_upload():
        if not is_admin():
            return redirect("/")
        db = get_db()
        name = request.form.get("name")
        formula = request.form.get("formula")
        properties = request.form.get("properties")
        uses = request.form.get("uses")
        economic = request.form.get("economic")
        countries = request.form.get("countries")

        image = request.files.get("image")
        image_path = None
        if image and image.filename and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            filepath = UPLOAD_FOLDER / filename
            image.save(str(filepath))
            image_path = f"/static/images/{filename}"

        db.execute(
            """INSERT INTO minerals (name, formula, properties, uses, economic, countries, image)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, formula, properties, uses, economic, countries, image_path)
        )
        db.commit()
        return redirect("/admin")

    @app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def admin_edit(id):
        if not is_admin():
            return redirect("/")
        db = get_db()
        mineral = db.execute("SELECT * FROM minerals WHERE id = ?", (id,)).fetchone()
        if request.method == "POST":
            image = request.files.get("image")
            image_path = mineral["image"]
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = UPLOAD_FOLDER / filename
                image.save(str(filepath))
                image_path = f"/static/images/{filename}"

            db.execute(
                """UPDATE minerals SET name=?, formula=?, properties=?, uses=?, economic=?, countries=?, image=? WHERE id=?""",
                (request.form.get("name"), request.form.get("formula"), request.form.get("properties"),
                 request.form.get("uses"), request.form.get("economic"), request.form.get("countries"),
                 image_path, id)
            )
            db.commit()
            return redirect(f"/mineral/{id}")
        return render_template("edit.html", mineral=mineral)

    @app.route("/admin/delete/<int:id>", methods=["POST"])
    @login_required
    def admin_delete(id):
        if not is_admin():
            return redirect("/")
        db = get_db()
        mineral = db.execute("SELECT image FROM minerals WHERE id = ?", (id,)).fetchone()
        if mineral and mineral["image"]:
            img_path = mineral["image"].lstrip("/")
            if os.path.exists(img_path):
                os.remove(img_path)
        db.execute("DELETE FROM minerals WHERE id = ?", (id,))
        db.commit()
        return redirect("/admin")
