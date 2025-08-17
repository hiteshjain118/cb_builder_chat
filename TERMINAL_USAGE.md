# Chat App Terminal Interface

This directory contains scripts that allow you to interact with the Chat App directly from your terminal.

## Quick Start

### 1. **Check if the app is running**
```bash
./chat.sh --status
```

### 2. **Check environment configuration**
```bash
./chat.sh --check-env
```

### 3. **Send a simple message**
```bash
./chat.sh "Hello, how are you?"
```

### 4. **Send authenticated message using Supabase login**
```bash
./chat.sh "Show me my data" --login user@example.com --password mypass
```

### 5. **Get conversation history**
```bash
./chat.sh --history --login user@example.com --password mypass
```

## Available Scripts

### **`send_message.py`** - Python script for sending messages
- Full-featured message sender
- **Supabase authentication** with email/password
- **Automatic .env file loading** with python-dotenv
- Supports all command line options
- Can be run directly with Python

### **`chat.sh`** - Shell script wrapper
- Easy-to-use interface
- Automatically activates virtual environment
- Colored output for better readability
- **Built-in authentication support**
- **Environment configuration checking**

## Environment Setup

### **1. Install python-dotenv**
```bash
pip install python-dotenv
```

### **2. Create .env file**
Create a `.env` file in the chat directory:
```bash
# .env file
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### **3. Check configuration**
```bash
./chat.sh --check-env
```

## Usage Examples

### **Basic Message Sending**
```bash
# Send a simple message
./chat.sh "Hello, how are you?"

# Send message with custom session
./chat.sh "What's the weather?" --session weather-chat

# Send message with custom user ID
./chat.sh "Show me my data" --user user123
```

### **Supabase Authentication (Recommended)**

#### **Using Email and Password (from .env file)**
```bash
# Send message with Supabase login (uses .env credentials)
./chat.sh "Show me my data" --login user@example.com --password mypass

# Get authenticated conversation history
./chat.sh --history --session my-session --login user@example.com --password mypass

# Custom session with authentication
./chat.sh "Analyze my data" --session analysis-session --login user@example.com --password mypass
```

#### **Using Existing JWT Token**
```bash
# Send message with existing token
./chat.sh "Show me my data" --token "your-jwt-token-here"

# Get authenticated conversation history
./chat.sh --history --session my-session --token "your-jwt-token-here"
```

#### **Custom Supabase Project (overrides .env)**
```bash
# Use different Supabase project
./chat.sh "Hello" --supabase-url https://your-project.supabase.co --supabase-key your-key --login user@example.com --password mypass
```

### **App Management**
```bash
# Check if the app is running
./chat.sh --status

# Check environment configuration
./chat.sh --check-env

# Check app at different URL
./chat.sh --status --url http://localhost:5003
```

### **Advanced Usage**
```bash
# Send message to different chat app instance
./chat.sh "Hello" --url http://localhost:5003

# Custom session with authentication
./chat.sh "Analyze my data" --session analysis-session --user analyst --login user@example.com --password mypass
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--session` | `-s` | Session ID for conversation | `terminal-session` |
| `--user` | `-u` | User ID | None |
| `--token` | `-t` | Supabase JWT token | None |
| `--login` | `-l` | **Supabase user email for authentication** | None |
| `--password` | `-p` | **Supabase user password for authentication** | None |
| `--url` | | Chat app URL | `http://localhost:5002` |
| `--supabase-url` | | **Supabase project URL (overrides .env)** | From .env file |
| `--supabase-key` | | **Supabase anonymous key (overrides .env)** | From .env file |
| `--history` | | Get conversation history | False |
| `--status` | | Check chat app status | False |
| `--check-env` | | **Check environment configuration (.env file)** | False |
| `--help` | `-h` | Show help message | False |

## Authentication Methods

### **1. Email/Password Authentication (Recommended)**
- **Most secure**: Credentials are not stored
- **Automatic token management**: Gets fresh token for each request
- **User-friendly**: No need to manage JWT tokens manually
- **Environment variables**: Uses `.env` file or `SUPABASE_URL` and `SUPABASE_ANON_KEY`

```bash
# Set up .env file (recommended)
# .env file contents:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Use login/password (automatically uses .env)
./chat.sh "Hello" --login user@example.com --password mypass
```

### **2. JWT Token Authentication**
- **Manual management**: You provide the token
- **Reusable**: Same token for multiple requests
- **Less secure**: Token stored in command history
- **Good for**: Testing, automation, when you already have a token

```bash
./chat.sh "Hello" --token "your-jwt-token"
```

### **3. No Authentication**
- **Requests will fail**: 401 Unauthorized expected
- **Useful for**: Testing authentication requirements
- **Good for**: Development and debugging

```bash
./chat.sh "Hello"  # Will fail with 401
```

## Environment Configuration

### **Required for Authentication**
```bash
# .env file (recommended)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Or set in shell
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
```

### **Optional Override**
```bash
# Override .env file with command line arguments
./chat.sh "Hello" \
  --supabase-url "https://different-project.supabase.co" \
  --supabase-key "different-key" \
  --login user@example.com \
  --password mypass
```

### **Environment Checking**
```bash
# Check your .env configuration
./chat.sh --check-env

# Check with Python script directly
python send_message.py --check-env
```

## Session Management

### **Default Session**
- Uses `terminal-session` by default
- All messages in one conversation thread
- Good for testing and development

### **Custom Sessions**
- Create separate conversation threads
- Useful for different topics or users
- Example: `--session "customer-support"`

## Error Handling

The scripts provide clear error messages:

- **Connection Errors**: App not running or wrong URL
- **Authentication Errors**: Missing or invalid credentials
- **Supabase Errors**: Invalid project URL or key
- **Environment Errors**: Missing .env file or python-dotenv
- **Timeout Errors**: Request took too long
- **API Errors**: Server-side issues

## Development Workflow

### **1. Start the Chat App**
```bash
python app.py
```

### **2. Test Basic Connectivity**
```bash
./chat.sh --status
```

### **3. Check Environment Configuration**
```bash
./chat.sh --check-env
```

### **4. Test Authentication**
```bash
# This should fail (no auth)
./chat.sh "Hello"

# This should work (with Supabase login from .env)
./chat.sh "Hello" --login user@example.com --password mypass

# This should also work (with existing token)
./chat.sh "Hello" --token "your-jwt-token"
```

### **5. Test Chat Functionality**
```bash
# Send a message
./chat.sh "Can you help me analyze my QuickBooks data?" --login user@example.com --password mypass

# Check history
./chat.sh --history --login user@example.com --password mypass
```

## Troubleshooting

### **"Connection Error"**
- Make sure the chat app is running
- Check the URL (default: http://localhost:5002)
- Verify the port is correct

### **"401 Unauthorized"**
- Include valid Supabase credentials
- Check if your password is correct
- Verify the Supabase project URL and key
- Ensure the user exists in your Supabase project

### **"Supabase URL and key are required"**
- Create a `.env` file with your credentials
- Or set `SUPABASE_URL` and `SUPABASE_ANON_KEY` environment variables
- Or use `--supabase-url` and `--supabase-key` arguments
- Check your `.env` file format and content

### **"python-dotenv not installed"**
- Install python-dotenv: `pip install python-dotenv`
- Or set environment variables manually
- Or use command line arguments for Supabase credentials

### **"Authentication failed"**
- Verify email and password are correct
- Check if the user exists in Supabase
- Ensure the user has the correct permissions
- Check Supabase project status

### **"Python script not found"**
- Make sure you're in the chat directory
- Check if `send_message.py` exists
- Verify file permissions

### **"Virtual environment not found"**
- The script will work without a virtual environment
- For best results, activate your virtual environment manually:
  ```bash
  source venv/bin/activate
  ./chat.sh "Hello" --login user@example.com --password mypass
  ```

## Integration with Other Tools

### **cURL Alternative**
```bash
# Instead of complex cURL with authentication:
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"message": "Hello", "session_id": "test"}'

# Use simple command:
./chat.sh "Hello" --session test --login user@example.com --password mypass
```

### **Scripting and Automation**
```bash
#!/bin/bash
# Example automation script with .env file

# Load environment variables from .env
source .env

# Check app status
if ./chat.sh --status; then
    echo "App is running, sending message..."
    
    # Send message with authentication from .env
    response=$(./chat.sh "Process my data" --login "$USER_EMAIL" --password "$USER_PASSWORD")
    
    if [ $? -eq 0 ]; then
        echo "Message sent successfully"
    else
        echo "Failed to send message"
    fi
else
    echo "App is not running"
fi
```

### **Environment File Setup**
```bash
# .env file
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Load in shell
source .env

# Use in scripts
./chat.sh "Hello" --login user@example.com --password mypass
```

## Security Best Practices

### **Credentials Management**
- **Use .env files** for local development
- **Never commit** credentials to version control
- **Use environment variables** for production
- **Rotate passwords** regularly
- **Use strong passwords** for Supabase accounts

### **Token Security**
- **Don't share** JWT tokens
- **Monitor token usage** for suspicious activity
- **Tokens expire** - use email/password for fresh tokens
- **Clear command history** if tokens were used

### **Network Security**
- **Use HTTPS** for production Supabase projects
- **Verify project URLs** before entering credentials
- **Check SSL certificates** for validity

## Support

If you encounter issues:

1. **Check the app logs** for detailed error messages
2. **Verify your .env file** configuration (SUPABASE_URL, SUPABASE_ANON_KEY)
3. **Test with the `--check-env` command** to verify configuration
4. **Check authentication requirements** and credentials
5. **Review the error messages** in the script output
6. **Test Supabase connection** with a simple browser request
7. **Ensure python-dotenv is installed** for .env file support

## Common Use Cases

### **Development Testing**
```bash
# Test unauthenticated requests
./chat.sh "Hello"  # Should fail with 401

# Test authenticated requests
./chat.sh "Hello" --login dev@example.com --password devpass

# Test different sessions
./chat.sh "Test message" --session dev-test --login dev@example.com --password devpass
```

### **Production Monitoring**
```bash
# Check app health
./chat.sh --status

# Send test message
./chat.sh "Health check" --login admin@example.com --password adminpass

# Monitor conversation history
./chat.sh --history --session monitoring --login admin@example.com --password adminpass
```

### **User Support**
```bash
# Create support session
./chat.sh "I need help with my data" --session support-123 --login user@example.com --password userpass

# Continue support conversation
./chat.sh "Can you show me the error logs?" --session support-123 --login user@example.com --password userpass
``` 