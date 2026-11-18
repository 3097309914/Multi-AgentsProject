from langgraph_sdk import get_client
import asyncio

# 调用agent发布的API接口地址
client = get_client(url="http://localhost:2024")

# 异步调用
async def main():
    async for chunk in client.runs.stream(
        None,  # Threadless run
        "agent", # Name of assistant. Defined in langgraph.json.
        input={
        "messages": [{
            "role": "human",
            "content": "给当前用户一个祝福语",
            }],
        },
        # stream_mode="messages",
        stream_mode="messages-tuple",  
        # stream_mode="updates", 
        config={"configurable": {"user_name": "老李"}}
    ):
        # print(f"Receiving new event of type: {chunk.event}...")
        # print(chunk.data)
        if isinstance(chunk.data, list) and 'type' in chunk.data[0] and chunk.data[0]["type"] == "AIMessageChunk":
            print(chunk.data[0]["content"],end="|")
        # print("\n\n")
if __name__ == '__main__':
    asyncio.run(main())


