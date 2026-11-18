from langgraph.prebuilt.chat_agent_executor import AgentState


# 自定义的智能体的状态类
class CustomState(AgentState):
    username:str # 用户名称
