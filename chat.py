from openai import OpenAI

client = OpenAI(
    api_key="sk-bc548b5bbdc34047b2c1400135c64a56",
    base_url="https://api.deepseek.com"
)

messages = [
    {"role": "system", "content": "你是一个AI开发学习助手，帮助用户学习AI应用开发"}
]

print("===AI助手启动， 输入quit 退出 ===\n")

while True:
    user_input = input("you:")

    if user_input.lower() == "quit":
        print("conversation is done")
        break
    
    if not user_input.strip():
        continue

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print(f"\nAI: {reply}\n")
    except Exception as e:
        print(f"error: {e}")