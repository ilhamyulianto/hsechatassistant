from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from rag import answer_question  


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    history: List[Dict[str, Any]] | None = None


class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Dict[str, Any]]


conversations_db: Dict[str, Conversation] = {}
@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
   
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    q = (payload.message or "").strip()
    if not q:
        return JSONResponse({"response": "Please enter a message."}, status_code=400)

    answer, sources = answer_question(q)

    conv_id = payload.conversation_id or "default"
    if conv_id not in conversations_db:
        conversations_db[conv_id] = Conversation(
            id=conv_id,
            title=q[:30] + ("..." if len(q) > 30 else ""),
            messages=[],
        )
    conversations_db[conv_id].messages.append({"content": q, "isUser": True})
    conversations_db[conv_id].messages.append({"content": answer, "isUser": False})

    return JSONResponse({
        "response": answer,
        "conversation_id": conv_id,
        "sources": sources,
    })


@app.get("/api/conversations")
async def get_conversations():
    return [
        {
            "id": conv.id,
            "title": conv.title,
            "messages": conv.messages,
            "timestamp": "2025-01-01T00:00:00Z",  
        }
        for conv in conversations_db.values()
    ]


@app.post("/api/conversations")
async def save_conversation(conversation: Conversation):
    conversations_db[conversation.id] = conversation
    return {"status": "ok"}

