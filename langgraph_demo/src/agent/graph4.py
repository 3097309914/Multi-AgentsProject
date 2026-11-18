import asyncio
from agent.llm_mcp_server_config import llm, zhipuai_mcp_server_config, my12306_mcp_server_config, chart_mcp_server_config
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.messages import ToolMessage,AIMessage

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

    # 检查点让状态图可以持久化其状态
    # 这个是整个状态图的完整内存 手动运行的
    memroy = MemorySaver()
    # 编译工作流 interrupt_before中断
    graph = builder.compile(checkpointer=memroy,interrupt_before=['tools'])
    # 不是手动的，服务器的
    # graph = builder.compile(interrupt_before=['tools'])
    return graph

# agent = asyncio.run(create_garph()) # 非手动运行

async def run_graph():
    graph = await create_garph() # 手动运行的
    # 配置参数，包含ID和线程ID
    config = {
        "configurable":{
            # 检查点由session_id访问
            "thread_id":'zs12311',
        }
    }
    def get_answer(tool_message, user_answer):
        """让人工介入，并且给一个问题的答案"""

        tool_name = tool_message.tool_calls[0]['name']
        answer = (
            f"人工强制终止了工具：{tool_name}的执行，拒绝的理由是：{user_answer}"
        )

        # 创建一个消息
        new_message = [
            ToolMessage(content=answer, tool_call_id=tool_message.tool_calls[0]['id']),
            AIMessage(content=answer)
        ]

        # 把新人造的消息，添加到工作流的state中
        graph.update_state(  # 手动修改state
            config=config,
            values={'messages': new_message,"age":"18"}
        )
    def print_message(event, result):
        """格式化输出消息"""
        messages = event.get('messages')
        if messages:
            if isinstance(messages, list):
                message = messages[-1]  # 如果消息是列表，则取最后一个
            if message.__class__.__name__ == 'AIMessage':
                if message.content:
                    # print(result)
                    result = message.content  # 需要在展示的消息
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > 1500:
                msg_repr = msg_repr[:1500] + " ... （已截断）"  # 超过最大长度则截断
            print(msg_repr)  # 输出消息的表示形式
        return result
    async def execute_graph(user_input: str) -> str:
        """执行工作流的函数"""
        result = '' # AI助手最后一条消息
        if user_input.strip().lower() != 'y': # 正常的用户提问
            current_state = graph.get_state(config)
            if current_state.next:  # 如果有下一步，则当前工作流处在中断中，没有到END节点
                tools_script_message = current_state.values['messages'][-1]  # 状态中存储的最后一个message
                # 通过提供关于请求的更改/改变主意的指示来满足工具调用
                get_answer(tools_script_message, user_input)
                message = graph.get_state(config).values['messages'][-1]
                result = message.content

                return result
            else:
                # 不是可等待对象（Awaitable），因此不能直接用于 await 表达式, 必须通过 async for 迭代
                async for chunk in graph.astream({'messages': ('user', user_input)}, config, stream_mode='values'):
                    result = print_message(chunk, result)
        else: # 用户输入 y 用户想继续工具的调用
            async for chunk in graph.astream(None,config,stream_mode='values'):
                result = print_message(chunk,result)

        current_state = graph.get_state(config)
        if current_state.next:  # 出现了工作流的中断
            ai_message = current_state.values['messages'][-1]
            tool_name = ai_message.tool_calls[0]['name']
            # ai_message.tool_calls[0]['args']
            result = f"AI助手马上根据你要求，执行{tool_name}工具。您是否批准继续执行？输入'y'继续；否则，请说明您理由。\n"
        return result


    # 执行工作流
    while True:
        user_input = input("用户：")
        res = await execute_graph(user_input)
        print("AI:",res)

if __name__ == '__main__':
    asyncio.run(run_graph())     # 仅仅需要在查询车票的时候调用工具触发中断 视频50
"""
$env:PYTHONUTF8="1"
langgraph dev
"""