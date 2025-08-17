"""
Supabase Authentication Middleware for Flask Chat App

This module provides authentication middleware that validates Supabase JWT tokens
using the Supabase client for simple and reliable validation.
"""

import os
import logging
from functools import wraps
from flask import request, jsonify
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseAuthMiddleware:
    """Middleware for handling Supabase authentication using client validation"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        # Initialize Supabase client with minimal configuration
        try:
            self.supabase: Client = create_client(
                self.supabase_url,
                self.supabase_anon_key
            )
            logger.info(f"Supabase client initialized for URL: {self.supabase_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def require_auth(self, f):
        """Decorator to require authentication for endpoints"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get the Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return jsonify({'error': 'Authorization header missing'}), 401
                
                # Extract the token (should be "Bearer <token>")
                if not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Invalid authorization header format. Use "Bearer <token>"'}), 401
                
                token = auth_header.split(' ')[1]
                if not token:
                    return jsonify({'error': 'Token missing'}), 401
                
                # Validate the token using Supabase client
                user = self.verify_token(token)
                if not user:
                    return jsonify({'error': 'Invalid or expired token'}), 401
                
                # Add user info to request context
                request.user = user
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return jsonify({'error': 'Authentication failed'}), 401
        
        return decorated_function
    
    def verify_token(self, token: str) -> dict:
        """
        Verify the token using Supabase client
        
        Args:
            token: JWT token string
            
        Returns:
            dict: User information if valid, None otherwise
        """
        try:
            # Use the correct method to verify the token
            # In newer versions of supabase-py, we can use get_user with the token directly
            user = self.supabase.auth.get_user(token)
            
            if user and user.user:
                user_info = {
                    'id': user.user.id,
                    'email': user.user.email,
                    'role': 'authenticated'
                }
                logger.info(f"Token verified for user: {user_info['email']}")
                return user_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None

# Global instance
auth_middleware = None

def init_auth():
    """Initialize the authentication middleware"""
    global auth_middleware
    try:
        auth_middleware = SupabaseAuthMiddleware()
        logger.info("Supabase authentication middleware initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize authentication middleware: {str(e)}")
        raise

def require_auth(f):
    """Decorator to require authentication - uses the global middleware instance"""
    if not auth_middleware:
        raise RuntimeError("Authentication middleware not initialized. Call init_auth() first.")
    
    return auth_middleware.require_auth(f) 