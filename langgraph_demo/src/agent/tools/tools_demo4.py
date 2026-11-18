from langchain_core.tools import tool 

@tool('calculate4', parse_docstring=True, return_direct=False)
def calculation4(a:float, b:float, operation: str) -> float:
    """工具函数：计算两个数字的运算结果
    
    Args:
        a (float): 第一个数字
        b (float): 第二个数字
        operation (str): 运算类型，只能是add、subtract、multiply或divide中的任意一个

    Returns:
        float: 运算结果
    """
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

print(calculation4.name)
print(calculation4.description)
print(calculation4.args)
print(calculation4.args_schema.model_json_schema())
print(calculation4.return_direct)
