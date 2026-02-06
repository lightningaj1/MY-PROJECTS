from flask import render_template
from app.db import get_db
from app.helpers import login_required

def map_routes(app):

    @app.route("/map")
    @login_required
    def map_page():
        db = get_db()
        rows = db.execute("SELECT name, countries FROM minerals").fetchall()
        markers = [{"name": m["name"], "country": m["countries"], "lat":0, "lng":20} for m in rows]
        return render_template("map.html", markers=markers)
