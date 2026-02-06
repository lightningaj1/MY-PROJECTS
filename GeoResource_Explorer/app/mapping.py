"""
Enhanced Mapping and Visualization
Advanced Leaflet.js features for geology and South Sudan data
"""

from flask import render_template, jsonify, request
from app.db import get_db
from app.helpers import login_required

def mapping_routes(app):
    
    # ============================================================
    # GEOLOGICAL MAP - South Sudan
    # ============================================================
    
    @app.route("/map/sudan")
    def map_sudan():
        """Interactive South Sudan geological map"""
        db = get_db()
        
        # Get states
        states = db.execute(
            "SELECT id, name, latitude, longitude, primary_minerals FROM ss_states ORDER BY name"
        ).fetchall()
        states = [dict(s) for s in states]  # Convert Row objects to dicts
        
        # Get deposits for markers
        deposits = db.execute("""
            SELECT d.id, d.name, d.latitude, d.longitude, d.region, 
                   mt.name as mineral, d.status
            FROM deposits d
            JOIN mineral_types mt ON d.mineral_type_id = mt.id
            WHERE d.country = 'South Sudan'
            ORDER BY d.status DESC
        """).fetchall()
        deposits = [dict(d) for d in deposits]  # Convert to dicts
        
        # Get exploration sites
        sites = db.execute("""
            SELECT id, name, latitude, longitude, state_id, accessibility, security_status
            FROM ss_exploration_sites
            ORDER BY exploration_status
        """).fetchall()
        sites = [dict(s) for s in sites]  # Convert to dicts
        
        # Get infrastructure
        infra = db.execute("""
            SELECT i.id, i.name, i.type, s.latitude, s.longitude, i.status
            FROM ss_infrastructure i
            JOIN ss_states s ON i.state_id = s.id
        """).fetchall()
        infra = [dict(i) for i in infra]  # Convert to dicts
        
        return render_template("map_sudan.html",
                             states=states,
                             deposits=deposits,
                             sites=sites,
                             infrastructure=infra)
    
    # ============================================================
    # DEPOSITS MAP
    # ============================================================
    
    @app.route("/map/deposits")
    def map_deposits():
        """Map view of mineral deposits"""
        db = get_db()
        
        # Get mineral types for filters
        minerals = db.execute(
            "SELECT DISTINCT mt.id, mt.name, mt.category FROM mineral_types mt ORDER BY name"
        ).fetchall()
        minerals = [dict(m) for m in minerals]  # Convert to dicts
        
        # Get deposits with icons based on mineral type
        # Handle deposits with or without mineral_type_id
        deposits = db.execute("""
            SELECT d.id, d.name, d.latitude, d.longitude, d.region,
                   mt.id as mineral_id, mt.name as mineral, mt.category,
                   d.estimated_reserves_tonnes, d.average_grade, d.status, d.confidence_level
            FROM deposits d
            LEFT JOIN mineral_types mt ON d.mineral_type_id = mt.id
            WHERE d.latitude IS NOT NULL AND d.longitude IS NOT NULL
            ORDER BY d.status DESC
        """).fetchall()
        deposits = [dict(d) for d in deposits]  # Convert to dicts
        
        return render_template("map_deposits.html", 
                             deposits=deposits, 
                             minerals=minerals)
    
    # ============================================================
    # MINING CLAIMS MAP
    # ============================================================
    
    @app.route("/map/claims")
    def map_claims():
        """Map view of mining claims"""
        db = get_db()
        
        # Get claims with boundaries (approximate circles based on hectares)
        claims = db.execute("""
            SELECT id, claim_id, company_name, latitude, longitude,
                   area_hectares, status, claim_type
            FROM mining_claims
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """).fetchall()
        claims = [dict(c) for c in claims]  # Convert to dicts
        
        return render_template("map_claims.html", claims=claims)
    
    # ============================================================
    # INFRASTRUCTURE MAP
    # ============================================================
    
    @app.route("/map/infrastructure")
    def map_infrastructure():
        """Map of South Sudan infrastructure"""
        db = get_db()
        
        # Group infrastructure by type
        infra = db.execute("""
            SELECT i.id, i.name, i.type, i.status, s.name as state,
                   s.latitude, s.longitude
            FROM ss_infrastructure i
            JOIN ss_states s ON i.state_id = s.id
            ORDER BY i.type, i.status
        """).fetchall()
        infra = [dict(i) for i in infra]  # Convert to dicts
        
        return render_template("map_infrastructure.html", infrastructure=infra)
    
    # ============================================================
    # API ENDPOINTS FOR DYNAMIC DATA
    # ============================================================
    
    @app.route("/api/deposits")
    def api_deposits():
        """API endpoint for deposit data (JSON)"""
        db = get_db()
        
        # Optional filters
        mineral_id = request.args.get('mineral_id')
        status = request.args.get('status')
        
        query = """
            SELECT d.id, d.name, d.latitude, d.longitude, d.region,
                   mt.name as mineral, d.status, d.estimated_reserves_tonnes,
                   d.average_grade, d.confidence_level
            FROM deposits d
            JOIN mineral_types mt ON d.mineral_type_id = mt.id
            WHERE 1=1
        """
        params = []
        
        if mineral_id:
            query += " AND mt.id = ?"
            params.append(int(mineral_id))
        
        if status:
            query += " AND d.status = ?"
            params.append(status)
        
        query += " ORDER BY d.name"
        
        deposits = db.execute(query, params).fetchall()
        
        return jsonify([dict(d) for d in deposits])
    
    @app.route("/api/ss-states")
    def api_ss_states():
        """API endpoint for South Sudan states data"""
        db = get_db()
        
        states = db.execute("""
            SELECT s.*, 
                   COUNT(DISTINCT d.id) as deposit_count,
                   COUNT(DISTINCT e.id) as site_count
            FROM ss_states s
            LEFT JOIN deposits d ON d.region = s.name
            LEFT JOIN ss_exploration_sites e ON e.state_id = s.id
            GROUP BY s.id
            ORDER BY s.name
        """).fetchall()
        
        return jsonify([dict(s) for s in states])
    
    @app.route("/api/mining-claims")
    def api_mining_claims():
        """API endpoint for mining claims data"""
        db = get_db()
        
        # Optional filters
        status = request.args.get('status')
        
        query = """
            SELECT c.id, c.claim_id, c.company_name, c.latitude, c.longitude,
                   c.area_hectares, c.status, c.claim_type, d.name as deposit_name
            FROM mining_claims c
            LEFT JOIN deposits d ON c.deposit_id = d.id
            WHERE c.latitude IS NOT NULL
        """
        params = []
        
        if status:
            query += " AND c.status = ?"
            params.append(status)
        
        claims = db.execute(query, params).fetchall()
        
        return jsonify([dict(c) for c in claims])
    
    @app.route("/api/exploration-sites")
    def api_exploration_sites():
        """API endpoint for exploration sites"""
        db = get_db()
        
        sites = db.execute("""
            SELECT e.id, e.name, e.latitude, e.longitude, e.accessibility,
                   e.security_status, e.exploration_status, s.name as state
            FROM ss_exploration_sites e
            JOIN ss_states s ON e.state_id = s.id
            WHERE e.latitude IS NOT NULL
        """).fetchall()
        
        return jsonify([dict(s) for s in sites])
    
    # ============================================================
    # STATISTICS & ANALYTICS
    # ============================================================
    
    @app.route("/analytics")
    @login_required
    def analytics():
        """Analytics dashboard with charts and statistics"""
        db = get_db()
        
        # Mineral statistics
        mineral_stats = db.execute("""
            SELECT mt.name, COUNT(d.id) as count, 
                   ROUND(SUM(d.estimated_reserves_tonnes)) as total_reserves
            FROM mineral_types mt
            LEFT JOIN deposits d ON d.mineral_type_id = mt.id
            GROUP BY mt.id, mt.name
            ORDER BY count DESC
        """).fetchall()
        mineral_stats = [dict(m) for m in mineral_stats]
        
        # Status statistics
        status_stats = db.execute("""
            SELECT status, COUNT(*) as count
            FROM deposits
            GROUP BY status
        """).fetchall()
        status_stats = [dict(s) for s in status_stats]
        
        # State minerals
        state_minerals = db.execute("""
            SELECT s.name as state, 
                   GROUP_CONCAT(DISTINCT mt.name) as minerals,
                   COUNT(DISTINCT d.id) as deposit_count
            FROM ss_states s
            LEFT JOIN deposits d ON d.region = s.name
            LEFT JOIN mineral_types mt ON d.mineral_type_id = mt.id
            GROUP BY s.id, s.name
            ORDER BY deposit_count DESC
        """).fetchall()
        state_minerals = [dict(s) for s in state_minerals]
        
        # Accessibility statistics
        accessibility_stats = db.execute("""
            SELECT accessibility, COUNT(*) as count
            FROM ss_exploration_sites
            GROUP BY accessibility
        """).fetchall()
        accessibility_stats = [dict(a) for a in accessibility_stats]
        
        return render_template("analytics.html",
                             mineral_stats=mineral_stats,
                             status_stats=status_stats,
                             state_minerals=state_minerals,
                             accessibility_stats=accessibility_stats)
    
    print("✓ Advanced mapping and data visualization routes registered")

