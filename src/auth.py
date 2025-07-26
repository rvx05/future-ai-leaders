"""
Authentication module for Flask app
"""
import json
from functools import wraps
from flask import request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

# Initialize Flask-Login
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return db.get_user_by_id(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access"""
    return jsonify({'error': 'Authentication required'}), 401

def init_auth(app):
    """Initialize authentication for the Flask app"""
    login_manager.init_app(app)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'  # Change this in production!
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for API endpoints

def register_user(email: str, username: str, password: str):
    """Register a new user"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if '@' not in email:
        return False, "Invalid email address"
    
    user = db.create_user(email, username, password)
    if user:
        return True, "User created successfully"
    else:
        return False, "Email or username already exists"

def authenticate_user(email: str, password: str):
    """Authenticate user and log them in"""
    user = db.get_user_by_email(email)
    if user and user.check_password(password):
        login_user(user)
        # Convert user object to dictionary for JSON serialization
        user_data = user.to_dict()
        return True, "Login successful", user_data
    return False, "Invalid email or password", None

def get_current_user_data():
    """Get current user data"""
    if current_user.is_authenticated:
        return current_user.to_dict()
    return None

def update_user_profile(profile_data: dict):
    """Update current user's profile"""
    if not current_user.is_authenticated:
        return False, "Not authenticated"
    
    try:
        profile_json = json.dumps(profile_data)
        success = db.update_user_profile(current_user.id, profile_json)
        if success:
            # Update current user's profile data
            current_user.profile_data = profile_json
            return True, "Profile updated successfully"
        else:
            return False, "Failed to update profile"
    except Exception as e:
        return False, f"Error updating profile: {str(e)}"

def get_user_progress():
    """Get current user's study progress"""
    if not current_user.is_authenticated:
        return {}
    
    return db.get_user_progress(current_user.id)

def add_study_session(session_type: str, duration_minutes: int = None, 
                     score: float = None, metadata: dict = None):
    """Add a study session for the current user"""
    if not current_user.is_authenticated:
        return None
    
    metadata_json = json.dumps(metadata or {})
    return db.add_study_session(
        current_user.id, session_type, duration_minutes, score, metadata_json
    )

def api_login_required(f):
    """Decorator for API endpoints that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function
