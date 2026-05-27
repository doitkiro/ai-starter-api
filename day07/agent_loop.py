from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def get_solace_queue_status(queue_name: str) -> str:
    mock_data = {
        "HKJ_ORDER_QUEUE": "积压：230条，消费者：3，状态：正常",
        "HKJ_PAYMENT_QUEUE": "积压：0条，消费者：2，状态：正常",
        "HKJ_ALERT_QUEUE": "积压：8900条，消费者：0，状态：异常！"
    }
    return mock_data.get(queue_name, f"队列 {queue_name} 不存在")

def send_alert(message: str) -> str:
    """模拟发送告警通知"""
    print(f"📢 告警已发送：{message}")
    return f"告警发送成功：{message}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_solace_queue_status",
            "description": "查询Solace消息队列状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "queue_name": {"type": "string", "description": "队列名称"}
                },
                "required": ["queue_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_alert",
            "description": "发送告警通知给运维团队",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "告警内容"}
                },
                "required": ["message"]
            }
        }
    }
]

def run_agent(user_message: str):
    print(f"\n用户：{user_message}")
    print("=" * 50)

    messages = [
        {"role": "system", "content": "你是一个智能运维Agent，可以查询队列状态，发现异常时主动发送告警。"},
        {"role": "user", "content": user_message}
    ]


    while True:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        if not message.tool_calls:
            print(f"\nAgent：{message.content}")
            break


        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"调用工具：{func_name}，参数：{func_args}")

            if func_name == "get_solace_queue_status":
                result = get_solace_queue_status(**func_args)
            elif func_name == "send_alert":
                result = send_alert(**func_args)
            else:
                result = "未知工具"

            print(f"工具结果：{result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })


run_agent("帮我检查HKJ_ALERT_QUEUE的状态，如果有问题就发送告警")