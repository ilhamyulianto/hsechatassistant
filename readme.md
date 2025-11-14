# **HSE Chat Assistant — System Architecture**

![alt text](https://github.com/ilhamyulianto/hsechatassistant/blob/main/materials/image/hsechat.png)

This document describes the architectural structure, components, and data flow of the **HSE Chat Assistant**, a Retrieval-Augmented Generation (RAG) system deployed inside a secure corporate environment.  
The system provides accurate, document-grounded answers to Health, Safety & Environment (HSE) queries.

---

## 1. Architectural Overview

The system is composed of three major layers:

1. **Frontend Layer**  
   - Browser-based chat UI  
   - Communicates with FastAPI over HTTPS  

2. **Application Layer (Backend)**  
   - FastAPI server hosting API endpoints  
   - RAG orchestration logic (retrieval + prompt construction)  
   - Vector Database (FAISS or Qdrant)  

3. **Inference Layer (LLM Server)**  
   - Dedicated Ollama server  
   - Hosts Llama3.1:8B and embedding models  
   - Provides local, offline inference for generation and embeddings  

The architecture is optimized for **security**, **traceability**, and **enterprise-scale maintainability**.

---

## 2. Component Diagram

```
End User
   │
   ▼
Web Browser UI
   │ (HTTPS)
   ▼
FastAPI Server
   │
   ├── RAG Logic
   │      ├── Embeddings (via LLM Server)
   │      ├── Retrieval (FAISS)
   │      └── Prompt Construction
   │
   └── Response Formatting
   │
Vector DB (FAISS)
   │
   ▼
LLM Server (Ollama)
   ├── Llama3.1:8B (Generation)
   └── mxbai-embed-large (Embeddings)
```

---

## 3. Detailed Components

### 3.1 Frontend Layer
- Simple HTML/CSS/JS UI.
- Sends POST requests to `/api/chat`.
- Displays model responses and source citations.
- Accessible only on the corporate intranet (after SSO).

---

### 3.2 FastAPI Backend

**Responsibilities:**
- Validate queries.
- Interact with the RAG logic.
- Call vector database for retrieval.
- Call LLM server for inference.
- Format and return structured JSON responses.

**Key File:** `main.py`

Contains:
- API routes (`/`, `/api/chat`)
- Templating setup
- JSON responses for chat messages

FastAPI serves as the gateway between the user and the RAG pipeline.

---

### 3.3 RAG Logic Layer

**File:** `rag.py`

**Responsibilities:**
1. **Embed the question**  
   - Uses Ollama embeddings (`mxbai-embed-large`)
2. **Retrieve relevant HSE context**  
   - Top-k document chunks via FAISS similarity search
3. **Construct the RAG prompt**  
   - Inject retrieved text directly into prompt template
4. **Call LLM Server**  
   - Local Llama3.1:8b for grounded instruction following
5. **Return answer + metadata**  
   - Includes source PDF name, page number, content snippet

**Why RAG?**
- Ensures answers are grounded in HSE documentation  
- Prevents hallucinations  
- Enforces compliance with official procedures  
- Enables traceability

---

### 3.4 Vector Database (FAISS)

FAISS stores:
- Document chunk embeddings  
- Chunk text  
- Metadata (pdf name, page number)

**Why FAISS?**
- Fast similarity search  
- Efficient for local intranet deployments  
- Zero infrastructure overhead  
- Works with Ollama embedding vectors seamlessly

**Structure Example:**
```
faiss_index/
   ├── index.faiss
   └── index.pkl
```

---

### 3.5 LLM Server (Ollama)

**Responsibilities:**
- Serve prompts and embeddings via HTTP
- Provide offline inference with local models
- Host multiple models for multi-purpose use

**Typical models:**
- **Llama 3.1:8B** → Answer generation  
- **mxbai-embed-large** → Embedding generation  

**API endpoints exposed:**
- `/api/chat`
- `/api/embeddings`

**Deployment:**
Runs on a dedicated internal VM or server.  
The main backend contacts it via:

```
http://ollama-server.internal:11434
```

This allows **shared usage** across multiple applications.

---

## 4. PDF's context processing

The PDF processing is separate from production runtime.

**File:** `ingest.py`

**Steps:**
1. Load HSE PDF documents  
2. Extract and clean text  
3. Split into chunked segments  
4. Generate embeddings (via Ollama)  
5. Build FAISS index  
6. Export index folder for deployment

**Deployment:**
- PDF processing runs OFFLINE on a local machine or data VM  
- Output index (`faiss_index_vX/`) is uploaded to production  
- FastAPI loads the new index at startup  
- Production system remains read-only and stable

This ensures safe, controlled updates of knowledge.

---

## 5. Runtime Sequence Flow
![alt text](https://github.com/ilhamyulianto/hsechatassistant/blob/main/materials/image/mermaid-diagram-2025-11-14-102353.png)

### User Query → Final Answer

```
1. User enters question in browser
2. Browser POST → /api/chat
3. FastAPI receives question
4. RAG logic:
      a. embed(question)
      b. similarity_search in FAISS
      c. select top-k chunks
      d. build RAG prompt
5. FastAPI → LLM server → generates answer
6. RAG adds citations
7. FastAPI returns JSON: { answer, sources }
8. Browser displays output
```

This ensures every response is:
- Context-grounded  
- Traceable to specific PDF pages  
- Safe and compliant  

---




