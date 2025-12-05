# backend/auth_middleware.py
"""
Authentication and Authorization middleware for API endpoints
"""
from functools import wraps
from flask import request, jsonify
from database import get_db_connection
import secrets
import hashlib
from datetime import datetime, timedelta

# In-memory token storage (for simplicity)
# In production, use Redis or database
TOKEN_STORE = {}  # token -> {"user_id": int, "username": str, "role": str, "expires": datetime}


def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def create_token(user_id, username, role):
    """Create and store a token for a user"""
    token = generate_token()
    expires = datetime.now() + timedelta(hours=24)  # Token expires in 24 hours
    
    TOKEN_STORE[token] = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "expires": expires
    }
    
    return token


def get_token_from_request():
    """Extract token from Authorization header"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "").strip()
    return None


def verify_token(token):
    """Verify token and return user info if valid"""
    if not token:
        return None
    
    # Check if token exists
    if token not in TOKEN_STORE:
        return None
    
    user_info = TOKEN_STORE[token]
    
    # Check if token expired
    if datetime.now() > user_info["expires"]:
        del TOKEN_STORE[token]  # Clean up expired token
        return None
    
    return user_info


def revoke_token(token):
    """Remove token from store (logout)"""
    if token in TOKEN_STORE:
        del TOKEN_STORE[token]


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        user_info = verify_token(token)
        
        if not user_info:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Attach user info to request for use in the endpoint
        request.current_user = user_info
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(allowed_roles):
    """Decorator to require specific role(s)"""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    def decorator(f):
        @wraps(f)
        @require_auth  # First check authentication
        def decorated_function(*args, **kwargs):
            user_info = request.current_user
            user_role = user_info.get("role")
            
            if user_role not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_customer(f):
    """Shortcut decorator for customer-only endpoints"""
    return require_role("customer")(f)


def require_manager(f):
    """Shortcut decorator for manager-only endpoints"""
    return require_role("manager")(f)


def get_current_user_id():
    """Helper to get current user ID from request"""
    if hasattr(request, 'current_user'):
        return request.current_user.get("user_id")
    return None


def get_current_user_role():
    """Helper to get current user role from request"""
    if hasattr(request, 'current_user'):
        return request.current_user.get("role")
    return None
