import json
from builder_package.core.qb_user_data_retriever import QBUserDataRetriever
from builder_package.core.qb_data_size_retriever import QBDataSizeRetriever
from builder_package.core.qb_data_schema_retriever import QBDataSchemaRetriever
from builder_package.core.python_function_runner import PythonFunctionRunner
from builder_package.qbo import QBOUser, QBORequestAuthParams, QBOHTTPConnection
from builder_package.core.itool_call import IToolCall, ToolCallResult
from builder_package.model_providers.itool_call_runner import IToolCallRunner
from openai.types.chat import ChatCompletionMessageToolCall
from builder_package.core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


class ToolCallRunner(IToolCallRunner):
    def __init__(self):
        self.cb_user = QBOUser(
            realm_id='193514810323534',
            user_timezone='America/Los_Angeles'
        )
        self.connection=QBOHTTPConnection(
            auth_params=QBORequestAuthParams(),
            qbo_user=self.cb_user,
        )

    def run_tool(self, tool_call: ChatCompletionMessageToolCall) -> ToolCallResult:
        tool_call_id = tool_call.id
        tool_name = tool_call.function.name
        tool_arguments = json.loads(tool_call.function.arguments)
        logger.info(f"Running tool call id:{tool_call_id} "
                    f"name:{tool_name} with arguments {tool_arguments}")
        if tool_name == QBUserDataRetriever.tool_name():
            result = self.run_qb_http_retriever(tool_arguments)
        elif tool_name == PythonFunctionRunner.tool_name():
            result = self.run_python_code_runner(tool_arguments)
        elif tool_name == QBDataSchemaRetriever.tool_name():
            result = self.run_qb_data_schema_retriever(tool_arguments)
        elif tool_name == QBDataSizeRetriever.tool_name():
            result = self.run_qb_data_size_retriever(tool_arguments)
        else:
            raise ValueError(f"Tool {tool_name} not found")
        
        if result.status == "error":
            logger.error(f"Tool {tool_call_id} failed: {result}")
        else:
            logger.info(f"Tool {tool_call_id} succeeded: {result.to_dict_w_truncated_content()}")
        return result
        
    def run_python_code_runner(self, arguments: dict) -> ToolCallResult:
        code = arguments.get("code")
        if code is None:
            return ToolCallResult.error(
                tool_name=PythonFunctionRunner.tool_name(),
                error_type="InvalidParameters", 
                error_message="Code is required"
            )
        runner = PythonFunctionRunner(code)
        return runner.call_tool()
    
    def run_qb_http_retriever(self, arguments: dict) -> ToolCallResult:
        endpoint = arguments.get("endpoint")
        params = arguments.get("parameters", {})
        expected_row_count = int(arguments.get("expected_row_count", -1))
        endpoint = endpoint.split("/")[-1]
        if endpoint is None or len(params) == 0:
            return ToolCallResult.error(
                tool_name=QBUserDataRetriever.tool_name(),
                error_type="InvalidParameters", 
                error_message="Endpoint and params are required"
            )
        retriever = QBUserDataRetriever(
            connection=self.connection,
            cb_user=self.cb_user,
            endpoint=endpoint,
            params=params,
            expected_row_count=expected_row_count,
            save_file_path='default'
        )
        return retriever.call_tool()
    
    def run_qb_data_schema_retriever(self, arguments: dict) -> ToolCallResult:
        table_name = arguments.get("table_name")
        retriever = QBDataSchemaRetriever(
            connection=self.connection,
            cb_user=self.cb_user,
            table_name=table_name,
            save_file_path='default'
        )
        return retriever.call_tool()
    
    def run_qb_data_size_retriever(self, arguments: dict) -> ToolCallResult:
        query = arguments.get("query")
        retriever = QBDataSizeRetriever(
            connection=self.connection,
            cb_user=self.cb_user,
            query=query,
            save_file_path='default'
        )
        return retriever.call_tool()
    
    @staticmethod
    def enabled_tools() -> list[IToolCall]:
        return [QBDataSchemaRetriever, QBDataSizeRetriever, QBUserDataRetriever, PythonFunctionRunner]
    
    @staticmethod
    def enabled_tool_descriptions() -> list[dict]:
        return [tool.tool_description() for tool in ToolCallRunner.enabled_tools()]