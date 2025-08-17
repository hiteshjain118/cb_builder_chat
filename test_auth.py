#!/usr/bin/env python3
"""
Test Script for Supabase Authentication

This script demonstrates how to use the new authentication functionality
in the send_message.py script.
"""

import os
import sys
import subprocess
from getpass import getpass

def run_command(cmd, description):
    """Run a command and display the result"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print(f"{'-'*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        print(f"Exit Code: {result.returncode}")
        print(f"Output:")
        print(result.stdout)
        if result.stderr:
            print(f"Errors:")
            print(result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without authentication"""
    print("\n🚀 Testing Basic Functionality")
    print("=" * 50)
    
    # Test app status
    success = run_command("./chat.sh --status", "Check if chat app is running")
    if not success:
        print("❌ Chat app is not running. Please start it first.")
        return False
    
    # Test unauthenticated message (should fail)
    run_command('./chat.sh "Hello, this should fail without auth"', "Send unauthenticated message (expected to fail)")
    
    return True

def test_authentication():
    """Test authentication functionality"""
    print("\n🔐 Testing Authentication")
    print("=" * 50)
    
    # Check if environment variables are set
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("⚠️  SUPABASE_URL and SUPABASE_ANON_KEY environment variables not set")
        print("💡 You can set them or use command line arguments")
        
        # Ask user for credentials
        print("\n🔑 Enter Supabase credentials:")
        supabase_url = input("Supabase URL: ").strip()
        supabase_key = input("Supabase Anonymous Key: ").strip()
        
        if not supabase_url or not supabase_key:
            print("❌ Credentials required for authentication tests")
            return False
    else:
        print("✅ Environment variables found")
        print(f"   URL: {supabase_url}")
        print(f"   Key: {supabase_key[:20]}...")
    
    # Get user credentials
    print("\n👤 Enter your Supabase user credentials:")
    email = input("Email: ").strip()
    password = getpass("Password: ")
    
    if not email or not password:
        print("❌ Email and password required")
        return False
    
    # Test authentication with email/password
    auth_cmd = f'./chat.sh "Test authenticated message" --login "{email}" --password "{password}"'
    success = run_command(auth_cmd, "Send authenticated message using email/password")
    
    if success:
        print("✅ Authentication successful!")
        
        # Test conversation history
        history_cmd = f'./chat.sh --history --login "{email}" --password "{password}"'
        run_command(history_cmd, "Get conversation history with authentication")
        
        # Test custom session
        session_cmd = f'./chat.sh "Test custom session" --session "test-auth-session" --login "{email}" --password "{password}"'
        run_command(session_cmd, "Send message to custom session with authentication")
        
    else:
        print("❌ Authentication failed")
        return False
    
    return True

def test_help_and_options():
    """Test help and command line options"""
    print("\n📖 Testing Help and Options")
    print("=" * 50)
    
    # Test help
    run_command("./chat.sh --help", "Display help information")
    
    # Test Python script help
    run_command("python send_message.py --help", "Display Python script help")

def main():
    """Main test function"""
    print("🧪 Chat App Terminal Interface - Authentication Test Suite")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists("chat.sh") or not os.path.exists("send_message.py"):
        print("❌ Error: This script must be run from the chat directory")
        print("💡 Please cd to the chat directory and try again")
        sys.exit(1)
    
    # Check if chat.sh is executable
    if not os.access("chat.sh", os.X_OK):
        print("⚠️  Making chat.sh executable...")
        os.chmod("chat.sh", 0o755)
    
    # Run tests
    print("\n🔍 Starting tests...")
    
    # Test 1: Basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality test failed. Please check your setup.")
        return
    
    # Test 2: Authentication
    if not test_authentication():
        print("\n❌ Authentication test failed. Please check your credentials.")
        return
    
    # Test 3: Help and options
    test_help_and_options()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Next steps:")
    print("   1. Use './chat.sh --help' to see all options")
    print("   2. Try sending messages with: './chat.sh \"Your message\" --login email@example.com --password yourpass'")
    print("   3. Check conversation history with: './chat.sh --history --login email@example.com --password yourpass'")
    print("   4. Use custom sessions for different conversations")

if __name__ == "__main__":
    main() 