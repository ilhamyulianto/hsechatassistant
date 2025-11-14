from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama

INDEX_DIR   = "faiss_index"          
EMBED_MODEL = "mxbai-embed-large"    
LLM_MODEL   = "llama3.1:8b"         


def load_retriever():
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vs = FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vs.as_retriever(search_kwargs={"k": 4})



retriever = load_retriever()

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0.1,
)

RAG_TEMPLATE = """kamu adalah HSE Chat assistant untuk membantu pelatihan awak kapal, jawab sesuai context.

Context:
{context}

Question:
{question}

Jawab dengan jelas dan ringkas dan dalam bahasa indonesia, jika jawaban tidak ada dalam konteks, improvisasi sedikit jawaban dengan informasi yang didapatkan,
tidak perlu menyampaikan asal halaman, tulis dengan paragraf atau bullet points yang sesuai.
"""


def format_docs(docs) -> str:
    return "\n\n".join(
        f"[Source: {d.metadata.get('source', '')}, page {d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    )


def answer_question(question: str):
    # 1) Retrieve relevant chunks
    docs = retriever.invoke(question)

    # 2) Build prompt
    context = format_docs(docs)
    prompt = RAG_TEMPLATE.format(context=context, question=question)

    # 3) Call Ollama LLM via LangChain
    response = llm.invoke(prompt)

    # 4) Extract answer text
    answer_text = getattr(response, "content", str(response))

    # 5) Prepare sources metadata
    sources = [
        {
            "source": d.metadata.get("source", "PDF"),
            "page": d.metadata.get("page", None),
            "snippet": d.page_content[:200] + "..."
        }
        for d in docs
    ]

    return answer_text, sources
