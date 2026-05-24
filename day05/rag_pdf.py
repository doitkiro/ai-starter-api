from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
import fitz 
import os
import tempfile

load_dotenv()

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_docs")

class QuestionRequest(BaseModel):
    question:str

def extract_and_chunk(pdf_path: str, chunk_size: int = 500):
    doc = fitz.open(pdf_path)
    chunks = []
    metadatas = []
    doc=fitz.open(pdf_path)
    full_text = ""

    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if not text:
            continue
        # 按页切块，每页再按字符数细切
        for i in range(0, len(text), chunk_size - 50):
            chunk = text[i:i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
                metadatas.append({"page": page_num + 1})

    doc.close()
    return chunks, metadatas

@app.get("/")
def health_check():
    return {"status": "running", "dos_count": collection.count()}

@app.post("/upload")
async def upload_pdf(file:UploadFile=File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "only support PDF File"}
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path=tmp.name

    try:
      
        pdf_info = fitz.open(tmp_path)
        page_count = len(pdf_info)
        pdf_info.close()
        chunks, metadatas = extract_and_chunk(tmp_path)

        if collection.count() > 0:
            all_ids = collection.get()["ids"]
            collection.delete(ids=all_ids)

        collection.add(
            documents=chunks,
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            metadatas=metadatas
        )
        return {
          "filename": file.filename,
          "pages": page_count,
          "total_chunks": len(chunks),
          "message": "PDF已成功加载到知识库"
        }
    finally:
        os.unlink(tmp_path)

@app.post("/ask")
def ask_question(req:QuestionRequest):
    if collection.count() == 0:
        return {"error": "Please upload the PDF file first"}
    results = collection.query(
        query_texts=[req.question],
        n_results=3,
        include=["documents", "metadatas"]
    )
    context = "\n\n".join(results["documents"][0])

    messages = [
        {"role": "system", "content": "你是文档助手，只根据提供的文档内容回答，不要编造。如果文档中没有相关信息，直接说没有。"},
        {"role": "user", "content": f"文档内容:\n {context}\n\n问题:{req.question}"}
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    source_pages = [m["page"] for m in results["metadatas"][0]]
    return {
       "question": req.question,
       "answer": response.choices[0].message.content,
       "source_pages": source_pages
    }