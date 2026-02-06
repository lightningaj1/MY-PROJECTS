from flask import session
from app.db import get_db
import pathlib

UPLOAD_FOLDER = pathlib.Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin():
    if "user_id" not in session:
        return False

    db = get_db()
    user = db.execute(
        "SELECT is_admin FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    return user and user["is_admin"] == 1
