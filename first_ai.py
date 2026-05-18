from openai import OpenAI
client = OpenAI(
    api_key="sk-bc548b5bbdc34047b2c1400135c64a56",
    base_url="http://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个专业的技术顾问"},
        {"role": "user", "content": "用一句话解释什么是RAG技术"}
    ]
)

answer = response.choices[0].message.content
print(answer)