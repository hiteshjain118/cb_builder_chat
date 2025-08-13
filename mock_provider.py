"""
Mock Model Provider for testing Chat API
"""

import logging
from typing import List, Dict, Any
from builder_package.core.imodel_io import IModelOutputParser, ModelIO
from builder_package.model_providers.imodel_provider import IModelProvider


class MockProvider(IModelProvider):
    """Mock model provider for testing purposes"""
    
    def __init__(self):
        """Initialize the mock provider"""
        self.name = "MockProvider"
        logging.info(f"Initialized {self.name}")
    
    def get_response(
        self, 
        model_io: ModelIO,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        tools: List[Dict[str, Any]] = [],
    ) -> IModelOutputParser:
        """Generate a mock response based on the prompt"""
        messages = model_io.prompt.get_messages()
        
        # Extract the user message from the prompt
        user_message = ""
        for message in messages:
            if message.get('role') == 'user':
                user_message = message.get('content', '')
                break
        
        # Generate a simple mock response
        if 'hello' in user_message.lower() or 'hi' in user_message.lower():
            response = "Hello! How can I help you today?"
        elif 'goodbye' in user_message.lower() or 'bye' in user_message.lower():
            response = "Goodbye! Have a great day!"
        elif 'help' in user_message.lower():
            response = "I'm here to help! You can ask me questions or we can have a conversation."
        else:
            response = f"I understand you said: '{user_message}'. How can I assist you further?"
        
        logging.info(f"Mock response: {response}")
        return model_io.output_parser().set_success(response)

    def get_model_name(self) -> str:
        """Get the name of the mock model"""
        return "mock-model" 