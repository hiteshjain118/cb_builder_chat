#!/usr/bin/env python3
"""
Startup script for the Chat App with Supabase authentication

This script checks the configuration and environment variables before starting the server.
"""

import os
import sys
import subprocess

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment configuration...")
    
    required_vars = {
        'SUPABASE_URL': 'Your Supabase project URL',
        'SUPABASE_ANON_KEY': 'Your Supabase anonymous/public key'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"{var}: {description}")
            print(f"❌ {var} is not set")
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file with these variables:")
        print("SUPABASE_URL=https://your-project-id.supabase.co")
        print("SUPABASE_ANON_KEY=your-anon-key-here")
        print("\nOr set them in your shell environment.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'flask',
        'supabase',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def run_config_check():
    """Run the configuration check script"""
    print("\n⚙️  Running configuration check...")
    
    try:
        result = subprocess.run([sys.executable, 'config.py'], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Configuration check passed")
            return True
        else:
            print("❌ Configuration check failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running configuration check: {str(e)}")
        return False

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting Chat App server...")
    print("The server will be available at: http://localhost:5002")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the Flask app
        subprocess.run([sys.executable, 'app.py'], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🔐 Chat App with Supabase Authentication")
    print("=" * 50)
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run configuration check
    if not run_config_check():
        print("\n⚠️  Configuration check failed, but continuing...")
        print("The server may not work correctly.")
    
    # Start the server
    start_server()

if __name__ == '__main__':
    main() 