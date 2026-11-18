from langchain_core.tools import tool 
@tool(return_direct=True)
def calculation(a:float, b:float, operation: str) -> float:
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

print(calculation.name)
print(calculation.description)
print(calculation.args)
print(calculation.args_schema.model_json_schema())
print(calculation.return_direct)
