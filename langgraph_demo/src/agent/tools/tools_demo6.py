from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel,Field
from langchain_openai import ChatOpenAI

class ToolArgs(BaseModel):
    topic: str = Field(description="报幕词的主题")
    language: str = Field(description="报幕词采用的语言")

prompt = (
    PromptTemplate.from_template("帮我生成一个简短的，关于{topic}的报幕词")
    + ",要求1,内容搞笑一点"
    + "2.输出内容采用{language}。"
)

llm = ChatOpenAI(
    model='qwen3.8-27b',
    temperature=0.8,
    api_key='sk-JRRVTm2dgXSjnGtgE2Af9f4e547649FeBaC100D6F149825b',
    base_url="https://api.apiyi.com/v1",
    extra_body={'chat_template_kwargs': {'enable_thinking': True}},
)
chain = prompt | llm | StrOutputParser()

runnable_tool = chain.as_tool(
    name='chain_tool',
    description='一个可以生成报幕词的工具',
    args_schema=ToolArgs
)
# print(runnable_tool.args_schema.model_json_schema())
# print(runnable_tool.description)
# print(runnable_tool.name)

