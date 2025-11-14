#app
import streamlit as st
import faiss, numpy as np, pickle, ollama
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="SPIL University: HSE Learning Assistant", layout="wide", page_icon="materials\image\spil-logo-removebg-preview.png")
st.title("SPIL UNIVERSITY - HSE TRAINING CHAT ASSISTANT")

#load data
@st.cache_resource
def load_system():
    model = SentenceTransformer("intfloat/multilingual-e5-base")
    index = faiss.read_index("faiss\hse_faiss.index")
    with open("faiss\hse_chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return model, index, chunks

embed_model, index, chunks = load_system()

def rag_query(query, top_k=5):
    query_emb = embed_model.encode([query]).astype("float32")
    D, I = index.search(query_emb, top_k)
    context = "\n".join([chunks[i] for i in I[0]])
    prompt = f"""
Anda adalah asisten pelatihan HSE untuk awak kapal.
Gunakan konteks di bawah ini untuk menjawab pertanyaan dengan bahasa Indonesia yang jelas dan informatif.

KONTEKS:
{context}

PERTANYAAN:
{query}

JAWABAN:
"""
    response = ollama.chat(model="llama3.1:8b", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


user_input = st.chat_input("Tanyakan sesuatu seputar HSE...")
if user_input:
    with st.spinner("Menjawab..."):
        answer = rag_query(user_input)
    st.chat_message("user").write(user_input)
    st.chat_message("assistant").write(answer)
