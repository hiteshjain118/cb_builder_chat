import logging
from builder_package.core.imodel_io import DefaultModelOutputParser, IModelPrompt, ModelIO
from builder_package.core.intents import IntentName, HOTEL_BOOKING_INTENTS
from builder_package.core.slots import SLOTS
from builder_package.core.enums import SlotName
from builder_package.core.tod_types import INTENT_REGISTRY, IIntentServer, IntentServerInput, STMemory
from builder_package.core.structs import TMessage
from builder_package.model_providers.gpt_provider import GPTProvider
from builder_package.model_providers.imodel_provider import IModelProvider

class AgentBuildingServerPrompt(IModelPrompt):
    def __init__(self, st_memory: STMemory, last_user_turn: TMessage):
        self.st_memory = st_memory
        self.last_user_turn = last_user_turn
        
    def get_system_prompt(self) -> str:
        return (
            "You are a helpful Agent building assistant that builds agents "
            "to automate their manual tasks. The agent architecture is as follows:\n"
            " - Intent server: This is the entry point into the entire processing "
            " and capabilities supported in the task. It is the overall coordinator "
            " to get information from various sources using retrievers and tools to perform "
            "actions using actors.\n"
            " - Retrievers: These are the tools that get information from various sources. "
            "The inputs to the retrievers are specified by the user. If not clear, ask the user. "
            "Each retriever can only run one tool. If the retreiver makes an HTTP call, it's "
            "output is a JSON response object. \n"
            " - Actors: These are the tools that perform actions. User specifies the type of "
            " actions they want to perform after processing the retrievers' output. After the " 
            " retreived data is processed, processing for actor input commences and actor "
            "input becomes available. Each actor can only run one tool.\n"
            " - Process nodes: These are the nodes that process the information. Use them "
            "to process retrievers' output and actors' input. Keep each process node simple.\n"
            "Create and/or arrange multiple process nodes as a directed graph to perform a complex task.\n\n"

            "You are given a task and you need to build an agent to automate it. Your output "
            "should be a JSON object as follows:\n"
            "{"
            "  \"intent_server\": {"
            "    \"retriver_process_node\": {"
            "      \"retrievers\": ["
            "        {"
            "          \"name\": \"retriever_name\","
            "          \"description\": \"description of the retriever\""
            "          \"slots\": \"input arguments to the retriever\""
            "        }"
            "      ]"
            "      \"process_nodes\": ["
            "        {"
            "          \"name\": \"process_node_name\","
            "          \"description\": \"description of the process node\""
            "        }"
            "      ]"
            "    },"
            "    \"actors\": ["
            "      {"
            "        \"name\": \"actor_name\","
            "        \"description\": \"description of the actor\""
            "        \"slots\": \"input arguments to the actor\""
            "        \"process_nodes\": \"process retrievers' output before passing it to the actor\""
            "      }"
            "    ]"
            "  }"
            "}"
        )
    
class AgentBuildingServerSuccessPrompt(AgentBuildingServerPrompt):
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
                    "If user ask is clear, provide the architecture of the agent in JSON format. "
                    "If user ask is not clear, ask the user to provide more information."
                )
            }
        ]


class AgentBuildingServer(IIntentServer):
    model_provider: IModelProvider
    def __init__(self, model_provider: IModelProvider):
        super().__init__(IntentName.AGENT_BUILDING)
        self.model_provider = model_provider

    def run_tools(self, input: IntentServerInput) -> dict:
        logging.info(f"Running tools for {self.my_intent}: {input.user_id}, {input.st_memory}")
        return {}
    
    def use_tool_output(self, tools_output: dict, input: IntentServerInput) -> dict:
        return self.model_provider.get_response(
            model_io=ModelIO(
                prompt=AgentBuildingServerSuccessPrompt(
                    input.st_memory,
                    input.user_turn,
                ),
                output_parser_class=DefaultModelOutputParser,
                intent=self.my_intent
            )
        ).get_output()

    def _handle_missing_slots(self, missing_slots: list[SlotName], input: IntentServerInput) -> dict:
        return {}