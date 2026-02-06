"""
Role-Based Access Control System
Defines user roles and permissions for the professional geology app
"""

from functools import wraps
from flask import session, redirect, abort, jsonify
from app.db import get_db

# ============================================================
# ROLE DEFINITIONS
# ============================================================

ROLES = {
    'viewer': {
        'name': 'Viewer',
        'description': 'Public viewer - read-only access to published data',
        'permissions': [
            'view_minerals',
            'view_deposits',
            'view_ss_overview',
            'search',
            'view_maps'
        ]
    },
    'geologist': {
        'name': 'Geologist',
        'description': 'Technical expert - can view and input geological data',
        'permissions': [
            'view_minerals',
            'view_deposits',
            'add_deposits',
            'edit_deposits',
            'add_assay_results',
            'add_drilling_logs',
            'add_reports',
            'edit_own_reports',
            'view_ss_overview',
            'search',
            'view_maps',
            'create_watchlist'
        ]
    },
    'explorer': {
        'name': 'Explorer/Miner',
        'description': 'Mining company - can manage claims and exploration projects',
        'permissions': [
            'view_minerals',
            'view_deposits',
            'view_claims',
            'add_claims',
            'edit_own_claims',
            'view_licenses',
            'apply_licenses',
            'view_ss_overview',
            'search',
            'view_maps',
            'create_watchlist',
            'view_regulations'
        ]
    },
    'investor': {
        'name': 'Investor',
        'description': 'Financial stakeholder - can view deposits and market data',
        'permissions': [
            'view_minerals',
            'view_deposits',
            'view_claims',
            'view_reports',
            'view_prices',
            'view_ss_overview',
            'search',
            'view_maps',
            'create_watchlist',
            'view_analytics'
        ]
    },
    'admin': {
        'name': 'Administrator',
        'description': 'System administrator - full access and control',
        'permissions': [
            '*'  # All permissions
        ]
    }
}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_user_role():
    """Get current user's role from session"""
    if 'user_id' not in session:
        return 'viewer'  # Default anonymous role
    
    db = get_db()
    user = db.execute(
        "SELECT role FROM users WHERE id = ?",
        (session['user_id'],)
    ).fetchone()
    
    return user['role'] if user and user['role'] else 'viewer'

def has_permission(permission):
    """Check if current user has a specific permission"""
    role = get_user_role()
    
    if role not in ROLES:
        return False
    
    perms = ROLES[role]['permissions']
    
    # Admin has all permissions
    if '*' in perms:
        return True
    
    return permission in perms

def get_user_data():
    """Get current user's full data"""
    if 'user_id' not in session:
        return None
    
    db = get_db()
    user = db.execute(
        "SELECT id, username, role, organization, expertise FROM users WHERE id = ?",
        (session['user_id'],)
    ).fetchone()
    
    return dict(user) if user else None

def is_geologist():
    """Check if user is a geologist"""
    return get_user_role() in ['geologist', 'admin']

def is_explorer():
    """Check if user is an explorer/miner"""
    return get_user_role() in ['explorer', 'admin']

def is_investor():
    """Check if user is an investor"""
    return get_user_role() in ['investor', 'admin']

def is_admin():
    """Check if user is an administrator"""
    return get_user_role() == 'admin'

# ============================================================
# DECORATORS FOR ROUTE PROTECTION
# ============================================================

def require_role(*allowed_roles):
    """Decorator: Require specific roles to access route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_role = get_user_role()
            
            # Allow if user has one of the allowed roles
            if current_role in allowed_roles or 'admin' in allowed_roles and is_admin():
                return f(*args, **kwargs)
            
            # Redirect unauthorized users
            if 'user_id' in session:
                abort(403)  # Forbidden
            else:
                return redirect('/login')
        
        return decorated_function
    return decorator

def require_permission(permission):
    """Decorator: Require specific permission to access route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_permission(permission):
                if 'user_id' in session:
                    abort(403)  # Forbidden
                else:
                    return redirect('/login')
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_geologist(f):
    """Decorator: Require geologist or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_geologist():
            if 'user_id' in session:
                abort(403)
            else:
                return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def require_explorer(f):
    """Decorator: Require explorer/miner or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_explorer():
            if 'user_id' in session:
                abort(403)
            else:
                return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def require_investor(f):
    """Decorator: Require investor or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_investor():
            if 'user_id' in session:
                abort(403)
            else:
                return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator: Require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            if 'user_id' in session:
                abort(403)
            else:
                return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# DATA ACCESS CONTROL
# ============================================================

def filter_deposits_by_role(deposits):
    """Filter deposits visibility based on user role"""
    role = get_user_role()
    
    # All roles can see deposits
    return deposits

def filter_reports_by_role(reports):
    """Filter reports visibility based on user role and access level"""
    role = get_user_role()
    user_id = session.get('user_id')
    
    filtered = []
    for report in reports:
        # Check access level
        if report['access_level'] == 'public':
            filtered.append(report)
        elif report['access_level'] == 'restricted' and user_id:
            filtered.append(report)
        elif report['access_level'] == 'private' and report['author_id'] == user_id:
            filtered.append(report)
    
    return filtered

def can_edit_deposit(deposit_id, user_id):
    """Check if user can edit a specific deposit"""
    if is_admin():
        return True
    
    if not is_geologist():
        return False
    
    # Geologists can edit deposits they created
    db = get_db()
    deposit = db.execute(
        "SELECT created_by FROM deposits WHERE id = ?",
        (deposit_id,)
    ).fetchone()
    
    return deposit and deposit['created_by'] == user_id

def can_edit_claim(claim_id, user_id):
    """Check if user can edit a specific mining claim"""
    if is_admin():
        return True
    
    if not is_explorer():
        return False
    
    # Explorers can edit their own claims
    db = get_db()
    claim = db.execute(
        "SELECT owner_id FROM mining_claims WHERE id = ?",
        (claim_id,)
    ).fetchone()
    
    return claim and claim['owner_id'] == user_id

def context_processor_roles(app):
    """Add role functions to template context"""
    @app.context_processor
    def inject_roles():
        return {
            'user_role': get_user_role(),
            'user_data': get_user_data(),
            'is_geologist': is_geologist,
            'is_explorer': is_explorer,
            'is_investor': is_investor,
            'is_admin': is_admin,
            'has_permission': has_permission,
            'ROLES': ROLES
        }

# ============================================================
# ROLE-SPECIFIC DASHBOARDS
# ============================================================

def get_dashboard_data(user_id):
    """Get personalized dashboard data based on user role"""
    db = get_db()
    user = db.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    role = user['role'] if user else 'viewer'
    
    dashboard_data = {
        'role': role,
        'user_id': user_id
    }
    
    if role == 'geologist':
        # Get my deposits and assay results
        dashboard_data['my_deposits'] = db.execute(
            "SELECT * FROM deposits WHERE created_by = ? ORDER BY created_at DESC LIMIT 5",
            (user_id,)
        ).fetchall()
        dashboard_data['recent_assays'] = db.execute(
            "SELECT a.*, d.name FROM assay_results a JOIN deposits d ON a.deposit_id = d.id WHERE a.created_by = ? ORDER BY a.created_at DESC LIMIT 5",
            (user_id,)
        ).fetchall()
    
    elif role == 'explorer':
        # Get my claims and licenses
        dashboard_data['my_claims'] = db.execute(
            "SELECT * FROM mining_claims WHERE owner_id = ? ORDER BY created_at DESC LIMIT 5",
            (user_id,)
        ).fetchall()
        dashboard_data['my_licenses'] = db.execute(
            "SELECT l.* FROM licenses l JOIN mining_claims c ON l.claim_id = c.id WHERE c.owner_id = ? ORDER BY l.created_at DESC LIMIT 5",
            (user_id,)
        ).fetchall()
    
    elif role == 'investor':
        # Get watchlist and market data
        dashboard_data['watchlist'] = db.execute(
            "SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_at DESC LIMIT 5",
            (user_id,)
        ).fetchall()
    
    return dashboard_data
