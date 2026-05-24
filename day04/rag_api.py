from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import shutil
import os

app = FastAPI()
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="solace_docs")

class QuestionRequest(BaseModel):
    question: str

class LoadRequest(BaseModel):
    filepath: str

@app.get("/")
def health_check():
    return {"status": "running", "message": "RAG Service is normal"}

@app.post("/load")
def load_document(req: LoadRequest):
    with open(req.filepath, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = [c.strip() for c in content.split("\n\n") if c.strip()]

    collection.delete(where={"exists": True}) if collection.count()> 0 else None 
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return {"message": f"loaded document successfully, tatol split cut to {len(chunks)}pieces"}

@app.post("/ask")
def ask_question(req: QuestionRequest):
    if collection.count() == 0:
        return {"error": "please load document first"}
    
    results = collection.query(
        query_texts=[req.question],
        n_results=2
    )
    context = "\n\n".join(results["documents"][0])
    messages=[
        {"role": "system","content": "你是文档助手，只根据提供的文档内容回答问题，不要编造。"},
        {"role": "user", "content": f"文档内容:\n {context} \n\n问题: {req.question}"}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    return {
        "question": req.question,
        "answer": response.choices[0].message.content,
        "source_chunks":results["documents"][0]
    }