"""
Deposit and Mining Claims Management
Manage deposits and claims imported from QGIS
"""

from flask import render_template, request, jsonify, redirect, session
from app.db import get_db
from app.utils import is_admin
from app.helpers import login_required

def deposit_routes(app):
    """Register deposit and claims management routes"""
    
    # ============================================================
    # DEPOSIT MANAGEMENT
    # ============================================================
    
    @app.route("/admin/deposits")
    @login_required
    def admin_deposits():
        """Admin interface to manage mineral deposits"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        
        # Get all deposits with mineral type info
        deposits = db.execute("""
            SELECT d.*, mt.name as mineral_name
            FROM deposits d
            LEFT JOIN mineral_types mt ON d.mineral_type_id = mt.id
            ORDER BY d.status DESC, d.name ASC
        """).fetchall()
        deposits = [dict(d) for d in deposits]
        
        # Get mineral types for dropdowns
        mineral_types = db.execute(
            "SELECT id, name, category FROM mineral_types ORDER BY name"
        ).fetchall()
        mineral_types = [dict(m) for m in mineral_types]
        
        # Get statistics
        stats = {
            'total': len(deposits),
            'active': len([d for d in deposits if d['status'] == 'Active']),
            'prospect': len([d for d in deposits if d['status'] == 'Prospect']),
            'historical': len([d for d in deposits if d['status'] == 'Historical'])
        }
        
        return render_template("admin_deposits.html",
                             deposits=deposits,
                             mineral_types=mineral_types,
                             stats=stats)
    
    @app.route("/admin/deposits/<int:deposit_id>", methods=["GET"])
    @login_required
    def admin_deposit_detail(deposit_id):
        """View deposit details"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        deposit = db.execute("""
            SELECT d.*, mt.name as mineral_name
            FROM deposits d
            LEFT JOIN mineral_types mt ON d.mineral_type_id = mt.id
            WHERE d.id = ?
        """, (deposit_id,)).fetchone()
        
        if not deposit:
            return redirect("/admin/deposits")
        
        deposit = dict(deposit)
        
        # Get related mining claims
        claims = db.execute("""
            SELECT * FROM mining_claims
            WHERE deposit_id = ?
            ORDER BY claim_id
        """, (deposit_id,)).fetchall()
        claims = [dict(c) for c in claims]
        
        return render_template("admin_deposit_detail.html",
                             deposit=deposit,
                             claims=claims)
    
    @app.route("/admin/deposits/<int:deposit_id>/edit", methods=["GET", "POST"])
    @login_required
    def admin_edit_deposit(deposit_id):
        """Edit deposit information"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        
        if request.method == "POST":
            # Update deposit
            db.execute("""
                UPDATE deposits
                SET name = ?, mineral_type_id = ?, location_name = ?,
                    latitude = ?, longitude = ?, country = ?, region = ?,
                    estimated_reserves_tonnes = ?, average_grade = ?,
                    confidence_level = ?, discovery_year = ?, status = ?, notes = ?
                WHERE id = ?
            """, (
                request.form.get('name'),
                request.form.get('mineral_type_id') or None,
                request.form.get('location_name'),
                float(request.form.get('latitude', 0)) if request.form.get('latitude') else None,
                float(request.form.get('longitude', 0)) if request.form.get('longitude') else None,
                request.form.get('country'),
                request.form.get('region'),
                float(request.form.get('reserves', 0)) if request.form.get('reserves') else None,
                float(request.form.get('grade', 0)) if request.form.get('grade') else None,
                request.form.get('confidence'),
                int(request.form.get('year', 0)) if request.form.get('year') else None,
                request.form.get('status'),
                request.form.get('notes'),
                deposit_id
            ))
            db.commit()
            
            return redirect(f"/admin/deposits/{deposit_id}")
        
        deposit = db.execute("""
            SELECT d.*, mt.name as mineral_name
            FROM deposits d
            LEFT JOIN mineral_types mt ON d.mineral_type_id = mt.id
            WHERE d.id = ?
        """, (deposit_id,)).fetchone()
        
        if not deposit:
            return redirect("/admin/deposits")
        
        deposit = dict(deposit)
        
        # Get mineral types
        mineral_types = db.execute(
            "SELECT id, name FROM mineral_types ORDER BY name"
        ).fetchall()
        mineral_types = [dict(m) for m in mineral_types]
        
        return render_template("admin_edit_deposit.html",
                             deposit=deposit,
                             mineral_types=mineral_types)
    
    @app.route("/admin/deposits/<int:deposit_id>/delete", methods=["POST"])
    @login_required
    def admin_delete_deposit(deposit_id):
        """Delete a deposit"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        
        # Delete related mining claims
        db.execute("DELETE FROM mining_claims WHERE deposit_id = ?", (deposit_id,))
        
        # Delete deposit
        db.execute("DELETE FROM deposits WHERE id = ?", (deposit_id,))
        db.commit()
        
        return redirect("/admin/deposits")
    
    # ============================================================
    # MINING CLAIMS MANAGEMENT
    # ============================================================
    
    @app.route("/admin/claims")
    @login_required
    def admin_claims():
        """Admin interface to manage mining claims"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        
        # Get all claims with deposit info
        claims = db.execute("""
            SELECT c.*, d.name as deposit_name
            FROM mining_claims c
            LEFT JOIN deposits d ON c.deposit_id = d.id
            ORDER BY c.status DESC, c.claim_id ASC
        """).fetchall()
        claims = [dict(c) for c in claims]
        
        # Get deposits for dropdown
        deposits = db.execute(
            "SELECT id, name FROM deposits ORDER BY name"
        ).fetchall()
        deposits = [dict(d) for d in deposits]
        
        # Get statistics
        stats = {
            'total': len(claims),
            'active': len([c for c in claims if c['status'] == 'Active']),
            'inactive': len([c for c in claims if c['status'] == 'Inactive']),
            'expired': len([c for c in claims if c['status'] == 'Expired'])
        }
        
        return render_template("admin_claims.html",
                             claims=claims,
                             deposits=deposits,
                             stats=stats)
    
    @app.route("/admin/claims/<int:claim_id>", methods=["GET"])
    @login_required
    def admin_claim_detail(claim_id):
        """View claim details"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        claim = db.execute("""
            SELECT c.*, d.name as deposit_name
            FROM mining_claims c
            LEFT JOIN deposits d ON c.deposit_id = d.id
            WHERE c.id = ?
        """, (claim_id,)).fetchone()
        
        if not claim:
            return redirect("/admin/claims")
        
        return render_template("admin_claim_detail.html", claim=dict(claim))
    
    @app.route("/admin/claims/<int:claim_id>/edit", methods=["GET", "POST"])
    @login_required
    def admin_edit_claim(claim_id):
        """Edit claim information"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        
        if request.method == "POST":
            # Update claim
            db.execute("""
                UPDATE mining_claims
                SET company_name = ?, location_description = ?,
                    area_hectares = ?, claim_type = ?, latitude = ?,
                    longitude = ?, status = ?, deposit_id = ?
                WHERE id = ?
            """, (
                request.form.get('company_name'),
                request.form.get('location_description'),
                float(request.form.get('area_hectares', 0)) if request.form.get('area_hectares') else None,
                request.form.get('claim_type'),
                float(request.form.get('latitude', 0)) if request.form.get('latitude') else None,
                float(request.form.get('longitude', 0)) if request.form.get('longitude') else None,
                request.form.get('status'),
                request.form.get('deposit_id') or None,
                claim_id
            ))
            db.commit()
            
            return redirect(f"/admin/claims/{claim_id}")
        
        claim = db.execute("""
            SELECT c.*, d.name as deposit_name
            FROM mining_claims c
            LEFT JOIN deposits d ON c.deposit_id = d.id
            WHERE c.id = ?
        """, (claim_id,)).fetchone()
        
        if not claim:
            return redirect("/admin/claims")
        
        claim = dict(claim)
        
        # Get deposits
        deposits = db.execute(
            "SELECT id, name FROM deposits ORDER BY name"
        ).fetchall()
        deposits = [dict(d) for d in deposits]
        
        return render_template("admin_edit_claim.html",
                             claim=claim,
                             deposits=deposits)
    
    @app.route("/admin/claims/<int:claim_id>/delete", methods=["POST"])
    @login_required
    def admin_delete_claim(claim_id):
        """Delete a claim"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        db.execute("DELETE FROM mining_claims WHERE id = ?", (claim_id,))
        db.commit()
        
        return redirect("/admin/claims")
    
    # ============================================================
    # API ENDPOINTS FOR DATA
    # ============================================================
    
    @app.route("/api/admin/deposits-summary")
    @login_required
    def api_deposits_summary():
        """Get deposit summary for admin dashboard"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        
        deposits = db.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
                   SUM(CASE WHEN status = 'Prospect' THEN 1 ELSE 0 END) as prospect,
                   SUM(CASE WHEN status = 'Historical' THEN 1 ELSE 0 END) as historical
            FROM deposits
        """).fetchone()
        
        return jsonify({
            'total': deposits['total'] or 0,
            'active': deposits['active'] or 0,
            'prospect': deposits['prospect'] or 0,
            'historical': deposits['historical'] or 0
        })
    
    @app.route("/api/admin/claims-summary")
    @login_required
    def api_claims_summary():
        """Get claims summary for admin dashboard"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        
        claims = db.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
                   SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END) as inactive,
                   SUM(CASE WHEN status = 'Expired' THEN 1 ELSE 0 END) as expired
            FROM mining_claims
        """).fetchone()
        
        return jsonify({
            'total': claims['total'] or 0,
            'active': claims['active'] or 0,
            'inactive': claims['inactive'] or 0,
            'expired': claims['expired'] or 0
        })
