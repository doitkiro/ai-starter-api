from  openai import OpenAI

client = OpenAI(
    api_key="sk-bc548b5bbdc34047b2c1400135c64a56",
    base_url="https://api.deepseek.com"
)

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
    
def ask_about_doc(doc_content, question):
    messages=[
       { "role": "system",
        "content": "你是一个文档助手，只根据用户提供的文档内容回答问题，不要编造文档中没有的信息。"
       },
       {
           "role": "user",
           "content": f"""请根据以下文档内容回答我的问题。

文档内容:
{doc_content}

我的问题: {question}"""
       }
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    return response.choices[0].message.content

doc = read_file("solace_manual.txt")
print(f"document has been load, total {len(doc)}char\n")

questions = [
    "队列名称有什么命名规范？",
    "消息堆积超过多少条需要处理？处理步骤是什么？",
    "每周需要检查什么？"
]

for q in questions:
    print(f"问： {q}")
    answer = ask_about_doc(doc, q)
    print(f"答： {answer}\n")
    print("-" * 40 +"\n")