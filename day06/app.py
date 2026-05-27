import streamlit as st 
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import fitz
import os
import tempfile

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

chroma_client=chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_docs")

def extract_and_chunk(pdf_path, chunk_size=500):
    doc = fitz.open(pdf_path)
    chunks,metadatas = [],[]
    for page_num,page in enumerate(doc):
        text = page.get_text().strip()
        if not text:
            continue
        for i in range(0,len(text), chunk_size-50):
            chunk = text[i:i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
                metadatas.append({"page": page_num+1})
    doc.close()
    return chunks, metadatas

def rag_answer(question):
    results = collection.query(
        query_texts=[question],
        n_results=3,
        include=["documents", "metadatas"]
    )
    context = "\n\n".join(results["documents"][0])
    pages = [m["page"] for m in results ["metadatas"][0]]

    messages = [
        {"role": "system", "content":"你是文档助手，只根据提供的文档内容回答,不要编造. 如果没有相关信息，直接说没有."},
        {"role": "user", "content": f"文档内容：\n{context}\n\n问题: {question}"}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    return response.choices[0].message.content, pages

st.title("PDF只能问答系统")

uploaded_file = st.file_uploader("上传PDF文件", type="pdf")

if uploaded_file:
    if st.button("加载文档"):
        with st.spinner("正在解析PDF..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path=tmp.name

            chunks,metadatas=extract_and_chunk(tmp_path)
            os.unlink(tmp_path)

            if collection.count()>0:
                all_ids = collection.get()["ids"]
                collection.delete(ids=all_ids)
            collection.add(
                documents=chunks,
                ids=[f"chunk_{i}"for i in range(len(chunks))],
                metadatas=metadatas
            )
        st.success(f"completed loading, total {len(chunks)} text blocks")

st.divider()
question = st.text_input("输入你的问题")

if st.button("提问") and question:
    if collection.count()==0:
        st.warning("please upload PDF file first")
    else:
        with st.spinner("thinking..."):
            answer, pages=rag_answer(question)
        
        st.markdown("**answer:**")
        st.write(answer)
        st.caption(f"source reference from: page {pages}")