import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import Dict, Any, List
from langchain_core.messages import ToolMessage,AIMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
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

class BasicToolNode:
    """异步工具节点，用于并发执行AIMessage中请求的工具调用
    from langchain_core.messages import HumanMessage AIMessage ToolMessage SystemMessage
    功能：
    1. 接收工具列表并建立名称索引
    2. 并发执行消息中的工具调用请求
    3. 自动处理同步/异步工具适配
    """
    def __init__(self, tools: list) -> None:
        """初始化工具节点
        Args:
            tools: 工具列表，每个工具需包含name属性
        """
        self.tools_by_name = {tool.name: tool for tool in tools}  # 建立工具名称索引，所有工具名字的字典，不能有重复工具名字
    # 所有智能体的状态State都是字典类型的 
    async def __call__(self, inputs: Dict[str, Any]) -> Dict[str, List[ToolMessage]]:
        """异步调用入口
        Args:
            inputs: 输入字典，需包含"messages"字段
        Returns:
            包含ToolMessage列表的字典
        Raises:
            ValueError: 当输入无效时抛出
        """
        # 1. 输入验证
        if not (messages := inputs.get("messages")):
            raise ValueError("输入数据中未找到消息内容")  # 改进后的中文错误提示
        message:AIMessage = messages[-1]  # 取最新消息 最后是AIMessage

        # 2. 并发执行工具调用 _私有函数
        outputs = await self._execute_tool_calls(message.tool_calls)
        return {"messages": outputs}
    # 私有函数，异步和并发
    async def _execute_tool_calls(self, tool_calls: List[Dict]) -> List[ToolMessage]:
        """执行实际工具调用
        Args:
            tool_calls: 工具调用请求列表
        Returns:
            ToolMessage结果列表
        """
        async def _invoke_tool(tool_call: Dict) -> ToolMessage:
            """执行单个工具调用
            Args:
                tool_call: 工具调用请求字典，需包含name/args参数/id字段
            Returns:
                封装的ToolMessage
            Raises:
                KeyError: 工具未注册时抛出
                RuntimeError: 工具调用失败时抛出
            """
            try:
                # 3. 异步调用工具
                tool = self.tools_by_name.get(tool_call["name"]) # 验证 工具是否在之前的 工具集合中
                if not tool:
                    raise KeyError(f"未注册的工具: {tool_call['name']}")

                if hasattr(tool, 'ainvoke'):  # 优先使用异步方法
                    tool_result = await tool.ainvoke(tool_call["args"])
                else:  # 同步工具通过线程池asyncio转异步
                    loop = asyncio.get_running_loop()
                    tool_result = await loop.run_in_executor(
                        None,  # 使用默认线程池
                        tool.invoke,  # 同步调用方法
                        tool_call["args"]  # 参数
                    )

                # 4. 构造ToolMessage 转换为JSON格式的并且在封装为
                return ToolMessage(
                    content=json.dumps(tool_result, ensure_ascii=False),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            except Exception as e:
                raise RuntimeError(f"工具调用失败: {tool_call['name']}") from e
        try:
            # 5. 并发执行所有工具调用
            # asyncio.gather() 是 Python 异步编程中用于并发调度多个协程的核心函数，其核心行为包括：
            # 并发执行：所有传入的协程会被同时调度到事件循环中，通过非阻塞 I/O 实现并行处理。
            # 结果收集：按输入顺序返回所有协程的结果（或异常），与任务完成顺序无关。
            # 异常处理：默认情况下，任一任务失败会立即取消其他任务并抛出异常；若设置 return_exceptions=True，则异常会作为结果返回。
            return await asyncio.gather(*[_invoke_tool(tool_call) for tool_call in tool_calls])
        except Exception as e:
            raise RuntimeError("并发执行工具时发生错误") from e

# 定义小秘书的工作流状态State
class State(MessagesState):
    pass

# 路由函数返回节点名称
def route_tools_func(state:State):
    """
    一个动态路由函数，如果大模型输出后的AIMessage，中包含有工具调用的请求（指令toolcalls），就进入到工具节点，否则结束节点END。
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages",[]):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to toll_edge:{state}")
    if hasattr(ai_message,"tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

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
    tool_node = BasicToolNode(tools)
    builder.add_node('tools', tool_node)
    # 创建边，节点到节点
    builder.add_conditional_edges(
        "chatbot",
        route_tools_func,
        {"tools":"tools", END:END}
    )
    # 工具回到大模型节点
    builder.add_edge('tools','chatbot')
    builder.add_edge(START,'chatbot')
    # 编译工作流
    graph = builder.compile()
    return graph

agent = asyncio.run(create_garph())
# 非手动时候 langgraph dev 使用在配置文件 langgraph.json文件     "agent": "./src/agent/graph2.py:agent"
"""
$env:PYTHONUTF8="1"
langgraph dev
"""