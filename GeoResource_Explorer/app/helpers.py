from flask import redirect, session
from functools import wraps
import re

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        
        from app.db import get_db
        from app.utils import is_admin
        
        if not is_admin():
            return redirect("/")
        
        return f(*args, **kwargs)
    return decorated_function

# Password validation function
def validate_password(password):
    """
    Validate password strength.
    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not isinstance(password, str):
        return "Invalid password format"
    
    if len(password) < 12:
        return "Password must be at least 12 characters"
    
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/]', password):
        return "Password must contain at least one special character (!@#$%^&*)"
    
    return None  # Password is valid
