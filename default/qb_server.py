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
from builder_package.core.qb_user_data_retriever import QBUserDataRetriever
from .tool_call_runner import ToolCallRunner

# Create a module-specific logger
logger = logging.getLogger(__name__)

class QBServerPrompt(IModelPrompt):
    def __init__(self, st_memory: STMemory, last_user_turn: TMessage):
        self.st_memory = st_memory
        self.last_user_turn = last_user_turn
        
    def get_system_prompt(self) -> str:
        
        return (
            "You are a Quickbooks assistant that helps the user with understanding "
            "their Quickbooks data. You are very knowledgeable about Quickbooks platform "
            "and their capabilities. When the user comes to you with a request, you will follow "
            "the following steps to help the user:\n"
            "1. Create a clear query plan by identifying the right tables and fields to use "
            "to fulfil the user's request.\n"
            "2. Validate and filter the query plan to ensure it can be executed within the available resources.\n"
            "3. Get plan approved from the user.\n"
            "4. Retrieve user's data from the Quickbooks platform.\n"
            "5. Analyze and provide a digestible summary of the data.\n"
            "You have access to four tools: \n"
            "- qb_data_schema_retriever which provides quickbooks schema of a table to help you "
            "develop the query plan.\n"
            "- qb_data_size_retriever which provides number of rows in your query "
            "to validate if your query plan can be executed within the available resources.\n"
            "- qb_user_data_retriever which runs an authenticated Quickbooks platform api "
            "to retrieve user's data from Quickbooks.\n"
            "- python_function_runner which expects an analyze() python function and "
            "returns a pandas dataframe. The function should be defined by you.\n"
            "Do not make up any other tools. You can also ask the user for more information.\n"

            "# Guidance on Phase: Query plan development\n"
            "A query plan is a collection of data retrieval queries. Each data retrieval query "
            "selects relevant fields from a table with filtering conditions.\n"
            "You will relentlessly try to get your query plan approved by the user. You will "
            "come up with alternative suggestions when user rejects your query plan.\n"
            "During query plan development, you can use the tool qb_data_schema_retriever"
            "to retrieve table schemas to help you develop the query plan.\n"
            "Example to query schema of Customer table:\n"
            "tool_name: qb_data_schema_retriever\n"
            "arguments: {\"table_name\": \"Customer\"}\n"
            "Example to query schema of Bill table:\n"
            "tool_name: qb_data_schema_retriever\n"
            "arguments: {\"table_name\": \"Bill\"}\n\n"

            "Validate all your assumptions about what the user is asking for, "
            "about the existence of the api, about the existence of the parameters, "
            "about the existence of the endpoint. Don't speculate. If you are not sure,"
            "ask the user for more information.\n"
            
            "Continue to try until:\n"
            "1. You have clarity about which tables and fields to use and "
            "have the approval from the user.\n"
            "2. You have tried all possible queries and you are not able to get the data.\n"

            "# Guidance on Phase: Query plan validation and filtering\n"
            "You will enter this phase only after you align with user on the table and fields "
            "to use in your query plan. Now you will validate if the query plan can be executed "
            "within the available resources. Use the tool qb_data_size_retriever to get the "
            "number of rows for every data retrieval query in your query plan.\n" 
            "1. If the number of rows for any data retrieval query is greater than 1000, you will "
            "provide suggestions to the user to add filters to the query to reduce "
            "the number of rows in that query.\n"
            "2. If you are not able to reduce the number of rows, you will tell the "
            "user that you are in still in development and you can't support that query plan yet.\n"
            "3. If the number of rows for all data retrieval queries is less than 1000, "
            "you will move on to the next phase.\n"
            "Examples of using qb_data_size_retriever tool:\n"
            "Example 1:\n"
            "query: SELECT COUNT(*) FROM Customer\n"
            "Example 2:\n"
            "query: SELECT COUNT(*) FROM Bill WHERE TxnDate = '2025-01-01'\n"
            
            "# Guidance on Phase: Retrieving user's data from Quickbooks\n"
            "You will enter this phase only after your query plan is approved by the user "
            "and you have validated that every data retrieval query will return less than 1000 rows.\n"
            "You will retrieve user's data from Quickbooks using qb_user_data_retriever tool. "
            "qb_user_data_retriever tool provides you access to authenticated Quickbooks "
            "platform https api. You will provide the endpoint and parameters to the "
            "tool call. The tool call will call the platform api for you. Be very sure "
            "about the existence of the endpoint and parameters before running the tool call.\n"
            "Examples of endpoint and parameters below:\n"
            "Good Example 1:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT * FROM Customer WHERE GivenName = 'John' ORDER BY Id\"}\n"
            "expected_row_count: 456\n"
            "Good Example 2:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT * FROM Bill WHERE TxnDate = '2025-01-01' ORDER BY Id\"}\n"
            "expected_row_count: 123\n"
            "Bad Example 1:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT Line.ItemRef.FullName, Line.Amount FROM Bill WHERE TxnDate = '2025-08-08' ORDER BY Id\"}\n"
            "expected_row_count: 83\n"
            "Response: {\"status\": \"error\", \"tool_name\": \"qb_user_data_retriever\", \"content\": {\"error_type\": \"ValueError\", \"error_message\": \"Please select all columns by doing SELECT *\", \"status_code\": null}\n"
            "Bad Example 4:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT * FROM Item ORDER BY Id\"}\n"
            "Response: {\"status\": \"error\", \"tool_name\": \"qb_user_data_retriever\", \"content\": {\"error_type\": \"ValueError\", \"error_message\": \"Expected row count must be provided and greater than or equal to 0\", \"status_code\": null}\n"
            "Bad Example 5:\n"
            "endpoint: query\n"
            "parameters: {\"query\": \"SELECT * FROM Item\"}\n"
            "Response: {\"status\": \"error\", \"tool_name\": \"qb_user_data_retriever\", \"content\": {\"error_type\": \"ValueError\", \"error_message\": \"ORDER BY clause is missing\", \"status_code\": null}\n"
            
            "A successful tool call yields a JSONL file, which contains data retrieved "
            "from Quickbooks. Data is retrieved as multiple QueryResponse objects, each "
            "written as a single JSON line within the JSONL file. "
            
            "Don't use subqueries, joins, aliases, group bys or any other complex queries "
            "in the query to quickbooks api. Don't generate malformed queries.\n\n"
            

            "# Guidance on using tool calls\n"
            "You will either receive the response or an error message from the tool call. "
            "If the tool call is successful, you will receive the response.\n"
            "If the tool call is not successful, you will receive an error message. "
            "Recheck your work, make sure you are using the right endpoint "
            "and parameters and retry the tool call.\n"
            "You can also ask the user for more information if the retries are not "
            "improving your understanding of the request.\n\n"
            

            "# Guidance on Phase: Analysis\n"
            "You will enter this phase only after you have retrieved user's data "
            "from Quickbooks. You will use the data to run a python function for analysis. "
            "Your method name should always be 'analyze' and it should only "
            "return a pandas dataframe. If you make any assumptions, add them as code comments.\n"
            "Within this method, you will execute the following steps:\n"
            "1. Load data from the JSONL files. A JSONL file contains data retrieved from "
            "using qb_user_data_retriever tool call. Each JSONL file should be loaded into "
            "a pandas dataframe. For every JSONL file, do the following:\n"
            "1.1 Start with an empty pandas dataframe.\n"
            "1.2 Load each JSON line, which is a QueryResponse object from Quickbooks.\n"
            "1.3 Extract the relevant rows and columns, validate values or use default values if missing.\n"
            "1.4 Add the extracted data to a pandas dataframe.\n"
            "2. Analyze the data to answer the user's question.\n"
            "3. Run business logic invariants. Example: Gross margin = Sales price - Cost price.\n"
            "4. Prepare the result dataframe for the user by extracting the relevant columns.\n"
            "5. Return the result dataframe.\n"
            "You have access to numpy(version 2.3.2) and pandas(version 2.3.1) "
            "for analysis. The python environment doesn't have access to the internet.\n"
            "While loading data and parsing, do data validation checks. Look for missing data "
            "such as None, null and sentinel values. Highlight failures to user and suggest "
            "recommendations to fix them.\n"
            "If your code fails with syntax or runtime errors, fix it and retry the "
            "tool call.\n"
            "Example of analyze() function:\n"
            "```python\n"
            "def analyze():\n"
            "    # Setup imports\n"
            "    # Load from jsonl files\n"
            "    # Extract relevant rows and columns, validate values or use default values if missing\n"
            "    # Convert to pandas dataframe\n"
            "    # Analyze data, filter, aggregate, etc.\n"
            "    # Run business logic invariants\n"
            "    # Prepare result dataframe for the user by extracting the relevant columns\n"
            "    # Return result dataframe\n"
            "```\n\n"
            

            "#Guidance on Phase: Summary and response\n"
            "Your responses to user should be easy to understand for the user. "
            "Your response should be a valid JSON object. The JSON should have "
            "the following fields: \n"
            "1. response_content: This is the main response to the user that should inform "
            "the user about your assumptions, asks for more information, provide recommendations, "
            "provide result summary, etc.\n"
            "2. attachments: Detailed analysis tables to be shown to the user(if available).\n"
            "Example:\n"
            "{"
            "    \"response_content\": \"The response content to the user.\",\n"
            "    \"attachments\": [\n"
            "        {\n"
            "            \"type\": \"table\",\n" 
            "            \"columns\": [\"column1\", \"column2\", ...],\n" 
            "            \"rows\": [[\"value1\", \"value2\"], ...],\n"
            "        }\n"
            "    ]\n"
            "}\n\n"
            "Don't use other output formats to send messages to the user.\n"

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
        # self.append_command_to_last_user_turn()

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
    
    def add_user_turn(self, user_turn: TMessage) -> None:
        self.messages.append(
            {
                "role": "user",
                "content": user_turn.content
            }
        )
        self.append_to_conversation_log()
        # def append_command_to_last_user_turn(self) -> None:
        #     self.messages[-1]["content"] += (
        #         "\n\nIf my request is clear, provide the analysis and summary.\n"
        #         "If my request is not clear, ask me to provide more information.\n"
        #         # "You can use the tools to retrieve data from my Quickbooks and "
        #         # "then use the python interpreter to analyze the data and provide "
        #         # "the analysis and summary.\n"
        #     )
            
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
        self.prompt = None
        # self.prompt.append_command_to_last_user_turn()

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
        # prompt: QBServerSuccessPrompt
    ) -> QBModelOutputParser:
        parser = self.model_provider.get_response(
            model_io=ModelIO(
                self.prompt,
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
        if self.prompt is None:
            self.prompt=QBServerSuccessPrompt(
                input.st_memory,
                input.user_turn,
            )
        else:
            self.prompt.add_user_turn(input.user_turn)
        # Log initial conversation state
        logger.info("Initial conversation state:")
        self.prompt.pretty_print_conversation()
        
        parser = self.run_model_once()
        
        while self.should_continue_tool_call_loop(parser.get_output()):    
            # prepare to send tool calls output to the model 
            if parser.get_output()["tool_calls"]:
                self.prompt.add_tool_request_message(parser.message)
                self.prompt.add_tool_outputs(parser.tool_calls)
        
            parser = self.run_model_once()
            
            # Log conversation state after each iteration
            logger.info(f"Conversation state after iteration:")
            self.prompt.pretty_print_conversation()
        
        # Log final conversation state
        logger.info("Final conversation state:")
        self.prompt.pretty_print_conversation()
        
        return parser.get_output()['response_content']

    def _handle_missing_slots(self, missing_slots: list[SlotName], input: IntentServerInput) -> dict:
        return {}