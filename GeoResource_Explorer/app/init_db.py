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
                  CREATE TABLE IF NOT EXISTS learning_content (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  category TEXT NOT NULL,
                  content TEXT NOT NULL,
                  image TEXT,
                  summary TEXT,
                  related_minerals TEXT,
                  difficulty_level TEXT DEFAULT 'beginner',
                  created_by INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(created_by) REFERENCES users(id)
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

# Insert sample learning content
sample_lessons = [
    (1, "Introduction to Minerals", "Basics", 
     "Minerals are naturally occurring, solid, inorganic substances with a definite chemical composition and an ordered atomic structure. They can be identified by their physical properties such as color, hardness, crystal system, and luster. Understanding minerals is fundamental to geology and mining.",
     "/static/images/minerals_intro.jpg", 
     "Learn the basic definition and classification of minerals",
     "Gold,Diamond,Gypsum", "beginner"),
    (1, "Crystal Systems in Geology", "Mineralogy",
     "Crystals form in seven major systems: cubic, tetragonal, orthorhombic, monoclinic, triclinic, hexagonal, and trigonal. The crystal system of a mineral is determined by the arrangement of atoms within its structure. Crystal structure is one of the most important diagnostic properties of minerals.",
     "/static/images/crystals.jpg",
     "Understanding crystal lattices and their classification",
     "Diamond", "intermediate"),
    (1, "Mineral Resources and Extraction", "Mining",
     "Mineral resources are extracted through various methods depending on the type and location of the deposit. Open-pit mining, underground mining, and placer mining are common techniques. Sustainable extraction practices are increasingly important in modern mining operations.",
     "/static/images/mining.jpg",
     "Learn about mining methods and resource extraction",
     "Gold,Gypsum", "intermediate"),
    (1, "Economic Importance of Minerals", "Economics",
     "Minerals are essential to modern society, providing raw materials for construction, manufacturing, electronics, and energy production. The global mineral market is valued in trillions of dollars annually, with significant economic impacts on developing nations.",
     "/static/images/economy.jpg",
     "Explore the economic aspects of mineral resources",
     "Gold,Diamond", "beginner"),
]

cur.executemany("""
                INSERT INTO learning_content (
                created_by, title, category, content, image, summary, related_minerals, difficulty_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, sample_lessons)

conn.commit()
conn.close()

print("database created successfully with admin user and sample minerals!")
