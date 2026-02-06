from flask import render_template, request, redirect, session
from app.db import get_db
from app.helpers import login_required

PER_PAGE = 8

def mineral_routes(app):

    @app.route("/")
    @login_required
    def home():
        db = get_db()
        minerals = db.execute("SELECT * FROM minerals ORDER BY id DESC LIMIT 6").fetchall()
        return render_template("home.html", minerals=minerals)

    @app.route("/minerals")
    @login_required
    def minerals():
        db = get_db()
        page = int(request.args.get('page', 1))
        q = request.args.get('q')
        group = request.args.get('group')

        params = []
        where = []
        if q:
            where.append('name LIKE ?')
            params.append('%'+q+'%')
        if group:
            where.append('properties LIKE ?')
            params.append('%'+group+'%')
        where_sql = ('WHERE ' + ' AND '.join(where)) if where else ''

        total = db.execute(f'SELECT COUNT(*) as cnt FROM minerals {where_sql}', params).fetchone()['cnt']
        offset = (page - 1) * PER_PAGE
        rows = db.execute(f'SELECT * FROM minerals {where_sql} LIMIT ? OFFSET ?', params + [PER_PAGE, offset]).fetchall()
        pages = (total + PER_PAGE - 1) // PER_PAGE

        return render_template("minerals.html", minerals=rows, page=page, pages=pages)

    @app.route("/mineral/<int:id>")
    @login_required
    def mineral(id):
        db = get_db()
        mineral = db.execute("SELECT * FROM minerals WHERE id = ?", (id,)).fetchone()
        if not mineral:
            return redirect("/minerals")
        
        mineral = dict(mineral)
        
        # Get related learning content
        related_lessons = db.execute("""
            SELECT id, title, category, summary, difficulty_level
            FROM learning_content
            WHERE related_minerals LIKE ?
            LIMIT 5
        """, (f'%{mineral["name"]}%',)).fetchall()
        related_lessons = [dict(l) for l in related_lessons]
        
        return render_template("mineral.html", mineral=mineral, related_lessons=related_lessons)

    @app.route("/search")
    @login_required
    def search():
        db = get_db()
        q = request.args.get("q")
        results = []
        if q:
            results = db.execute("SELECT * FROM minerals WHERE name LIKE ? OR countries LIKE ? OR properties LIKE ?", 
                                 (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        return render_template("search.html", results=results, q=q)

    @app.route("/favorites")
    @login_required
    def favorites():
        db = get_db()
        favs = db.execute(
            "SELECT minerals.* FROM minerals JOIN favorites ON minerals.id = favorites.mineral_id WHERE favorites.user_id = ?", 
            (session["user_id"],)
        ).fetchall()
        return render_template("favorites.html", minerals=favs)

