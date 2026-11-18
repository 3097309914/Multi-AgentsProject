from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from agent.tools.tools_demo7 import MySearchTool
from agent.tools.tools_demo3 import calculation3
from agent.tools.tools_demo6 import runnable_tool
from agent.tools.tools_demo9 import get_user_name,greet_user
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
# $env:PYTHONUTF8="1"
# langgraph dev

# 在开发环境中使用内存来存储短期记忆,多轮对话的追踪
# checkpointer = InMemorySaver()    
DB_URI = "postgresql://postgres:123456@localhost:5432/langgraph_db"
   # 本地私有化部署的大模型
llm = ChatOpenAI(
    model='qwen3.8-27b',
    temperature=0.8,
    api_key='sk-JRRVTm2dgXSjnGtgE2Af9f4e547649FeBaC100D6F149825b',
    base_url="https://api.apiyi.com/v1",
    extra_body={'chat_template_kwargs': {'enable_thinking': True}},
)
with (
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    PostgresStore.from_conn_string(DB_URI) as store,
    ):
    # checkpointer.setup() # 第一次使用关系型数据库
    store.setup() # 第一次使用关系型数据库,已经有了可以注释
    # 创建一个网络搜索的工具
    search_tool = MySearchTool()
    graph = create_react_agent(
        llm,
        tools=[calculation3, runnable_tool, search_tool, get_user_name, greet_user],
        prompt="你是一个智能助手，尽可能地调用工具回答用户的问题！",
        checkpointer=checkpointer,
        store=store
    )

    config = {
        'configurable':{
            'thread_id': "1"
        }
    }
    # 从短期记忆存储中，返回当前所有会话的上下文
    rest = list(graph.get_state(config))
    # print(rest)
    # 从长期记忆存储中，返回当前所有会话的上下文
    rest2 = list(graph.get_state_history(config))
    print(rest2)

    resp1 = graph.invoke(
        {"messages":[{"role":"user","content":"给我一个关于相声的报幕词？"}]},
        config,
    )

    print(resp1['messages'][-1].content)

    resp2 = graph.invoke(
        {"messages":[{"role":"user","content":"在给我关于流行歌曲<<忐忑>>的？"}]},
        config,
    )

    print(resp2['messages'][-1].content)