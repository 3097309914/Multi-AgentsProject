from langchain_openai import ChatOpenAI
# F:\env_python\new_langgraph_env\Scripts
# (base) PS G:\my_project\langgraph_demo> (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; 
# (& f:\env_python\new_langgraph_env\Scripts\Activate.ps1)
# (new_langgraph_env) (base) PS G:\my_project\langgraph_demo> 
# qwen3.8-27b gpt-6.1-terra ， 工具的信息等组成的LLM支持的上下文环境的大小是不低于8KB
llm = ChatOpenAI(
    model='gpt-5.5',
    temperature=0.8,
    api_key='sk-ie6zdD00QM05lMjvAb44A2Cc9a35496dA30dA9E1Dd0c1168',
    base_url="https://api.apiyi.com/v1",
)

# https://open.bigmodel.cn/apikey/platform
# 外网 MCP服务端的连接配置 视频 8 MCP认证机制
zhipuai_mcp_server_config = {
    "url":"https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp?Authorization=2c96d8bd32454d229e91dbc2cbf69f04.vYnko9tzZDYT9GMP",
    "transport":"streamable_http"
}


# 外网 MCP服务端的连接配置 12306车票查询 https://www.modelscope.cn/mcp/servers/@Joooook/12306-mcp
my12306_mcp_server_config = {
    "url":"https://mcp.api-inference.modelscope.net/59d87c12a4ee4f/mcp",
    "transport":"streamable_http"
}


# 外网 MCP服务端的连接配置 可视化图表 MCP Server https://www.modelscope.cn/mcp/servers/antvis/mcp-server-chart
chart_mcp_server_config = {
    "url":"https://mcp.api-inference.modelscope.net/61549f869ee74a/mcp",
    "transport":"streamable_http"
}

# 外网 MCP服务端的连接配置 Fetch网页内容抓取 MCP Server  https://www.modelscope.cn/mcp/servers/@modelcontextprotocol/fetch
fetch_mcp_server_config = {
    "url":"https://mcp.api-inference.modelscope.net/a340bb82c5ac45/mcp",
    "transport":"streamable_http"
}

# 外网 MCP服务端的连接配置 高德地图 MCP Server https://www.modelscope.cn/mcp/servers/@amap/amap-maps
# https://console.amap.com/dev/user/info APIkey花钱

# 外网 MCP服务端的连接配置 Github MCP Server https://www.modelscope.cn/mcp/servers/@modelcontextprotocol/github 
# https://github.com/settings/personal-access-tokens  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
github_mcp_server_config = {
    "url":"https://mcp.api-inference.modelscope.net/f88b682bc08142/mcp",
    "transport":"streamable_http"
}

# Google搜索 https://www.modelscope.cn/mcp/servers/@adenot/mcp-google-search
# 外网 MCP服务端的连接配置 携程 MCP Server https://www.modelscope.cn/mcp/servers/mako2026/Trip.com-mcp
xiechen_mcp_server_config = {
    "url":"https://mcp.api-inference.modelscope.net/9f9a4d51edc74a/mcp",
    "transport":"streamable_http"
}
# 外网 MCP服务端的连接配置 Github的维基百科DeepWiKi MCP Server https://www.modelscope.cn/mcp/servers/@regenrek/mcp-deepwiki
deepwiki_mcp_server_config = {
    "url":"https://mcp.api-inference.modelscope.net/7022b04dab2e42/mcp",
    "transport":"streamable_http"
}

# 外网 MCP服务端的连接配置 agentNEWs MCP Server https://smithery.ai/servers/theagenttimes/news
agentnews_mcp_server_config = {
    "url":"https://theagenttimes.com/mcp",
    "transport":"streamable_http"
}

# 外网 MCP服务端的连接配置 微信开发者 MCP Server https://skillhub.cn/skills/tencent-adm/weixin-docs
wxdoc_mcp_server_config = {
    "url":"https://developers.weixin.qq.com/doc/mcp",
    "transport":"streamable_http"
}
