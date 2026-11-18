from fastmcp import FastMCP
from zhipuai import ZhipuAI
from fastmcp.server.auth.providers.jwt import RSAKeyPair,JWTVerifier
from fastmcp.server.dependencies import AccessToken,get_access_token


zhipuai_client = ZhipuAI(api_key="2c96d8bd32454d229e91dbc2cbf69f04.vYnko9tzZDYT9GMP") 

# 1、生成RSA的密钥对
key_pair = RSAKeyPair.generate()

# print(key_pair.public_key)

# 2、配置认证提供方
auth = JWTVerifier(
    public_key=key_pair.public_key,  # 公钥用于校验签名
    issuer="http://localhost",       # 令牌签发方标识
    audience="my-dev-server",        # 目标服务标识
)

# 3、服务器，模拟生成一个token
token = key_pair.create_token(
    subject="dev-user",
    issuer="http://localhost",
    audience="my-dev-server",
    scopes=["read", "write"],  # token中包含的数据
    expires_in_seconds=3600  # 1小时后过期
)
print(f'Token:{token}')


server = FastMCP(
    name='laoli_MCP',
    instructions='老李的python代码实现MCP服务器',
    auth=auth, # 服务用于校验token的
)

@server.tool(name='zhipuai_search')
def my_search(query:str) -> str:
    """搜索互联网上的内容，包括实时天气等"""
    try:
        print("执行我的Python中的工具，输入的参数为:", query)
        # 得到了验证通过之后的
        access_token: AccessToken = get_access_token()
        if access_token:
            print("<整个token:>",access_token)
            print(access_token.scopes)
        else:
            return "由于没有权限，所以不能搜索到任何内容，请客户端传入一个有效的token"
        response = zhipuai_client.web_search.web_search(
            search_engine="search_pro",
            search_query=query
            )
        # print(response)
        if response.search_result:
            return "\n\n".join([d.content for d in response.search_result])
        return '没有搜索到任何内容！'
    except Exception as e:
        print(e)
        return '没有搜索到任何内容！'
    

