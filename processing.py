import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

PDF_PATH = "books\source_hse.pdf"           
INDEX_DIR = "faiss_index"  
EMBED_MODEL = "mxbai-embed-large"   

def load_single_pdf(pdf_path: str):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    # tag the source nicely
    for d in docs:
        d.metadata["source"] = os.path.basename(pdf_path)
    return docs

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    return splitter.split_documents(docs)

def build_index():
    print(f"loading PDF: {PDF_PATH}")
    docs = load_single_pdf(PDF_PATH)
    print(f"loaded {len(docs)} pages")

    print("splitting to chunks")
    chunks = split_docs(docs)
    print(f"created {len(chunks)} chunks")

    print("creare embeddings")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    print("build index")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    print(f"save index {INDEX_DIR}")
    vectorstore.save_local(INDEX_DIR)
    print("dah")

if __name__ == "__main__":
    build_index()