from langchain_core.tools import StructuredTool


def calculation5(a:float, b:float, operation: str) -> float:
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
# 异步函数定义
async def calculation6(a:float, b:float, operation: str) -> float:
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

# 结构化工具变为工具
calculater = StructuredTool.from_function(
    func=calculation5,
    name="calculation5",
    description="工具函数：计算两个数字的运算结果",
    return_direct=False,
    coroutine=calculation6 
)

print(calculater.description)
