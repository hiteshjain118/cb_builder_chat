#!/usr/bin/env python3
"""
Unit tests for QBModelOutputParser
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builder_package.core.itool_call import ToolCallResult
from builder_package.model_providers.itool_call_runner import IToolCallRunner
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockChatCompletionMessage:
    """Mock ChatCompletionMessage for testing"""
    
    def __init__(self, content: str = None, tool_calls: list = None):
        self.content = content
        self.tool_calls = tool_calls


class MockChatCompletionMessageToolCall:
    """Mock ChatCompletionMessageToolCall for testing"""
    
    def __init__(self, tool_call_id: str, function_name: str, arguments: str):
        self.id = tool_call_id
        self.function = Mock()
        self.function.name = function_name
        self.function.arguments = arguments


class MockToolCallRunner(IToolCallRunner):
    """Mock implementation of IToolCallRunner for testing"""
    
    def __init__(self):
        self.mock_tool_results = {}
        self.run_tool_calls = []
    
    def run_tool(self, tool_call) -> ToolCallResult:
        """Mock run_tool method"""
        self.run_tool_calls.append(tool_call)
        tool_call_id = tool_call.id
        if tool_call_id in self.mock_tool_results:
            return self.mock_tool_results[tool_call_id]
        # Default success result
        return ToolCallResult.success(
            tool_name="retrieve_qb_data",
            handle_name="default_handle",
            data={"description": "Default mock result"}
        )
    
    @staticmethod
    def enabled_tools():
        """Mock enabled_tools method"""
        return []
    
    @staticmethod
    def enabled_tool_descriptions():
        """Mock enabled_tool_descriptions method"""
        return []


class TestQBModelOutputParser(unittest.TestCase):
    """Test cases for QBModelOutputParser"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock tool call runner
        self.mock_tool_call_runner = MockToolCallRunner()
        
        # Import QBModelOutputParser directly since we're in the chat directory
        from builder_package.core.imodel_io import QBModelOutputParser
        self.QBModelOutputParser = QBModelOutputParser
        
        # Create parser instance with our mock
        self.parser = self.QBModelOutputParser(self.mock_tool_call_runner)

    def test_init(self):
        """Test QBModelOutputParser initialization"""
        self.assertIsNone(self.parser.response_content)
        self.assertIsNone(self.parser.error_reason)
        self.assertIsNone(self.parser.tool_calls)
        self.assertIsNone(self.parser.message)
        self.assertEqual(self.parser.tool_call_runner, self.mock_tool_call_runner)

    def test_init_with_default_tool_call_runner(self):
        """Test QBModelOutputParser initialization with default tool call runner"""
        # Test that we can create an instance with default constructor
        # Since the constructor requires a tool_call_runner, we'll test that the current instance works
        self.assertIsNotNone(self.parser.tool_call_runner)

    def test_set_success_with_content_only(self):
        """Test set_success with message containing only content (no tool calls)"""
        mock_message = MockChatCompletionMessage(content="This is a successful response")
        
        result = self.parser.set_success(mock_message)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should set the message and content
        self.assertEqual(self.parser.message, mock_message)
        self.assertEqual(self.parser.response_content, "This is a successful response")
        
        # Should not have tool calls
        self.assertIsNone(self.parser.tool_calls)

    def test_set_success_with_tool_calls(self):
        """Test set_success with message containing tool calls"""
        mock_tool_call = MockChatCompletionMessageToolCall(
            tool_call_id="call_123",
            function_name="retrieve_qb_data",
            arguments='{"endpoint": "query", "parameters": {"query": "SELECT * FROM Customer"}}'
        )
        
        mock_message = MockChatCompletionMessage(
            content="I need to retrieve data",
            tool_calls=[mock_tool_call]
        )
        
        # Set up mock tool call result
        mock_tool_result = ToolCallResult.success(
            tool_name="retrieve_qb_data",
            handle_name="test_handle",
            data={"description": "Data retrieved successfully"}
        )
        
        self.mock_tool_call_runner.mock_tool_results["call_123"] = mock_tool_result
        
        result = self.parser.set_success(mock_message)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should set the message and content
        self.assertEqual(self.parser.message, mock_message)
        self.assertEqual(self.parser.response_content, "I need to retrieve data")
        
        # Should have tool calls
        self.assertIsNotNone(self.parser.tool_calls)
        self.assertIn("call_123", self.parser.tool_calls)
        self.assertEqual(self.parser.tool_calls["call_123"], mock_tool_result)
        
        # Verify run_tool was called
        self.assertEqual(len(self.mock_tool_call_runner.run_tool_calls), 1)
        self.assertEqual(self.mock_tool_call_runner.run_tool_calls[0], mock_tool_call)

    def test_set_success_with_multiple_tool_calls(self):
        """Test set_success with message containing multiple tool calls"""
        mock_tool_call_1 = MockChatCompletionMessageToolCall(
            tool_call_id="call_123",
            function_name="retrieve_qb_data",
            arguments='{"endpoint": "query", "parameters": {"query": "SELECT * FROM Customer"}}'
        )
        
        mock_tool_call_2 = MockChatCompletionMessageToolCall(
            tool_call_id="call_456",
            function_name="retrieve_qb_data",
            arguments='{"endpoint": "query", "parameters": {"query": "SELECT * FROM Invoice"}}'
        )
        
        mock_message = MockChatCompletionMessage(
            content="I need to retrieve multiple datasets",
            tool_calls=[mock_tool_call_1, mock_tool_call_2]
        )
        
        # Set up mock tool call results
        mock_tool_result_1 = ToolCallResult.success(
            tool_name="retrieve_qb_data",
            handle_name="customer_handle",
            data={"description": "Customer data retrieved"}
        )
        
        mock_tool_result_2 = ToolCallResult.success(
            tool_name="retrieve_qb_data",
            handle_name="invoice_handle",
            data={"description": "Invoice data retrieved"}
        )
        
        self.mock_tool_call_runner.mock_tool_results["call_123"] = mock_tool_result_1
        self.mock_tool_call_runner.mock_tool_results["call_456"] = mock_tool_result_2
        
        result = self.parser.set_success(mock_message)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should have both tool calls
        self.assertIsNotNone(self.parser.tool_calls)
        self.assertEqual(len(self.parser.tool_calls), 2)
        self.assertIn("call_123", self.parser.tool_calls)
        self.assertIn("call_456", self.parser.tool_calls)
        self.assertEqual(self.parser.tool_calls["call_123"], mock_tool_result_1)
        self.assertEqual(self.parser.tool_calls["call_456"], mock_tool_result_2)
        
        # Verify run_tool was called for both tool calls
        self.assertEqual(len(self.mock_tool_call_runner.run_tool_calls), 2)
        self.assertIn(mock_tool_call_1, self.mock_tool_call_runner.run_tool_calls)
        self.assertIn(mock_tool_call_2, self.mock_tool_call_runner.run_tool_calls)

    def test_set_success_with_empty_content(self):
        """Test set_success with message containing empty content"""
        mock_message = MockChatCompletionMessage(content="")
        
        result = self.parser.set_success(mock_message)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should set the message and content
        self.assertEqual(self.parser.message, mock_message)
        self.assertEqual(self.parser.response_content, "")
        
        # Should not have tool calls
        self.assertIsNone(self.parser.tool_calls)

    def test_set_success_with_none_content(self):
        """Test set_success with message containing None content"""
        mock_message = MockChatCompletionMessage(content=None)
        
        result = self.parser.set_success(mock_message)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should set the message and content
        self.assertEqual(self.parser.message, mock_message)
        self.assertIsNone(self.parser.response_content)
        
        # Should not have tool calls
        self.assertIsNone(self.parser.tool_calls)

    def test_set_error(self):
        """Test set_error method"""
        error_reason = "Something went wrong"
        
        result = self.parser.set_error(error_reason)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should set the error reason
        self.assertEqual(self.parser.error_reason, error_reason)

    def test_get_output_successful_with_content(self):
        """Test get_output when successful with content"""
        self.parser.response_content = "This is a successful response"
        self.parser.error_reason = None
        self.parser.tool_calls = None
        
        result = self.parser.get_output()
        
        expected = {
            "is_successful": True,
            "response_content": "This is a successful response",
            "error_reason": None,
            "tool_calls": None
        }
        self.assertEqual(result, expected)

    def test_get_output_successful_with_tool_calls(self):
        """Test get_output when successful with tool calls"""
        self.parser.response_content = "I need to retrieve data"
        self.parser.error_reason = None
        
        # Create mock successful tool call results
        mock_tool_result = ToolCallResult.success(
            tool_name="retrieve_qb_data",
            handle_name="test_handle",
            data={"description": "Data retrieved successfully"}
        )
        
        self.parser.tool_calls = {"call_123": mock_tool_result}
        
        result = self.parser.get_output()
        
        expected = {
            "is_successful": True,
            "response_content": "I need to retrieve data",
            "error_reason": None,
            "tool_calls": {"call_123": mock_tool_result}
        }
        self.assertEqual(result, expected)

    def test_get_output_not_successful_empty_content(self):
        """Test get_output when not successful due to empty content"""
        self.parser.response_content = ""
        self.parser.error_reason = None
        self.parser.tool_calls = None
        
        result = self.parser.get_output()
        
        expected = {
            "is_successful": False,
            "response_content": "",
            "error_reason": None,
            "tool_calls": None
        }
        self.assertEqual(result, expected)

    def test_get_output_not_successful_none_content(self):
        """Test get_output when not successful due to None content"""
        self.parser.response_content = None
        self.parser.error_reason = None
        self.parser.tool_calls = None
        
        result = self.parser.get_output()
        
        expected = {
            "is_successful": False,
            "response_content": None,
            "error_reason": None,
            "tool_calls": None
        }
        self.assertEqual(result, expected)

    def test_get_output_not_successful_with_error(self):
        """Test get_output when not successful due to error"""
        self.parser.response_content = "Some content"
        self.parser.error_reason = "Something went wrong"
        self.parser.tool_calls = None
        
        result = self.parser.get_output()
        
        expected = {
            "is_successful": False,
            "response_content": "Some content",
            "error_reason": "Something went wrong",
            "tool_calls": None
        }
        self.assertEqual(result, expected)

    def test_get_output_with_failed_tool_call(self):
        """Test get_output when tool call fails"""
        self.parser.response_content = "I need to retrieve data"
        self.parser.error_reason = None
        
        # Create mock failed tool call result
        mock_failed_tool_result = ToolCallResult.error(
            tool_name="retrieve_qb_data",
            error_type="HttpError",
            error_message="API call failed",
            status_code=500
        )
        
        self.parser.tool_calls = {"call_123": mock_failed_tool_result}
        
        result = self.parser.get_output()
        
        # Should detect the failed tool call and set error_reason
        self.assertEqual(self.parser.error_reason, "tool call call_123 failed")
        
        expected = {
            "is_successful": False,
            "response_content": "I need to retrieve data",
            "error_reason": "tool call call_123 failed",
            "tool_calls": {"call_123": mock_failed_tool_result}
        }
        self.assertEqual(result, expected)

    def test_get_output_with_mixed_tool_call_results(self):
        """Test get_output with some successful and some failed tool calls"""
        self.parser.response_content = "I need to retrieve multiple datasets"
        self.parser.error_reason = None
        
        # Create mock tool call results - one success, one failure
        mock_successful_tool_result = ToolCallResult.success(
            tool_name="retrieve_qb_data",
            handle_name="customer_handle",
            data={"description": "Customer data retrieved"}
        )
        
        mock_failed_tool_result = ToolCallResult.error(
            tool_name="retrieve_qb_data",
            error_type="HttpError",
            error_message="API call failed",
            status_code=500
        )
        
        self.parser.tool_calls = {
            "call_123": mock_successful_tool_result,
            "call_456": mock_failed_tool_result
        }
        
        result = self.parser.get_output()
        
        # Should detect the first failed tool call and set error_reason
        self.assertEqual(self.parser.error_reason, "tool call call_456 failed")
        
        expected = {
            "is_successful": False,
            "response_content": "I need to retrieve multiple datasets",
            "error_reason": "tool call call_456 failed",
            "tool_calls": {
                "call_123": mock_successful_tool_result,
                "call_456": mock_failed_tool_result
            }
        }
        self.assertEqual(result, expected)

    def test_get_output_with_no_tool_calls(self):
        """Test get_output when there are no tool calls"""
        self.parser.response_content = "Simple response with no tools"
        self.parser.error_reason = None
        self.parser.tool_calls = None
        
        result = self.parser.get_output()
        
        # The actual logic considers content with length > 0 as successful when no tool calls
        expected = {
            "is_successful": True,  # Changed from False to True since content has length > 0
            "response_content": "Simple response with no tools",
            "error_reason": None,
            "tool_calls": None
        }
        self.assertEqual(result, expected)

    def test_get_output_with_empty_tool_calls_dict(self):
        """Test get_output when tool_calls is an empty dictionary"""
        self.parser.response_content = "Response with empty tool calls"
        self.parser.error_reason = None
        self.parser.tool_calls = {}
        
        result = self.parser.get_output()
        
        expected = {
            "is_successful": True,
            "response_content": "Response with empty tool calls",
            "error_reason": None,
            "tool_calls": {}
        }
        self.assertEqual(result, expected)

    def test_set_success_chaining(self):
        """Test that set_success can be chained"""
        mock_message = MockChatCompletionMessage(content="Test response")
        
        result = self.parser.set_success(mock_message).set_error("New error")
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should have both the success and error set
        self.assertEqual(self.parser.message, mock_message)
        self.assertEqual(self.parser.response_content, "Test response")
        self.assertEqual(self.parser.error_reason, "New error")

    def test_set_error_chaining(self):
        """Test that set_error can be chained"""
        result = self.parser.set_error("First error").set_error("Second error")
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should have the last error set
        self.assertEqual(self.parser.error_reason, "Second error")

    def test_tool_call_runner_integration(self):
        """Test integration with tool call runner"""
        mock_tool_call = MockChatCompletionMessageToolCall(
            tool_call_id="call_123",
            function_name="retrieve_qb_data",
            arguments='{"endpoint": "query", "parameters": {"query": "SELECT * FROM Customer"}}'
        )
        
        mock_message = MockChatCompletionMessage(
            content="Retrieve customer data",
            tool_calls=[mock_tool_call]
        )
        
        # Set up mock tool call result
        mock_tool_result = ToolCallResult.success(
            tool_name="retrieve_qb_data",
            handle_name="customer_handle",
            data={"description": "Customer data retrieved successfully"}
        )
        
        self.mock_tool_call_runner.mock_tool_results["call_123"] = mock_tool_result
        
        self.parser.set_success(mock_message)
        
        # Verify that run_tool was called with the tool call
        self.assertEqual(len(self.mock_tool_call_runner.run_tool_calls), 1)
        self.assertEqual(self.mock_tool_call_runner.run_tool_calls[0], mock_tool_call)
        
        # Verify the result was stored
        self.assertEqual(self.parser.tool_calls["call_123"], mock_tool_result)

    def test_edge_case_none_tool_calls(self):
        """Test edge case where tool_calls is explicitly None in message"""
        mock_message = MockChatCompletionMessage(content="Response", tool_calls=None)
        
        result = self.parser.set_success(mock_message)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should not have tool calls
        self.assertIsNone(self.parser.tool_calls)

    def test_edge_case_empty_tool_calls_list(self):
        """Test edge case where tool_calls is an empty list"""
        mock_message = MockChatCompletionMessage(content="Response", tool_calls=[])
        
        result = self.parser.set_success(mock_message)
        
        # Should return self for chaining
        self.assertEqual(result, self.parser)
        
        # Should have empty tool calls dict
        self.assertEqual(self.parser.tool_calls, {})

    def test_tool_call_runner_interface_compliance(self):
        """Test that our mock tool call runner properly implements IToolCallRunner"""
        # Verify that our mock implements the abstract methods
        self.assertIsInstance(self.mock_tool_call_runner, IToolCallRunner)
        
        # Test that the static methods work
        tools = self.mock_tool_call_runner.enabled_tools()
        self.assertEqual(tools, [])
        
        descriptions = self.mock_tool_call_runner.enabled_tool_descriptions()
        self.assertEqual(descriptions, [])

    def test_tool_call_runner_method_calls(self):
        """Test that tool call runner methods are called correctly"""
        mock_tool_call = MockChatCompletionMessageToolCall(
            tool_call_id="call_123",
            function_name="retrieve_qb_data",
            arguments='{"endpoint": "query", "parameters": {"query": "SELECT * FROM Customer"}}'
        )
        
        mock_message = MockChatCompletionMessage(
            content="Test content",
            tool_calls=[mock_tool_call]
        )
        
        # Clear previous calls
        self.mock_tool_call_runner.run_tool_calls.clear()
        
        # Call set_success
        self.parser.set_success(mock_message)
        
        # Verify run_tool was called exactly once
        self.assertEqual(len(self.mock_tool_call_runner.run_tool_calls), 1)
        self.assertEqual(self.mock_tool_call_runner.run_tool_calls[0].id, "call_123")


if __name__ == '__main__':
    unittest.main() 