"""
Enhanced Deposits Data Addition Script
Adds more comprehensive mineral deposit data with assay results, drilling logs, and resource estimates
"""

import sqlite3
from datetime import datetime, timedelta

def add_more_deposits():
    """Add extended mineral deposit data to enrich the database"""
    
    conn = sqlite3.connect('minerals.db')
    cur = conn.cursor()
    
    print("\nAdding Extended Mineral Deposits Data...")
    print("=" * 70)
    
    # Get mineral types and ore types
    cur.execute("SELECT id, name FROM mineral_types")
    mineral_map = {row[1]: row[0] for row in cur.fetchall()}
    
    cur.execute("SELECT id, name FROM ore_types")
    ore_map = {row[1]: row[0] for row in cur.fetchall()}
    
    # Get states
    cur.execute("SELECT id, name FROM ss_states")
    states = {row[1]: row[0] for row in cur.fetchall()}
    
    # ============================================================
    # ADDITIONAL GOLD DEPOSITS
    # ============================================================
    
    print("\n1. Adding Gold Deposits...")
    
    gold_deposits = [
        {
            'name': 'Nzara Gold Field',
            'mineral': 'Gold',
            'ore': 'Vein deposits',
            'state': 'Eastern Equatoria',
            'location': 'Nzara District, Eastern Equatoria',
            'lat': 4.25, 'lng': 32.30,
            'reserves': 520000,
            'grade': 3.5,
            'confidence': 'indicated',
            'status': 'exploration',
            'discovery_year': 2015
        },
        {
            'name': 'Kambe Gold Prospect',
            'mineral': 'Gold',
            'ore': 'Oxidized ore',
            'state': 'Eastern Equatoria',
            'location': 'Kambe area, near Torit',
            'lat': 4.30, 'lng': 32.45,
            'reserves': 280000,
            'grade': 2.9,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2018
        },
        {
            'name': 'Liria Gold Zone',
            'mineral': 'Gold',
            'ore': 'Vein deposits',
            'state': 'West Equatoria',
            'location': 'Liria region, West Equatoria',
            'lat': 4.45, 'lng': 28.80,
            'reserves': 380000,
            'grade': 3.1,
            'confidence': 'indicated',
            'status': 'exploration',
            'discovery_year': 2016
        },
        {
            'name': 'Kajo-Keji Gold District',
            'mineral': 'Gold',
            'ore': 'Primary ore',
            'state': 'Central Equatoria',
            'location': 'Kajo-Keji, Central Equatoria',
            'lat': 3.75, 'lng': 32.18,
            'reserves': 420000,
            'grade': 2.7,
            'confidence': 'indicated',
            'status': 'under_development',
            'discovery_year': 2014
        },
        {
            'name': 'Pibor Region Gold',
            'mineral': 'Gold',
            'ore': 'Placer deposits',
            'state': 'Jonglei',
            'location': 'Pibor region, Jonglei',
            'lat': 6.25, 'lng': 33.10,
            'reserves': 150000,
            'grade': 1.8,
            'confidence': 'possible',
            'status': 'exploration',
            'discovery_year': 2019
        },
        {
            'name': 'Magwi Gold Prospects',
            'mineral': 'Gold',
            'ore': 'Oxidized ore',
            'state': 'Eastern Equatoria',
            'location': 'Magwi County, Eastern Equatoria',
            'lat': 3.70, 'lng': 32.27,
            'reserves': 290000,
            'grade': 2.6,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2017
        },
    ]
    
    # ============================================================
    # COPPER DEPOSITS
    # ============================================================
    
    print("2. Adding Copper Deposits...")
    
    copper_deposits = [
        {
            'name': 'Fula Ridge Copper',
            'mineral': 'Copper',
            'ore': 'Primary ore',
            'state': 'Central Equatoria',
            'location': 'Fula Ridge, Central Equatoria',
            'lat': 4.15, 'lng': 31.85,
            'reserves': 2500000,
            'grade': 0.8,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2013
        },
        {
            'name': 'Terekeka Copper Zone',
            'mineral': 'Copper',
            'ore': 'Primary ore',
            'state': 'Central Equatoria',
            'location': 'Terekeka District',
            'lat': 4.50, 'lng': 31.45,
            'reserves': 1800000,
            'grade': 0.65,
            'confidence': 'possible',
            'status': 'exploration',
            'discovery_year': 2018
        },
    ]
    
    # ============================================================
    # RARE EARTH ELEMENTS
    # ============================================================
    
    print("3. Adding Rare Earth Elements Deposits...")
    
    ree_deposits = [
        {
            'name': 'Dinka REE Prospects',
            'mineral': 'Rare Earth Elements',
            'ore': 'Primary ore',
            'state': 'Lakes',
            'location': 'Dinka Hills, Lakes State',
            'lat': 7.25, 'lng': 31.40,
            'reserves': 450000,
            'grade': 0.35,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2020
        },
        {
            'name': 'Akobo REE Zone',
            'mineral': 'Rare Earth Elements',
            'ore': 'Oxidized ore',
            'state': 'Jonglei',
            'location': 'Akobo region, Jonglei',
            'lat': 6.75, 'lng': 33.20,
            'reserves': 380000,
            'grade': 0.28,
            'confidence': 'possible',
            'status': 'exploration',
            'discovery_year': 2019
        },
    ]
    
    # ============================================================
    # DIAMOND DEPOSITS
    # ============================================================
    
    print("4. Adding Diamond Deposits...")
    
    diamond_deposits = [
        {
            'name': 'Rumbek Diamond Field',
            'mineral': 'Diamond',
            'ore': 'Placer deposits',
            'state': 'Lakes',
            'location': 'Rumbek County, Lakes',
            'lat': 6.80, 'lng': 31.75,
            'reserves': 85000,
            'grade': 0.95,
            'confidence': 'indicated',
            'status': 'exploration',
            'discovery_year': 2016
        },
        {
            'name': 'Yei Diamond Prospects',
            'mineral': 'Diamond',
            'ore': 'Placer deposits',
            'state': 'Central Equatoria',
            'location': 'Yei region, Central Equatoria',
            'lat': 3.85, 'lng': 30.68,
            'reserves': 55000,
            'grade': 0.72,
            'confidence': 'probable',
            'status': 'exploration',
            'discovery_year': 2017
        },
    ]
    
    # Combine all deposits
    all_deposits = gold_deposits + copper_deposits + ree_deposits + diamond_deposits
    
    # Insert deposits and track inserted ones
    inserted_deposits = []
    deposit_id_map = {}
    
    for dep in all_deposits:
        mineral_id = mineral_map.get(dep['mineral'])
        ore_id = ore_map.get(dep['ore'])
        
        if mineral_id and ore_id and dep['state'] in states:
            # Check if deposit exists
            cur.execute(
                "SELECT id FROM deposits WHERE name = ?",
                (dep['name'],)
            )
            existing = cur.fetchone()
            
            if not existing:
                cur.execute("""
                    INSERT INTO deposits 
                    (name, mineral_type_id, ore_type_id, location_name, latitude, longitude,
                     country, region, estimated_reserves_tonnes, average_grade, 
                     confidence_level, discovery_year, status, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    dep['name'], mineral_id, ore_id, dep['location'],
                    dep['lat'], dep['lng'], 'South Sudan', dep['state'],
                    dep['reserves'], dep['grade'], 
                    dep['confidence'], dep['discovery_year'], dep['status']
                ))
                conn.commit()
                
                # Get the inserted ID
                dep_id = cur.lastrowid
                deposit_id_map[dep['name']] = dep_id
                inserted_deposits.append(dep['name'])
                print(f"   ✓ {dep['name']} ({dep['mineral']})")
            else:
                dep_id = existing[0]
                deposit_id_map[dep['name']] = dep_id
    
    print(f"\n  Total: Added {len(inserted_deposits)} new deposits")
    
    # ============================================================
    # ADD ASSAY RESULTS FOR SELECTED DEPOSITS (if table exists)
    # ============================================================
    
    print("\n5. Adding Assay Results...")
    
    assay_count = 0
    # Check if assay_results table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assay_results'")
    if cur.fetchone():
        assay_data = [
            ('Juba Gold Field', [
                {'sample': 'JDF-001', 'depth_from': 0, 'depth_to': 50, 'au': 2.1, 'ag': 0.3},
                {'sample': 'JDF-002', 'depth_from': 50, 'depth_to': 100, 'au': 2.8, 'ag': 0.4},
                {'sample': 'JDF-003', 'depth_from': 100, 'depth_to': 150, 'au': 3.2, 'ag': 0.5},
            ]),
            ('Torit Gold District', [
                {'sample': 'TGD-001', 'depth_from': 0, 'depth_to': 75, 'au': 3.0, 'ag': 0.35},
                {'sample': 'TGD-002', 'depth_from': 75, 'depth_to': 150, 'au': 3.5, 'ag': 0.45},
                {'sample': 'TGD-003', 'depth_from': 150, 'depth_to': 200, 'au': 3.1, 'ag': 0.4},
            ]),
        ]
        
        for deposit_name, samples in assay_data:
            if deposit_name in deposit_id_map:
                dep_id = deposit_id_map[deposit_name]
                for sample in samples:
                    cur.execute("""
                        INSERT INTO assay_results
                        (deposit_id, sample_id, depth_from, depth_to, au_ppm, ag_ppm, cu_ppm, fe_percent, lab_name, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (
                        dep_id,
                        sample['sample'],
                        sample['depth_from'],
                        sample['depth_to'],
                        sample.get('au'),
                        sample.get('ag'),
                        None,
                        None,
                        'Regional Geological Survey Lab'
                    ))
                    assay_count += 1
        print(f"  ✓ Added {assay_count} assay results")
    else:
        print(f"  ⊘ Assay results table not found (schema may be basic)")
    
    # ============================================================
    # ADD DRILLING LOGS FOR SELECTED DEPOSITS (if table exists)
    # ============================================================
    
    print("\n6. Adding Drilling Logs...")
    
    drilling_count = 0
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='drilling_logs'")
    if cur.fetchone():
        drilling_logs_data = [
            ('Juba Gold Field', [
                {'hole': 'JDF-DD-001', 'depth': 200, 'rock': 'Gneiss and quartz veins', 'recovery': 92},
                {'hole': 'JDF-DD-002', 'depth': 250, 'rock': 'Granodiorite with gold mineralization', 'recovery': 88},
            ]),
        ]
        
        for deposit_name, logs in drilling_logs_data:
            if deposit_name in deposit_id_map:
                dep_id = deposit_id_map[deposit_name]
                for log in logs:
                    cur.execute("""
                        INSERT INTO drilling_logs
                        (deposit_id, hole_id, total_depth, rock_type, core_recovery_percent, 
                         mineralization_notes, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                    """, (
                        dep_id,
                        log['hole'],
                        log['depth'],
                        log['rock'],
                        log['recovery'],
                        'Visible mineralization observed'
                    ))
                    drilling_count += 1
        print(f"  ✓ Added {drilling_count} drilling logs")
    else:
        print(f"  ⊘ Drilling logs table not found (schema may be basic)")
    
    # ============================================================
    # ADD RESOURCE ESTIMATES FOR MAJOR DEPOSITS (if table exists)
    # ============================================================
    
    print("\n7. Adding Resource Estimates...")
    
    resource_count = 0
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource_estimates'")
    if cur.fetchone():
        resource_estimates_data = [
            ('Juba Gold Field', {'tonnage': 450000, 'grade': 2.5, 'metal': 11250, 'confidence': 'probable'}),
            ('Torit Gold District', {'tonnage': 320000, 'grade': 3.2, 'metal': 10240, 'confidence': 'indicated'}),
        ]
        
        for deposit_name, estimate in resource_estimates_data:
            if deposit_name in deposit_id_map:
                dep_id = deposit_id_map[deposit_name]
                cur.execute("""
                    INSERT INTO resource_estimates
                    (deposit_id, tonnage, grade, metal_content, confidence_level, estimate_date, created_by)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), 1)
                """, (
                    dep_id,
                    estimate['tonnage'],
                    estimate['grade'],
                    estimate['metal'],
                    estimate['confidence']
                ))
                resource_count += 1
        print(f"  ✓ Added {resource_count} resource estimates")
    else:
        print(f"  ⊘ Resource estimates table not found (schema may be basic)")
    
    # ============================================================
    # ADD MINING CLAIMS FOR ACTIVE DEPOSITS (if table exists)
    # ============================================================
    
    print("\n8. Adding Mining Claims...")
    
    claims_count = 0
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mining_claims'")
    if cur.fetchone():
        claims_data = [
            ('Juba Gold Field', {
                'claim_id': 'SSU-CENT-GLD-001',
                'company': 'Exploration South Sudan Ltd',
                'area': 25000,
                'claim_type': 'exploration',
                'issue_date': '2020-06-15',
                'expiry_date': '2025-06-15',
                'status': 'active',
                'lat': 4.85, 'lng': 31.59
            }),
            ('Torit Gold District', {
                'claim_id': 'SSU-EAST-GLD-001',
                'company': 'Pan African Resources plc',
                'area': 35000,
                'claim_type': 'exploration',
                'issue_date': '2019-03-20',
                'expiry_date': '2024-03-20',
                'status': 'active',
                'lat': 4.40, 'lng': 32.60
            }),
        ]
        
        for deposit_name, claim in claims_data:
            if deposit_name in deposit_id_map:
                dep_id = deposit_id_map[deposit_name]
                cur.execute("""
                    INSERT INTO mining_claims
                    (claim_id, deposit_id, company_name, location_description, area_hectares,
                     claim_type, issue_date, expiry_date, status, latitude, longitude, owner_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    claim['claim_id'],
                    dep_id,
                    claim['company'],
                    f"Mining claim for {deposit_name}",
                    claim['area'],
                    claim['claim_type'],
                    claim['issue_date'],
                    claim['expiry_date'],
                    claim['status'],
                    claim['lat'],
                    claim['lng']
                ))
                claims_count += 1
        print(f"  ✓ Added {claims_count} mining claims")
    else:
        print(f"  ⊘ Mining claims table not found (schema may be basic)")
    
    conn.commit()
    conn.close()
    
    # Print summary
    print("\n" + "=" * 70)
    print("✓ EXTENDED DEPOSITS DATA ADDITION COMPLETE!")
    print("=" * 70)
    print(f"\nData Summary:")
    print(f"  • Gold deposits: {len(gold_deposits)}")
    print(f"  • Copper deposits: {len(copper_deposits)}")
    print(f"  • Rare Earth Element deposits: {len(ree_deposits)}")
    print(f"  • Diamond deposits: {len(diamond_deposits)}")
    print(f"  • Total new deposits: {len(inserted_deposits)}")
    print(f"  • Assay results: {assay_count}")
    print(f"  • Drilling logs: {drilling_count}")
    print(f"  • Resource estimates: {resource_count}")
    print(f"  • Mining claims: {claims_count}")
    print("\n")

if __name__ == "__main__":
    add_more_deposits()
