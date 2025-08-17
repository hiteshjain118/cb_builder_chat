"""
Configuration file for the Chat App

This file documents the required environment variables and configuration options.
"""

import os

# Required environment variables for Supabase authentication
REQUIRED_ENV_VARS = {
    'SUPABASE_URL': 'Your Supabase project URL (e.g., https://your-project-id.supabase.co)',
    'SUPABASE_ANON_KEY': 'Your Supabase anonymous/public key',
}

# Optional environment variables
OPTIONAL_ENV_VARS = {
    'OPENAI_API_KEY': 'Your OpenAI API key (defaults to placeholder)',
    'OPENAI_MODEL': 'OpenAI model to use (defaults to gpt-4o)',
    'FLASK_ENV': 'Flask environment (development/production)',
    'PORT': 'Server port (defaults to 5002)',
    'HOST': 'Server host (defaults to 0.0.0.0)',
}

def check_required_env_vars():
    """Check if all required environment variables are set"""
    missing_vars = []
    
    for var, description in REQUIRED_ENV_VARS.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables before running the app.")
        return False
    
    return True

def get_config():
    """Get configuration dictionary"""
    return {
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_anon_key': os.getenv('SUPABASE_ANON_KEY'),
        'openai_api_key': os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here'),
        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
        'flask_env': os.getenv('FLASK_ENV', 'development'),
        'port': int(os.getenv('PORT', 5002)),
        'host': os.getenv('HOST', '0.0.0.0'),
    }

if __name__ == '__main__':
    print("Chat App Configuration")
    print("=" * 50)
    
    print("\nRequired Environment Variables:")
    for var, description in REQUIRED_ENV_VARS.items():
        value = os.getenv(var, 'NOT SET')
        status = "✓" if value != 'NOT SET' else "✗"
        print(f"  {status} {var}: {description}")
        if value != 'NOT SET':
            print(f"    Current value: {value[:20]}..." if len(value) > 20 else f"    Current value: {value}")
    
    print("\nOptional Environment Variables:")
    for var, description in OPTIONAL_ENV_VARS.items():
        value = os.getenv(var, 'NOT SET')
        print(f"  {var}: {description}")
        if value != 'NOT SET':
            print(f"    Current value: {value[:20]}..." if len(value) > 20 else f"    Current value: {value}")
    
    print("\nConfiguration Check:")
    if check_required_env_vars():
        print("✓ All required environment variables are set")
    else:
        print("✗ Some required environment variables are missing") 