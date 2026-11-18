import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode,tools_condition
from agent.llm_mcp_server_config import llm, zhipuai_mcp_server_config, my12306_mcp_server_config, chart_mcp_server_config

# # 外网 MCP服务端的连接配置 视频 8 MCP认证机制
# zhipuai_mcp_server_config = {
#     "url":"https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp?Authorization=2c96d8bd32454d229e91dbc2cbf69f04.vYnko9tzZDYT9GMP",
#     "transport":"streamable_http"
# }

# # 外网 MCP服务端的连接配置 12306车票查询
# my12306_mcp_server_config = {
#     "url":"https://mcp.api-inference.modelscope.net/6aaa819fb65d40/mcp",
#     "transport":"streamable_http"
# }

# # 外网 MCP服务端的连接配置 可视化图表 MCP Server
# chart_mcp_server_config = {
#     "url":"https://mcp.api-inference.modelscope.net/aa949faa28084b/mcp",
#     "transport":"streamable_http"
# }

mcp_client = MultiServerMCPClient(
    {
        'chart_mcp':chart_mcp_server_config,
        'zhipuai_mcp':zhipuai_mcp_server_config,
        'my12306_mcp':my12306_mcp_server_config,
    }
)

# {
#   "mcpServers": {
#     "12306-mcp": {
#       "type": "streamable_http",
#       "url": "https://mcp.api-inference.modelscope.net/6aaa819fb65d40/mcp"
#     }
#   }
# }

# {
#   "mcpServers": {
#     "mcp-server-chart": {
#       "type": "streamable_http",
#       "url": "https://mcp.api-inference.modelscope.net/aa949faa28084b/mcp"
#     }
#   }
# }

# # qwen3.8-27b gpt-6.1-terra ， 工具的信息等组成的LLM支持的上下文环境的大小是不低于8KB
# llm = ChatOpenAI(
#     model='gpt-5.5',
#     temperature=0.8,
#     api_key='sk-ie6zdD00QM05lMjvAb44A2Cc9a35496dA30dA9E1Dd0c1168',
#     base_url="https://api.apiyi.com/v1",
# )

# class BasicToolNode:异步工具节点，用于并发执行AIMessage中请求的工具调用

# 定义小秘书的工作流状态State
class State(MessagesState):
    pass

# 路由函数返回节点名称
# def route_tools_func(state:State):
#     一个动态路由函数，如果大模型输出后的AIMessage，中包含有工具调用的请求（指令toolcalls），就进入到工具节点，否则结束节点END。


async def create_garph():
    tools = await mcp_client.get_tools() # 来自MCP服务端的30多个以上的工具
    # 构建工作流（使用StateGraph）
    builder = StateGraph(State)
    # 大模型调用哪些工具，大模型与工具绑定
    llm_with_tools = llm.bind_tools(tools)
    # 第一个节点是大模型
    async def chatbot(state:State):
        return {"messages": [await llm_with_tools.ainvoke(state["messages"])]}
    # 添加大模型自动决策的节点
    builder.add_node('chatbot', chatbot)
    # 工具调用节点
    # tool_node = BasicToolNode(tools)
    tool_node = ToolNode(tools)
    builder.add_node('tools', tool_node)
    # 创建边，节点到节点
    builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        # route_tools_func,
    )
    # 工具回到大模型节点
    builder.add_edge('tools','chatbot')
    builder.add_edge(START,'chatbot')
    # 编译工作流
    graph = builder.compile()
    return graph

agent = asyncio.run(create_garph())
# # 非手动时候 langgraph dev 使用在配置文件 langgraph.json文件     "agent": "./src/agent/graph3.py:agent"
"""
$env:PYTHONUTF8="1"
langgraph dev
"""