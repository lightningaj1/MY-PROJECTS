import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required
from werkzeug.utils import secure_filename
import pathlib
import time

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

#Connect to DB
def get_db():
    conn = sqlite3.connect("minerals.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

db = get_db()

# simple in-memory cache to avoid repeated external requests
_price_cache = {'timestamp': 0, 'data': {}}
CACHE_TTL = 60 * 10 # 10 minutes


#allowed file extensions for upload
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
def allowed_file(filename):
    return "." in filename and \
              filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

#simple admin check: user with id 1 is admin
def is_admin():
    if "user_id" not in session:
        return False

    user = db.execute("SELECT is_admin FROM users WHERE id = ?",
                      (session["user_id"],)
                      ).fetchone()

    return user and user["is_admin"] == 1

@app.context_processor
def inject_admin():
    return dict(is_admin=is_admin())

@app.route("/admin")
@login_required
def admin_page():
    if not is_admin():
        return redirect("/")
    return render_template("admin.html")

@app.route('/admin/upload', methods=['POST'])
@login_required
def admin_upload():
    if not is_admin():
        return redirect('/')
    name = request.form.get('name')
    formula = request.form.get('formula')
    properties = request.form.get('properties')
    uses = request.form.get('uses')
    economic = request.form.get('economic')
    countries = request.form.get('countries')

    image = request.files.get('image')
    image_path = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        upload_dir = pathlib.Path('static/images')
        upload_dir.mkdir(parents=True, exist_ok=True)
        filepath = upload_dir / filename
        image.save(str(filepath))
        image_path = f'/static/images/{filename}'

    db.execute(
        'INSERT INTO minerals (name, formula, properties, uses, economic, countries, image) VALUES (?, ?, ?, ?, ?, ?, ?)', (name, formula, properties, uses, economic, countries, image_path)
    )
    db.commit()
    return redirect('/')

PER_PAGE = 8


@app.route("/")
@login_required
def home():
    minerals = db.execute("SELECT * FROM minerals ORDER BY id DESC LIMIT 6").fetchall()
    return render_template("index.html", minerals=minerals)

@app.route("/minerals")
@login_required
def minerals():
    page = int(request.args.get('page', 1))
    q = request.args.get('q')
    group = request.args.get('group')

    params = []
    where = []
    if q:
        where.append('name LIKE ?')
        params.append('%' + q + '%')
    if group:
        where.append('properties LIKE ?')
        params.append('%' + group + '%')

    where_sql = ('WHERE ' + ' AND '.join(where)) if where else ''
    total = db.execute(f'SELECT COUNT(*) as cnt FROM minerals {where_sql}', params).fetchone()['cnt']
    offset = (page - 1)*PER_PAGE
    rows = db.execute(f'SELECT * FROM minerals {where_sql} LIMIT ? OFFSET ?', params + [PER_PAGE, offset]).fetchall()

    pages = (total + PER_PAGE - 1) // PER_PAGE
    return render_template('minerals.html', minerals=rows, page=page, pages=pages)

@app.route("/mineral/<int:id>")
@login_required
def mineral(id):
    mineral = db.execute("SELECT * FROM minerals WHERE id = ?", (id,)).fetchone()

    if not mineral:
        return redirect("/minerals")
    return render_template("mineral.html", mineral=mineral)

@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    results = []

    if q:
        results = db.execute(" SELECT * FROM minerals WHERE name LIKE ? OR countries LIKE ? OR properties LIKE ? ", (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    return render_template("search.html", results=results, q=q)


@app.route("/favorite/<int:id>")
@login_required
def favorite(id):
    exists = db.execute("""
                        SELECT 1 FROM favorites
                        WHERE user_id = ? AND mineral_id=?
                        """, (session["user_id"], id)).fetchone()

    if not exists:
        db.execute(
            "INSERT INTO favorites (user_id, mineral_id) VALUES (?, ?)",
            (session["user_id"], id)
            )
        db.commit()
        return redirect(f"/mineral/{id}")




@app.route("/favorites")
@login_required
def favorites():
    favs = db.execute("SELECT minerals.* FROM minerals JOIN favorites ON minerals.id = favorites.mineral_id WHERE favorites.user_id = ?", (session["user_id"],)).fetchall()
    return render_template("favorites.html", minerals=favs)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if not username or not password:
            return render_template("login.html", error="All fields are required")

        if user and check_password_hash(user["hash"], password):
            session["user_id"] = user["id"]
            return redirect("/")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if len(password) < 6:
            return render_template("register.html", error="password must be at least 6 characters")

        if password != confirm:
            return render_template("register.html", error="Passwords do not match")
        hash_pw = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_pw))
            db.commit()
        except:
            return render_template("register.html", error="Username already exists")
        return redirect("/login")
    return render_template("register.html")

#commodity price API
@app.route("/prices")
@login_required
def prices():
    # If cache is fresh, return
    if time.time() - _price_cache['timestamp'] < CACHE_TTL:
        prices = _price_cache['data']
    else:
        # Example: use Metals-API (replace with real key and endpoint). the user must register and set METALS_API_KEY
        API_KEY = os.environ.get('METALS_API_KEY')
        prices = {}
        metals = {'gold':'XAU', 'silver':'XAG', 'copper':'XCU'}
        if API_KEY:
            for name, symbol in metals.items():
                try:
                    r = requests.get(f'https://metals-api.com/api/latest?access_key={API_KEY}&symbols={symbol}&base=USD')
                    data = r.json()
                    # parse depending on provider - here is a generic example
                    prices[name] = data.get('rates', {}).get(symbol, 'N/A')
                except Exception as e:
                    prices[name] = 'Unavailable'
        else:
            #fallback: static example values
            prices = {'gold':'2000.00', 'silver':'25.20', 'copper':'4.10'}

        _price_cache['timestamp'] = time.time()
        _price_cache['data'] = prices

    return render_template('prices.html', prices=prices)

@app.route("/map")
@login_required
def map_page():
    rows = db.execute("SELECT name, countries FROM minerals").fetchall()

    # Convert country names into coordinates (static example)
    markers = [
        {"name": m["name"], "country": m["countries"], "lat":0, "lng": 20}
        for m in rows
    ]

    return render_template("map.html", markers=markers)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if not is_admin():
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name")
        formula = request.form.get("formula")
        properties = request.form.get("properties")
        uses = request.form.get("uses")
        economic = request.form.get("economic")
        countries = request.form.get("countries")
        image = request.form.get("image")

        db.execute(
            "INSERT INTO minerals (name, formula, properties, uses, economic, countries, image) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, formula, properties, uses, economic, countries, image)
        )
        db.commit()
        return redirect("/minerals")
    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    if not is_admin():
        return redirect("/")

    mineral = db.execute("SELECT * FROM minerals WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        image = request.files.get("image")
        image_path = mineral["image"]

        if image and image.filename:
            filename = secure_filename(image.filename)
            upload_dir = pathlib.Path("static/images")
            upload_dir.mkdir(parents=True, exist_ok=True)
            filepath = upload_dir / filename
            image.save(str(filepath))
            image_path = f"/static/images/{filename}"

        db.execute(""" UPDATE minerals SET name=?, formula=?, properties=?, uses=?, economic=?, countries=?, image=? WHERE id=? """,(
            request.form.get("name"),
            request.form.get("formula"),
            request.form.get("properties"),
            request.form.get("uses"),
            request.form.get("economic"),
            request.form.get("countries"),
            image_path,
            id
        ))
        db.commit()
        return redirect(f"/mineral/{id}")
    return render_template("edit.html", mineral=mineral)

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    if not is_admin():
        return redirect("/")

    mineral = db.execute(
        "SELECT image FROM minerals WHERE id = ?", (id,)
    ).fetchone()

    # delete image file if exists
    if not mineral:
        return redirect("/minerals")
    image_path = mineral["image"]

    if image_path:
        try:
            img_path = mineral["image"].lstrip("/")
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass

        db.execute("DELETE FROM minerals WHERE id = ?", (id,))
        db.commit()
        return redirect("/minerals")

if __name__ == "__main__":
    app.run()
