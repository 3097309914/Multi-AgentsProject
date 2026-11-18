import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

"""
$env:PYTHONUTF8="1"
langgraph dev
"""
# 本地私有化部署的大模型
llm = ChatOpenAI(
    model='qwen3.8-27b',
    temperature=0.8,
    api_key='sk-JRRVTm2dgXSjnGtgE2Af9f4e547649FeBaC100D6F149825b',
    base_url="https://api.apiyi.com/v1",
    extra_body={'chat_template_kwargs': {'enable_thinking': True}},
)
test_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtdXNlciIsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3QiLCJpYXQiOjE3OTE5NjI3NDksImV4cCI6MTc5MTk2NjM0OSwiYXVkIjoibXktZGV2LXNlcnZlciIsInNjb3BlIjoicmVhZCB3cml0ZSJ9.fOyPx9HQCOBbDm0ksc50ZaN4rX8SC4Xbz-0C18-AUZCsOOBSLULC-TocY25WtLa5LVa0uq6aKehZg2j2whQVumPsZFWrx0r5QLZUBndB7CEilHYjazg2Zap6MBvhAPlaHqdyDf_x3xUAMpGvxOTvUyoLrLzpAw1QWC7093xIzwGk-fiLbGEjfgyI3Mw1Ryu_CWzY_inp6p-ZmGFheJub56oLIYUmfPsyLhXv5cBuT8pM5GvORQpcWrWiXu5DrZPHS4kxnsU_dUVTrIuYITi8cFoE8bZ994VdlR3fQaW-KONGQj-T2LM3iEsecB6mZF1dMWGKc92l8hCKv7QVwlFnBw"

# Python MCP服务端的连接配置
python_mcp_server_config = {
    # "url":"http://127.0.0.1:8080/sse",
    # "transport":"sse",
    "url":"http://127.0.0.1:8080/streamable",
    "transport":"streamable_http",
    "headers":{
        "Authorization": f"Bearer {test_token}"
    }
}

# Java MCP服务端的连接配置
# java_mcp_server_config = {
#     "url":"http://127.0.0.1:8086/sse",
#     "transport":"sse",
#     # "url":"http://127.0.0.1:8080/streamable",
#     # "transport":"streamable_http",
# }

# 外网 MCP服务端的连接配置 视频 8 MCP认证机制
zhipuai_mcp_server_config = {
    "url":"https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp?Authorization=2c96d8bd32454d229e91dbc2cbf69f04.vYnko9tzZDYT9GMP",
    "transport":"streamable_http"
}

# {
#   "mcpServers": {
#     "zhipu-web-search-sse": {
#       "url": "https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp?Authorization=Your Zhipu API Key"
#     }
#   } 
# }

# mcp的客户端
mcp_client = MultiServerMCPClient(
    {
        'python_mcp':python_mcp_server_config,
        # 'zhipuai_mcp':zhipuai_mcp_server_config,
        # 'java_mcp':java_mcp_server_config,
    }
)

async def create_agent():
    """必须是异步函数中"""
    mcp_tools = await mcp_client.get_tools()
    print(mcp_tools)
    # p = await mcp_client.get_prompt(server_name="python_mcp",prompt_name="ask_about_topic",arguments={'topic':'深度学习'})
    # print(p)
    # data = await mcp_client.get_resources(server_name="python_mcp",uris="resource://config") # python_mcp是别名
    # print(data[0])
    # print(data[0].data) # JSON数据
    # return create_react_agent(
    #     llm,
    #     tools=mcp_tools,
    #     prompt="你是一个智能助手，尽可能地调用工具回答用户的问题！"
    # )
    agent = create_react_agent(
        llm,
        tools=mcp_tools,
        prompt="你是一个智能助手，尽可能地调用工具回答用户的问题！"
    )
    rest = await agent.ainvoke(
        {"messages":[{"role":"user","content":"今天,北京天气怎么样？"}]}
    )
    print(rest["messages"]) # AgentSate里面的内容
    print(rest["messages"][-1].content)


# agent = asyncio.run(create_agent())

if __name__ == '__main__':
    asyncio.run(create_agent())
# python G:\my_project\langgraph_demo\src\agent\mcp_agent2.py
