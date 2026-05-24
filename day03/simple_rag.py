import chromadb 
from openai import OpenAI
client = OpenAI(
    api_key="sk-bc548b5bbdc34047b2c1400135c64a56",
    base_url="https://api.deepseek.com"
)

chroma_client= chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(name="solace_docs")

def load_and_store(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content=f.read()
    chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
    print(f"document cut to {len(chunks)} pieces")

    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    print("all chunks have been saved to vector database")


def rag_answer(question):
    results = collection.query(
        query_texts=[question],
        n_results=2
    )
    relevant_chunks=results["documents"][0]
    context = "\n\n".join(relevant_chunks)
    print(f"检索的相关内容：\n{context}\n")
    messages = [
        {
            "role": "system",
            "content": "你是文档助手，只根据提供的文档内容回答，不要编造。"
        },
        {
            "role": "user",
            "content": f"文档内容：\n{context}\n\n问题:{question}"
        }
    ]
    response = client.chat.completions.create(
       model="deepseek-chat",
       messages=messages
    )
    return response.choices[0].message.content

load_and_store("solace_manual.txt")
questions = [
    # "消息堆积了怎么处理?",
    # "每天需要做哪些巡检?",
    # "队列命名有哪些规定？"
    "solace license 费用？"
]

for q in questions:
    print(f"问：{q}")
    answer=rag_answer(q)
    print(f"答:{answer}")
    print("=" *50 + "\n")