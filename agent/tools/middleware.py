from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompt, load_system_prompt


#日志监控
@wrap_tool_call
def monitor_tool(
        #请求的数据封装
        request: ToolCallRequest,
        #执行的函数本身
        handler: Callable[[ToolCallRequest], ToolMessage|Command],
)-> ToolMessage|Command:
    logger.info(f"[monitor_tool]执行工具：{request.tool_call['name']}")
    logger.info(f"[monitor_tool]请求参数：{request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[monitor_tool]执行结果：{request.tool_call['name']}成功")

        if request.tool_call['name']=="fill_context_for_report":
            request.runtime.context["report"]=True

        return result
    except Exception as e:
        logger.error(f"[monitor_tool]执行工具：{request.tool_call['name']}失败，错误信息：{str(e)}")
        raise e

#模型监控
@before_model
def log_before_model(
        #整个Agent智能体中的状态记录
        state: AgentState,
        #记录了整个执行过程中的上下文信心
        runtime:Runtime,
):
    """
    在模型输出前输出日志
    """

    logger.info(f"[log_before_model]即将调用模型：带有{len(state['messages'])}条消息")
    logger.debug(
        f"[log_before_model]模型输入：{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}"
    )

    return None

@dynamic_prompt
#每一次在生成提示词之前，调用此函数
def report_prompt_switch(request:ModelRequest):
    """
    动态prompt切换
    """
    is_report=request.runtime.context.get("report",False)
    if is_report:
        return load_report_prompt()
    return  load_system_prompt()





















