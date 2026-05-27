from openai import OpenAI
from dotenv import load_dotenv
import os 
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com"
)

def get_weather(city: str) -> str:
    """模拟天气查询（实际项目里这里调用真实API）"""
    weather_data = {
        "深圳": "晴天，28度，湿度70%",
        "北京": "多云，22度，湿度45%",
        "上海": "小雨，20度，湿度85%"        
    }
    return weather_data.get(city, f"暂无{city}的天气数据")
def get_solace_queue_status(queue_name: str) -> str:
    """模拟查询Solace队列状态（结合你的工作背景）"""
    mock_data = {
        "HKJ_ORDER_QUEUE": "消息积压：230条，消费者数量：3，状态：正常",
        "HKJ_PAYMENT_QUEUE": "消息积压：0条，消费者数量：2，状态：正常",
        "HKJ_ALERT_QUEUE": "消息积压：8900条，消费者数量：0，状态：异常！"
    }
    return mock_data.get(queue_name, f"队列 {queue_name} 不存在")

tools = [
    {

        "type":"function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气情况",
            "parameters": {
                "type": "object",
                "properties":{
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：深圳、北京"
                    }
                },
                "required": ["city"] 
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_solace_queue_status",
            "description": "查询solace消息队列的当前状态",
            "parameters": {
                "type": "object",
                "properties":{
                    "queue_name":{
                        "type": "string",
                        "description": "队列名称，例如 hkj_order_queue"
                    }
                },
                "required": ["queue_name"]
            }
    }
    }
]
def chat_with_tools(user_message:str):
    print(f"\nuser:{user_message}")

    messages=[
        {"role": "system", "content": "你是一个运维助手,可以查询天气和solace队列状态。"},
        {"role": "user","content": user_message}
    ]
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    message = response.choices[0].message
    if message.tool_calls:
        print(f"LLM决定调用工具: {message.tool_calls[0].function.name}")

        tool_call = message.tool_calls[0]
        function_name=tool_call.function.name
        function_args=json.loads(tool_call.function.arguments)

        if function_name=="get_weather":
            result = get_weather(**function_args)
        elif function_name== "get_solace_queue_status":
            result=get_solace_queue_status(**function_args)
        
        print(f"函数执行结果：{result}")

        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

        final_response=client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        print(f"AI:{final_response.choices[0].message.content}")
    
    else:
        print(f"AI:{message.content}")
chat_with_tools("深圳今天天气怎么样?")
chat_with_tools("帮我查一下HKJ_ALERT_QUEUE的状态")
chat_with_tools("你叫什么名字?")