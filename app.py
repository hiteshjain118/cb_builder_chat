#!/usr/bin/env python3
"""
Builder Web - Flask Chat Application

A web-based chat interface that uses the builder library for conversational AI
"""

# Setup logging configuration FIRST, before any other imports
from builder_package.core.logging_config import setup_logging
setup_logging()

import traceback
from default.agent_building_server import AgentBuildingServer
from default.retreiver_building_server import RetrieverBuildingServer
from default.qb_server import QBServer
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import time
from datetime import datetime
import os

# Import builder components
from builder_package.core.intent_classifier import IntentClassifier
from builder_package.core.tod_types import IntentServerInput, INTENT_REGISTRY
from builder_package.core.memory import STMemory
from builder_package.core.structs import TMessage
from builder_package.core.enums import IntentName
from builder_package.model_providers.gpt_provider import GPTProvider

# Get logger for this module
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the model provider and intent classifier
# Using mock provider for testing

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "your-openai-api-key-here"
)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


model_provider = GPTProvider(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
intent_classifier = IntentClassifier(model_provider)
INTENT_REGISTRY.register(IntentName.AGENT_BUILDING, AgentBuildingServer(model_provider))
INTENT_REGISTRY.register(IntentName.RETRIEVER_BUILDING, RetrieverBuildingServer(model_provider))
INTENT_REGISTRY.register(IntentName.QB, QBServer(model_provider))
# Store conversation memory (in production, use a proper database)
conversation_memory = {}

@app.route('/')
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'Chat API',
        'description': 'Builder library conversational AI API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/chat': 'Send a chat message',
            'GET /api/session/<id>/history': 'Get conversation history',
            'GET /health': 'Health check'
        },
        'usage': {
            'example': 'curl -X POST http://localhost:5002/api/chat -H "Content-Type: application/json" -d \'{"message": "Hello", "session_id": "test"}\''
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        user_id = data.get('user_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        logger.info(f"Received message from user {user_id} in session {session_id}: {user_message}")
        
        # Get or create conversation memory for this session
        if session_id not in conversation_memory:
            conversation_memory[session_id] = STMemory(
                user_id=user_id, 
                conversation_history=[], 
                slots={}
            )
        
        memory = conversation_memory[session_id]
        
        # Create user message
        user_turn = TMessage(
            role="user",
            content=user_message,
            intent=IntentName.OTHER,
            timestamp=int(time.time()),
            slots={}
        )
        
        # Add to memory
        memory.add_message(user_turn)
        
        # Classify intent
        input_data = IntentServerInput(
            st_memory=memory, 
            user_turn=user_turn,
            user_id=user_id
        )


        # classification_result = intent_classifier.classify_with_entities(input_data)
        
        # Generate response based on intent
        # response = generate_response(classification_result, user_message)
        
        intent_server = INTENT_REGISTRY.server(IntentName.QB)
        response = intent_server.serve(input_data)
        # Create assistant message
        assistant_turn = TMessage(
            role="assistant",
            content=response,
            intent=IntentName.OTHER,
            timestamp=int(time.time()),
            slots={}
        )
        
        # Add to memory
        memory.add_message(assistant_turn)
        
        # Prepare response
        response_data = {
            'message': response,
            # 'intent': intent_server.my_intent,
            'entities': {},
            'session_id': session_id,
            'timestamp': int(time.time())
        }
        
        logger.info(f"Response for session {session_id}: {response}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/session/<session_id>/history', methods=['GET'])
def get_history(session_id):
    """Get conversation history for a session"""
    try:
        if session_id not in conversation_memory:
            return jsonify({'messages': []})
        
        memory = conversation_memory[session_id]
        messages = []
        
        for msg in memory.messages:
            messages.append({
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
            })
        
        return jsonify({'messages': messages})
        
    except Exception as e:
        logger.error(f"Error getting history for session {session_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def generate_response(classification_result, user_message):
    """Generate a response based on the classified intent"""
    intent = classification_result.get('intent', 'unknown')
    entities = classification_result.get('entities', {})
    
    # Simple response generation based on intent
    if intent == 'greeting':
        return "Hello! How can I help you today?"
    
    elif intent == 'goodbye':
        return "Goodbye! Have a great day!"
    
    elif intent == 'help':
        return "I'm here to help! You can ask me questions or we can have a conversation."
    
    elif intent == 'unknown':
        return "I'm not sure how to respond to that. Could you rephrase or ask for help?"
    
    else:
        return f"I understand you're talking about {intent}. Can you tell me more about what you need?"

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logger.info("Starting Chat API Server...")
    app.run(debug=True, host='0.0.0.0', port=5002) 