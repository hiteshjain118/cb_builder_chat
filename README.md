# Chat

A Flask-based API server that uses the Builder library for conversational AI with **Supabase authentication**.

## Features

- **Supabase Authentication**: All API requests require valid Supabase JWT tokens
- **Intent Classification**: Uses Builder's intent classifier to understand user messages
- **Session Management**: Maintains conversation history per session
- **RESTful API**: Clean API endpoints for chat functionality
- **CORS Support**: Cross-origin request support for API integration
- **Secure**: Protected endpoints ensure only authenticated users can access the API

## ⚠️ Important: Authentication Required

**All API endpoints (except `/health`) now require authentication.** You must include a valid Supabase JWT token in the `Authorization` header for all requests.

### Quick Setup

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set environment variables**: Create a `.env` file with your Supabase credentials
3. **Run configuration check**: `python config.py`
4. **Start the server**: `python app.py`

For detailed authentication setup instructions, see [AUTHENTICATION.md](./AUTHENTICATION.md).

## API Endpoints

### POST `/api/chat` 🔒
Send a chat message and receive a response. **Requires authentication.**

**Headers:**
```
Authorization: Bearer <your-supabase-jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "message": "Hello, how are you?",
    "session_id": "session_123"
}
```

**Response:**
```json
{
    "message": "Hello! How can I help you today?",
    "intent": "greeting",
    "entities": {},
    "session_id": "session_123",
    "timestamp": "2025-08-07T11:30:00",
    "user_id": "authenticated-user-id"
}
```

### GET `/api/session/<session_id>/history` 🔒
Get conversation history for a session. **Requires authentication.**

**Headers:**
```
Authorization: Bearer <your-supabase-jwt-token>
```

**Response:**
```json
{
    "messages": [
        {
            "role": "user",
            "content": "Hello",
            "timestamp": "2025-08-07T11:30:00"
        },
        {
            "role": "assistant",
            "content": "Hello! How can I help you?",
            "timestamp": "2025-08-07T11:30:01"
        }
    ]
}
```

### GET `/health` ✅
Health check endpoint. **No authentication required.**

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-08-07T11:30:00"
}
```

## Installation

1. Navigate to the chat directory:
```bash
cd builder/chat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Set up Supabase authentication** (see [AUTHENTICATION.md](./AUTHENTICATION.md))

## Running the Application

1. **Verify your configuration**:
```bash
python config.py
```

2. Start the Flask server:
```bash
python app.py
```

3. The API will be available at:
```
http://localhost:5002
```

## Authentication

The Chat App uses Supabase for authentication. All API requests must include a valid JWT token in the `Authorization` header.

**Example with curl:**
```bash
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-supabase-token" \
  -d '{"message": "Hello", "session_id": "test"}'
```

**Example with JavaScript:**
```javascript
const response = await fetch('http://localhost:5002/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${supabaseToken}`
  },
  body: JSON.stringify({
    message: 'Hello, how are you?',
    session_id: 'user-session-123'
  })
});
```

## Environment Variables

**Required:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous/public key

**Optional:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o)
- `FLASK_ENV`: Flask environment (default: development)
- `PORT`: Server port (default: 5002)
- `HOST`: Server host (default: 0.0.0.0)

## Troubleshooting

- **Authentication errors**: Check your Supabase configuration and token validity
- **Missing environment variables**: Run `python config.py` to verify setup
- **Token validation issues**: Ensure your Supabase project is active and accessible

For detailed troubleshooting, see [AUTHENTICATION.md](./AUTHENTICATION.md). 