"""
Remove Unverified Deposits - Keep Only Verified Sudan Resources
Removes all deposits except the 8 verified oil fields and gold regions
"""

import sqlite3

def remove_unverified_deposits():
    """Remove unverified deposits, keep only the verified ones sent by user"""
    
    conn = sqlite3.connect('minerals.db')
    cur = conn.cursor()
    
    print("\nRemoving Unverified Deposits...")
    print("=" * 70)
    
    # List of verified deposits to KEEP
    verified_deposits = [
        'Palogue Oil Field',
        'Unity Oil Field',
        'Adar Oil Field',
        'Block 5A Oil Concession',
        'Luri River Gold Region',
        'Kinyeti River Gold Region',
        'Nimule Gold Region',
        'Nyangea/Lauro/Buno/Namurunyan Gold Region'
    ]
    
    print(f"\nVerified deposits to KEEP ({len(verified_deposits)}):")
    for i, name in enumerate(verified_deposits, 1):
        print(f"  {i}. {name}")
    
    # Get all current deposits
    cur.execute("SELECT id, name FROM deposits ORDER BY name")
    all_deposits = cur.fetchall()
    
    print(f"\nCurrent deposits in database: {len(all_deposits)}")
    
    # Identify unverified deposits to DELETE
    unverified_ids = []
    for deposit_id, deposit_name in all_deposits:
        if deposit_name not in verified_deposits:
            unverified_ids.append(deposit_id)
    
    if unverified_ids:
        print(f"\nUnverified deposits to DELETE: {len(unverified_ids)}")
        print("-" * 70)
        
        # Get details of deposits being deleted
        cur.execute("SELECT id, name, country, region FROM deposits WHERE id IN ({})".format(
            ','.join(['?' for _ in unverified_ids])
        ), unverified_ids)
        
        for deposit_id, name, country, region in cur.fetchall():
            print(f"  ✗ {name} ({region}, {country})")
        
        # Delete unverified deposits
        # Need to handle foreign keys first
        print("\nDeleting associated data...")
        
        # Get list of tables that do exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cur.fetchall()}
        
        deleted_counts = {}
        
        # Delete from tables that reference deposits (if they exist)
        if 'assay_results' in existing_tables:
            cur.execute("DELETE FROM assay_results WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            deleted_counts['assay_results'] = cur.rowcount
        
        if 'drilling_logs' in existing_tables:
            cur.execute("DELETE FROM drilling_logs WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            deleted_counts['drilling_logs'] = cur.rowcount
        
        if 'resource_estimates' in existing_tables:
            cur.execute("DELETE FROM resource_estimates WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            deleted_counts['resource_estimates'] = cur.rowcount
        
        if 'geological_reports' in existing_tables:
            cur.execute("DELETE FROM geological_reports WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            deleted_counts['geological_reports'] = cur.rowcount
        
        if 'ss_exploration_sites' in existing_tables:
            cur.execute("DELETE FROM ss_exploration_sites WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            deleted_counts['ss_exploration_sites'] = cur.rowcount
        
        if 'watchlist' in existing_tables:
            cur.execute("DELETE FROM watchlist WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            deleted_counts['watchlist'] = cur.rowcount
        
        # Handle mining_claims and licenses (which reference mining_claims)
        if 'mining_claims' in existing_tables:
            # First, get the claim IDs for unverified deposits
            cur.execute("SELECT id FROM mining_claims WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            claim_ids = [row[0] for row in cur.fetchall()]
            
            # Delete licenses for these claims
            if claim_ids and 'licenses' in existing_tables:
                cur.execute("DELETE FROM licenses WHERE claim_id IN ({})".format(
                    ','.join(['?' for _ in claim_ids])
                ), claim_ids)
                deleted_counts['licenses'] = cur.rowcount
            
            # Delete the claims themselves
            cur.execute("DELETE FROM mining_claims WHERE deposit_id IN ({})".format(
                ','.join(['?' for _ in unverified_ids])
            ), unverified_ids)
            deleted_counts['mining_claims'] = cur.rowcount
        
        # Delete the deposits themselves
        cur.execute("DELETE FROM deposits WHERE id IN ({})".format(
            ','.join(['?' for _ in unverified_ids])
        ), unverified_ids)
        deleted_deposits = cur.rowcount
        
        conn.commit()
        
        print(f"\n✓ Deleted {deleted_deposits} unverified deposits")
        for table_name, count in sorted(deleted_counts.items()):
            if count > 0:
                print(f"✓ Deleted {count} records from {table_name}")
    else:
        print("\n✓ No unverified deposits found to delete")
    
    # Verify final state
    cur.execute("SELECT COUNT(*) FROM deposits")
    final_count = cur.fetchone()[0]
    
    print("\n" + "=" * 70)
    print(f"✓ DATABASE CLEANED")
    print("=" * 70)
    print(f"\nRemaining verified deposits in database: {final_count}")
    print("\nVerified Resources:")
    print("\n  Oil Fields (4):")
    print("    • Palogue Oil Field (Upper Nile, 10.4337°, 32.4671°)")
    print("    • Unity Oil Field (Unity, 9.4699°, 29.6764°)")
    print("    • Adar Oil Field (Upper Nile, 10.8°, 32.0°)")
    print("    • Block 5A Oil Concession (Unity, 9.7°, 29.6°)")
    print("\n  Gold Regions (4):")
    print("    • Luri River Gold Region (Eastern Equatoria, 4.650°, 31.450°)")
    print("    • Kinyeti River Gold Region (Eastern Equatoria, 3.600°, 32.030°)")
    print("    • Nimule Gold Region (Central Equatoria, 3.600°, 32.000°)")
    print("    • Nyangea/Lauro/Buno/Namurunyan Gold Region (Central Equatoria, 4.300°, 33.000°)")
    
    conn.close()
    return True

if __name__ == "__main__":
    remove_unverified_deposits()
