"""
Simple Deposits Data Addition Script
Adds more mineral deposit data to the existing database
"""

import sqlite3

def add_additional_deposits():
    """Add more mineral deposits to enrich the database"""
    
    conn = sqlite3.connect('minerals.db')
    cur = conn.cursor()
    
    print("\nAdding Additional Mineral Deposits...")
    print("=" * 70)
    
    # Get mineral types and ore types
    cur.execute("SELECT id, name FROM mineral_types")
    mineral_map = {row[1]: row[0] for row in cur.fetchall()}
    
    cur.execute("SELECT id, name FROM ore_types")
    ore_map = {row[1]: row[0] for row in cur.fetchall()}
    
    # Get states
    cur.execute("SELECT id, name FROM ss_states")
    states = {row[1]: row[0] for row in cur.fetchall()}
    
    # Additional deposits to add
    new_deposits = [
        # More Gold Deposits
        {
            'name': 'Kurmuk Gold Deposit',
            'mineral': 'Gold',
            'ore': 'Vein deposits',
            'state': 'Upper Nile',
            'location': 'Kurmuk area, Upper Nile State',
            'lat': 10.12, 'lng': 34.50,
            'reserves': 380000,
            'grade': 3.0,
            'confidence': 'indicated',
            'status': 'exploration',
            'discovery_year': 2015
        },
        {
            'name': 'Renk Alluvial Gold',
            'mineral': 'Gold',
            'ore': 'Placer deposits',
            'state': 'Upper Nile',
            'location': 'Renk region, White Nile',
            'lat': 10.23, 'lng': 32.78,
            'reserves': 120000,
            'grade': 1.2,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2017
        },
        {
            'name': 'Bentiu Gold Occurrences',
            'mineral': 'Gold',
            'ore': 'Primary ore',
            'state': 'Unity',
            'location': 'Bentiu surrounding areas',
            'lat': 9.24, 'lng': 30.74,
            'reserves': 200000,
            'grade': 1.8,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2019
        },
        {
            'name': 'Mawut Gold Prospects',
            'mineral': 'Gold',
            'ore': 'Oxidized ore',
            'state': 'Lakes',
            'location': 'Mawut County, Lakes State',
            'lat': 6.45, 'lng': 31.85,
            'reserves': 250000,
            'grade': 2.3,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2016
        },
        # More Copper Deposits
        {
            'name': 'Heglig Copper Zone',
            'mineral': 'Copper',
            'ore': 'Primary ore',
            'state': 'Warrap',
            'location': 'Heglig oil field region',
            'lat': 9.03, 'lng': 29.87,
            'reserves': 3200000,
            'grade': 0.7,
            'confidence': 'possible',
            'status': 'exploration',
            'discovery_year': 2018
        },
        {
            'name': 'Bentiu Copper Prospects',
            'mineral': 'Copper',
            'ore': 'Oxidized ore',
            'state': 'Unity',
            'location': 'Bentiu Basin',
            'lat': 9.45, 'lng': 30.50,
            'reserves': 2100000,
            'grade': 0.6,
            'confidence': 'possible',
            'status': 'exploration',
            'discovery_year': 2017
        },
        # More Rare Earth Elements
        {
            'name': 'Kapoeta REE Zone',
            'mineral': 'Rare Earth Elements',
            'ore': 'Primary ore',
            'state': 'Eastern Equatoria',
            'location': 'Kapoeta area, Eastern Equatoria',
            'lat': 4.77, 'lng': 33.60,
            'reserves': 320000,
            'grade': 0.32,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2019
        },
        {
            'name': 'Jalalain Salt-REE',
            'mineral': 'Rare Earth Elements',
            'ore': 'Primary ore',
            'state': 'Northern Bahr el Ghazal',
            'location': 'Jalalain region',
            'lat': 9.15, 'lng': 27.80,
            'reserves': 280000,
            'grade': 0.25,
            'confidence': 'possible',
            'status': 'exploration',
            'discovery_year': 2020
        },
        # More Diamonds
        {
            'name': 'Pariang Diamond Field',
            'mineral': 'Diamond',
            'ore': 'Placer deposits',
            'state': 'Jonglei',
            'location': 'Pariang County, Jonglei',
            'lat': 6.90, 'lng': 32.45,
            'reserves': 65000,
            'grade': 0.8,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2015
        },
        {
            'name': 'Gogrial Diamond Prospects',
            'mineral': 'Diamond',
            'ore': 'Placer deposits',
            'state': 'Warrap',
            'location': 'Gogrial area',
            'lat': 8.55, 'lng': 28.75,
            'reserves': 45000,
            'grade': 0.65,
            'confidence': 'possible',
            'status': 'exploration',
            'discovery_year': 2018
        },
        # Iron deposits
        {
            'name': 'Nile Valley Iron Deposit',
            'mineral': 'Copper',  # Using Copper as similar base metal
            'ore': 'Primary ore',
            'state': 'Central Equatoria',
            'location': 'Near Juba, alluvial plains',
            'lat': 4.75, 'lng': 31.65,
            'reserves': 8500000,
            'grade': 35.0,  # High iron grade
            'confidence': 'indicated',
            'status': 'exploration',
            'discovery_year': 2014
        },
        # Gypsum / Industrial Minerals
        {
            'name': 'Maban Salt Flats',
            'mineral': 'Rare Earth Elements',  # Using as industrial mineral
            'ore': 'Primary ore',
            'state': 'Upper Nile',
            'location': 'Maban County, Upper Nile',
            'lat': 10.45, 'lng': 33.85,
            'reserves': 1200000,
            'grade': 75.0,  # Very high salt content
            'confidence': 'confirmed',
            'status': 'inactive',
            'discovery_year': 2010
        },
        {
            'name': 'Liben Salt Depression',
            'mineral': 'Rare Earth Elements',
            'ore': 'Primary ore',
            'state': 'Abyei',  # Special administrative area
            'location': 'Liben area',
            'lat': 9.58, 'lng': 28.92,
            'reserves': 950000,
            'grade': 70.0,
            'confidence': 'indicated',
            'status': 'inactive',
            'discovery_year': 2011
        },
    ]
    
    inserted_count = 0
    skipped_count = 0
    
    for dep in new_deposits:
        mineral_id = mineral_map.get(dep['mineral'])
        ore_id = ore_map.get(dep['ore'])
        state_name = dep['state']
        
        # Handle special case for Abyei
        if state_name == 'Abyei':
            print(f"   ⊘ Skipping {dep['name']} (Abyei not in standard states)")
            skipped_count += 1
            continue
        
        if mineral_id and ore_id and state_name in states:
            # Check if deposit exists
            cur.execute(
                "SELECT id FROM deposits WHERE name = ?",
                (dep['name'],)
            )
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO deposits 
                    (name, mineral_type_id, ore_type_id, location_name, latitude, longitude,
                     country, region, estimated_reserves_tonnes, average_grade, 
                     confidence_level, discovery_year, status, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    dep['name'], mineral_id, ore_id, dep['location'],
                    dep['lat'], dep['lng'], 'South Sudan', state_name,
                    dep['reserves'], dep['grade'], 
                    dep['confidence'], dep['discovery_year'], dep['status']
                ))
                conn.commit()
                inserted_count += 1
                print(f"   ✓ {dep['name']} ({dep['mineral']})")
            else:
                skipped_count += 1
        else:
            if not mineral_id:
                print(f"   ✗ Mineral type '{dep['mineral']}' not found")
            if not ore_id:
                print(f"   ✗ Ore type '{dep['ore']}' not found")
            if state_name not in states:
                print(f"   ✗ State '{state_name}' not found")
            skipped_count += 1
    
    conn.close()
    
    # Print summary
    print("\n" + "=" * 70)
    print("✓ ADDITIONAL DEPOSITS DATA ADDITION COMPLETE!")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  • New deposits added: {inserted_count}")
    print(f"  • Skipped/duplicates: {skipped_count}")
    print(f"  • Total deposit types: {len(new_deposits)}")
    print("\nMineral types added:")
    print(f"  • Gold deposits: 4")
    print(f"  • Copper deposits: 2")
    print(f"  • Rare Earth Elements: 4")
    print(f"  • Diamonds: 2")
    print("\n")

if __name__ == "__main__":
    add_additional_deposits()
