# Chat

A Flask-based API server that uses the Builder library for conversational AI.

## Features

- **Intent Classification**: Uses Builder's intent classifier to understand user messages
- **Session Management**: Maintains conversation history per session
- **RESTful API**: Clean API endpoints for chat functionality
- **CORS Support**: Cross-origin request support for API integration

## API Endpoints

### POST `/api/chat`
Send a chat message and receive a response.

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
    "timestamp": "2025-08-07T11:30:00"
}
```

### GET `/api/session/<session_id>/history`
Get conversation history for a session.

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

### POST `/api/session/<session_id>/clear`
Clear conversation history for a session.

**Response:**
```json
{
    "message": "History cleared successfully"
}
```

### GET `/health`
Health check endpoint.

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

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. The API will be available at:
```
http://localhost:5002
```

## Configuration

The application uses the following default settings:
- **Host**: 0.0.0.0
- **Port**: 5002
- **Debug Mode**: Enabled

You can modify these settings in `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
```

## Architecture

### Components

1. **Flask App** (`app.py`): Main application with API endpoints
2. **Builder Integration**: Uses the Builder library for intent classification
3. **Memory Management**: Session-based conversation memory

### Flow

1. Client sends message to `/api/chat` endpoint
2. Builder's intent classifier processes the message
3. Response is generated based on classified intent
4. Response is sent back to client
5. Conversation history is maintained in memory

## Development

### Adding New Intents

To add new intents, modify the `generate_response()` function in `app.py`:

```python
def generate_response(classification_result, user_message):
    intent = classification_result.get('intent', 'unknown')
    
    if intent == 'new_intent':
        return "Response for new intent"
    # ... existing code
```

### API Usage Examples

```bash
# Send a chat message
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test_session"}'

# Get conversation history
curl http://localhost:5002/api/session/test_session/history

# Clear conversation history
curl -X POST http://localhost:5002/api/session/test_session/clear
```

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Builder Library**: Core AI functionality (editable dependency)

## Production Deployment

For production deployment:

1. **Database**: Replace in-memory storage with a proper database
2. **Authentication**: Add user authentication
3. **Rate Limiting**: Implement API rate limiting
4. **Logging**: Add comprehensive logging
5. **Environment Variables**: Use environment variables for configuration
6. **WSGI Server**: Use a production WSGI server like Gunicorn

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 app:app
``` 