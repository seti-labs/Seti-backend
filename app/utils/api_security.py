"""
Secure API endpoint decorators and utilities
"""

from functools import wraps
from flask import request, jsonify, g
from app.middleware.security import InputValidator, require_auth, require_admin
import logging

logger = logging.getLogger(__name__)

def validate_input(schema=None):
    """Validate and sanitize input data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validate JSON data
                if request.is_json:
                    data = request.get_json()
                    if data:
                        # Basic sanitization
                        sanitized_data = {}
                        for key, value in data.items():
                            if isinstance(value, str):
                                sanitized_data[key] = InputValidator.sanitize_string(value)
                            else:
                                sanitized_data[key] = value
                        g.sanitized_data = sanitized_data
                
                # Validate query parameters
                if request.args:
                    sanitized_args = {}
                    for key, value in request.args.items():
                        if isinstance(value, str):
                            sanitized_args[key] = InputValidator.sanitize_string(value, 100)
                        else:
                            sanitized_args[key] = value
                    g.sanitized_args = sanitized_args
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Input validation error: {e}")
                return jsonify({'error': 'Invalid input data'}), 400
        return decorated_function
    return decorator

def secure_endpoint(require_auth_flag=False, require_admin_flag=False, rate_limit=True):
    """Secure endpoint decorator with multiple security layers"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Apply authentication if required
            if require_auth_flag:
                auth_result = require_auth(f)
                if auth_result:
                    return auth_result
            
            # Apply admin authentication if required
            if require_admin_flag:
                admin_result = require_admin(f)
                if admin_result:
                    return admin_result
            
            # Apply input validation
            validation_result = validate_input()(f)
            if validation_result:
                return validation_result
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_prediction_data(data):
    """Validate prediction creation data"""
    errors = []
    
    # Required fields
    required_fields = ['market_id', 'user_address', 'outcome', 'amount']
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing required field: {field}')
    
    # Validate user address
    if 'user_address' in data:
        if not InputValidator.validate_address(data['user_address']):
            errors.append('Invalid user address format')
    
    # Validate amount
    if 'amount' in data:
        if not InputValidator.validate_amount(data['amount']):
            errors.append('Invalid amount - must be positive number')
    
    # Validate outcome
    if 'outcome' in data:
        if data['outcome'] not in ['YES', 'NO']:
            errors.append('Outcome must be YES or NO')
    
    return errors

def validate_market_data(data):
    """Validate market creation data"""
    errors = []
    
    # Required fields
    required_fields = ['question', 'description', 'end_time']
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing required field: {field}')
    
    # Validate question length
    if 'question' in data:
        if len(data['question']) > 500:
            errors.append('Question too long (max 500 characters)')
        if len(data['question']) < 10:
            errors.append('Question too short (min 10 characters)')
    
    # Validate description length
    if 'description' in data:
        if len(data['description']) > 2000:
            errors.append('Description too long (max 2000 characters)')
    
    # Validate end time
    if 'end_time' in data:
        import time
        try:
            end_time = int(data['end_time'])
            if end_time <= int(time.time()):
                errors.append('End time must be in the future')
        except (ValueError, TypeError):
            errors.append('Invalid end time format')
    
    return errors

def validate_user_data(data):
    """Validate user update data"""
    errors = []
    
    # Validate username
    if 'username' in data:
        username = data['username']
        if len(username) > 100:
            errors.append('Username too long (max 100 characters)')
        if len(username) < 3:
            errors.append('Username too short (min 3 characters)')
        # Check for valid characters
        if not username.replace('_', '').replace('-', '').isalnum():
            errors.append('Username contains invalid characters')
    
    # Validate bio
    if 'bio' in data:
        if len(data['bio']) > 500:
            errors.append('Bio too long (max 500 characters)')
    
    # Validate avatar URL
    if 'avatar_url' in data:
        avatar_url = data['avatar_url']
        if len(avatar_url) > 500:
            errors.append('Avatar URL too long (max 500 characters)')
        # Basic URL validation
        if avatar_url and not (avatar_url.startswith('http://') or avatar_url.startswith('https://')):
            errors.append('Invalid avatar URL format')
    
    return errors

def handle_api_error(f):
    """Handle API errors gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API Error in {f.__name__}: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

def log_api_access(f):
    """Log API access for monitoring"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"API Access: {request.method} {request.path} from {request.remote_addr}")
        return f(*args, **kwargs)
    return decorated_function
