import hashlib
import secrets
from flask import request
import re
from markupsafe import escape

def hash_ip(ip_address):
    """Hash IP address for privacy while maintaining uniqueness for analytics"""
    salt = "quiz_system_salt"  # Use environment variable in production
    return hashlib.sha256(f"{ip_address}{salt}".encode()).hexdigest()[:16]

def hash_user_agent(user_agent):
    """Hash user agent for privacy"""
    if not user_agent:
        return ""
    return hashlib.sha256(user_agent.encode()).hexdigest()[:16]

def sanitize_input(input_string, max_length=500):
    """Sanitize user input to prevent XSS and other attacks"""
    if not input_string:
        return ""
    
    # Remove potential script tags and other dangerous content
    input_string = str(input_string)
    input_string = re.sub(r'<script.*?</script>', '', input_string, flags=re.IGNORECASE | re.DOTALL)
    input_string = re.sub(r'javascript:', '', input_string, flags=re.IGNORECASE)
    input_string = re.sub(r'on\w+\s*=', '', input_string, flags=re.IGNORECASE)
    
    # Escape HTML entities
    input_string = escape(input_string)
    
    # Limit length
    return input_string[:max_length]

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_date(date_string):
    """Validate date format YYYY-MM-DD"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(pattern, date_string) is not None

def generate_session_id():
    """Generate cryptographically secure session ID"""
    return secrets.token_urlsafe(32)

def get_client_info():
    """Get sanitized client information"""
    return {
        'ip_hash': hash_ip(request.remote_addr or ''),
        'user_agent_hash': hash_user_agent(request.headers.get('User-Agent', ''))
    }