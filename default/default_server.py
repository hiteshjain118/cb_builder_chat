from builder_package.core.enums import SlotName
from builder_package.core.tod_types import IIntentServer, IntentServerInput, STMemory, TMessage
from builder_package.core.intents import IntentName, HOTEL_BOOKING_INTENTS
from builder_package.model_providers.gpt_provider import GPTProvider
from builder_package.model_providers.imodel_provider import IModelProvider
from builder_package.core.imodel_io import DefaultModelOutputParser, IModelPrompt, ModelIO

class DefaultServerPrompt(IModelPrompt):
    def __init__(self, st_memory: STMemory, last_user_turn: TMessage):
        self.st_memory = st_memory
        self.last_user_turn = last_user_turn
        
    def get_system_prompt(self) -> str:
        return (
            "You are a helpful hotel booking assistant. "
            "The user's request does not match any known intent. "
            "Be helpful and politely ask the user to clarify or rephrase their request."
            "You can help the user with the following intents: "
            f"{', '.join([intent.name for intent in HOTEL_BOOKING_INTENTS])}"
        )

    def get_messages(self) -> list[dict]:
        conversation_summary = self.st_memory.conversation_history_before_last_user_turn()
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
                    "The user's message could not be classified into any known intent. "
                    "Here's the conversation history: "
                    f"{conversation_summary}\n"
                    "Here's the user's last message: "
                    f"{self.last_user_turn.content}\n"
                    "Be helpful and politely ask the user to clarify or rephrase their request."
                )
            }
        ]

class DefaultServer(IIntentServer):
    model_provider: IModelProvider
    def __init__(self, model_provider: IModelProvider):
        super().__init__(IntentName.OTHER)
        self.model_provider = model_provider

    def run_tools(self, input: IntentServerInput) -> dict:
        return {}

    def use_tool_output(self, tools_output: dict, input: IntentServerInput) -> dict:
        return self.model_provider.get_response(
            model_io=ModelIO(
                prompt=DefaultServerPrompt(input.st_memory, input.user_turn),
                output_parser_class=DefaultModelOutputParser,
                intent=self.my_intent
            ),
        ).get_output()

    def _handle_missing_slots(self, missing_slots: list[SlotName], input: IntentServerInput) -> dict:
        # For OTHER intent, just return the default response
        raise NotImplementedError("OTHER intent does not support missing slots")