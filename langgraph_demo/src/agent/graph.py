from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from typing import Literal, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END, START
from agent.llm_mcp_server_config import llm

# # qwen3.8-27b gpt-6.1-terra
# llm = ChatOpenAI(
#     model='gpt-5.5',
#     temperature=0.8,
#     api_key='sk-ie6zdD00QM05lMjvAb44A2Cc9a35496dA30dA9E1Dd0c1168',
#     base_url="https://api.apiyi.com/v1",
# )

# 定义图状态结构（使用TypedDict实现类型安全）
class State(TypedDict):
    joke: str          # 生成的冷笑话内容 定义的是字典中的key值，value在工作流中修改，所有的智能体的状态State的数据结构都是字典类型的。
    topic: str         # 用户指定的主题
    feedback: str      # 改进建议
    funny_or_not: str  # 幽默评级

# 结构化输出模型 （用于LLM评估反馈）scheme 大模型支持 结构化输出with_structured_output()
class Feedback(BaseModel):
    """使用此工具来结构化你的响应"""
    grade: Literal["funny", "not funny"] = Field(
        description="判断笑话是否幽默",
        examples=["funny", "not funny"]
    )
    feedback: str = Field(
        description="若不幽默，提供改进建议",
        example="可以加入双关语或意外结局"
    )

# 节点函数
def generator_func(state: State) -> dict:
    """LLM生成笑话节点"""
    prompt = (
        f"根据反馈改进笑话：{state['feedback']}\n主题：{state['topic']}"
        if state.get("feedback")
        else f"创作一个关于{state['topic']}的笑话"
    )
    # 第一种
    resp = llm.invoke(prompt) # 返回值是 AIMessage 对象, 更新到State的joke这个键 就是resp的内容
    return {"joke": resp.content}
    # # 第二种
    # chain = llm | StrOutputParser()
    # resp = chain.invoke(prompt) # 输出的解析器AIMessage 对象的字符串，就是一个字符串
    # return {"joke": resp}


# 节点函数
def evaluator_func(state: State) -> dict:
    """LLM笑话评估节点 结构化输出"""
    # 第一种大模型支持结果化输出的模型 openAI 
    chain = llm.with_structured_output(Feedback)
    resp = chain.invoke(
        f"评估此笑话的幽默程度：\n{state['joke']}\n"
        "注意：幽默应包含意外性或巧妙措辞"
    ) # 返回的是Feedback对象的属性
    return {
        "funny_or_not": resp.grade,
        "feedback": resp.feedback
    }
    # # 第二种大模型不支持结果化输出的模型
    # chain = llm.bind_tools([Feedback])
    # evaluation = chain.invoke(
    #     f"评估此笑话的幽默程度：\n{state['joke']}\n"
    #     "注意：幽默应包含意外性或巧妙措辞"
    # )
    # evaluation = evaluation.tool_calls[-1]['args'] # 返回的是一个字典
    # return {
    #     "funny_or_not": evaluation['grade'],
    #     "feedback": evaluation['feedback']
    # }

# 条件边的路由函数 ， 下一个节点的名称的字符串
def route_func(state: State) -> str:
    """动态路由决策（基于评估结果）"""
    return "Accepted" if state.get("funny_or_not", None) == "funny" else "Rejected + Feedback"
    # return END if state.get("funny_or_not", None) == "funny" else "generator" # 上面需要映射字典 "Accepted" == END

# 构建工作流（使用StateGraph）
builder = StateGraph(State)

# 添加节点（可替换为MCP工具[5](@ref)）
builder.add_node('generator',generator_func)
builder.add_node('evaluator',evaluator_func)

builder.add_edge(START,'generator')
builder.add_edge('generator','evaluator')
builder.add_conditional_edges(
    'evaluator',
    route_func,
    {
        "Accepted": END,  # 合格则结束
        "Rejected + Feedback": "generator"  # 不合格则循环优化
    }
)

# 编译工作流（可导出为MCP服务[6](@ref)） 非手动时候 langgraph dev 使用在配置文件 langgraph.json文件     "agent": "./src/agent/graph.py:graph"
graph = builder.compile()

# 执行示例（主题可动态替换）
result = graph.invoke({"topic": "程序员"})
print(f"最终笑话：{result['joke']}")

