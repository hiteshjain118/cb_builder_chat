#!/usr/bin/env python3
"""
Demo Script for Supabase Authentication

This script demonstrates the new authentication functionality
in a simple, interactive way.
"""

import os
import sys
import subprocess

def print_header():
    """Print a nice header"""
    print("🚀 Chat App Terminal Interface - Authentication Demo")
    print("=" * 60)
    print()

def print_examples():
    """Print usage examples"""
    print("📚 Usage Examples:")
    print("-" * 30)
    
    examples = [
        ("Check app status", "./chat.sh --status"),
        ("Check environment config", "./chat.sh --check-env"),
        ("Send unauthenticated message (will fail)", './chat.sh "Hello"'),
        ("Send authenticated message (from .env)", './chat.sh "Hello" --login user@example.com --password mypass'),
        ("Get conversation history", "./chat.sh --history --login user@example.com --password mypass"),
        ("Custom session", './chat.sh "Hello" --session my-session --login user@example.com --password mypass'),
        ("Help", "./chat.sh --help"),
    ]
    
    for i, (desc, cmd) in enumerate(examples, 1):
        print(f"{i}. {desc}")
        print(f"   {cmd}")
        print()

def check_environment():
    """Check if environment variables are set"""
    print("🔍 Environment Check:")
    print("-" * 20)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        print("💡 Create .env file with your Supabase credentials")
    
    # Check if python-dotenv is available
    try:
        import dotenv
        print("✅ python-dotenv available")
    except ImportError:
        print("❌ python-dotenv not installed")
        print("💡 Install with: pip install python-dotenv")
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        print("✅ SUPABASE_URL: Set")
        print("✅ SUPABASE_ANON_KEY: Set")
        print(f"   Project: {supabase_url}")
        print(f"   Key: {supabase_key[:20]}...")
    else:
        print("❌ SUPABASE_URL: Not set")
        print("❌ SUPABASE_ANON_KEY: Not set")
        print("\n💡 You can set them with:")
        print("   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_ANON_KEY='your-anon-key'")
        print("\n💡 Or create a .env file:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_ANON_KEY=your-anon-key")
        print("\n💡 Or use command line arguments:")
        print("   --supabase-url and --supabase-key")
    
    print()

def interactive_demo():
    """Run an interactive demo"""
    print("🎯 Interactive Demo:")
    print("-" * 20)
    
    # Check if chat app is running
    print("1. Checking if chat app is running...")
    try:
        result = subprocess.run(["./chat.sh", "--status"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Chat app is running!")
        else:
            print("❌ Chat app is not running")
            print("💡 Start it with: python app.py")
            return
    except Exception as e:
        print(f"❌ Error checking app status: {e}")
        return
    
    # Check environment configuration
    print("\n2. Checking environment configuration...")
    try:
        result = subprocess.run(["./chat.sh", "--check-env"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Environment check completed")
        else:
            print("⚠️  Environment check had issues")
    except Exception as e:
        print(f"❌ Error checking environment: {e}")
    
    print("\n3. Testing unauthenticated request (should fail)...")
    try:
        result = subprocess.run(["./chat.sh", "Hello"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("✅ Unauthenticated request correctly failed (expected)")
        else:
            print("⚠️  Unauthenticated request succeeded (unexpected)")
    except Exception as e:
        print(f"❌ Error testing unauthenticated request: {e}")
    
    print("\n4. Ready for authenticated requests!")
    print("💡 Use: ./chat.sh \"Your message\" --login email@example.com --password yourpass")
    print("💡 Make sure your .env file is set up with SUPABASE_URL and SUPABASE_ANON_KEY")

def show_env_setup():
    """Show how to set up the .env file"""
    print("🔧 Environment Setup:")
    print("-" * 20)
    
    print("1. Create a .env file in the chat directory:")
    print("   touch .env")
    print()
    
    print("2. Add your Supabase credentials to .env:")
    print("   SUPABASE_URL=https://your-project.supabase.co")
    print("   SUPABASE_ANON_KEY=your-anon-key")
    print()
    
    print("3. Install python-dotenv if not already installed:")
    print("   pip install python-dotenv")
    print()
    
    print("4. Test your configuration:")
    print("   ./chat.sh --check-env")
    print()

def main():
    """Main demo function"""
    print_header()
    
    # Check environment
    check_environment()
    
    # Show environment setup
    show_env_setup()
    
    # Show examples
    print_examples()
    
    # Interactive demo
    interactive_demo()
    
    print("\n🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   1. Set up your .env file with Supabase credentials")
    print("   2. Install python-dotenv: pip install python-dotenv")
    print("   3. Check configuration: ./chat.sh --check-env")
    print("   4. Try sending an authenticated message")
    print("   5. Check conversation history")
    print("   6. Use custom sessions for different conversations")
    print("\n🔗 For more help: ./chat.sh --help")

if __name__ == "__main__":
    main() 