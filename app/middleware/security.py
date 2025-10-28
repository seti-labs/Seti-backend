"""
Security middleware for Flask application
Implements comprehensive security headers, rate limiting, and request validation
"""

import time
import hashlib
import hmac
from functools import wraps
from flask import request, jsonify, g
from collections import defaultdict, deque
import os
import re
from typing import Dict, List, Optional

class SecurityMiddleware:
    """Comprehensive security middleware"""
    
    def __init__(self, app=None):
        self.app = app
        self.rate_limits = defaultdict(lambda: deque())
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',  # XSS
            r'on\w+\s*=',  # XSS event handlers
            r'union\s+select',  # SQL injection
            r'drop\s+table',  # SQL injection
            r'delete\s+from',  # SQL injection
            r'insert\s+into',  # SQL injection
            r'update\s+set',  # SQL injection
            r'--',  # SQL comment
            r'/\*.*?\*/',  # SQL comment
            r'\.\./',  # Path traversal
            r'\.\.\\',  # Path traversal
        ]
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Security configuration
        app.config.setdefault('SECURITY_HEADERS', True)
        app.config.setdefault('RATE_LIMIT_ENABLED', True)
        app.config.setdefault('RATE_LIMIT_REQUESTS', 100)
        app.config.setdefault('RATE_LIMIT_WINDOW', 3600)  # 1 hour
        app.config.setdefault('BLOCK_SUSPICIOUS_REQUESTS', True)
        app.config.setdefault('CORS_STRICT', True)
    
    def before_request(self):
        """Security checks before processing request"""
        # Block suspicious IPs
        if request.remote_addr in self.blocked_ips:
            return jsonify({'error': 'Access denied'}), 403
        
        # Rate limiting
        if self.app.config.get('RATE_LIMIT_ENABLED', True):
            if not self.check_rate_limit():
                return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Validate request for suspicious patterns
        if self.app.config.get('BLOCK_SUSPICIOUS_REQUESTS', True):
            if self.detect_suspicious_request():
                self.block_ip(request.remote_addr)
                return jsonify({'error': 'Suspicious request detected'}), 400
        
        # Validate content length
        if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
            return jsonify({'error': 'Request too large'}), 413
    
    def after_request(self, response):
        """Add security headers after processing request"""
        if self.app.config.get('SECURITY_HEADERS', True):
            self.add_security_headers(response)
        return response
    
    def check_rate_limit(self) -> bool:
        """Check if request is within rate limit"""
        client_id = f"{request.remote_addr}:{request.endpoint}"
        now = time.time()
        window = self.app.config.get('RATE_LIMIT_WINDOW', 3600)
        max_requests = self.app.config.get('RATE_LIMIT_REQUESTS', 100)
        
        # Clean old requests
        while self.rate_limits[client_id] and self.rate_limits[client_id][0] < now - window:
            self.rate_limits[client_id].popleft()
        
        # Check if limit exceeded
        if len(self.rate_limits[client_id]) >= max_requests:
            return False
        
        # Add current request
        self.rate_limits[client_id].append(now)
        return True
    
    def detect_suspicious_request(self) -> bool:
        """Detect suspicious patterns in request"""
        # Check URL parameters
        for key, value in request.args.items():
            if self.contains_suspicious_pattern(str(value)):
                return True
        
        # Check form data
        if request.form:
            for key, value in request.form.items():
                if self.contains_suspicious_pattern(str(value)):
                    return True
        
        # Check JSON data
        if request.is_json and request.get_json():
            json_data = str(request.get_json())
            if self.contains_suspicious_pattern(json_data):
                return True
        
        return False
    
    def contains_suspicious_pattern(self, text: str) -> bool:
        """Check if text contains suspicious patterns"""
        text_lower = text.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def block_ip(self, ip: str):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        print(f"Blocked suspicious IP: {ip}")
    
    def add_security_headers(self, response):
        """Add comprehensive security headers"""
        headers = {
            # Prevent XSS attacks
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            
            # HTTPS enforcement
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            
            # Content Security Policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            ),
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Permissions policy
            'Permissions-Policy': (
                'geolocation=(), '
                'microphone=(), '
                'camera=(), '
                'payment=(), '
                'usb=(), '
                'magnetometer=(), '
                'gyroscope=(), '
                'speaker=(), '
                'vibrate=(), '
                'fullscreen=(self)'
            ),
            
            # Cache control for sensitive endpoints
            'Cache-Control': 'no-store, no-cache, must-revalidate, private',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        for header, value in headers.items():
            response.headers[header] = value

# Authentication decorators
def require_auth(f):
    """Require authentication for endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Simple token validation (implement proper JWT in production)
        if not validate_token(auth_header):
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Require admin authentication for endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_key = request.headers.get('X-Admin-Key')
        expected_key = os.getenv('ADMIN_KEY')
        
        if not admin_key or not expected_key:
            return jsonify({'error': 'Admin authentication required'}), 401
        
        # Use HMAC for secure comparison
        if not hmac.compare_digest(admin_key, expected_key):
            return jsonify({'error': 'Invalid admin key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_token(token: str) -> bool:
    """Validate authentication token"""
    # Implement proper JWT validation in production
    # For now, simple validation
    if not token.startswith('Bearer '):
        return False
    
    token_value = token[7:]  # Remove 'Bearer ' prefix
    
    # Simple validation - replace with proper JWT validation
    return len(token_value) > 10 and token_value.isalnum()

# Input validation utilities
class InputValidator:
    """Input validation and sanitization utilities"""
    
    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate blockchain address format"""
        if not address or len(address) < 20:
            return False
        
        # Basic address validation (implement proper checksum validation)
        return re.match(r'^[0-9a-fA-Fx]+$', address) is not None
    
    @staticmethod
    def validate_amount(amount) -> bool:
        """Validate amount is positive number"""
        try:
            amount_float = float(amount)
            return amount_float > 0 and amount_float < 1e18  # Reasonable upper limit
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Limit length
        text = text[:max_length]
        
        # Escape HTML characters
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace('"', '&quot;').replace("'", '&#x27;')
        
        return text.strip()
    
    @staticmethod
    def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> tuple:
        """Validate and sanitize pagination parameters"""
        page = max(1, int(page)) if page else 1
        per_page = min(max(1, int(per_page)), max_per_page) if per_page else 20
        return page, per_page

# Initialize security middleware
security_middleware = SecurityMiddleware()
