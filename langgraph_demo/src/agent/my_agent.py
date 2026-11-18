from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from agent.tools.tools_demo3 import calculation3
from agent.tools.tools_demo6 import runnable_tool
from agent.tools.tools_demo7 import MySearchTool
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState
from agent.tools.tools_demo9 import get_user_name,greet_user
from agent.my_state import CustomState
# 本地私有化部署的大模型
llm = ChatOpenAI(
    model='qwen3.8-27b',
    temperature=0.8,
    api_key='sk-JRRVTm2dgXSjnGtgE2Af9f4e547649FeBaC100D6F149825b',
    base_url="https://api.apiyi.com/v1",
    extra_body={'chat_template_kwargs': {'enable_thinking': True}},
)

# # 本地 Ollama gemma4:12b
# llm = ChatOpenAI(
#     model="gemma4:12b",  # 和 ollama pull 的模型名保持一致
#     temperature=0.8,
#     api_key="dummy_key",  # ollama本地接口不需要真实key，随便写字符串
#     base_url="http://localhost:11434/v1",  # ollama 默认openai兼容地址
#     # extra_body 这个参数 ollama 不支持，直接删掉
# )

# def get_weather(city: str) -> str:
#     """Get weather for a given city."""
#     return f"今天天气晴朗，在 {city}!"
# graph = create_react_agent(
#     llm,
#     tools=[get_weather],
#     prompt="你是一个智能助手！"
# )

# 创建一个网络搜索的工具
search_tool = MySearchTool()

# 提示词模板的函数:由用户传入内容，组成一个动态的系统提示词
def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
    user_name = config["configurable"].get('user_name', 'zhangsan')  # 获取用户名称
    print("用户名称为:", user_name)
    system_message = f"你是一个智能助手，尽可能地调用工具回答用户的问题，当前用户的名字是： {user_name}"
    return [{'role':'system', 'content': system_message}] + state['messages']


graph = create_react_agent(
    llm,
    # tools=[calculation3, runnable_tool, search_tool, get_user_info_by_name],
    tools=[calculation3, runnable_tool, search_tool, get_user_name, greet_user],
    prompt=prompt,  # 使用自定义的提示词模板函数
    # prompt="你是一个智能助手！"
    state_schema=CustomState # 指定自定义的状态
)
"""HunmanMessage -State AIMessage -State ToolMessage -State AIMessage -State"""

# 执行智能体,不需要严格的目录结构
# result = graph.stream(
#     input={"messages":[{"role": "user", "content": "计算一下(3+5) x 12的结果"}]},
#     stream_mode='messages-tuple'
# )
# for chunk in result:
#     print(chunk)

# graph.invoke({"input": "北京的天气怎么样？"}) # 同步执行的
# graph.ainvoke({"input": "北京的天气怎么样？"}) # 异步执行的

# $env:PYTHONUTF8="1"
# langgraph dev


