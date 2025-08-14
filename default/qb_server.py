from datetime import datetime
import json
import logging
import traceback
from requests.exceptions import HTTPError
from openai.types.chat import ChatCompletionMessage
from builder_package.core.itool_call import ToolCallResult
from builder_package.core.imodel_io import DefaultModelOutputParser, IModelPrompt, ModelIO, QBModelOutputParser
from builder_package.core.intents import IntentName, HOTEL_BOOKING_INTENTS
from builder_package.core.slots import SLOTS
from builder_package.core.enums import SlotName
from builder_package.core.tod_types import INTENT_REGISTRY, IIntentServer, IntentServerInput, STMemory
from builder_package.core.structs import TMessage
from builder_package.model_providers.gpt_provider import GPTProvider
from builder_package.model_providers.imodel_provider import IModelProvider
from builder_package.qbo import QBOHTTPConnection, QBORequestAuthParams, QBOUser
from builder_package.core.http_retriever import ModelHTTPRetriever
from .tool_call_runner import ToolCallRunner

# Create a module-specific logger
logger = logging.getLogger(__name__)

class QBServerPrompt(IModelPrompt):
    def __init__(self, st_memory: STMemory, last_user_turn: TMessage):
        self.st_memory = st_memory
        self.last_user_turn = last_user_turn
        
    def get_system_prompt(self) -> str:
        with open("/Users/hiteshjai/Documents/cb/qbo/qbo_inventory_server/qb_inventory_api_retriever.py", "r") as f:
            qbo_inventory_retriever_code = f.read()
         
        with open("/Users/hiteshjai/Documents/cb/qbo/qbo_purchase_transactions/qb_purchase_transactions_api_retriever.py", "r") as f:
            qbo_purchase_transactions_retriever_code = f.read()
        
        return (
            "You are a Quickbooks assistant that helps the user with understanding "
            "their Quickbooks data. You are very knowledgeable about Quickbooks platform "
            "and their capabilities. You are given a user request that requires "
            "retrieval of data from the Quickbooks platform, followed by analysis "
            "and summarization of the data to make it easy for the user to understand.\n"
            "You have access to two tools: \n"
            "- qb_http_retriever which is an authenticated Quickbooks platform api.\n"
            "- python_function_runner which expects an analyze() python function and "
            "returns a pandas dataframe. The function should be defined by you.\n"
            "Do not make up any other tools. You can also ask the user for more information.\n"

            "## Tool: qb_http_retriever ##\n"
            "This tool provides you access to authenticated Quickbooks platform https api. "
            "Use your knowledge about quickbooks platform api and run tool calls to retrieve "
            "data from Quickbooks. Don't make assumptions about existence of the api. You will "
            "provide the endpoint and parameters to the tool call. The tool call will call the "
            "platform api for you. Be very sure about the existence of the endpoint and "
            "parameters before running the tool call.  \n"

            "You will either receive the response or an error message from the tool call. "
            "If the tool call is successful, you will receive the response.\n"
            "If the tool call is not successful, you will receive an error message. "
            "Recheck your work, make sure you are using the right endpoint "
            "and parameters and retry the tool call. Do not output message content "
            "when you are just retrying the tool calls.\n"
            "You can also ask the user for more information if the retries are not "
            "improving your understanding of the request.\n"

            "Examples of endpoint and parameters below:\n"
            "Good Example 1:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT * FROM Customer WHERE GivenName = 'John'\"}\n"
            "Good Example 2:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT * FROM Bill WHERE TxnDate = '2025-01-01'\"}\n"
            "Bad Example 1:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT Line.ItemRef.FullName, Line.Amount FROM Bill WHERE TxnDate = '2025-08-08'\"}\n"
            "Response: {\"status\": \"error\", \"tool_name\": \"qb_http_retriever\", \"content\": {\"error_type\": \"HTTPError\", \"error_message\": \"400 Client Error: Bad Request for url: https://quickbooks.api.intuit.com/v3/company/193514810323534/query?query=SELECT+Line.ItemRef.FullName%2C+Line.Amount+FROM+Bill+WHERE+TxnDate+%3D+%272025-08-08%27\", \"status_code\": null}\n"
            "Correction: Query all columns from Bill instead of specific columns.\n"
            "\n"

            "Do not make assumptions about what the user is asking for, "
            "about the existence of the api, about the existence of the parameters, "
            "about the existence of the endpoint. Instead, you can "
            "1. Ask the user when you are not sure.\n"
            "2. Try queries that will return a small amount of data to see if the "
            "api is working and learn the data schema. Example:\n"
            "   - endpoint: query\n"
            "   - parameters: {\"query\": \"SELECT * FROM Customer MAXRESULTS 2\"}\n"
            
            "Don't make up any information.\n"
            
            "If you not sure about the data schema, it is ok to query more data than " 
            "needed for the query. So SELECT all columns from the table. Once you have "
            "the data, you will know the data schema and you can use the python_function_runner "
            "tool to analyze the data.\n"
            "Don't use subqueries, joins, aliases, or any other complex queries "
            "in the query to quickbooks api. Don't generate malformed queries.\n"
            "Refuse queries that require over a day worth of data.\n"

            "## Tool: python_function_runner ##\n"
            "You can use this tool to run a python function for analysis. "
            "Your method name should always be 'analyze' and it should only "
            "return a pandas dataframe. Within this method, you can load the json data "
            "from jsonl files using the qb_http_retriever tool. You have access to "
            "numpy(version 2.3.2) and pandas(version 2.3.1) for analysis. The python "
            "environment doesn't have access to the internet.\n"
            "If your code fails with syntax or runtime errors, fix it and retry the "
            "tool call. Do not output message content during retries.\n"
            "Example of analyze() function:\n"
            "```python\n"
            "def analyze():\n"
            "    # Setup imports\n"
            "    # Load data from jsonl files\n"
            "    # Extract relevant columns\n"
            "    # Convert to pandas dataframe\n"
            "    # Filter, aggregate, etc.\n"
            "    # Return result dataframe\n"
            "```\n"
            
            f"Current date and time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

class QBServerSuccessPrompt(QBServerPrompt):
    def __init__(self, st_memory: STMemory, user_turn: TMessage):
        self.user_turn = user_turn
        self.st_memory = st_memory
        timestamp_int  = int(datetime.now().timestamp())
        self.conversation_file_name = f"conversation_{timestamp_int}.jsonl"
        self.messages = [
            {
                "role": "system",
                "content": self.get_system_prompt()
            },
        ]
        self.append_existing_messages()
        self.append_to_conversation_log()
        self.append_command_to_last_user_turn()

    def append_to_conversation_log(self) -> None:
        with open(self.conversation_file_name, "a") as f:
            for message in self.messages:
                if isinstance(message, ChatCompletionMessage):
                    message = message.to_dict()
                f.write(json.dumps(message) + "\n")

    def append_existing_messages(self) -> None:
        for message in self.st_memory.get_conversation_history():
            self.messages.append(
                {
                    "role": message.role,
                    "content": message.content
                }
            )
    
    def append_command_to_last_user_turn(self) -> None:
        self.messages[-1]["content"] += (
            "\n\nIf my request is clear, provide the analysis and summary.\n"
            "If my request is not clear, ask me to provide more information.\n"
            # "You can use the tools to retrieve data from my Quickbooks and "
            # "then use the python interpreter to analyze the data and provide "
            # "the analysis and summary.\n"
        )
        
    def get_messages(self) -> list[dict]:
        return self.messages 
    
    def add_tool_outputs(
        self, 
        tool_calls: dict[str, ToolCallResult]
    ) -> None:
        for tool_call_id, tool_call in tool_calls.items():
            self.add_tool_output(tool_call_id, tool_call)

    def add_tool_output(
        self, 
        tool_call_id: str, 
        tool_output: ToolCallResult
    ) -> None:
        self.messages.append(
            IModelPrompt.message_from_tool_call_result(
                tool_call_id, 
                tool_output
            )
        )
        self.append_to_conversation_log()

    def add_tool_request_message(self, message: ChatCompletionMessage) -> None:
        self.messages.append(message)
        self.append_to_conversation_log()
        
    def pretty_print_conversation(self) -> None:
        """Pretty print the current conversation to the log (excluding system messages)"""
        logger.info("=" * 80)
        logger.info("CONVERSATION HISTORY")
        logger.info("=" * 80)
        
        message_count = 0
        for message in self.messages:
            if isinstance(message, dict):
                role = message.get('role', 'unknown')
                content = message.get('content', '')
            elif isinstance(message, ChatCompletionMessage):
                role = message.role
                content = message.content
            else:
                raise ValueError(f"Unexpected message type: {type(message)}")
            
            if role == 'system':
                continue
                
            message_count += 1
            
            # Handle different message types
            if role == 'user':
                logger.info(f"[{message_count}] USER: {content}")
                
            elif role == 'assistant':
                logger.info(f"[{message_count}] ASSISTANT: {content}")
                
            elif role == 'tool':
                # always a dict
                tool_call_id = message.get('tool_call_id', 'unknown')
                tool_name = message.get('name', 'unknown')
                content = f"{content[:100]}...{len(content)}" if len(content) > 100 else content
                logger.info(f"[{message_count}] TOOL CALL RESULT (ID: {tool_call_id}, Tool: {tool_name}): {content}")
                
            logger.info("")  # Empty line between messages
        
        logger.info("=" * 80)
        logger.info(f"Total Messages (excluding system): {message_count}")
        logger.info("=" * 80)

class QBServer(IIntentServer):
    model_provider: IModelProvider
    def __init__(self, model_provider: IModelProvider):
        super().__init__(IntentName.QB)
        self.model_provider = model_provider
        self.tool_call_runner = ToolCallRunner()

    def run_tools(self, input: IntentServerInput) -> dict:
        logger.info(f"Running tools for {self.my_intent}: {input.user_id}")
        return {}
    
    def should_continue_tool_call_loop(
        self, 
        output: dict
    ) -> bool:
        return output["tool_calls"] is not None 
    
    def run_model_once(
        self, 
        prompt: QBServerSuccessPrompt
    ) -> QBModelOutputParser:
        parser = self.model_provider.get_response(
            model_io=ModelIO(
                prompt,
                output_parser=QBModelOutputParser(self.tool_call_runner),
                intent=self.my_intent,
            ),
            tools=self.tool_call_runner.enabled_tool_descriptions()
        )
        return parser
        

    def use_tool_output(
        self, 
        tools_output: dict, 
        input: IntentServerInput
    ) -> dict:
        logger.info(f"Using tool output: {tools_output}")
        prompt=QBServerSuccessPrompt(
            input.st_memory,
            input.user_turn,
        )
        
        # Log initial conversation state
        logger.info("Initial conversation state:")
        prompt.pretty_print_conversation()
        
        parser = self.run_model_once(prompt)
        
        while self.should_continue_tool_call_loop(parser.get_output()):    
            # prepare to send tool calls output to the model 
            if parser.get_output()["tool_calls"]:
                prompt.add_tool_request_message(parser.message)
                prompt.add_tool_outputs(parser.tool_calls)
        
            parser = self.run_model_once(prompt)
            
            # Log conversation state after each iteration
            logger.info(f"Conversation state after iteration:")
            prompt.pretty_print_conversation()
        
        # Log final conversation state
        logger.info("Final conversation state:")
        prompt.pretty_print_conversation()
        
        return parser.get_output()['response_content']

    def _handle_missing_slots(self, missing_slots: list[SlotName], input: IntentServerInput) -> dict:
        return {}