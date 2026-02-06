"""
Professional Geology Routes
Handles deposits, regulations, claims, and exploration data
"""

from flask import render_template, request, jsonify, redirect, session
from app.db import get_db
from app.roles import require_geologist, require_explorer, is_geologist, is_explorer, is_admin, has_permission
from app.helpers import login_required

def professional_routes(app):
    
    # ============================================================
    # SOUTH SUDAN OVERVIEW
    # ============================================================
    
    @app.route("/sudan")
    @login_required
    def sudan_overview():
        """South Sudan geological overview"""
        db = get_db()
        
        # Get all states with statistics
        states = db.execute("""
            SELECT s.*, 
                   COUNT(DISTINCT e.id) as site_count,
                   COUNT(DISTINCT d.id) as deposit_count
            FROM ss_states s
            LEFT JOIN ss_exploration_sites e ON s.id = e.state_id
            LEFT JOIN deposits d ON e.deposit_id = d.id
            GROUP BY s.id
            ORDER BY s.name
        """).fetchall()
        states = [dict(s) for s in states]
        
        # Get summary statistics
        stats = db.execute("""
            SELECT 
                COUNT(DISTINCT s.id) as total_states,
                COUNT(DISTINCT d.id) as total_deposits,
                COUNT(DISTINCT d.mineral_type_id) as mineral_types,
                COUNT(DISTINCT e.id) as exploration_sites
            FROM ss_states s
            LEFT JOIN ss_exploration_sites e ON s.id = e.state_id
            LEFT JOIN deposits d ON e.deposit_id = d.id
        """).fetchone()
        stats = dict(stats) if stats else {}
        
        return render_template("sudan.html", states=states, stats=stats)
    
    @app.route("/sudan/<state_name>")
    @login_required
    def sudan_state(state_name):
        """State-specific geological profile"""
        db = get_db()
        
        # Get state info
        state = db.execute(
            "SELECT * FROM ss_states WHERE name = ?",
            (state_name,)
        ).fetchone()
        
        if not state:
            return "State not found", 404
        
        # Get deposits in state
        deposits = db.execute("""
            SELECT d.*, mt.name as mineral_name, ot.name as ore_name
            FROM deposits d
            JOIN mineral_types mt ON d.mineral_type_id = mt.id
            JOIN ore_types ot ON d.ore_type_id = ot.id
            WHERE d.region = ?
            ORDER BY d.status DESC
        """, (state_name,)).fetchall()
        deposits = [dict(d) for d in deposits]
        
        # Get exploration sites
        sites = db.execute("""
            SELECT * FROM ss_exploration_sites WHERE state_id = ?
        """, (state['id'],)).fetchall()
        sites = [dict(s) for s in sites]
        
        # Get infrastructure
        infrastructure = db.execute("""
            SELECT * FROM ss_infrastructure WHERE state_id = ? ORDER BY type
        """, (state['id'],)).fetchall()
        infrastructure = [dict(i) for i in infrastructure]
        
        return render_template("sudan_state.html", 
                             state=state, 
                             deposits=deposits, 
                             sites=sites,
                             infrastructure=infrastructure)
    
    # ============================================================
    # DEPOSITS DATABASE
    # ============================================================
    
    @app.route("/deposits")
    def deposits():
        """Browse mineral deposits"""
        db = get_db()
        
        # Get filter parameters
        search = request.args.get('q', '')
        mineral_filter = request.args.get('mineral', '')
        country_filter = request.args.get('country', '')
        status_filter = request.args.get('status', '')
        
        # Base query
        query = """
            SELECT d.*, mt.name as mineral_name, mt.category as mineral_category,
                   ot.name as ore_name
            FROM deposits d
            JOIN mineral_types mt ON d.mineral_type_id = mt.id
            JOIN ore_types ot ON d.ore_type_id = ot.id
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if search:
            query += " AND (d.name LIKE ? OR d.location_name LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        if mineral_filter:
            query += " AND mt.id = ?"
            params.append(int(mineral_filter))
        
        if country_filter:
            query += " AND d.country = ?"
            params.append(country_filter)
        
        if status_filter:
            query += " AND d.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY d.status DESC, d.discovery_year DESC"
        
        deposits = db.execute(query, params).fetchall()
        deposits = [dict(d) for d in deposits]
        
        # Get filter options
        minerals = db.execute("SELECT id, name FROM mineral_types ORDER BY name").fetchall()
        minerals = [dict(m) for m in minerals]
        countries = db.execute("SELECT DISTINCT country FROM deposits ORDER BY country").fetchall()
        countries = [dict(c) for c in countries]
        
        return render_template("deposits.html",
                             deposits=deposits,
                             minerals=minerals,
                             countries=countries,
                             search=search)
    
    @app.route("/deposits/<int:deposit_id>")
    def deposit_detail(deposit_id):
        """Detailed deposit view with geological data"""
        db = get_db()
        
        # Get deposit info
        deposit = db.execute("""
            SELECT d.*, mt.name as mineral_name, ot.name as ore_name
            FROM deposits d
            JOIN mineral_types mt ON d.mineral_type_id = mt.id
            JOIN ore_types ot ON d.ore_type_id = ot.id
            WHERE d.id = ?
        """, (deposit_id,)).fetchone()
        
        if not deposit:
            return "Deposit not found", 404
        
        # Get assay results
        assays = db.execute("""
            SELECT * FROM assay_results WHERE deposit_id = ? ORDER BY depth_from
        """, (deposit_id,)).fetchall()
        assays = [dict(a) for a in assays]
        
        # Get drilling logs
        drilling = db.execute("""
            SELECT * FROM drilling_logs WHERE deposit_id = ? ORDER BY total_depth
        """, (deposit_id,)).fetchall()
        drilling = [dict(d) for d in drilling]
        
        # Get resource estimates
        resources = db.execute("""
            SELECT * FROM resource_estimates WHERE deposit_id = ? ORDER BY estimate_date DESC
        """, (deposit_id,)).fetchall()
        resources = [dict(r) for r in resources]
        
        # Get reports
        reports = db.execute("""
            SELECT * FROM geological_reports WHERE deposit_id = ? ORDER BY report_date DESC
        """, (deposit_id,)).fetchall()
        reports = [dict(r) for r in reports]
        
        # Get exploration sites
        sites = db.execute("""
            SELECT * FROM ss_exploration_sites WHERE deposit_id = ?
        """, (deposit_id,)).fetchall()
        sites = [dict(s) for s in sites]
        
        return render_template("deposit_detail.html",
                             deposit=deposit,
                             assays=assays,
                             drilling=drilling,
                             resources=resources,
                             reports=reports,
                             sites=sites)
    
    # ============================================================
    # MINING REGULATIONS
    # ============================================================
    
    @app.route("/regulations")
    @login_required
    def regulations():
        """South Sudan mining regulations and requirements"""
        db = get_db()
        
        # Get all regulations
        regs = db.execute("""
            SELECT * FROM ss_regulations ORDER BY title
        """).fetchall()
        regs = [dict(r) for r in regs]
        
        return render_template("regulations.html", regulations=regs)
    
    @app.route("/regulations/<int:reg_id>")
    def regulation_detail(reg_id):
        """Detailed regulation view"""
        db = get_db()
        
        reg = db.execute(
            "SELECT * FROM ss_regulations WHERE id = ?",
            (reg_id,)
        ).fetchone()
        
        if not reg:
            return "Regulation not found", 404
        
        return render_template("regulation_detail.html", regulation=reg)
    
    # ============================================================
    # MINING CLAIMS (Explorer feature)
    # ============================================================
    
    @app.route("/claims")
    def claims():
        """Browse mining claims in South Sudan"""
        db = get_db()
        
        # Get filter parameters
        search = request.args.get('q', '')
        status_filter = request.args.get('status', '')
        
        # Base query
        query = """
            SELECT c.*, d.name as deposit_name FROM mining_claims c
            LEFT JOIN deposits d ON c.deposit_id = d.id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (c.claim_id LIKE ? OR c.company_name LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        if status_filter:
            query += " AND c.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY c.issue_date DESC"
        
        claims = db.execute(query, params).fetchall()
        claims = [dict(c) for c in claims]
        
        return render_template("claims.html", claims=claims, search=search)
    
    @app.route("/claims/<claim_id>")
    def claim_detail(claim_id):
        """Detailed claim view"""
        db = get_db()
        
        claim = db.execute(
            "SELECT * FROM mining_claims WHERE claim_id = ?",
            (claim_id,)
        ).fetchone()
        
        if not claim:
            return "Claim not found", 404
        
        # Get associated licenses
        licenses = db.execute(
            "SELECT * FROM licenses WHERE claim_id = ? ORDER BY issue_date DESC",
            (claim['id'],)
        ).fetchall()
        licenses = [dict(l) for l in licenses]
        
        return render_template("claim_detail.html", claim=claim, licenses=licenses)
    
    # Require explorer role for claim management
    @app.route("/claims/add", methods=["GET", "POST"])
    @require_explorer
    def add_claim():
        """Add new mining claim (explorer only)"""
        if request.method == "POST":
            db = get_db()
            
            try:
                db.execute("""
                    INSERT INTO mining_claims
                    (claim_id, deposit_id, owner_id, company_name, location_description,
                     area_hectares, claim_type, issue_date, expiry_date, status, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request.form.get('claim_id'),
                    request.form.get('deposit_id') or None,
                    session['user_id'],
                    request.form.get('company_name'),
                    request.form.get('location'),
                    float(request.form.get('area', 0)),
                    request.form.get('claim_type', 'exploration'),
                    request.form.get('issue_date'),
                    request.form.get('expiry_date'),
                    'active',
                    float(request.form.get('latitude', 0)),
                    float(request.form.get('longitude', 0))
                ))
                db.commit()
                
                return redirect(f"/claims/{request.form.get('claim_id')}")
            except Exception as e:
                return render_template("add_claim.html", error=str(e))
        
        # Get deposits for dropdown
        db = get_db()
        deposits = db.execute(
            "SELECT id, name FROM deposits ORDER BY name"
        ).fetchall()
        deposits = [dict(d) for d in deposits]
        
        return render_template("add_claim.html", deposits=deposits)
    
    # ============================================================
    # EXPLORATION SITES
    # ============================================================
    
    @app.route("/exploration-sites")
    def exploration_sites():
        """Browse South Sudan exploration sites"""
        db = get_db()
        
        # Get filter parameters
        state_filter = request.args.get('state', '')
        accessibility_filter = request.args.get('accessibility', '')
        
        query = """
            SELECT e.*, s.name as state_name FROM ss_exploration_sites e
            JOIN ss_states s ON e.state_id = s.id
            WHERE 1=1
        """
        params = []
        
        if state_filter:
            query += " AND s.id = ?"
            params.append(int(state_filter))
        
        if accessibility_filter:
            query += " AND e.accessibility = ?"
            params.append(accessibility_filter)
        
        query += " ORDER BY e.exploration_status DESC"
        
        sites = db.execute(query, params).fetchall()
        sites = [dict(s) for s in sites]
        
        # Get state options
        states = db.execute(
            "SELECT id, name FROM ss_states ORDER BY name"
        ).fetchall()
        states = [dict(s) for s in states]
        
        return render_template("exploration_sites.html", sites=sites, states=states)
    
    # ============================================================
    # GEOLOGICAL REPORTS
    # ============================================================
    
    @app.route("/reports")
    def reports():
        """Browse geological reports"""
        db = get_db()
        
        query = """
            SELECT r.*, d.name as deposit_name FROM geological_reports r
            LEFT JOIN deposits d ON r.deposit_id = d.id
            WHERE r.access_level IN ('public', 'restricted')
            ORDER BY r.report_date DESC
        """
        
        if session.get('user_id'):
            # Logged-in users can see private reports they authored
            query = """
                SELECT r.*, d.name as deposit_name FROM geological_reports r
                LEFT JOIN deposits d ON r.deposit_id = d.id
                WHERE r.access_level IN ('public', 'restricted') 
                   OR (r.access_level = 'private' AND r.author_id = ?)
                ORDER BY r.report_date DESC
            """
            reports = db.execute(query, (session['user_id'],)).fetchall()
        else:
            reports = db.execute("""
                SELECT r.*, d.name as deposit_name FROM geological_reports r
                LEFT JOIN deposits d ON r.deposit_id = d.id
                WHERE r.access_level = 'public'
                ORDER BY r.report_date DESC
            """).fetchall()
        reports = [dict(r) for r in reports]
        
        return render_template("reports.html", reports=reports)
    
    print("✓ Professional geology routes registered")

