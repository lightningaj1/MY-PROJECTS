import os
import sqlite3
from werkzeug.security import generate_password_hash

# create and connect to database
conn = sqlite3.connect("minerals.db")
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# create tables
cur.executescript(""" CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  hash TEXT NOT NULL,
                  is_admin INTEGER DEFAULT 0
                  );
                  CREATE TABLE IF NOT EXISTS minerals (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  name TEXT NOT NULL,
                  formula TEXT,
                  properties TEXT,
                  uses TEXT,
                  economic TEXT,
                  countries TEXT,
                  image TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id)
                  );
                  CREATE TABLE IF NOT EXISTS favorites (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  mineral_id INTEGER,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  FOREIGN KEY(mineral_id) REFERENCES minerals(id)
                  );
                  """)

# insert admin user
admin_username = "admin"
admin_password = generate_password_hash("Admin@123")

cur.execute("""
            INSERT OR IGNORE INTO users (username, hash, is_admin)
            VALUES (?, ?, 1)
            """, (admin_username, admin_password))

# Insert sample minerals
sample_data = [
    (1, "Gold", "Au", "Yellow metal; dense; soft", "Jewellery; electronics; investment",
     "very high economic value", "South Africa, Australia, China", "/static/images/gold.jpg"),
    (1, "Diamond", "C", "Extremely hard; crystal", "Gemstones; drilling; cutting",
     "very high economic importance", "Botswana, Russia, Canada", "/static/images/diamond.jpg"),
    (1, "Gypsum", "CaSO4.2H2O", "Soft; scratched by nail", "cement; plaster; fertilizer",
     "Medium economic value", "USA, China, Iran", "/static/images/gypsum.jpg")
]

cur.executemany("""
                INSERT INTO minerals (
                user_id, name, formula, properties, uses, economic, countries, image
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, sample_data)

conn.commit()
conn.close()

print("database created successfully with admin user and sample minerals!")
