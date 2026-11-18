from langchain_core.tools import tool,InjectedToolCallId
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langchain_core.messages import ToolMessage,HumanMessage,AIMessage,BaseMessage
from typing import Annotated
from agent.my_state import CustomState
from langgraph.prebuilt import InjectedState

@tool
def get_user_name(tool_call_id: Annotated[str, InjectedToolCallId], config:RunnableConfig) -> Command:
    """获取当前用户的用户username，以便生成祝福语句"""
    user_name = config["configurable"].get('user_name', 'zhangsan')
    print(f"调用工具，传入的用户名是: {user_name}")

    # 模拟
    return Command(update={
        "username": user_name, # 更新智能体CustomState状态中的username字段
        # 更新一条工具执行后的消息 ToolMessage
        "messages": [
            ToolMessage(
                content="成功得到当前用户的username",
                tool_call_id=tool_call_id
            )
        ]

        })


@tool
def greet_user(state: Annotated[CustomState, InjectedState]) -> str:
    """获取用户的username之后生成祝福语句"""
    username = state["username"] # 从状态在获取用户名
    return f'祝贺你: {username}'
