"""
Trusted Data Import Framework for Mineral Deposits
Allows importing real geological data from trusted sources
"""

import sqlite3
import csv
import json
from datetime import datetime

def import_deposits_from_csv(csv_file_path, data_source, confidence_level='unverified'):
    """
    Import mineral deposits from a CSV file with data source tracking
    
    CSV should have columns:
    - name (required)
    - mineral_type (required)
    - ore_type (required)
    - region (required)
    - location_name (optional)
    - latitude (optional)
    - longitude (optional)
    - estimated_reserves_tonnes (optional)
    - average_grade (optional)
    - confidence_level (optional: confirmed, probable, possible)
    - status (optional: active, inactive, exploration, under_development)
    - discovery_year (optional)
    - notes (optional)
    """
    
    conn = sqlite3.connect('minerals.db')
    cur = conn.cursor()
    
    # Create data source tracking table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            url TEXT,
            last_updated TIMESTAMP,
            credibility_level TEXT,
            institution TEXT
        )
    """)
    
    # Create deposit source mapping table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deposit_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deposit_id INTEGER NOT NULL,
            source_id INTEGER NOT NULL,
            citation TEXT,
            verification_status TEXT DEFAULT 'pending',
            verified_by TEXT,
            verified_date TIMESTAMP,
            FOREIGN KEY(deposit_id) REFERENCES deposits(id),
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        )
    """)
    
    # Register the data source
    cur.execute("""
        INSERT OR IGNORE INTO data_sources (name, description, credibility_level, last_updated)
        VALUES (?, ?, ?, datetime('now'))
    """, (data_source, f"Imported from {data_source}", confidence_level))
    
    conn.commit()
    
    # Get source ID
    cur.execute("SELECT id FROM data_sources WHERE name = ?", (data_source,))
    source_id = cur.fetchone()[0]
    
    # Get mineral and ore type mappings
    cur.execute("SELECT id, name FROM mineral_types")
    mineral_map = {row[1]: row[0] for row in cur.fetchall()}
    
    cur.execute("SELECT id, name FROM ore_types")
    ore_map = {row[1]: row[0] for row in cur.fetchall()}
    
    # Get states
    cur.execute("SELECT id, name FROM ss_states")
    states = {row[1]: row[0] for row in cur.fetchall()}
    
    # Import deposits from CSV
    imported = 0
    errors = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Extract required fields
                    name = row.get('name', '').strip()
                    mineral_type = row.get('mineral_type', '').strip()
                    ore_type = row.get('ore_type', '').strip()
                    region = row.get('region', '').strip()
                    
                    if not (name and mineral_type and ore_type and region):
                        errors.append(f"Row {row_num}: Missing required fields")
                        continue
                    
                    # Check if mineral and ore types exist, skip row if not
                    mineral_id = mineral_map.get(mineral_type)
                    ore_id = ore_map.get(ore_type)
                    
                    if not mineral_id:
                        errors.append(f"Row {row_num}: Mineral type '{mineral_type}' not found in database")
                        continue
                    if not ore_id:
                        errors.append(f"Row {row_num}: Ore type '{ore_type}' not found in database")
                        continue
                    if region not in states:
                        errors.append(f"Row {row_num}: Region '{region}' not found in database")
                        continue
                    
                    # Check if deposit already exists
                    cur.execute("SELECT id FROM deposits WHERE name = ?", (name,))
                    existing = cur.fetchone()
                    
                    # Extract optional fields
                    location = row.get('location_name', name)
                    lat = float(row.get('latitude', 0)) if row.get('latitude') else None
                    lng = float(row.get('longitude', 0)) if row.get('longitude') else None
                    reserves = float(row.get('estimated_reserves_tonnes', 0)) if row.get('estimated_reserves_tonnes') else None
                    grade = float(row.get('average_grade', 0)) if row.get('average_grade') else None
                    confidence = row.get('confidence_level', 'possible')
                    status = row.get('status', 'exploration')
                    discovery_year = int(row.get('discovery_year', datetime.now().year)) if row.get('discovery_year') else None
                    notes = row.get('notes', '')
                    
                    if not existing:
                        # Insert new deposit
                        cur.execute("""
                            INSERT INTO deposits 
                            (name, mineral_type_id, ore_type_id, location_name, latitude, longitude,
                             country, region, estimated_reserves_tonnes, average_grade,
                             confidence_level, discovery_year, status, created_by)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (
                            name, mineral_id, ore_id, location, lat, lng, 'South Sudan',
                            region, reserves, grade, confidence, discovery_year, status
                        ))
                        
                        deposit_id = cur.lastrowid
                        imported += 1
                    else:
                        deposit_id = existing[0]
                    
                    # Link deposit to source
                    cur.execute("""
                        INSERT OR IGNORE INTO deposit_sources (deposit_id, source_id, citation)
                        VALUES (?, ?, ?)
                    """, (deposit_id, source_id, notes))
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
        
        conn.commit()
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found")
        conn.close()
        return False
    
    conn.close()
    
    # Print results
    print(f"\n{'='*70}")
    print(f"DATA IMPORT COMPLETE")
    print(f"{'='*70}")
    print(f"\nSource: {data_source}")
    print(f"Deposits imported: {imported}")
    
    if errors:
        print(f"\nWarnings/Errors ({len(errors)}):")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    return True

def list_data_sources():
    """List all registered data sources"""
    conn = sqlite3.connect('minerals.db')
    cur = conn.cursor()
    
    cur.execute("SELECT name, description, credibility_level, last_updated FROM data_sources")
    sources = cur.fetchall()
    
    conn.close()
    
    if not sources:
        print("No data sources registered yet")
        return
    
    print("\n" + "="*70)
    print("REGISTERED DATA SOURCES")
    print("="*70)
    
    for name, desc, credibility, updated in sources:
        print(f"\n• {name}")
        print(f"  Credibility: {credibility}")
        print(f"  Description: {desc}")
        print(f"  Last updated: {updated}")

def create_sample_csv():
    """Create a sample CSV template for data import"""
    
    sample_csv = """name,mineral_type,ore_type,region,location_name,latitude,longitude,estimated_reserves_tonnes,average_grade,confidence_level,status,discovery_year,notes
Juba North Gold,Gold,Vein deposits,Central Equatoria,North of Juba city,5.00,31.65,350000,2.8,indicated,exploration,2018,USGS Report 2018
Torit East Extension,Gold,Primary ore,Eastern Equatoria,Torit East zone,4.42,32.65,280000,3.0,probable,exploration,2019,Pan African Resources field data
Bentiu Copper Zone,Copper,Primary ore,Unity,Bentiu Basin extension,9.50,30.80,1200000,0.75,possible,exploration,2020,World Bank geological assessment
Upper Nile Diamond,Diamond,Placer deposits,Upper Nile,Upper Nile alluvial,10.35,33.00,50000,0.85,indicated,exploration,2017,Academic research
Lakes Salt Deposit,Rare Earth Elements,Primary ore,Lakes,Panyalar Salt Flats,6.85,31.20,600000,40.0,confirmed,inactive,2015,Government survey data"""
    
    with open('sample_deposits_import.csv', 'w') as f:
        f.write(sample_csv)
    
    print("Sample CSV file created: sample_deposits_import.csv")
    print("\nYou can:")
    print("1. Edit this file with your real data")
    print("2. Run: python -c \"from import_trusted_data import import_deposits_from_csv; import_deposits_from_csv('sample_deposits_import.csv', 'USGS Reports 2018-2020', 'verified')\"")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python import_trusted_data.py create-sample     # Create sample CSV template")
        print("  python import_trusted_data.py import <file> <source> [confidence]")
        print("  python import_trusted_data.py list-sources      # List registered data sources")
        print("\nExample:")
        print("  python import_trusted_data.py create-sample")
        print("  python import_trusted_data.py import sample_deposits_import.csv \"USGS 2020\" verified")
    
    elif sys.argv[1] == 'create-sample':
        create_sample_csv()
    
    elif sys.argv[1] == 'list-sources':
        list_data_sources()
    
    elif sys.argv[1] == 'import':
        if len(sys.argv) < 4:
            print("Error: import requires file and source arguments")
            print("Usage: python import_trusted_data.py import <file> <source> [confidence]")
        else:
            csv_file = sys.argv[2]
            source = sys.argv[3]
            confidence = sys.argv[4] if len(sys.argv) > 4 else 'unverified'
            
            import_deposits_from_csv(csv_file, source, confidence)
    else:
        print("Unknown command")
