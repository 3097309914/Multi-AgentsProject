from langchain_core.tools import tool 
from langchain_core.tools import tool 
from langchain_core.runnables import RunnableConfig

@tool('get_user_info_by_name', return_direct=False)
def get_user_info_by_name(config:RunnableConfig) -> float:
    """获取用户的所有信息，包括：性别、年龄等"""
    user_name = config["configurable"].get('user_name', 'zhangsan')
    print(f"调用工具，传入的用户名是: {user_name}")
    # 模拟
    return {'user_name': user_name, 'gender': '男', 'age': 18}