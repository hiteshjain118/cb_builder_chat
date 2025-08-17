# Supabase Authentication Setup for Chat App

This document explains how to set up and use Supabase authentication with the Chat App using **public key validation**.

## Overview

The Chat App now requires authentication for all API endpoints (except `/health` and `/debug/auth`). Users must provide a valid Supabase JWT token in the `Authorization` header for all requests. The app uses **direct JWT validation with public keys** from Supabase's JWKS endpoint for efficient and secure authentication.

## 🔑 Key Benefits of Public Key Validation

- **⚡ Faster Authentication**: No network calls to Supabase for each token validation
- **🔄 Automatic Key Management**: Public keys are cached and refreshed automatically
- **🛡️ Enhanced Security**: Local JWT validation with cryptographic verification
- **📡 Reduced Dependencies**: Works even if Supabase is temporarily unavailable
- **🏭 Production Ready**: Industry-standard JWT validation approach

## Prerequisites

1. A Supabase project (create one at [supabase.com](https://supabase.com))
2. Python 3.8+ with pip
3. The required Python packages (see `requirements.txt`)

## Setup Steps

### 1. Install Dependencies

```bash
cd chat
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `chat` directory with the following variables:

```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# OpenAI Configuration (OPTIONAL)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o

# Flask Configuration (OPTIONAL)
FLASK_ENV=development
PORT=5002
HOST=0.0.0.0
```

**Important**: Replace `your-project-id` and `your-anon-key-here` with your actual Supabase project values.

### 3. Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the **Project URL** and **anon/public key**
4. Paste them in your `.env` file

### 4. Verify Configuration

Run the configuration check:

```bash
python config.py
```

This will verify that all required environment variables are set correctly.

## How It Works

### 1. **Initialization**
- App fetches public keys from Supabase's JWKS endpoint (`/auth/v1/jwks`)
- Keys are converted from JWK format to PEM format
- Keys are cached locally for 1 hour

### 2. **Token Validation**
- JWT token header is decoded to extract the key ID (`kid`)
- Corresponding public key is retrieved from cache
- Token is verified using the public key with RS256 algorithm
- User information is extracted from the verified payload

### 3. **Key Refresh**
- Public keys are automatically refreshed every hour
- Failed refresh attempts don't clear existing cache
- App continues working with cached keys during network issues

## Usage

### Frontend Integration

When making requests to the Chat App API, include the Supabase JWT token in the `Authorization` header:

```javascript
// Example using fetch
const response = await fetch('http://localhost:5002/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${supabaseToken}` // Your Supabase JWT token
  },
  body: JSON.stringify({
    message: 'Hello, how are you?',
    session_id: 'user-session-123'
  })
});
```

### API Endpoints

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/` | GET | ❌ | API information and documentation |
| `/health` | GET | ❌ | Health check |
| `/debug/auth` | GET | ❌ | Authentication debug information |
| `/api/chat` | POST | ✅ | Send chat message |
| `/api/session/<id>/history` | GET | ✅ | Get conversation history |

### Authentication Flow

1. **User signs in** to your frontend application using Supabase Auth
2. **Frontend receives** a JWT token from Supabase
3. **Frontend includes** the token in the `Authorization: Bearer <token>` header
4. **Chat App validates** the token using cached public keys
5. **If valid**, the request proceeds and user info is available in `request.user`
6. **If invalid**, a 401 Unauthorized response is returned

## Debugging and Monitoring

### Debug Endpoint

The `/debug/auth` endpoint provides real-time information about the authentication system:

```bash
curl http://localhost:5002/debug/auth
```

Response includes:
- Cache status and key count
- Last refresh time
- Supabase URL configuration
- Cache age and TTL settings

### Logging

The authentication middleware provides detailed logging:
- Key caching and refresh events
- Token validation results
- Error details for debugging

## Error Handling

### Common Authentication Errors

- **401 Unauthorized**: Missing or invalid Authorization header
- **401 Unauthorized**: Invalid or expired JWT token
- **401 Unauthorized**: Token signature verification failed
- **500 Internal Server Error**: Authentication middleware initialization failure

### Error Response Format

```json
{
  "error": "Description of the error"
}
```

## Security Considerations

1. **Public Key Validation**: Uses industry-standard JWT validation with RSA public keys
2. **Key Rotation**: Automatically handles Supabase key rotation
3. **Cache Security**: Public keys are read-only and cannot be used for signing
4. **Algorithm Enforcement**: Only accepts RS256 (RSA with SHA-256) tokens
5. **Audience Validation**: Verifies token audience matches 'authenticated'
6. **Issuer Validation**: Ensures tokens are issued by your Supabase project

## Performance Optimization

### Caching Strategy

- **Public Keys**: Cached for 1 hour to reduce JWKS requests
- **Token Validation**: Local cryptographic verification (no network calls)
- **Automatic Refresh**: Background refresh prevents cache expiration

### Network Efficiency

- **Initial Load**: One JWKS request on startup
- **Subsequent Validations**: Zero network calls
- **Fallback**: Continues working with cached keys during network issues

## Development vs Production

### Development Mode

- Authentication errors are logged but don't crash the app
- Useful for testing without full Supabase setup
- Cache TTL can be reduced for testing

### Production Mode

- Authentication middleware initialization failures crash the app
- Ensures security is enforced
- Optimized cache TTL for production workloads

Set `FLASK_ENV=production` in production environments.

## Troubleshooting

### "Authentication middleware not initialized"

- Check that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set correctly
- Verify your Supabase project is active and accessible
- Check the logs for specific error messages

### "Could not fetch public key for kid"

- Ensure your Supabase project is accessible
- Check network connectivity to Supabase
- Verify the JWKS endpoint is accessible

### "Token signature verification failed"

- Ensure the token is fresh (not expired)
- Verify the token was issued by your Supabase project
- Check that the token uses RS256 algorithm

### "Authorization header missing"

- Ensure your frontend is sending the `Authorization` header
- Check the header format: `Authorization: Bearer <token>`
- Verify the token is not empty

## Testing Authentication

### Test with curl

```bash
# This will fail without authentication
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'

# This will work with a valid token
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-supabase-token" \
  -d '{"message": "Hello", "session_id": "test"}'
```

### Test Authentication System

```bash
# Run the comprehensive test suite
python test_auth.py

# Check debug information
curl http://localhost:5002/debug/auth
```

### Test with Postman

1. Set the `Authorization` header to `Bearer your-token`
2. Send requests to protected endpoints
3. Verify you get user information in the response

## Advanced Configuration

### Customizing Cache TTL

You can modify the cache TTL in `auth_middleware.py`:

```python
self.jwks_cache_ttl = 3600  # Cache JWKS for 1 hour
```

### Adding Custom Claims Validation

Extend the `verify_token` method to validate additional claims:

```python
# Example: Validate custom role
if payload.get('role') not in ['user', 'admin']:
    return None
```

## Support

If you encounter issues:

1. Check the application logs for detailed error messages
2. Verify your Supabase configuration with `python config.py`
3. Test the authentication system with `python test_auth.py`
4. Check debug information at `/debug/auth` endpoint
5. Ensure your Supabase project is active and accessible

## Migration from Client-Based Validation

If you were previously using the Supabase client for validation:

1. **No code changes required** - the API remains the same
2. **Better performance** - no network calls for validation
3. **Enhanced reliability** - works during network issues
4. **Improved security** - cryptographic verification with public keys 