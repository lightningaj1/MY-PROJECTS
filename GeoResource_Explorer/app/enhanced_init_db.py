"""
Enhanced Database Schema for Professional Geology & Exploration App
Includes South Sudan focus with advanced features
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

def create_enhanced_db(db_path="minerals.db"):
    """Create or upgrade database with professional geology schema"""
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    
    # Check if tables exist (for migration logic)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cur.fetchall()}
    
    print("Creating Enhanced Professional Geology Database Schema...")
    
    # ============================================================
    # 1. CORE TABLES (Keep existing, enhance if needed)
    # ============================================================
    
    if "users" not in existing_tables:
        cur.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                role TEXT DEFAULT 'viewer',  -- viewer, geologist, explorer, investor, admin
                organization TEXT,
                expertise TEXT,  -- specializations: mining, hydrocarbons, gems, etc.
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created users table (enhanced with roles)")
    
    if "minerals" not in existing_tables:
        cur.execute("""
            CREATE TABLE minerals (
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
            )
        """)
        print("✓ Created minerals table")
    
    if "favorites" not in existing_tables:
        cur.execute("""
            CREATE TABLE favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                mineral_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(mineral_id) REFERENCES minerals(id)
            )
        """)
        print("✓ Created favorites table")
    
    # ============================================================
    # 2. GEOLOGICAL CLASSIFICATION TABLES
    # ============================================================
    
    if "mineral_types" not in existing_tables:
        cur.executescript("""
            CREATE TABLE mineral_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT  -- precious, industrial, base_metal, rare_earth, fossil_fuel
            );
            
            CREATE TABLE ore_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                extraction_difficulty TEXT  -- easy, moderate, difficult
            );
        """)
        print("✓ Created mineral_types and ore_types tables")
    
    # ============================================================
    # 3. DEPOSITS & RESOURCE TABLES
    # ============================================================
    
    if "deposits" not in existing_tables:
        cur.executescript("""
            CREATE TABLE deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mineral_type_id INTEGER,
                ore_type_id INTEGER,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                country TEXT,
                region TEXT,
                estimated_reserves_tonnes REAL,
                average_grade REAL,  -- percentage or g/tonne
                confidence_level TEXT,  -- confirmed, probable, possible
                discovery_year INTEGER,
                status TEXT,  -- active, inactive, exploration, under_development
                notes TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(mineral_type_id) REFERENCES mineral_types(id),
                FOREIGN KEY(ore_type_id) REFERENCES ore_types(id),
                FOREIGN KEY(created_by) REFERENCES users(id)
            );
            
            CREATE TABLE assay_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deposit_id INTEGER NOT NULL,
                sample_id TEXT,
                depth_from REAL,
                depth_to REAL,
                au_ppm REAL,  -- Gold
                ag_ppm REAL,  -- Silver
                cu_ppm REAL,  -- Copper
                pb_ppm REAL,  -- Lead
                zn_ppm REAL,  -- Zinc
                fe_percent REAL,
                other_elements TEXT,
                sample_date TIMESTAMP,
                lab_name TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deposit_id) REFERENCES deposits(id),
                FOREIGN KEY(created_by) REFERENCES users(id)
            );
            
            CREATE TABLE drilling_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deposit_id INTEGER NOT NULL,
                hole_id TEXT,
                total_depth REAL,
                rock_type TEXT,
                core_recovery_percent REAL,
                mineralization_notes TEXT,
                drilling_date TIMESTAMP,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deposit_id) REFERENCES deposits(id),
                FOREIGN KEY(created_by) REFERENCES users(id)
            );
            
            CREATE TABLE resource_estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deposit_id INTEGER NOT NULL,
                tonnage REAL,
                grade REAL,
                metal_content REAL,
                confidence_level TEXT,  -- measured, indicated, inferred
                estimate_date TIMESTAMP,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deposit_id) REFERENCES deposits(id),
                FOREIGN KEY(created_by) REFERENCES users(id)
            );
        """)
        print("✓ Created deposits, assay_results, drilling_logs, resource_estimates tables")
    
    # ============================================================
    # 4. SOUTH SUDAN SPECIFIC TABLES
    # ============================================================
    
    if "ss_states" not in existing_tables:
        cur.executescript("""
            CREATE TABLE ss_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                capital TEXT,
                area_km2 REAL,
                population INTEGER,
                primary_minerals TEXT,
                geological_description TEXT,
                latitude REAL,
                longitude REAL
            );
            
            CREATE TABLE ss_exploration_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                state_id INTEGER NOT NULL,
                deposit_id INTEGER,
                latitude REAL,
                longitude REAL,
                accessibility TEXT,  -- accessible, difficult, impassable
                infrastructure_notes TEXT,
                security_status TEXT,  -- secure, unstable, restricted
                exploration_status TEXT,  -- early_stage, advanced, production
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(state_id) REFERENCES ss_states(id),
                FOREIGN KEY(deposit_id) REFERENCES deposits(id),
                FOREIGN KEY(created_by) REFERENCES users(id)
            );
            
            CREATE TABLE ss_regulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                applicable_states TEXT,  -- comma-separated
                requirements TEXT,
                contact_authority TEXT,
                last_updated TIMESTAMP,
                document_url TEXT
            );
            
            CREATE TABLE ss_infrastructure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_id INTEGER NOT NULL,
                type TEXT,  -- road, port, airport, electrical, water
                name TEXT,
                location TEXT,
                status TEXT,  -- operational, under_construction, planned
                capacity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(state_id) REFERENCES ss_states(id)
            );
        """)
        print("✓ Created South Sudan specific tables (states, sites, regulations, infrastructure)")
    
    # ============================================================
    # 5. MINING CLAIMS & LICENSES
    # ============================================================
    
    if "mining_claims" not in existing_tables:
        cur.executescript("""
            CREATE TABLE mining_claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT UNIQUE NOT NULL,
                deposit_id INTEGER,
                owner_id INTEGER,
                company_name TEXT,
                location_description TEXT,
                area_hectares REAL,
                claim_type TEXT,  -- exploration, mining, processing
                issue_date TIMESTAMP,
                expiry_date TIMESTAMP,
                status TEXT,  -- active, expired, suspended, transferred
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deposit_id) REFERENCES deposits(id),
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
            
            CREATE TABLE licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id TEXT UNIQUE NOT NULL,
                claim_id INTEGER NOT NULL,
                license_type TEXT,  -- exploration, mining, export
                issuing_authority TEXT,
                issue_date TIMESTAMP,
                expiry_date TIMESTAMP,
                conditions TEXT,
                status TEXT,  -- active, expired, revoked
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(claim_id) REFERENCES mining_claims(id)
            );
        """)
        print("✓ Created mining_claims and licenses tables")
    
    # ============================================================
    # 6. REPORTS & DOCUMENTS
    # ============================================================
    
    if "geological_reports" not in existing_tables:
        cur.executescript("""
            CREATE TABLE geological_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deposit_id INTEGER NOT NULL,
                report_type TEXT,  -- survey, assessment, feasibility, environmental
                title TEXT NOT NULL,
                summary TEXT,
                file_path TEXT,
                file_name TEXT,
                author_id INTEGER,
                report_date TIMESTAMP,
                access_level TEXT,  -- public, restricted, private
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deposit_id) REFERENCES deposits(id),
                FOREIGN KEY(author_id) REFERENCES users(id)
            );
        """)
        print("✓ Created geological_reports table")
    
    # ============================================================
    # 7. WATCHLIST (Enhanced Favorites)
    # ============================================================
    
    if "watchlist" not in existing_tables:
        cur.execute("""
            CREATE TABLE watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                deposit_id INTEGER,
                mineral_id INTEGER,
                site_id INTEGER,
                note TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(deposit_id) REFERENCES deposits(id),
                FOREIGN KEY(mineral_id) REFERENCES minerals(id),
                FOREIGN KEY(site_id) REFERENCES ss_exploration_sites(id)
            )
        """)
        print("✓ Created watchlist table")
    
    # ============================================================
    # 8. SEED DATA
    # ============================================================
    
    # Insert default admin user (if not exists)
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        admin_hash = generate_password_hash("Admin@123")
        cur.execute("""
            INSERT INTO users (username, hash, is_admin, role, organization, expertise)
            VALUES (?, ?, 1, 'admin', 'GeoResource Admin', 'geology, mining')
        """, (admin_hash,))
        print("✓ Inserted admin user")
    
    # Insert mineral types if empty
    cur.execute("SELECT COUNT(*) FROM mineral_types")
    if cur.fetchone()[0] == 0:
        mineral_types_data = [
            ('Gold', 'Precious metal used in jewelry and electronics', 'precious'),
            ('Diamond', 'Precious stone for jewelry and industrial uses', 'precious'),
            ('Copper', 'Base metal for electrical and construction', 'base_metal'),
            ('Rare Earth Elements', 'Critical for technology and green energy', 'rare_earth'),
            ('Oil & Gas', 'Hydrocarbon fossil fuels', 'fossil_fuel'),
            ('Gypsum', 'Industrial mineral for construction', 'industrial'),
        ]
        cur.executemany("""
            INSERT INTO mineral_types (name, description, category)
            VALUES (?, ?, ?)
        """, mineral_types_data)
        print("✓ Inserted mineral types")
    
    # Insert South Sudan states
    cur.execute("SELECT COUNT(*) FROM ss_states")
    if cur.fetchone()[0] == 0:
        ss_states_data = [
            ('Central Equatoria', 'Juba', 28473, 1728000, 'Gold, diamonds, limestone', 'Equatorial region with complex geology'),
            ('Eastern Equatoria', 'Torit', 25620, 800000, 'Gold, water', 'Eastern highlands, mountainous terrain'),
            ('Jonglei', 'Bor', 40180, 1100000, 'Oil, minerals', 'Nile Basin with oil fields'),
            ('Lakes', 'Rumbek', 19373, 450000, 'Salt, minerals', 'Lacustrine sediments, salt deposits'),
            ('Northern Bahr el Ghazal', 'Aweil', 38701, 600000, 'Minerals, salt', 'Savanna with mineral potential'),
            ('Upper Nile', 'Malakal', 48434, 800000, 'Oil, gold, water', 'Major oil producing region'),
            ('Warrap', 'Kuacjok', 40658, 550000, 'Oil, minerals', 'Oil-rich region, pastoral area'),
            ('West Equatoria', 'Yambio', 79483, 1200000, 'Gold, diamonds, timber', 'Mineral-rich, complex geology'),
            ('Unity', 'Bentiu', 34210, 600000, 'Oil, minerals', 'Major oil fields'),
        ]
        cur.executemany("""
            INSERT INTO ss_states (name, capital, area_km2, population, primary_minerals, geological_description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ss_states_data)
        print("✓ Inserted South Sudan states")
        
    # Insert ore types
    cur.execute("SELECT COUNT(*) FROM ore_types")
    if cur.fetchone()[0] == 0:
        ore_types_data = [
            ('Primary ore', 'Unoxidized ore containing original minerals', 'difficult'),
            ('Oxidized ore', 'Weathered ore with oxidation products', 'moderate'),
            ('Placer deposits', 'Sedimentary deposits in streams and rivers', 'easy'),
            ('Vein deposits', 'Mineral-filled fractures in rock', 'moderate'),
            ('Porphyry ore', 'Disseminated ore in igneous rocks', 'moderate'),
        ]
        cur.executemany("""
            INSERT INTO ore_types (name, description, extraction_difficulty)
            VALUES (?, ?, ?)
        """, ore_types_data)
        print("✓ Inserted ore types")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✓ ENHANCED DATABASE CREATED SUCCESSFULLY!")
    print("="*60)
    print("\nNew Tables:")
    print("  - mineral_types, ore_types")
    print("  - deposits, assay_results, drilling_logs, resource_estimates")
    print("  - ss_states, ss_exploration_sites, ss_regulations, ss_infrastructure")
    print("  - mining_claims, licenses")
    print("  - geological_reports")
    print("  - watchlist")
    print("\nEnhanced Tables:")
    print("  - users (added roles, organization, expertise)")
    print("\nSeeded Data:")
    print("  - Admin user, mineral types, ore types, South Sudan 9 states")
    return True

if __name__ == "__main__":
    create_enhanced_db()
