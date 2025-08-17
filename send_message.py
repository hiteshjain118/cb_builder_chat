#!/usr/bin/env python3
"""
Chat App Message Sender Script

This script allows you to send messages to the chat app from your terminal.
It supports both authenticated and unauthenticated requests for testing purposes.
"""

import requests
import json
import argparse
import sys
import os
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("💡 Environment variables must be set manually")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")

# Default configuration
DEFAULT_CHAT_URL = "http://localhost:5002"
DEFAULT_SESSION_ID = "terminal-session"

def get_supabase_token(email, password, supabase_url, supabase_anon_key):
    """
    Get authentication token from Supabase using email and password
    
    Args:
        email (str): User email
        password (str): User password
        supabase_url (str): Supabase project URL
        supabase_anon_key (str): Supabase anonymous key
    
    Returns:
        str: JWT token if successful, None otherwise
    """
    
    try:
        print(f"🔐 Authenticating with Supabase...")
        print(f"📧 Email: {email}")
        print(f"🌐 URL: {supabase_url}")
        
        # Supabase auth endpoint
        auth_url = f"{supabase_url}/auth/v1/token?grant_type=password"
        
        headers = {
            "Content-Type": "application/json",
            "apikey": supabase_anon_key,
            "Authorization": f"Bearer {supabase_anon_key}"
        }
        
        payload = {
            "email": email,
            "password": password
        }
        
        response = requests.post(auth_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print(f"✅ Authentication successful!")
                print(f"🔑 Token obtained (length: {len(token)})")
                
                # Get user info
                user_info = data.get('user', {})
                if user_info:
                    print(f"👤 User ID: {user_info.get('id', 'N/A')}")
                    print(f"📧 Email: {user_info.get('email', 'N/A')}")
                
                return token
            else:
                print(f"❌ No access token in response")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                print(f"🔍 Error: {error_msg}")
            except:
                print(f"🔍 Error Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to Supabase")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error: Authentication request took too long")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return None

def send_message(message, session_id=None, user_id=None, auth_token=None, chat_url=None):
    """
    Send a message to the chat app
    
    Args:
        message (str): The message to send
        session_id (str): Session ID for the conversation
        user_id (str): User ID (optional)
        auth_token (str): Supabase JWT token for authentication
        chat_url (str): Base URL of the chat app
    
    Returns:
        dict: Response from the chat app
    """
    
    # Set defaults
    session_id = session_id or DEFAULT_SESSION_ID
    chat_url = chat_url or DEFAULT_CHAT_URL
    
    # Prepare the request
    url = f"{chat_url}/api/chat"
    payload = {
        "message": message,
        "session_id": session_id
    }
    
    if user_id:
        payload["user_id"] = user_id
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add authentication if token provided
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        print(f"🔐 Sending authenticated request...")
    else:
        print(f"⚠️  Sending unauthenticated request (will likely fail with 401)")
    
    try:
        print(f"📤 Sending message to: {url}")
        print(f"💬 Message: {message}")
        print(f"🆔 Session: {session_id}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"🤖 Assistant Response: {data.get('message', 'No response')}")
            print(f"🆔 Session ID: {data.get('session_id', 'N/A')}")
            print(f"👤 User ID: {data.get('user_id', 'N/A')}")
            print(f"⏰ Timestamp: {data.get('timestamp', 'N/A')}")
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Error Details: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"🔍 Error Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {chat_url}")
        print(f"💡 Make sure the chat app is running on {chat_url}")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error: Request took too long")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return None

def get_conversation_history(session_id, auth_token=None, chat_url=None):
    """
    Get conversation history for a session
    
    Args:
        session_id (str): Session ID to get history for
        auth_token (str): Supabase JWT token for authentication
        chat_url (str): Base URL of the chat app
    
    Returns:
        dict: Conversation history
    """
    
    chat_url = chat_url or DEFAULT_CHAT_URL
    url = f"{chat_url}/api/session/{session_id}/history"
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        print(f"🔐 Getting authenticated history...")
    else:
        print(f"⚠️  Getting unauthenticated history (will likely fail with 401)")
    
    try:
        print(f"📚 Getting conversation history for session: {session_id}")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            print(f"✅ Found {len(messages)} messages in history")
            
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', 'No content')
                timestamp = msg.get('timestamp', 'No timestamp')
                print(f"  {i}. [{role.upper()}] {content}")
                print(f"     ⏰ {timestamp}")
                print()
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Error Details: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"🔍 Error Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting history: {str(e)}")
        return None

def check_app_status(chat_url=None):
    """
    Check if the chat app is running and get basic info
    
    Args:
        chat_url (str): Base URL of the chat app
    
    Returns:
        bool: True if app is running, False otherwise
    """
    
    chat_url = chat_url or DEFAULT_CHAT_URL
    
    try:
        print(f"🔍 Checking chat app status at: {chat_url}")
        
        # Check health endpoint
        health_url = f"{chat_url}/health"
        health_response = requests.get(health_url, timeout=10)
        
        if health_response.status_code == 200:
            print(f"✅ Health check passed")
            
            # Get API info
            info_url = f"{chat_url}/"
            info_response = requests.get(info_url, timeout=10)
            
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"📋 API Info:")
                print(f"   Name: {info.get('name', 'N/A')}")
                print(f"   Version: {info.get('version', 'N/A')}")
                print(f"   Description: {info.get('description', 'N/A')}")
                
                auth_info = info.get('authentication', {})
                if auth_info:
                    print(f"🔐 Authentication:")
                    print(f"   Type: {auth_info.get('type', 'N/A')}")
                    print(f"   Method: {auth_info.get('method', 'N/A')}")
                    print(f"   Header: {auth_info.get('header', 'N/A')}")
                
                return True
            else:
                print(f"⚠️  Could not get API info")
                return True
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {chat_url}")
        print(f"💡 Make sure the chat app is running on {chat_url}")
        return False
    except Exception as e:
        print(f"❌ Error checking status: {str(e)}")
        return False

def check_env_config():
    """
    Check and display environment configuration
    """
    print("🔍 Environment Configuration:")
    print("-" * 30)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        print("✅ SUPABASE_URL: Set")
        print("✅ SUPABASE_ANON_KEY: Set")
        print(f"   Project: {supabase_url}")
        print(f"   Key: {supabase_key[:20]}...")
        return True
    else:
        print("❌ SUPABASE_URL: Not set")
        print("❌ SUPABASE_ANON_KEY: Not set")
        print("\n💡 Create a .env file with:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_ANON_KEY=your-anon-key")
        print("\n💡 Or set environment variables manually:")
        print("   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_ANON_KEY='your-anon-key'")
        return False

def main():
    """Main function to handle command line arguments"""
    
    parser = argparse.ArgumentParser(
        description="Send messages to the Chat App from terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send a simple message
  python send_message.py "Hello, how are you?"
  
  # Send message with custom session
  python send_message.py "What's the weather?" --session weather-chat
  
  # Send authenticated message using Supabase login (from .env)
  python send_message.py "Show me my data" --login user@example.com --password mypass
  
  # Send authenticated message with existing token
  python send_message.py "Show me my data" --token your-jwt-token
  
  # Get conversation history
  python send_message.py --history --session my-session --login user@example.com --password mypass
  
  # Check app status
  python send_message.py --status
  
  # Check environment configuration
  python send_message.py --check-env
  
  # Use custom chat app URL
  python send_message.py "Hello" --url http://localhost:5003
  
  # Use custom Supabase URL (overrides .env)
  python send_message.py "Hello" --supabase-url https://your-project.supabase.co --supabase-key your-key
        """
    )
    
    parser.add_argument("message", nargs="?", help="Message to send to the chat app")
    parser.add_argument("--session", "-s", default=DEFAULT_SESSION_ID, 
                       help=f"Session ID (default: {DEFAULT_SESSION_ID})")
    parser.add_argument("--user", "-u", help="User ID")
    parser.add_argument("--token", "-t", help="Supabase JWT token for authentication")
    parser.add_argument("--url", default=DEFAULT_CHAT_URL, 
                       help=f"Chat app URL (default: {DEFAULT_CHAT_URL})")
    
    # Supabase authentication options
    parser.add_argument("--login", "-l", help="Supabase user email for authentication")
    parser.add_argument("--password", "-p", help="Supabase user password for authentication")
    parser.add_argument("--supabase-url", help="Supabase project URL (overrides .env)")
    parser.add_argument("--supabase-key", help="Supabase anonymous key (overrides .env)")
    
    parser.add_argument("--history", action="store_true", 
                       help="Get conversation history instead of sending message")
    parser.add_argument("--status", action="store_true", 
                       help="Check chat app status")
    parser.add_argument("--check-env", action="store_true", 
                       help="Check environment configuration")
    
    args = parser.parse_args()
    
    # Check environment configuration if requested
    if args.check_env:
        check_env_config()
        return
    
    # Check app status if requested
    if args.status:
        check_app_status(args.url)
        return
    
    # Get Supabase credentials from environment or command line
    supabase_url = args.supabase_url or os.getenv('SUPABASE_URL')
    supabase_key = args.supabase_key or os.getenv('SUPABASE_ANON_KEY')
    
    # Get authentication token if login credentials provided
    auth_token = args.token
    if args.login and args.password:
        if not supabase_url or not supabase_key:
            print("❌ Error: Supabase URL and key are required for authentication")
            print("💡 Set them in your .env file or use --supabase-url and --supabase-key arguments")
            print("\n💡 Example .env file:")
            print("   SUPABASE_URL=https://your-project.supabase.co")
            print("   SUPABASE_ANON_KEY=your-anon-key")
            sys.exit(1)
        
        auth_token = get_supabase_token(args.login, args.password, supabase_url, supabase_key)
        if not auth_token:
            print("❌ Failed to get authentication token")
            sys.exit(1)
    
    # Get history if requested
    if args.history:
        get_conversation_history(args.session, auth_token, args.url)
        return
    
    # Send message if provided
    if args.message:
        send_message(args.message, args.session, args.user, auth_token, args.url)
    else:
        print("❌ No message provided. Use --help for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main() 