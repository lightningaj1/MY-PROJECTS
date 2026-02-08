from flask import session
from app.db import get_db
import pathlib
import os
import re
from bleach import clean
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = pathlib.Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    """
    Check if file extension is allowed.
    """
    if not filename or "." not in filename:
        return False
    
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def secure_upload_file(file_obj):
    """
    Securely handle file uploads with validation and sanitization.
    Returns: (success: bool, filename: str, error: str)
    """
    if not file_obj or file_obj.filename == "":
        return False, None, "No file selected"
    
    # Check file size
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return False, None, f"File size exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit"
    
    # Validate filename and extension
    if not allowed_file(file_obj.filename):
        return False, None, "File type not allowed. Use: PNG, JPG, JPEG, WEBP"
    
    # Secure the filename
    filename = secure_filename(file_obj.filename)
    
    # Add timestamp to make filename unique and prevent collisions
    import time
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}{ext}"
    
    # Ensure upload directory exists
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    
    filepath = UPLOAD_FOLDER / unique_filename
    
    try:
        file_obj.save(str(filepath))
        return True, unique_filename, None
    except Exception as e:
        return False, None, "Failed to save file"

def is_admin():
    """
    Check if current user is admin.
    """
    if "user_id" not in session:
        return False

    db = get_db()
    user = db.execute(
        "SELECT is_admin FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    return user and user["is_admin"] == 1

def sanitize_input(text, allowed_tags=None):
    """
    Sanitize user input to prevent XSS attacks.
    """
    if not isinstance(text, str):
        return ""
    
    if allowed_tags is None:
        allowed_tags = []
    
    # Clean HTML with bleach
    cleaned = clean(text, tags=allowed_tags, strip=True)
    return cleaned

def validate_input(text, field_name="Input", max_length=255, pattern=None):
    """
    Validate user input with optional regex pattern.
    Returns: (valid: bool, value: str, error: str)
    """
    if not isinstance(text, str):
        return False, None, f"{field_name} must be text"
    
    text = text.strip()
    
    if not text:
        return False, None, f"{field_name} is required"
    
    if len(text) > max_length:
        return False, None, f"{field_name} exceeds maximum length of {max_length}"
    
    if pattern:
        if not re.match(pattern, text):
            return False, None, f"{field_name} format is invalid"
    
    return True, text, None
