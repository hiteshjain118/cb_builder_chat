import logging
from builder_package.core.imodel_io import DefaultModelOutputParser, IModelPrompt, ModelIO
from builder_package.core.intents import IntentName, HOTEL_BOOKING_INTENTS
from builder_package.core.slots import SLOTS
from builder_package.core.enums import SlotName
from builder_package.core.tod_types import INTENT_REGISTRY, IIntentServer, IntentServerInput, STMemory
from builder_package.core.structs import TMessage
from builder_package.model_providers.gpt_provider import GPTProvider
from builder_package.model_providers.imodel_provider import IModelProvider

class RetrieverBuildingServerPrompt(IModelPrompt):
    def __init__(self, st_memory: STMemory, last_user_turn: TMessage):
        self.st_memory = st_memory
        self.last_user_turn = last_user_turn
        
    def get_system_prompt(self) -> str:
        with open("/Users/hiteshjai/Documents/cb/qbo/qbo_inventory_server/qb_inventory_api_retriever.py", "r") as f:
            qbo_inventory_retriever_code = f.read()
        
        with open("/Users/hiteshjai/Documents/cb/qbo/qbo_purchase_transactions/qb_purchase_transactions_api_retriever.py", "r") as f:
            qbo_purchase_transactions_retriever_code = f.read()
        
        return (
            "You are a Retriever building assistant that is very knowledgeable about "
            "platform apis and their capabilities. You are given a user request that has "
            "retrieval and action components. You need to focus on the retrieval part "
            "of the user request. You need to identify the all relevant platform apis "
            "that need to be used to fulfill the retrieval part of the user request.\n"
            "Don't make any assumptions about platform apis or the user request. "
            "Recheck your work before providing the output.\n"
            "Each retriever only uses one platform api. It inherits authentication, batching "
            " and caching and executing the http request from the parent class(HTTPRetriever).\n"
            
            "All arguments to the retrievers should be specified by the user "
            "and injected into the constructor by the retriever caller."
            "If arguments are not clear, ask the user.\n"
            "Arguments should be added as constructor arguments to the retriever class. "
            "Don't make up placeholders.\n"
            "For instance:\n"
            "- Avoid using 'YOUR_SUBDOMAIN' randomly within the code class. Instead, define "
            " a constructor argument subdomain and use that in the class. "
            "Recheck you work that you didn't introduce any placeholders. If you did, fix it.\n"
            
            "The output of a retriever is the query response as a json object.\n"
            "Your output should be runnable code files that can be used right away "
            " to query the platform api. If there are dependencies, create a constructor "
            " argument to accept the dependencies from the caller. "
            "Don't any any extra text. Code comments are acceptable. "
            "Two examples code files are listed below.\n"
            # how to write python code to this prompt 
            "Example 1: \n"
            "```python\n"
            + qbo_inventory_retriever_code + "\n"
            "```\n"
            "Example 2: \n"
            "```python\n"
            + qbo_purchase_transactions_retriever_code + "\n"
            "```\n"
        )
        
        previous_prompt = (
            """
            {
                "retriever1": {
                    "input_arguments": "input_arguments",
                    "example_output": "example output from the platform api from your knowledge",
                    "description": "description of the retriever",
                    "python_code": "def retriever1(input_arguments): url = 'https://api.example.com/retriever1' ; response = requests.get(url) ; return response.json()"
                }
            }
            {
                "retriever2": {
                    "input_arguments": "input_arguments",
                    "example_output": "example output from the platform api from your knowledge",
                    "description": "description of the retriever",
                    "python_code": "def retriever2(input_arguments): url = 'https://api.example.com/retriever2' ; response = requests.get(url) ; return response.json()"
                }
            }
            """
        )
    
class RetrieverBuildingServerSuccessPrompt(RetrieverBuildingServerPrompt):
    def __init__(self, st_memory: STMemory, user_turn: TMessage):
        self.user_turn = user_turn
        self.st_memory = st_memory

    def get_messages(self) -> list[dict]:
        conversation_summary = self.st_memory.conversation_summary()
        if conversation_summary == "":
            conversation_summary = "No conversation history."
        return [
            {
                "role": "system",
                "content": self.get_system_prompt()
            },
            {
                "role": "user",
                "content": (
                    "Here's the conversation history: "
                    f"{conversation_summary}\n"
                    "If user ask is clear, provide the retrievers in code files. "
                    "Don't provide any extra text. "
                    "If user ask is not clear, ask the user to provide more information."
                )
            }
        ]


class RetrieverBuildingServer(IIntentServer):
    model_provider: IModelProvider
    def __init__(self, model_provider: IModelProvider):
        super().__init__(IntentName.RETRIEVER_BUILDING)
        self.model_provider = model_provider

    def run_tools(self, input: IntentServerInput) -> dict:
        logging.info(f"Running tools for {self.my_intent}: {input.user_id}, {input.st_memory}")
        return {}
    
    def use_tool_output(self, tools_output: dict, input: IntentServerInput) -> dict:
        return self.model_provider.get_response(
            model_io=ModelIO(
                prompt=RetrieverBuildingServerSuccessPrompt(
                    input.st_memory,
                    input.user_turn,
                ),
                output_parser_class=DefaultModelOutputParser,
                intent=self.my_intent
            )
        ).get_output()

    def _handle_missing_slots(self, missing_slots: list[SlotName], input: IntentServerInput) -> dict:
        return {}