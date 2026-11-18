from langchain_core.tools import tool 
from pydantic import Field
from typing import Annotated


@tool('calculate3', return_direct=False)
def calculation3(
    a:Annotated[float, Field(description="第一个数字")], 
    b:Annotated[float, Field(description="第二个数字")], 
    operation: Annotated[str, Field(description="运算类型只能是add、subtract、multiply或divide中的任意一个")]) -> float:
    """工具函数：计算两个数字的运算结果"""
    print(f"调用 calculation工具: 一个数字：{a}, 第二个数字：{b}, 运算类型：{operation}")

    result = 0.0
    match operation:
        case "add":
            result = a + b
        case "subtract":
            result = a - b
        case "multiply":
            result = a * b
        case "divide":
            if b != 0:
                result = a / b
            else:
                raise ValueError("除数不能为零")
        case _:
            raise ValueError("不支持的运算类型")
    return result

# print(calculation3.name)
# print(calculation3.description)
# print(calculation3.args)
# print(calculation3.args_schema.model_json_schema())
# print(calculation3.return_direct)

# 调用 工具calculation3
# print(calculation3.invoke({"a": 40, "b": 2, "operation": "multiply"}))